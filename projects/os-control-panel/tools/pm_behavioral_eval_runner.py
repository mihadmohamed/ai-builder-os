from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
CASES_FILE = PROJECT_ROOT / "evals" / "pm_behavioral_cases.json"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pm_behavioral_evals import (  # noqa: E402
    aggregate_pm_trials,
    billing_boundary,
    build_fingerprints,
    grade_pm_behavior,
    load_pm_behavior_catalog,
    require_live_authorization,
)


def _fingerprints(dataset_payload: object, model_label: str):
    return build_fingerprints(
        dataset_payload=dataset_payload,
        prompt_payload=(REPO_ROOT / "agent" / "roles" / "pm.md").read_text(encoding="utf-8"),
        tool_policy_payload=(SRC_ROOT / "agents_runtime" / "support.py").read_text(encoding="utf-8"),
        guardrail_payload=(SRC_ROOT / "pm_guardrails.py").read_text(encoding="utf-8"),
        model_label=model_label,
    )


def run_pm_behavioral_evals(
    *,
    backend: str = "deterministic",
    model_label: str = "deterministic-fixture-v1",
    trials_per_case: int = 3,
    live: bool = False,
    billing_acknowledged: bool = False,
    trial_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    require_live_authorization(
        backend=backend,
        live=live,
        billing_acknowledged=billing_acknowledged,
    )
    dataset_payload = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    dataset_version, cases = load_pm_behavior_catalog(CASES_FILE)
    by_id = {case.case_id: case for case in cases}
    grades = []
    if backend == "deterministic":
        if trials_per_case < 1:
            raise ValueError("trials_per_case must be positive")
        for case in cases:
            for _ in range(trials_per_case):
                grades.append(grade_pm_behavior(case, case.mock_trial))
    else:
        if not trial_records:
            raise ValueError(
                "Live PM evaluation requires host-produced trial records. Export the typed trial records from the "
                "Codex task or authorized Agents SDK run and pass --trial-file."
            )
        for record in trial_records:
            case_id = str(record.get("case_id", ""))
            if case_id not in by_id or not isinstance(record.get("trial"), dict):
                raise ValueError(f"Invalid live PM trial record for case {case_id!r}")
            grades.append(grade_pm_behavior(by_id[case_id], record["trial"]))
    return aggregate_pm_trials(
        dataset_version=dataset_version,
        backend=backend,
        model_label=model_label,
        fingerprints=_fingerprints(dataset_payload, model_label),
        grades=grades,
    )


def _load_trial_file(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Live trial file must contain a JSON list")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic or explicitly authorized live PM behavioral evaluations."
    )
    parser.add_argument("--backend", choices=("deterministic", "codex", "agents-sdk"), default="deterministic")
    parser.add_argument("--model-label", default="deterministic-fixture-v1")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--live", action="store_true", help="Required for model-backed Codex or Agents SDK trials.")
    parser.add_argument(
        "--acknowledge-billing",
        action="store_true",
        help="Confirms the displayed backend usage boundary; this is not an external-action approval.",
    )
    parser.add_argument("--trial-file", default="", help="Host-produced typed live trial records.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = run_pm_behavioral_evals(
            backend=args.backend,
            model_label=args.model_label,
            trials_per_case=args.trials,
            live=args.live,
            billing_acknowledged=args.acknowledge_billing,
            trial_records=_load_trial_file(args.trial_file) if args.trial_file else None,
        )
    except (OSError, ValueError, PermissionError, json.JSONDecodeError) as exc:
        print(f"BLOCKED PM behavioral eval — {exc}")
        print(f"BILLING: {billing_boundary(args.backend)}")
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for case_id, result in report["cases"].items():
            status = "PASS" if result["threshold_passed"] else "FAIL"
            print(f"{status} {case_id} — {result['trials']} trials, {result['pass_rate']:.0%} pass rate")
        print(f"BILLING: {report['billing_boundary']}")
        print(
            f"SUMMARY: {report['overall']['cases']} cases, {report['overall']['trials']} trials, "
            f"{report['overall']['pass_rate']:.0%} passing"
        )
    return 0 if report["overall"]["threshold_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

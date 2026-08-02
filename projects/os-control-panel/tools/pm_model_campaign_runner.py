from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
CASES_FILE = PROJECT_ROOT / "evals" / "pm_behavioral_cases.json"
for path in (SRC_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from pm_behavioral_evals import load_pm_behavior_catalog  # noqa: E402
from pm_model_selection import (  # noqa: E402
    PMCandidateReport,
    load_pm_model_configuration,
    materialize_selected_configuration,
    select_pm_model,
)
from pm_live_campaign import build_live_campaign_manifest  # noqa: E402


def _load_reports(path: str) -> list[PMCandidateReport]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("PM report file must contain a JSON list")
    return [PMCandidateReport.model_validate(item) for item in payload]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and grade the R101 PM model campaign without silently invoking a live backend."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    manifest = subparsers.add_parser("manifest", help="Generate a deterministic, unauthorized work manifest.")
    manifest.add_argument("--stage", choices=("sentinel", "full"), default="sentinel")
    manifest.add_argument("--qualifying", action="append", default=[])
    live_sentinel = subparsers.add_parser(
        "run-sentinel",
        help="Run only the explicitly authorized 20-item Agents SDK sentinel batch.",
    )
    live_sentinel.add_argument("--batch-id", required=True)
    live_sentinel.add_argument("--authorization-scope", required=True)
    live_sentinel.add_argument("--live", action="store_true")
    live_sentinel.add_argument("--acknowledge-api-billing", action="store_true")
    live_sentinel.add_argument("--max-estimated-cost-usd", required=True, type=float)
    live_sentinel.add_argument("--max-output-tokens", type=int, default=6000)
    selection = subparsers.add_parser("select", help="Evaluate imported provider-reported live candidate reports.")
    selection.add_argument("--reports", required=True)
    selection.add_argument("--show-proposed-config", action="store_true")
    args = parser.parse_args()

    config = load_pm_model_configuration()
    _, cases = load_pm_behavior_catalog(CASES_FILE)
    try:
        if args.command == "manifest":
            payload = build_live_campaign_manifest(
                config,
                list(cases),
                stage=args.stage,
                qualifying_candidate_ids=args.qualifying,
            )
        elif args.command == "run-sentinel":
            if not args.live or not args.acknowledge_api_billing:
                raise PermissionError(
                    "Live sentinel execution requires both --live and --acknowledge-api-billing"
                )
            from pm_live_campaign import campaign_result_path, run_authorized_sentinel

            payload = run_authorized_sentinel(
                project_name="os-control-panel",
                batch_id=args.batch_id,
                authorization_scope=args.authorization_scope,
                billing_acknowledged=args.acknowledge_api_billing,
                max_estimated_cost_usd=args.max_estimated_cost_usd,
                max_output_tokens=args.max_output_tokens,
            )
            payload = {
                "batch_id": payload["batch_id"],
                "status": payload["status"],
                "attempted_work_items": len(payload.get("attempts", [])),
                "completed_evaluation_trials": len(payload["trials"]),
                "accounting": payload.get("accounting", {}),
                "estimated_cost_usd": payload.get(
                    "estimated_cost_usd",
                    round(
                        sum(
                            float(item.get("estimated_cost_usd", 0.0))
                            for item in payload.get("attempts", [])
                        ),
                        8,
                    ),
                ),
                "candidate_summaries": {
                    key: {
                        field: value
                        for field, value in summary.items()
                        if field != "behavior_report"
                    }
                    for key, summary in payload.get("candidate_summaries", {}).items()
                },
                "result_path": str(campaign_result_path("os-control-panel", args.batch_id)),
            }
        else:
            reports = _load_reports(args.reports)
            decision = select_pm_model(config, reports, case_count=len(cases))
            payload = {"decision": decision.model_dump(mode="json")}
            if args.show_proposed_config:
                payload["proposed_configuration"] = materialize_selected_configuration(
                    config, decision, reports
                ).model_dump(mode="json")
    except (OSError, ValueError, PermissionError, json.JSONDecodeError) as exc:
        print(f"BLOCKED PM model campaign — {exc}")
        return 2

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

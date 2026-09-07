from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
for candidate in (PROJECT_SRC, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from codex_telemetry import ingest_codex_local_session, ingest_codex_otel  # noqa: E402


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Import privacy-safe Codex telemetry into the private AI Builder OS runtime store."
    )
    value.add_argument("--project", required=True, help="Registered AI Builder OS project name.")
    value.add_argument("--source", choices=("otel", "local-session"), required=True)
    value.add_argument("--input", type=Path, required=True, help="OTLP JSON or Codex rollout JSONL file.")
    value.add_argument(
        "--accepted-fingerprint",
        action="append",
        default=[],
        help="Optional approved local-session schema fingerprint; repeat for multiple fingerprints.",
    )
    value.add_argument("--disabled", action="store_true", help="Exercise the independently disabled adapter state.")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.source == "otel":
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = ingest_codex_otel(args.project, payload, enabled=not args.disabled)
    else:
        with args.input.open("r", encoding="utf-8") as handle:
            result = ingest_codex_local_session(
                args.project,
                handle,
                enabled=not args.disabled,
                accepted_fingerprints=set(args.accepted_fingerprint) or None,
            )
    # Counts and opaque record identities are safe operator diagnostics. Raw input is never echoed.
    print(json.dumps({
        "source": result.source,
        "availability": result.availability,
        "adapter_version": result.adapter_version,
        "accepted": len(result.accepted_ids),
        "duplicates": len(result.duplicate_ids),
        "quarantined": len(result.quarantined_ids),
        "ignored": result.ignored_count,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

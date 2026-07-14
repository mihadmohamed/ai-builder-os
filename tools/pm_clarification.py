from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    create_pm_clarification,
    load_pm_clarification_store,
    resolve_pm_clarification_in_store,
)
from project_registry import resolve_project


def _clarification_path(project_name: str) -> Path:
    return resolve_project(project_name).workspace_path / "data" / "pm_clarifications.json"


def create_command(args: argparse.Namespace) -> int:
    clarification = create_pm_clarification(
        _clarification_path(args.project_name),
        project_name=args.project_name,
        requirement_id=args.requirement_id,
        requirement_title=args.requirement_title,
        summary=args.summary,
        questions=args.question,
    )
    print(f"CREATED {clarification['clarification_id']}")
    print(f"PROJECT {clarification['project_name']}")
    print(f"REQUIREMENT {clarification['requirement_id']}")
    print(f"SUMMARY {clarification['summary']}")
    return 0


def list_command(args: argparse.Namespace) -> int:
    items = load_pm_clarification_store(_clarification_path(args.project_name))
    if args.status:
        items = [item for item in items if str(item.get("status", "")).upper() == args.status.upper()]

    print(f"PROJECT {args.project_name}")
    print(f"CLARIFICATIONS {len(items)}")
    for item in items:
        print(
            f"- {item.get('clarification_id')} [{item.get('status')}] "
            f"{item.get('requirement_id')}: {item.get('summary')}"
        )
    return 0


def resolve_command(args: argparse.Namespace) -> int:
    item = resolve_pm_clarification_in_store(_clarification_path(args.project_name), args.clarification_id)
    print(f"RESOLVED {item['clarification_id']}")
    print(f"PROJECT {item['project_name']}")
    print(f"REQUIREMENT {item['requirement_id']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create, list, and resolve PM clarification artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a PM clarification artifact.")
    create_parser.add_argument("project_name")
    create_parser.add_argument("requirement_id")
    create_parser.add_argument("--requirement-title", required=True)
    create_parser.add_argument("--summary", required=True)
    create_parser.add_argument("--question", action="append", required=True)
    create_parser.set_defaults(func=create_command)

    list_parser = subparsers.add_parser("list", help="List PM clarification artifacts.")
    list_parser.add_argument("project_name")
    list_parser.add_argument("--status", help="Optional status filter such as OPEN or RESOLVED.")
    list_parser.set_defaults(func=list_command)

    resolve_parser = subparsers.add_parser("resolve", help="Resolve a PM clarification artifact.")
    resolve_parser.add_argument("project_name")
    resolve_parser.add_argument("clarification_id")
    resolve_parser.set_defaults(func=resolve_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

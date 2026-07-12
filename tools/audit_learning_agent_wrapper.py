from __future__ import annotations

from common import audit_learning_agent_wrapper


def main() -> int:
    issues = audit_learning_agent_wrapper()
    if issues:
        print("FAIL learning-agent wrapper audit")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print("PASS learning-agent wrapper audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

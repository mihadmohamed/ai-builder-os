from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
CASES_FILE = PROJECT_ROOT / "evals" / "sdk_contract_cases.json"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents_runtime.registry import build_agent_registry  # noqa: E402


@dataclass(frozen=True)
class SDKContractEvalResult:
    case_id: str
    passed: bool
    detail: str


def _agent_tool_names(agent) -> set[str]:
    return {tool.name for tool in agent.tools if bool(getattr(tool, "_is_agent_tool", False))}


def run_sdk_contract_evals() -> list[SDKContractEvalResult]:
    """Evaluate the non-negotiable SDK architecture without calling a paid model."""
    registry = build_agent_registry()
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    results: list[SDKContractEvalResult] = []
    for case in cases:
        kind = case["kind"]
        actual: object
        expected: object = case.get("expected")
        if kind == "roles":
            actual = sorted(agent.name for agent in registry.values())
            passed = actual == expected
        elif kind == "handoffs":
            actual = sorted(agent.name for agent in registry[case["agent"]].handoffs)
            passed = actual == expected
        elif kind == "agent_tools":
            actual = sorted(_agent_tool_names(registry[case["agent"]]))
            passed = actual == expected
        elif kind == "approval_tool":
            tool = next((item for item in registry[case["agent"]].tools if item.name == case["tool"]), None)
            actual = bool(tool and getattr(tool, "needs_approval", False))
            expected = True
            passed = actual is True
        elif kind == "output_type":
            output_type = registry[case["agent"]].output_type
            actual = getattr(output_type, "__name__", "")
            passed = actual == expected
        elif kind == "required_tools":
            names = {tool.name for tool in registry[case["agent"]].tools}
            actual = sorted(name for name in expected if name in names)
            passed = actual == expected
        elif kind == "forbidden_tools":
            names = {tool.name for tool in registry[case["agent"]].tools}
            actual = sorted(name for name in expected if name in names)
            expected = []
            passed = actual == expected
        elif kind == "guardrails":
            missing = [
                agent.name
                for agent in registry.values()
                if not agent.input_guardrails or not agent.output_guardrails
            ]
            actual = missing
            expected = []
            passed = not missing
        elif kind == "legacy_removed":
            forbidden = ("run_structured_agent", "tool_requests", "client.responses.parse")
            offenders = []
            for path in SRC_ROOT.rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                if any(token in text for token in forbidden):
                    offenders.append(str(path.relative_to(SRC_ROOT)))
            if (SRC_ROOT / "agent_runtime.py").exists():
                offenders.append("agent_runtime.py")
            actual = sorted(offenders)
            expected = []
            passed = not offenders
        elif kind == "entrypoints":
            app_text = (SRC_ROOT / "app.py").read_text(encoding="utf-8")
            bridge_text = (SRC_ROOT / "codex_bridge" / "server.py").read_text(encoding="utf-8")
            actual = {
                "streamlit_start": "_agents_sdk_runtime().run(" in app_text,
                "streamlit_resume": "_agents_sdk_runtime().resume(" in app_text,
                "streamlit_explicit_gate": "AI_BUILDER_OS_ENABLE_API_AGENTS" in app_text,
                "codex_start": "def start_agent_workflow(" in bridge_text,
                "codex_resume": "def resolve_agent_approval(" in bridge_text,
            }
            expected = {key: True for key in actual}
            passed = actual == expected
        elif kind == "pm_entrypoints":
            bridge_text = (SRC_ROOT / "codex_bridge" / "server.py").read_text(encoding="utf-8")
            service_text = (SRC_ROOT / "control_plane" / "service.py").read_text(encoding="utf-8")
            actual = {
                "codex_submit": "def submit_pm_proposal(" in bridge_text,
                "codex_approve": "def approve_pm_proposal(" in bridge_text,
                "codex_reject": "def reject_pm_proposal(" in bridge_text,
                "controller_submit": "def submit_pm_proposal(" in service_text,
                "controller_approve": "def approve_pm_proposal(" in service_text,
                "controller_reject": "def reject_pm_proposal(" in service_text,
            }
            expected = {key: True for key in actual}
            passed = actual == expected
        elif kind == "pm_operational_workflow":
            app_text = (SRC_ROOT / "app.py").read_text(encoding="utf-8")
            service_text = (SRC_ROOT / "control_plane" / "service.py").read_text(encoding="utf-8")
            contract_text = (SRC_ROOT / "pm_contract.py").read_text(encoding="utf-8")
            actual = {
                "typed_request": "class PMWorkRequestPayload" in contract_text,
                "workbench": "def render_pm_workbench" in app_text,
                "proposal_review": "def render_pm_proposal_workflow" in app_text,
                "codex_request": "def create_pm_codex_work_request" in service_text,
                "sdk_state_resume": "_agents_sdk_runtime().resume(" in app_text,
                "api_warning": "consumes OpenAI API project tokens" in app_text,
            }
            expected = {key: True for key in actual}
            passed = actual == expected
        else:
            actual = f"unknown kind: {kind}"
            passed = False
        results.append(
            SDKContractEvalResult(
                case_id=case["id"],
                passed=passed,
                detail=f"expected={expected!r}; actual={actual!r}",
            )
        )
    return results


if __name__ == "__main__":
    evaluated = run_sdk_contract_evals()
    for item in evaluated:
        print(f"{'PASS' if item.passed else 'FAIL'} {item.case_id} - {item.detail}")
    passed = sum(1 for item in evaluated if item.passed)
    print(f"SUMMARY: {passed}/{len(evaluated)} passing")
    raise SystemExit(0 if passed == len(evaluated) else 1)

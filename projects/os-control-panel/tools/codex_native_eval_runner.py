from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"


@dataclass(frozen=True)
class CodexNativeEvalResult:
    case_id: str
    passed: bool
    detail: str


def run_codex_native_evals() -> list[CodexNativeEvalResult]:
    """Verify the Codex-native default architecture without invoking any model backend."""
    skill_text = (REPO_ROOT / ".agents" / "skills" / "ai-builder-os-workflow" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    app_text = (SRC_ROOT / "app.py").read_text(encoding="utf-8")
    bridge_text = (SRC_ROOT / "codex_bridge" / "server.py").read_text(encoding="utf-8")
    service_text = (SRC_ROOT / "control_plane" / "service.py").read_text(encoding="utf-8")
    workspace_text = (SRC_ROOT / "workspace.py").read_text(encoding="utf-8")
    agent_paths = sorted((REPO_ROOT / ".codex" / "agents").glob("*.toml"))
    agent_configs = [tomllib.loads(path.read_text(encoding="utf-8")) for path in agent_paths]
    config = tomllib.loads((REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
    native_ui = app_text.split("def render_codex_workflow", 1)[1].split("def render_sdk_agent_workflow", 1)[0]
    bridge_preamble = bridge_text.split("def _agents_sdk_runtime", 1)[0]

    checks = [
        (
            "codex-project-agents",
            len(agent_configs) == 8
            and all(config.get("name") and config.get("description") and config.get("developer_instructions") for config in agent_configs),
            f"agents={len(agent_configs)}",
        ),
        (
            "codex-bounded-delegation",
            config.get("agents", {}).get("max_threads", 99) <= 4 and config.get("agents", {}).get("max_depth") == 1,
            f"agents_config={config.get('agents', {})}",
        ),
        (
            "codex-native-skill-default",
            "Keep model work in the current Codex chat by default" in skill_text
            and "only when the user explicitly asks" in skill_text,
            "skill declares native default and explicit SDK boundary",
        ),
        (
            "codex-durable-work-queue",
            all(
                token in service_text
                for token in (
                    "def create_codex_work_request",
                    "def list_codex_work_requests",
                    "def claim_codex_work_request",
                    "def resolve_codex_work_request",
                )
            ),
            "controller owns READY_FOR_CODEX lifecycle",
        ),
        (
            "codex-mcp-work-queue",
            all(
                f"def {name}" in bridge_text
                for name in (
                    "create_codex_work_request",
                    "list_codex_work_requests",
                    "claim_codex_work_request",
                    "resolve_codex_work_request",
                )
            ),
            "MCP exposes deterministic queue lifecycle",
        ),
        (
            "codex-typed-pm-work-queue",
            "def create_pm_codex_work_request" in service_text
            and "def create_pm_codex_work_request" in bridge_text
            and "PMWorkRequestPayload" in service_text,
            "typed prioritisation and task-planning requests remain model-free until claimed",
        ),
        (
            "codex-native-ui-no-api-runtime",
            "create_codex_work_request" in native_ui
            and "_agents_sdk_runtime" not in native_ui
            and "AgentsWorkflowRuntime" not in native_ui,
            "native Streamlit path only writes controller state",
        ),
        (
            "agents-sdk-explicit-opt-in",
            "AI_BUILDER_OS_ENABLE_API_AGENTS" in app_text
            and "if not api_agents_enabled():" in workspace_text
            and "from agents_runtime import AgentsWorkflowRuntime" not in bridge_preamble,
            "SDK UI and legacy live flows are gated; MCP imports runtime lazily",
        ),
    ]
    return [CodexNativeEvalResult(case_id, passed, detail) for case_id, passed, detail in checks]


if __name__ == "__main__":
    evaluated = run_codex_native_evals()
    for item in evaluated:
        print(f"{'PASS' if item.passed else 'FAIL'} {item.case_id} - {item.detail}")
    passed = sum(item.passed for item in evaluated)
    print(f"SUMMARY: {passed}/{len(evaluated)} passing")
    raise SystemExit(0 if passed == len(evaluated) else 1)

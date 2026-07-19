from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ElicitResult

from control_plane import ACTION_RISKS
from control_plane import WorkflowController
from pm_contract import PMDecisionEnvelope, PMRequirementChange
from tools.project_registry import ProjectLocation, register_project


REPO_ROOT = Path(__file__).resolve().parents[4]


class CodexBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_server_negotiates_and_lists_workflow_tools(self) -> None:
        parameters = StdioServerParameters(
            command=str(REPO_ROOT / ".venv" / "bin" / "python"),
            args=[str(REPO_ROOT / "tools" / "ai_builder_os_mcp.py")],
            cwd=REPO_ROOT,
        )
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listed = await session.list_tools()
                projects = await session.call_tool("list_projects", {})

        names = {tool.name for tool in listed.tools}
        self.assertEqual(names, set(ACTION_RISKS))
        self.assertTrue(
            {
                "get_next_action",
                "get_execution_backends",
                "get_approval_risk_policy",
                "create_codex_work_request",
                "create_pm_codex_work_request",
                "list_codex_work_requests",
                "claim_codex_work_request",
                "resolve_codex_work_request",
                "list_pm_proposals",
                "submit_pm_proposal",
                "describe_pm_proposal_action",
                "decide_pm_proposal",
                "approve_pm_proposal",
                "reject_pm_proposal",
                "claim_implementation",
                "record_implementation_evidence",
                "start_agent_workflow",
                "list_agent_approvals",
                "list_external_approvals",
                "decide_external_approval",
                "resolve_agent_approval",
            }.issubset(names)
        )
        tools = {tool.name: tool for tool in listed.tools}
        self.assertTrue(tools["inspect_project"].annotations.readOnlyHint)
        self.assertFalse(tools["inspect_project"].annotations.openWorldHint)
        self.assertFalse(tools["submit_pm_proposal"].annotations.readOnlyHint)
        self.assertFalse(tools["submit_pm_proposal"].annotations.destructiveHint)
        self.assertTrue(tools["decide_pm_proposal"].annotations.destructiveHint)
        self.assertTrue(tools["decide_pm_proposal"].annotations.idempotentHint)
        self.assertFalse(tools["decide_pm_proposal"].annotations.openWorldHint)
        self.assertTrue(tools["decide_external_approval"].annotations.destructiveHint)
        self.assertTrue(tools["decide_external_approval"].annotations.openWorldHint)
        self.assertFalse(projects.isError)
        self.assertIn("os-control-panel", " ".join(str(item) for item in projects.content))

    async def test_stdio_native_pm_decision_round_trips_form_elicitation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            product = project / "product"
            product.mkdir(parents=True)
            (product / "requirements.md").write_text(
                """# Product: MCP Demo

# Product Requirements

## Active Requirements

### R1 — Existing

Status: NEW
Priority: HIGH
Effort: S
Description:
Existing truth.

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

* Only approved proposals change product truth.
""",
                encoding="utf-8",
            )
            (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
            (product / "memory.md").write_text("# Memory\n", encoding="utf-8")
            (product / "history.jsonl").write_text("", encoding="utf-8")
            registry = root / "registry.json"
            runtime = root / "runtime"
            previous_registry = os.environ.get("AI_BUILDER_OS_PROJECT_REGISTRY")
            previous_runtime = os.environ.get("AI_BUILDER_OS_RUNTIME_ROOT")
            os.environ["AI_BUILDER_OS_PROJECT_REGISTRY"] = str(registry)
            os.environ["AI_BUILDER_OS_RUNTIME_ROOT"] = str(runtime)
            try:
                register_project(
                    ProjectLocation(
                        project_id="mcp-native-demo",
                        name="mcp-native-demo",
                        display_name="MCP Native Demo",
                        mode="attached_repository",
                        workspace_path=project,
                        visibility="private",
                        ownership="self",
                        repository="owner/mcp-native-demo",
                    )
                )
                proposal = WorkflowController().submit_pm_proposal(
                    "mcp-native-demo",
                    PMDecisionEnvelope(
                        project_name="mcp-native-demo",
                        mode="requirement_draft",
                        status="READY_FOR_APPROVAL",
                        next_action="draft_requirement",
                        assistant_message="Ready.",
                        requirement_changes=[
                            PMRequirementChange(
                                title="Native MCP result",
                                status="NEW",
                                priority="HIGH",
                                effort="S",
                                description="Prove protocol elicitation.",
                            )
                        ],
                        approval_summary="Create Native MCP result.",
                    ),
                    actor="pm-test",
                    source="unit",
                )
                messages: list[str] = []

                async def elicit(_context: object, params: object) -> ElicitResult:
                    messages.append(str(getattr(params, "message", "")))
                    return ElicitResult(
                        action="accept",
                        content={"decision": "approve", "rejection_reason": ""},
                    )

                parameters = StdioServerParameters(
                    command=str(REPO_ROOT / ".venv" / "bin" / "python"),
                    args=[str(REPO_ROOT / "tools" / "ai_builder_os_mcp.py")],
                    cwd=REPO_ROOT,
                    env={
                        **os.environ,
                        "AI_BUILDER_OS_PROJECT_REGISTRY": str(registry),
                        "AI_BUILDER_OS_RUNTIME_ROOT": str(runtime),
                    },
                )
                async with stdio_client(parameters) as (reader, writer):
                    async with ClientSession(
                        reader,
                        writer,
                        elicitation_callback=elicit,
                    ) as session:
                        await session.initialize()
                        result = await session.call_tool(
                            "decide_pm_proposal",
                            {
                                "project_name": "mcp-native-demo",
                                "proposal_id": proposal["proposal_id"],
                                "proposal_revision": proposal["proposal_revision"],
                            },
                        )
                self.assertFalse(result.isError)
                self.assertEqual(len(messages), 1, str(result.content))
                self.assertIn("Action: decide_pm_proposal", messages[0])
                self.assertIn(proposal["proposal_id"], messages[0])
                self.assertIn("Native MCP result", product.joinpath("requirements.md").read_text())
            finally:
                if previous_registry is None:
                    os.environ.pop("AI_BUILDER_OS_PROJECT_REGISTRY", None)
                else:
                    os.environ["AI_BUILDER_OS_PROJECT_REGISTRY"] = previous_registry
                if previous_runtime is None:
                    os.environ.pop("AI_BUILDER_OS_RUNTIME_ROOT", None)
                else:
                    os.environ["AI_BUILDER_OS_RUNTIME_ROOT"] = previous_runtime


if __name__ == "__main__":
    unittest.main()

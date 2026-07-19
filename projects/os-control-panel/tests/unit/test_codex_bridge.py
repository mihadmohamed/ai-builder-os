from __future__ import annotations

import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


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
        self.assertTrue(
            {
                "get_next_action",
                "get_execution_backends",
                "create_codex_work_request",
                "create_pm_codex_work_request",
                "list_codex_work_requests",
                "claim_codex_work_request",
                "resolve_codex_work_request",
                "list_pm_proposals",
                "submit_pm_proposal",
                "approve_pm_proposal",
                "reject_pm_proposal",
                "claim_implementation",
                "record_implementation_evidence",
                "start_agent_workflow",
                "list_agent_approvals",
                "resolve_agent_approval",
            }.issubset(names)
        )
        self.assertFalse(projects.isError)
        self.assertIn("os-control-panel", " ".join(str(item) for item in projects.content))


if __name__ == "__main__":
    unittest.main()

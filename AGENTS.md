# AI Builder OS Codex workflow

This repository uses Codex-native execution by default. The current Codex chat and project-scoped agents under `.codex/agents/` perform model work using Codex plan/credits. The local `ai_builder_os` MCP server owns deterministic workflow state and does not itself invoke a model.

The OpenAI Agents SDK is an optional API-billed deployment backend. Do not call `start_agent_workflow`, `list_agent_approvals`, or `resolve_agent_approval` unless the user explicitly requests Agents SDK/API mode and understands that it uses their OpenAI API project.

When a user asks to change a governed project:

1. Use the `ai_builder_os` MCP server to inspect the project and get the deterministic next action.
2. Check for `READY_FOR_CODEX` requests. Claim a queued request before acting on it and resolve it once work ends.
3. Record only durable product intent. Never store raw chat transcripts, hidden reasoning, credentials, or private data in product files.
4. Before editing for an eligible requirement, call `claim_implementation`. Keep its lease token private to the active turn.
5. Preserve unrelated worktree changes and stay within the claimed requirement.
6. Run proportionate verification, then call `record_implementation_evidence` exactly once. Close unfinished work as `BLOCKED` or `FAILED` with evidence.
7. Do not bypass approval gates.

Use one main Codex agent by default. Delegate only bounded, independent specialist work when it materially improves quality or speed. The PM, experience designer, UI designer, architect, QA, learning, and orchestrator custom agents are read-only. The engineer custom agent may edit only after the main agent has obtained the applicable controller claim. Subagents must not call the Agents SDK backend.

Canonical truth precedence is:

1. `projects/<project>/product/requirements.md`
2. `projects/<project>/product/tasks.md`
3. `projects/<project>/product/memory.md`
4. `projects/<project>/product/history.jsonl` for append-only decisions and evidence
5. Runtime stores under the configured runtime root for queues, leases, sessions, and resumable SDK state

Use `.agents/skills/ai-builder-os-workflow` for exact MCP sequencing and backend boundaries.

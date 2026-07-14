---
name: ai-builder-os-workflow
description: Run the repository's deterministic AI Builder OS workflow from Codex without OpenAI API billing. Use when inspecting governed project state, processing READY_FOR_CODEX requests, recording durable product intent, routing work to project-scoped Codex specialists, claiming and implementing eligible requirements, handling approvals, or recording implementation evidence and canonical history. Use the optional Agents SDK backend only when the user explicitly requests API/Agents SDK mode.
---

# AI Builder OS Workflow

Use the `ai_builder_os` MCP tools as the deterministic control plane. Keep model work in the current Codex chat by default. Do not reproduce controller decisions in prompts, skills, or UI code.

Read [control-plane-contract.md](references/control-plane-contract.md) before choosing an execution backend, processing queued work, or closing a run.

## Inspect and route

0. Read `.ai-builder-os/project.json` when the current repository contains one. Use its stable project ID or name; never infer controller identity from the directory name alone.
1. Call `get_execution_backends` when execution mode is ambiguous.
2. Call `list_projects` when the project is unclear.
3. Call `inspect_project`, then `get_next_action` before choosing work or a role.
4. Surface blocking approvals and stop only when the required decision cannot be obtained in the current turn.

## Process READY_FOR_CODEX work

1. Call `list_codex_work_requests` for the selected project.
2. Claim exactly one request with `claim_codex_work_request` before acting on it.
3. Treat its task, role, and requirement ID as a bounded work packet.
4. If it names a governed requirement that will be edited, also call `claim_implementation` before changing files.
5. Resolve the queue request once with `resolve_codex_work_request`; link the implementation run ID when one exists.

Use `BLOCKED` when user authority or external state is required, `FAILED` after an attempted execution fails, and `COMPLETED` only when requested work and relevant verification are finished.

## Record product intent

Call `record_product_intent` only for concise, durable intent that belongs in canonical product history. Use a stable idempotency key for retries. Exclude raw chat, hidden reasoning, credentials, personal data, and exploratory notes.

## Route Codex-native roles

Keep orchestration in the main Codex chat. Use the project-scoped agents in `.codex/agents/` only for bounded specialist work:

- `pm`, `experience_designer`, `ui_designer`, `architect`, `qa`, and `learning_agent` are read-only reviewers.
- `engineer` may edit only after the main agent has acquired the applicable controller claim.
- `orchestrator` is a read-only independent routing reviewer for unusually complex workflows.

Use one main agent by default. Delegate only independent work where specialist context isolation or parallelism materially improves quality or speed. Do not delegate trivial sequential steps. Give each specialist the request ID, relevant canonical context, constraints, and expected output. Subagents must not invoke the API-backed Agents SDK.

## Implement in Codex

1. Call `claim_implementation` for the eligible requirement before editing.
2. Keep the lease token out of responses, logs, commits, product files, and subagent prompts unless an editing agent strictly needs it; prefer the main agent retaining it.
3. Implement only the work packet and preserve unrelated worktree changes. Work in the resolved target repository; a chat scoped to one repository must not edit unrelated registered repositories.
4. Verify in proportion to risk. Use `qa` for an independent pass when risk or scope justifies the extra Codex tokens.
5. Call `record_implementation_evidence` exactly once with the run ID, lease token, summary, changed files, tests, and terminal status.

## Use API mode only by explicit request

Call `start_agent_workflow`, `list_agent_approvals`, or `resolve_agent_approval` only when the user explicitly asks for the OpenAI Agents SDK/API-backed backend. State that this consumes OpenAI API project tokens before starting it. An SDK approval authorizes only the displayed tool call and arguments.

## Maintain canonical history

Treat requirements, tasks, memory, then append-only history as product truth. Runtime queue entries, leases, Codex threads, SDK sessions, and serialized approvals are operational state. Use MCP tools for canonical events instead of editing `history.jsonl` manually.

Canonical truth lives in the governed project repository, whether it is an embedded showcase, a managed standalone repository, or an attached repository. Portable repository settings may live in that repository's manifest. Machine-specific workspace paths and the aggregate cross-project catalog belong in the private registry/runtime store and must not be copied into public showcase files.

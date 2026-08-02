# Source Directory

This directory contains the OS Control Panel application code.

## Files

- `app.py`
  - main Streamlit application
  - renders workspace, project, inbox, and creation flows
  - owns the project sections for `Agents`, `Requirements`, `Delivery`, and `Quality`
  - coordinates live PM / Experience Designer / UI Designer threads and deterministic Architect / QA / Orchestrator surfaces

- `workspace.py`
  - file-backed project and workflow helpers
  - parses requirements, tasks, memory, and workflow artifacts
  - manages approvals, clarifications, agent threads, implementation runs, quality reviews, and related project state

## Current Code Scope

The current source layer supports:

- workspace overview and project selection
- live PM requirement discovery for new and existing projects
- shared `Agents` workspace with PM, Experience Designer, UI Designer, Architect, QA, and Orchestrator
- project `Requirements`, `Delivery`, and `Quality` sections
- sprint planning, requirement implementation initiation, and one-active-run-per-project guardrails
- delivery inspection through implementation runs and workflow timeline history
- deterministic quality review and manual verification support
- approval, clarification, and routed-finding workflow handling

## Source-of-Truth Expectations

- Keep durable product truth in project files such as `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md`.
- Treat `data/` as local operational state, not as the canonical product backlog.
- Project validation should fail if `product/` contains orphan supporting artifacts that are not linked from canonical `requirements.md` or `tasks.md`.
- Keep runtime or generated operational artifacts out of `src/`.
- Keep `app.py` focused on UI composition and interaction flow; keep file-backed parsing and state helpers in `workspace.py` unless there is a strong reason to split further.

## Notes

- Codex-native workflow execution is the default. Streamlit writes `READY_FOR_CODEX` requests through `control_plane/`; Codex chats process them through the local MCP bridge without OpenAI API usage.
- Project-scoped role definitions live in `.codex/agents/`. The main Codex chat orchestrates and uses specialist subagents selectively because each subagent consumes additional Codex tokens.
- `agents_runtime/` is an optional API-billed deployment backend using Agents SDK agents, typed tools, handoffs, agents-as-tools, guardrails, sessions, resumable approvals, SDK traces, and redacted local lifecycle events.
- API-backed PM entry points load their effective model and reasoning effort from the typed `config/pm_model.json` contract. R101 closed as `no_selection` after the finite remediated sentinel; `gpt-5-mini` remains the legacy-safe fallback and is explicitly not an evaluation winner.
- The post-release product learning loop is project-scoped and deterministic: completed requirements expose review timing and expected evidence, safe first-party sources are assembled with provenance and confidence, and missing or stale telemetry is never treated as success. PM proposes an exact close, iterate, experiment, revise, or stop decision; consequential decisions return to the existing proposal approval lifecycle and any follow-up requirement retains history lineage to its released source.
- Outcome evidence sources remain privacy-bounded through `product/evidence/sources.json`. Canonical history stores safe evidence identifiers and summaries, never raw customer records, hidden reasoning, credentials, or unrestricted traces.
- Codex-native outcome review uses Codex plan or credits. OpenAI Agents SDK outcome review remains an explicit API-token opt-in and is never started by deterministic verification.
- Codex-native PM configuration remains owned by the Codex host and is not overridden by `config/pm_model.json`; it consumes Codex plan or credits rather than OpenAI API project tokens.
- Enable the Streamlit SDK surface explicitly with `AI_BUILDER_OS_ENABLE_API_AGENTS=1`; SDK MCP tools also require an explicit user request for API mode.
- `operations_dashboard.py` summarizes trace runs, role performance, and tool usage for the top-level Operations dashboards.
- `workspace.operations_dashboard_snapshot()` joins those metrics with file-backed workflow, oversight, quality, implementation, activity, and learning state.
- The deterministic controller remains authoritative for next action, approvals, queues, leases, and canonical history regardless of model backend.
- This source tree backs the operator control panel, not the public showcase app.

## Optional PM evidence sources

PM always reads bounded canonical history, implementation, QA, and release evidence. Optional customer-feedback, analytics, and experiment evidence is considered configured only when `product/evidence/sources.json` exists with schema `2026-07-21.pm-evidence-sources.v1`. Each source must declare `kind`, `source_id`, `owner`, `privacy_boundary`, and a relative JSON or JSONL `path` contained inside `product/evidence/`.

Only bounded safe fields are exposed to PM. Missing, malformed, oversized, or path-escaping sources are reported as unavailable; they are never inferred or fetched automatically.

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

- Live PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator Workflow Review flows require `OPENAI_API_KEY`.
- Model-backed roles run through `agent_runtime.py` for canonical prompts, bounded read-only tools, guardrails, limits, redacted traces, and human hand-back.
- `operations_dashboard.py` summarizes trace runs, role performance, and tool usage for the top-level Operations dashboards.
- `workspace.operations_dashboard_snapshot()` joins those metrics with file-backed workflow, oversight, quality, implementation, activity, and learning state.
- Architect and QA remain deterministic. Orchestrator Next Step is deterministic; Workflow Review adds a bounded advisory model review without changing state.
- This source tree backs the operator control panel, not the public showcase app.

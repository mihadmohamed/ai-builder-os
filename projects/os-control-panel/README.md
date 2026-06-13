# OS Control Panel

Local-first operator control panel for running AI Builder OS.

This app is the working control surface for the OS itself. It is designed for truthful workflow operation, file-backed state, and agent-guided product work rather than for public marketing or passive browsing.

## What It Does

The control panel helps the Product Director operate AI Builder OS through a local UI while keeping the underlying file-based operating model intact.

Current scope includes:

- workspace overview and project selection
- project sections for `Agents`, `Requirements`, `Delivery`, and `Quality`
- live PM requirement discovery for new and existing projects
- live Experience Designer and UI Designer review flows
- deterministic Architect, QA, and Orchestrator surfaces
- file-backed approvals, clarifications, findings, agent threads, and implementation runs
- sprint planning and sequential requirement implementation
- project-level delivery inspection and quality review
- requirement-level manual verification and guided signoff support

## Main Surfaces

### Workspace

Use the workspace to orient yourself across projects, review agent summaries, and reach the main operator destinations.

### Open Project

Use project cards to compare current project state, open a project, and see the next meaningful work signal before entering the project.

### Inbox

Use the Inbox to review active approvals, blocked clarifications, waiting threads, routed findings, and running implementation work.

### Project Detail

Inside a project, the control panel is organized into:

- `Agents` for PM, Experience Designer, UI Designer, Architect, QA, and Orchestrator
- `Requirements` for structured requirement editing, prioritization, sprint planning, and requirement-level verification
- `Delivery` for implementation-run inspection and workflow timeline history
- `Quality` for deterministic validation status and recent quality signal

## Core Workflow Behaviors

- Requirements remain file-backed through `product/requirements.md`.
- PM requirement discovery runs through live agent-thread flows rather than a separate staged draft store.
- Experience Designer and UI Designer operate inside the shared `Agents` workspace and continue through approval and PM completion rather than stopping at archive.
- Requirement implementation routing can move work through Experience Designer, UI Designer, Architect, Engineer, and QA when that better matches the kind of change being made.
- The control panel enforces one active implementation run per project.
- Delivery and Quality stay separate from Requirements so planning, execution, and validation do not collapse into one overloaded surface.
- Workspace agent summaries are informational only; they do not execute agents or mutate workflow state.
- Open approvals, routed findings, active threads, and running implementation work are treated as real workflow state.

## Running The App

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run projects/os-control-panel/src/app.py
```

## Validation

```bash
.venv/bin/python projects/os-control-panel/tools/eval_runner.py
```

For disposable local testing, you can direct runtime state outside the repo:

```bash
export AI_BUILDER_OS_RUNTIME_ROOT="/private/tmp/ai-builder-os-runtime"
```

This keeps approvals, clarifications, runs, quality reviews, and similar runtime files out of the worktree while preserving the normal project structure under the runtime root.

This runs the project-local deterministic validation baseline.
It also fails if `product/` contains orphan supporting artifacts that are not linked from canonical `requirements.md` or `tasks.md`.

Captured live-agent traces can be graded separately:

```bash
.venv/bin/python projects/os-control-panel/tools/live_eval_runner.py --project os-control-panel
```

The live roles share canonical prompts, read-only context tools, guardrails, run limits, redacted traces, and explicit human hand-back. The deterministic Orchestrator remains authoritative; Workflow Review can request an advisory live review.

The top-level `Operations` area turns those runtime and workflow records into eight dashboards:

- Agent Operations
- Agent Quality
- Workflow Health
- Human Oversight
- Agent Performance
- Tool Usage
- Learning Progress
- System Activity

These dashboards are read-only views over existing trace, product, workflow, quality, implementation, and learning sources.

## Setup Notes

- `OPENAI_API_KEY` is required for live PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator Workflow Review flows.
- Deterministic Architect, QA, and Orchestrator Next Step surfaces do not require live model access.
- Keep project-specific logic inside the project directory.
- Reuse shared OS helpers where that reduces duplication cleanly.

## Source-of-Truth Rules

- Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as durable product truth.
- Treat `data/` as local operational state for the control panel itself, not as the canonical product backlog.
- Keep UI wording honest about the difference between guided local flows and real downstream role execution.
- Treat this app as the operator surface, not the public showcase app.

## Learning Agent Relationship

- `projects/os-control-panel` is the canonical source of truth for Learning Agent behavior.
- The external hosted app under `projects/learning-agent` reuses the learning experience from this project through the external V2 release profile.
- Changes to tutoring behavior, concept hierarchy, concept catalog, progression, or learning UX should be made here and then inherited by the hosted wrapper.
- `projects/learning-agent` should remain limited to authentication, tenancy, deployment, and hosted runtime concerns.

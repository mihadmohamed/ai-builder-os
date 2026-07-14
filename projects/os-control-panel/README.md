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
- stable project manifests and private registry-based resolution
- embedded showcase, managed standalone, and attached repository modes
- approval-gated GitHub repository creation and attachment

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

## Codex-native workflow and optional Agents SDK

Codex-native execution is the default. Streamlit creates durable `READY_FOR_CODEX` requests through the deterministic controller in `src/control_plane/`; a Codex chat claims the request through the local MCP server, performs the work, and records its outcome in canonical product history. These local controller calls do not use OpenAI API tokens. Model work in the chat and optional Codex subagents uses the user's Codex plan or credits.

Codex discovers the MCP server from `.codex/config.toml`, durable rules from the root `AGENTS.md`, the workflow skill from `.agents/skills/ai-builder-os-workflow/`, and specialist definitions from `.codex/agents/`. Start a new Codex chat after changing that configuration. Ask Codex to `Use $ai-builder-os-workflow to claim and complete the next READY_FOR_CODEX request.`

The runtime in `src/agents_runtime/` remains a genuine OpenAI Agents SDK deployment backend with SDK agents, handoffs, agents-as-tools, SQLite sessions, resumable approval state, guardrails, and OpenAI traces. It is optional and API-billed. Streamlit exposes it only when `AI_BUILDER_OS_ENABLE_API_AGENTS=1`; Codex may call its MCP tools only when the user explicitly requests Agents SDK/API mode.

You can smoke-test the stdio server directly with the bridge unit test:

```bash
PYTHONPATH="$PWD/projects/os-control-panel/src:$PWD" \
  .venv/bin/python -m unittest projects.os-control-panel.tests.unit.test_codex_bridge
```

Runtime-only state—including the Codex queue, implementation lease tokens, SDK sessions, and resumable approval state—lives below `AI_BUILDER_OS_RUNTIME_ROOT` when configured. Queue transitions and implementation evidence are canonical history events; mutable queue records, lease tokens, and raw chat are not product truth.
By default, registry and runtime state use the ignored `private/ai-builder-os/` boundary. `AI_BUILDER_OS_HOME` moves both stores together; the more specific registry/runtime variables override them independently.
SDK trace export is enabled by default with sensitive model/tool payload capture disabled. Set `AI_BUILDER_OS_DISABLE_SDK_TRACING=1` only for deterministic tests or deliberately offline operation.

## GitHub Publishing

GitHub publication drafts are created from the Delivery area and reviewed from Inbox.
Approving a policy-passing GitHub publication draft publishes it to GitHub when a token is configured:

```bash
export AI_BUILDER_OS_GITHUB_TOKEN="github_pat_..."
```

The repo is inferred from `origin`. Override it when needed:

```bash
export AI_BUILDER_OS_GITHUB_REPO="owner/repo"
```

Issue drafts and eval summaries publish as GitHub issues. PR-description drafts update the open pull request for the current branch; set `AI_BUILDER_OS_GITHUB_BRANCH` if the app should target a different branch.

The normal OS completion path is release delivery approval. When a requirement is marked `DONE`, the OS creates an Inbox release bundle instead of silently closing it. Approving that bundle marks the requirement `DONE`, publishes the GitHub issue, commits the approved public files, and pushes the current branch. Manual Delivery draft buttons remain available for one-off publication tasks.

## Project Types

Repository mode is separate from UI project type. A Streamlit or web-app project can be an embedded public showcase, a managed standalone repository, or an attached repository. Standalone creation defaults to private and requires Inbox approval before GitHub creation or push.

Projects have a first-class project type capability profile:

- `streamlit` for Python Streamlit apps with Railway as the default hosted-service deployment capability
- `web_app` for Vercel-compatible Next.js/React web apps

The project type is selected during new-project creation, stored in `product/ui-runtime.json`, shown as project type in the UI, and used by preview, Engineer guidance, release readiness, and release delivery approvals. Streamlit projects keep Railway-oriented hosted Python service expectations. Web app projects scaffold a minimal Next.js starter, preview with `npm run dev`, and use Vercel as the default deployment capability.

Before a web app release can be approved for Vercel delivery, run local Playwright browser verification:

```bash
.venv/bin/python tools/verify_web_app.py my-web-project
```

The verifier starts `npm run dev`, opens Chromium at desktop and mobile viewports, captures screenshots under `product/browser-verification/`, records console/page errors and click checks, and writes `product/browser-verification.json`. Web app release approval is blocked until that evidence is passing.

For web app releases, the OS can look up the Vercel preview deployment after GitHub push:

```bash
export AI_BUILDER_OS_VERCEL_TOKEN="vercel_token_here"
```

Optional project/team mapping:

```bash
export AI_BUILDER_OS_VERCEL_TEAM_ID="team_..."
export AI_BUILDER_OS_VERCEL_PROJECT_MY_PROJECT="prj_..."
```

If no project-specific variable is set, the OS asks Vercel for deployments using the AI Builder OS project slug as the project name.

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

When explicitly enabled, the API-backed live roles share canonical prompts, least-privilege typed tools, SDK guardrails, bounded turns, non-sensitive OpenAI traces, correlated local lifecycle events, and durable approval hand-back. The deterministic controller remains authoritative.

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

- Codex-native mode is the default and does not require `OPENAI_API_KEY`.
- `AI_BUILDER_OS_ENABLE_API_AGENTS=1` and `OPENAI_API_KEY` are both required for API-backed PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator Workflow Review flows in Streamlit.
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

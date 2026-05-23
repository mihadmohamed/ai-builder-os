# OS Control Panel

Local-first operator control panel for running AI Builder OS.

This app is the working control surface for the OS itself. It is optimized for truthful workflow operation, file-backed state, and agent-guided product work rather than for public marketing or passive browsing.

## Current Scope

The current product slice includes:

- workspace shell
- workspace summary view
- workflow inbox
- static role cards
- local deterministic validation baseline
- new-project creation flow with live PM discovery by default
- project detail page with structured requirement editing
- project detail sections for requirements, agents, delivery, and quality
- multi-agent workspace foundation inside `Agents`
- PM agent workspace with live chat-based requirement discovery and draft approval into requirements
- Experience Designer agent workspace with live feedback synthesis and usability review
- UI Designer agent workspace with live design direction and UI review
- Architect workspace surface with deterministic structural review
- QA workspace surface with deterministic validation review
- Orchestrator workspace surface with deterministic next-step guidance
- live PM requirement discovery across new-project and in-project PM workflows
- file-backed Experience Designer handoff states
- requirement-level implementation initiation with one active run at a time per project
- explicit approval requests for draft-to-artifact transitions
- confirmed deletion for unfinished requirements
- clickable workspace agent summaries with capability, memory/context, and workflow-position popups
- refined requirement-page and workspace layout polish

## Key Behaviors

- requirement editing remains file-backed through `product/requirements.md`
- the New Project tab uses a live PM requirement-discovery thread to shape the first requirement before the project is scaffolded
- PM requirement discovery inside existing projects also runs as a live PM chat thread and saves draft artifacts before approval into requirements
- Experience Designer runs inside the shared `Agents` workspace and approved findings now continue automatically through a PM completion step
- UI Designer runs inside the shared `Agents` workspace and approved design reviews now continue automatically into backlog or scope confirmation instead of stopping at archive
- Orchestrator is exposed in the UI as a code-driven workflow authority, not a freeform chat persona
- the Inbox shows active approvals, blocked clarifications, waiting threads, routed findings, and running implementation work
- Inbox approval cards now let the Product Director review the full underlying draft before approving or rejecting it
- approved Experience Designer and UI Designer review work no longer stops at `approved`; the workflow continues automatically to backlog or explicit scope confirmation
- requirement implementation routing now recognizes meaningful experience-heavy and UI-heavy work and routes it through Experience Designer or UI Designer before Engineer instead of treating all non-structural work as pure implementation
- PM, Experience Designer, and UI Designer now create explicit approval requests before important draft transitions are committed
- the agent workspace now uses guided agent and mode selection instead of a blind dropdown-first flow
- Inbox workflow items are grouped more clearly by state so approvals and active work scan faster
- project cards now emphasize project identity, attention signals, and primary actions more intentionally
- backlog requirements can now be assembled into a project sprint and reordered before execution
- Sprint V1 runs sequentially inside each project and preserves the one-active-implementation-per-project rule
- sprint completion is now explicit: a finished sprint becomes ready to close, then clears only after confirmation
- recent implementation runs are now inspectable from the requirements page, with timestamps, summaries, errors, and log/output previews
- recent implementation runs are now inspectable from the project `Delivery` section, with timestamps, summaries, errors, and log/output previews
- a project-level workflow timeline now lives in `Delivery` and shows recent artifact history across approvals, clarifications, findings, agent-thread transitions, and implementation outcomes
- a dedicated quality signal now lives in `Quality` and shows the latest deterministic validation result, failing cases, confidence, and last-run timestamp for each project
- requirements now carry their own manual verification checks, pass/fail notes, and signoff summaries inside the control panel
- selected manual verification checks can now be pinned as a guided card at the project level while you move through the relevant project surfaces
- the guided verification card lets the Product Director record pass/fail and notes without losing the current testing step while navigating inside the project
- completed requirements now live in a compact archive instead of a long stack of read-only cards
- the project preview control now uses a tighter utility-card layout
- workspace agent summaries are derived from the current role and workflow files rather than maintained as a separate static catalog
- Experience Designer findings remain file-backed workflow artifacts and now re-enter the product through the shared `Agents` workspace instead of a bespoke project tab
- routed and pending findings are part of the real workflow state for orchestration and status reporting
- the control panel now uses a live PM runtime for requirement discovery wherever PM chat is offered
- the agent workspace now supports PM, Experience Designer, UI Designer, Architect, QA, and Orchestrator, with room for more agents later
- the legacy staged PM discovery store has been removed; PM discovery now uses only the agent-thread model
- requirement implementation can be initiated from eligible requirement cards and writes a background run summary/error back into the UI
- the one-active-run guardrail is enforced per project, not across the whole OS
- PM can now create durable clarification requests automatically from live discovery when a materially blocking ambiguity is detected
- PM clarification requests can still be raised manually from the requirement UI and are treated as blocking workflow artifacts
- open approvals are treated as active workflow state by Orchestrator and status tooling
- unfinished requirements can be deleted after explicit confirmation; completed requirements remain read-only and non-deletable
- workspace agent summary popups are informational only and do not trigger agent execution or mutate workflow state
- `OPENAI_API_KEY` is required for the live agent flows in the control panel

## Run The App

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run projects/os-control-panel/src/app.py
```

## Validate

```bash
.venv/bin/python projects/os-control-panel/tools/eval_runner.py
```

This runs the project-local deterministic validation baseline.

## Notes

- Keep project-specific logic inside the project directory
- Reuse shared OS helpers where that reduces duplication cleanly
- Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as the durable product source of truth
- Treat `data/` as local operational state for the control panel itself, not as the canonical product backlog
- Keep UI wording honest about the difference between guided local flows and real downstream role execution
- Treat this app as the operator surface, not the eventual public showcase app

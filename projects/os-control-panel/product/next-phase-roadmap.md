# Next-Phase Roadmap — OS Control Panel

## Purpose

Keep the roadmap aligned with the real state of `os-control-panel` as it evolves from a local PM-first control surface into a fuller agent workflow and control plane for AI Builder OS.

This version replaces the earlier roadmap snapshot that still described several already-shipped capabilities as future work.

---

## Current Reality

`os-control-panel` is no longer just a PM discovery UI.

It now includes:

- workspace-level navigation and summary
- project-level requirements and agent workspace
- live PM discovery in both:
  - `New Project`
  - project-level `Agents`
- Experience Designer in `Agents`
- UI Designer in `Agents`
- Orchestrator in `Agents`
- workflow Inbox
- explicit approval artifacts and approval actions
- automatic PM completion after approved Experience Designer and UI Designer reviews
- requirement-level implementation initiation
- project-scoped implementation locking
- sprint planning and sequential sprint execution
- explicit sprint closeout confirmation
- compact completed-requirements archive
- automatic PM clarification generation from live discovery when ambiguity is materially blocking
- deterministic tests and scenario evals

The product has moved past the earlier “add the missing agents and inbox” phase.

The next work is now about:

- observability
- execution trust
- workflow clarity
- richer inspection
- better quality/control surfaces

---

## What Has Been Delivered

### Foundation

- local-first file-backed control panel
- structured requirement editing
- project preview support
- improved workspace/project navigation

### Agent Workspace

- PM live requirement discovery
- Experience Designer:
  - `Feedback Synthesis`
  - `Usability Review`
- UI Designer:
  - `Design Direction`
  - `UI Review`
- Orchestrator:
  - deterministic next-step guidance

### Workflow Layer

- workflow Inbox
- approval requests
- PM clarifications
- active agent threads
- routed findings
- implementation runs

### Workflow Completion

- approved PM drafts -> requirements
- approved Experience Designer findings -> saved artifact + PM completion
- approved UI Designer briefs -> PM completion
- PM completion outcomes:
  - backlog requirement
  - scope confirmation

### Implementation Flow

- requirement-level implementation start
- background run records
- project-scoped one-active-run rule
- routing of relevant work through:
  - Architect
  - Experience Designer
  - UI Designer
  before Engineer where appropriate

### Sprint Flow

- add backlog requirements into a sprint
- reorder sprint items
- sequential sprint execution
- block on intervention when needed
- explicit sprint completion confirmation
- empty next-planning sprint shell after closeout

### UI/UX Refinement

- guided agent selection
- clearer mode explanations
- improved Inbox hierarchy
- improved project entry cards
- compact completed archive
- lighter workflow card hierarchy
- explicit main/project navigation distinction

---

## What Is Still Missing

These are now the real missing pieces for a fuller control plane.

### 1. Run Observability

We still do not have a strong in-app run inspection surface for:

- implementation history
- active run timeline
- recent failures
- blocked runs
- what happened during a workflow transition

### 2. Trace / Timeline Visibility

We need a truthful per-work-item timeline that shows:

- which role acted
- what artifact was created
- what approval happened
- what state changed next

The system has state, but the narrative of that state is still hard to inspect.

### 3. Quality Surfaces In The UI

We have tests and evals, but not a proper control-panel quality surface for:

- eval status
- recent regressions
- manual verification progress
- requirement-level signoff evidence

### 4. Deeper Artifact Outcome Visibility

Architect and QA now exist as real user-facing review surfaces in `Agents`.

What still remains is stronger inspection of what those reviews and other workflow actions produced over time.

### 5. Better Artifact Outcome Visibility

The workflow now completes more automatically, which is good.

But the UI still needs to make it more obvious:

- where approved reviews went
- what PM completion decided
- what changed in requirements or scope as a result

### 6. Hosted / Team-Ready Architecture

Still future:

- auth
- permissions
- service-backed state
- worker separation
- hosted execution controls

---

## Core Product Principles From Here

1. Keep one source of truth for workflow state.
2. Keep Orchestrator code-driven and authoritative.
3. Separate:
   - conversation state
   - workflow state
   - execution state
4. Favor explicit approvals for meaningful state transitions.
5. Make workflow completion visible, not merely implied.
6. Prefer fewer clearer surfaces over more tabs.
7. Make runs and validations inspectable enough to be trusted.
8. Keep execution workers and the control surface conceptually separate.

---

## Recommended Next Phases

## Phase A — Observability And Workflow Inspection

Goal:

- make the current workflow legible and trustworthy

Build:

1. run history list
2. run detail surface
3. workflow timeline per requirement / approval / review
4. recent blocked/failure surface
5. better “what happened after approval?” visibility

Deliverables:

- implementation run history
- workflow timeline view
- artifact outcome visibility
- better failure/blocked inspection

Why now:

- the workflow is now rich enough that invisibility is the main risk

---

## Phase B — Quality And Verification Control Layer

Goal:

- bring validation discipline into the UI itself

Build:

1. in-app eval summary
2. requirement-level verification status
3. manual verification plan UI
4. pass/fail recording inside the control panel
5. optional guided test-card flow for step-by-step manual testing

Deliverables:

- quality dashboard
- manual verification UI
- signoff evidence tied to requirements

Why now:

- manual verification proved valuable, but the CLI/file loop was too painful

---

## Phase C — Agent/Mode Interaction Improvements

Goal:

- make agent use more intentional and less dropdown-driven

Build:

1. hybrid mode selection:
   - infer likely mode from first message
   - allow override
2. better agent/mode explainer surfaces
3. clearer distinction between similar modes
4. more direct routing from workflow items into the right agent context

Deliverables:

- inferred mode suggestion
- explorable agent/mode chooser
- cleaner mode boundaries

Why now:

- the role set is strong enough that clarity and discoverability matter more than adding more modes
- after the recent agent-page cleanup, this phase is explicitly lower-priority; the current explicit flow is working well enough and hybrid mode suggestion can wait for a later version unless new friction appears

---

## Phase D1 — Execution Recovery And Trust

Goal:

- make execution easier to recover and safer to trust without turning the UI into a full engineering console

Build:

1. better run error inspection
2. clearer rerun/recover paths
3. stronger blocked/stale-run handling
4. safer execution boundary controls

Deliverables:

- richer implementation inspection
- safer execution controls
- clearer recovery paths for the Product Director

Why next:

- execution is already real enough that recovery and trust gaps will show up before we need a full Engineer operating surface

---

## Phase D2 — Engineer Surface And Deeper Execution Control

Goal:

- expose deeper engineering-facing execution control only after recovery, inspection, and boundary controls are trustworthy

Build:

1. engineer-facing run review
2. deeper execution command controls
3. richer intervention tooling
4. stronger engineering-specific workflow surfaces

Deliverables:

- engineer interaction surface
- deeper execution control
- stronger engineering intervention model

Why later:

- exposing Engineer too early creates expectations we still cannot support cleanly
- this work starts to move the control panel toward an execution IDE, which is better treated as V2 scope

---

## Phase E — Public Showcase Readiness

Goal:

- prepare AI Builder OS for a high-quality public GitHub repo and a polished public Streamlit showcase

Build in two tracks:

### E1 — Public Repo Readiness

- curate the repo for public viewing
- remove or replace local-only operational residue from the public narrative
- tighten README, setup, screenshots, and architecture explanation
- make the workspace feel intentional as a public showcase rather than a private operating directory
- preserve the local-first truth of the system without exposing rough internal state as the main story

### E2 — Public Streamlit Showcase

- create a separate public-facing Streamlit showcase app for AI Builder OS
- show what the OS is, how the workflow works, and what projects it powers
- keep the control panel as an operator surface, not the public demo surface
- make the showcase deployable from the public repo in a way that is easy to share

### Later — Hosted / Team-Ready Control Plane

- auth
- permissions
- service-backed state
- worker separation
- hosted governance

---

## Deferred / Revisit Items

These are worth revisiting, but not the center of the roadmap right now.

- whether saved Experience Designer findings need their own dedicated surface
- whether routed-to-PM items need a dedicated PM queue beyond Inbox + Orchestrator
- whether agent modes should become more inferred everywhere
- whether project personas should become first-class artifacts or agent surfaces
- whether UI Designer and Experience Designer need additional modes
- whether sprint history should become a richer first-class surface

---

## Recommended Immediate Execution Order

If we continue from here, the best order is:

1. Phase E — Public showcase readiness
2. Phase D1 — Execution recovery and trust
3. Phase C — Agent/mode interaction improvements
4. Phase D2 — Engineer surface and deeper execution control

Reason for the override:

- Public showcase readiness is now a strategic priority because the OS needs to serve as a high-quality public GitHub artifact and a shareable Streamlit demonstration, not only an internal operating surface.

---

## Bottom Line

The control panel is no longer missing its basic workflow primitives.

It now needs to become:

- more inspectable
- more trustworthy
- more explicit about outcomes
- better at validating and closing work

That is the real next phase from here.

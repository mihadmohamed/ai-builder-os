# Project: OS Control Panel

## Goal

Provide a local-first operator surface for AI Builder OS that makes project setup, requirement shaping, workflow routing, delivery inspection, and quality review easier to operate without replacing the underlying file-based system.

---

## Inputs

- Project definitions and metadata from the workspace
- Product files such as `product/requirements.md`, `product/tasks.md`, and `memory.md`
- File-backed workflow artifacts such as approvals, clarifications, findings, agent threads, and implementation runs
- Operator input through project surfaces such as Requirements, Agents, Delivery, and Quality
- Deterministic validation output and role summaries derived from project state

---

## Outputs

- Structured project and workspace UI surfaces that reflect current file state
- Durable updates to product files when the operator approves or edits product work
- Honest workflow summaries, routing guidance, and inspection surfaces
- Deterministic validation summaries and project-quality signals
- Background implementation-run summaries, errors, and lightweight artifact previews when execution is supported

---

## Rules

- Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as durable product truth.
- Treat `data/` as local operational state for the control panel, not as the canonical product backlog.
- Keep the product local-first; do not introduce hosted or multi-user assumptions into core control-panel behavior unless explicitly required.
- Keep workflow state file-backed and inspectable rather than hidden in transient UI state.
- Keep UI wording honest about whether a surface is conversational, deterministic, review-oriented, or execution-oriented.
- Do not present fake agent autonomy where the system is actually showing deterministic summaries or routing guidance.
- Respect role boundaries: PM shapes work, Engineer executes, QA validates, Architect reviews structure, Orchestrator routes.
- Route meaningful experience-heavy work through Experience Designer and meaningful interface-design work through UI Designer before treating it as straightforward implementation.
- Preserve the one-active-implementation-per-project rule unless the product model is explicitly changed.
- Prefer concise summaries over raw traces, long logs, or heavy internal debugging surfaces in the default UI.
- Keep implementation logs, raw traces, and low-level operational detail behind secondary inspection surfaces rather than making them the main product experience.
- Reconstruct workflow history only from durable artifacts the OS actually stores; do not fabricate history that was never recorded.
- Keep project navigation focused on operator jobs rather than turning the control panel into a documentation browser.
- Do not let delivery, quality, approvals, and requirements collapse back into one overloaded surface when separate sections communicate them more clearly.
- Maintain the public/private boundary: public tracked files should hold product truth, while private planning and strategy belong in ignored `private/` directories.
- Do NOT hallucinate missing information.

---

## Decision Logic

1. Read current file-backed project state before deciding what the UI should display or what action should be offered.
2. Prefer the smallest truthful UI change that improves operator clarity without inventing a new workflow model.
3. When a workflow artifact is active, treat it as real workflow state before declaring the project idle or complete.
4. When a requirement is unclear, blocked, or routed, preserve that state visibly rather than smoothing over it in the UI.
5. When adding new operator affordances, keep them aligned with existing role boundaries and durable artifacts.

---

## Success Criteria

- The operator can understand project state without reading raw product files directly.
- Requirement, delivery, and quality surfaces stay distinct enough that planning, execution, and validation do not blur together.
- Live and deterministic agent surfaces accurately reflect what the OS can really do.
- Workflow state stays inspectable and trustworthy because file-backed artifacts remain the source of truth.
- Product changes improve operability without turning the control panel into a full execution IDE or an inauthentic public demo.

---

## Out of Scope

- Replacing the underlying file-based operating model with a database-first or hidden-state system
- Pretending every role is a live autonomous chat agent when some are deterministic review surfaces
- Exposing raw internal debugging data as a primary operator experience
- Turning the control panel into the public showcase app
- Keeping strategic roadmap or sensitive planning notes in public tracked product files

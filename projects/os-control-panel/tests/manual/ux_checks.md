# Manual UX Checks

Use this file for lightweight human-reviewed UX checks when a change affects the OS Control Panel's operator experience but is not meaningfully machine-evaluable.

Keep checks small, concrete, and easy to run.

---

## Test: Workspace scanability

Input:
Open the control panel to the `Workspace` view with multiple projects present.

Expected:
- The workspace heading is clearly distinct from any individual project name.
- Project cards are easy to scan without opening them.
- Agent summaries feel informational rather than action-heavy.

Pass if:
An operator can understand the overall workspace state in under 10 seconds without feeling pulled into the wrong surface.

---

## Test: Open Project card clarity

Input:
Open the `Open Project` view and compare multiple project cards.

Expected:
- Project identity is clear before action buttons.
- The primary action is obvious.
- The next-work signal is understandable at a glance.
- Preview access reads as a secondary utility rather than the main job of the page.

Pass if:
An operator can quickly decide which project to open without reading each card in full.

---

## Test: Agent selection clarity

Input:
Open a project and go to `Agents`.

Expected:
- It is clear which agent is currently selected.
- Mode selection feels connected to the selected agent.
- Architect, QA, and Orchestrator read as honest deterministic surfaces rather than fake chat roles.

Pass if:
A new operator can understand how to start the intended role workflow without guessing what each surface actually is.

---

## Test: Requirements focus

Input:
Open a project with active, backlog, and completed requirements.

Expected:
- The most important unfinished work appears first.
- Sprint planning does not overpower the main requirement focus.
- Completed work feels archived rather than visually competing with active work.

Pass if:
An operator can tell what deserves attention first without scrolling through completed or low-priority work.

---

## Test: Delivery and Quality separation

Input:
Open a project and compare `Requirements`, `Delivery`, and `Quality`.

Expected:
- `Requirements` feels like planning and signoff.
- `Delivery` feels like execution/run inspection.
- `Quality` feels like validation state.
- The three surfaces do not blur into one overloaded page.

Pass if:
An operator can explain the purpose of each section in one short sentence without confusion.

---

## Test: Guided verification usability

Input:
Pin a guided verification check and move between relevant project surfaces.

Expected:
- The pinned verification card remains easy to follow.
- The current test step stays visible while navigating.
- Recording pass/fail and notes does not feel brittle or disorienting.

Pass if:
The operator can complete a verification step without losing context about what is being tested next.

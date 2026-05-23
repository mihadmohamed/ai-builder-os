# Post-Test Review List — Phase 1 and Phase 2

This list captures follow-up design and workflow questions raised during manual verification of:

- `R25 — Phase 1 multi-agent workspace foundation`
- `R26 — Phase 2 workflow inbox and approval layer`

These are intentionally tracked after the active verification pass so we do not change behavior mid-test.

---

## Confirmed Follow-Up Items

### 1. Review whether Experience Designer and UI Designer should keep explicit user-selected modes

Tracked in:
- `R28`

Why:
- the Product Director has now chosen the preferred direction: keep modes, but move toward inferred defaults with explicit override

Chosen direction:
- use a hybrid approach
- user chooses the agent first
- the system suggests a likely mode from the first message
- the user can override the suggestion

Remaining design work:
- how the suggested mode should appear in the UI
- whether override should happen before the first reply, during the thread, or both
- how much explanation/examples to show alongside the suggestion

---

### 2. Revisit whether a dedicated saved Experience Designer findings surface is actually needed

Tracked in:
- `R32`

Why:
- after approval, findings are saved into `experience_findings.json`
- but findings are now visible through the Inbox/workflow surfaces, so it is no longer obvious that a separate dedicated surface is worth the extra UI weight

Needed outcome:
- decide whether the current workflow visibility is already enough
- only add a dedicated saved-findings surface if it solves a real review problem that Inbox and workflow views do not

---

### 3. Revisit whether routed-to-PM findings need an explicit UI review queue

Status:
- open workflow-design question

Why:
- saved experience findings can be routed toward PM
- today, it is not obvious in the UI where “awaiting PM review” lives as a dedicated surface
- this may already be acceptable if Orchestrator is expected to pick up routed PM work automatically

Question to resolve:
- is Orchestrator-only pickup sufficient?
- or do we want a visible PM review queue in the UI for routed findings?

---

### 4. Review whether auto-generated PM clarifications feel right in practice

Status:
- follow-up after shifting PM clarifications toward automatic generation

Why:
- the manual-first clarification flow felt heavy
- the new direction is for PM to detect meaningful ambiguity automatically and route durable clarification questions into the Inbox when needed

Questions to resolve:
- does the automatic clarification threshold feel right?
- when should PM keep ambiguity inline in the thread versus escalate it into a durable Inbox clarification?
- does answering a clarification from the Inbox feel natural enough, or should the follow-up flow change further?

---

### 5. Bring manual verification workflow into the control panel itself

Status:
- high-value workflow improvement identified during testing

Why:
- the manual verification process before signoff was useful and confidence-building
- but having to run it outside the UI was unnecessarily painful
- the OS should support this workflow directly if manual verification is part of the signoff path

Questions to resolve:
- should the OS generate and surface manual test plans inside the UI?
- should the Product Director be able to:
  - view the current test plan
  - step through one test at a time
  - mark pass/fail
  - attach short notes
  - track verification state against the requirement directly
- should requirements remain unsigned off until their manual verification plan is completed when such a plan exists?

Potential outcome:
- make manual verification a first-class OS workflow surface rather than an external markdown process
- a strong variant to explore: let the Product Director pick a test card that hovers over the UI, guides the manual test step by step, tracks actions, and points to the next step while the test is being performed

---

### 6. Make agent and mode selection more explorable before choosing

Status:
- design and workflow improvement identified during post-test review

Why:
- the current dropdown-based agent and mode selection hides too much useful context
- the Product Director wants to see all agents and their modes up front, then click into the details before choosing intentionally
- the explanations of the modes were much clearer in conversation than in the current UI

Questions to resolve:
- should the agent selection surface show all agents as cards rather than a single dropdown?
- should each agent expose its modes inline with expandable explanations and examples?
- what level of role, scope, and example detail is enough to help intentional selection without making the UI heavy?

---

### 7. Add a user persona agent or persona surface per project

Status:
- major strategic workflow idea identified during post-test review

Why:
- if each project can develop a durable user persona from Product Director and PM discussions, other agents could use that persona to generate ideas, pressure-test assumptions, and validate whether the project is staying grounded in a real user

Questions to resolve:
- should the persona be a first-class agent, a durable project artifact, or both?
- which inputs should shape the first persona draft?
- which other agents should be allowed to use the persona for ideation, critique, or assumption validation?
- how do we keep the persona evidence-based rather than turning it into decorative fiction?

---

## Suggested Post-Test Discussion Order

1. `R28` — explicit mode selection vs inferred mode
2. `R32` — revisit whether a dedicated saved findings surface is needed
3. revisit routed-to-PM queue vs Orchestrator-only pickup
4. review how automatic PM clarifications feel in practice
5. bring manual verification workflow into the UI and OS signoff path
6. improve agent and mode selection UX
7. review the role of project user personas in the OS

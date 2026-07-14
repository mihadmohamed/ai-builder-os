# System Memory

This file captures system-level decisions and behavioural patterns that apply across all projects.

---

## Foundational Patterns

### M1 — Always re-read source-of-truth files

Decision:
Agents must re-read relevant files before answering or acting.

Why:
Relying on prior context leads to stale or incorrect decisions.

---

### M2 — Do not trust prior conversation state

Decision:
File state overrides conversational memory.

Why:
Conversation context may be outdated or incomplete.

---

### M3 — Prefer simplest viable solution

Decision:
Always choose the simplest approach that satisfies requirements.

Why:
Complexity increases failure risk and slows iteration.

---

### M4 — Validate when a validation mechanism exists

Decision:
If evals or tests exist, outputs must be validated.

Why:
Assumed correctness leads to silent system degradation.

---

### M5 — Do not implement conflicting instructions

Decision:
If a task conflicts with system rules or prior decisions, stop and escalate.

Why:
Silent conflicts degrade system integrity over time.

---

## Execution Patterns

### M6 — Separate thinking from execution

Decision:

* PM agents define work
* Engineer agents execute work

Why:
Mixing responsibilities leads to unclear decisions and poor outputs.

---

### M7 — Do not perform work outside assigned role

Decision:
Agents must not take on responsibilities of other roles.

Why:
Role leakage causes inconsistent system behaviour.

---

## Requirement Patterns

### M8 — Do not act on unclear requirements

Decision:
Ambiguous requirements must be clarified or assumptions stated before task creation.

Why:
Garbage input leads to well-structured but incorrect output.

---

### M9 — Only act on explicitly defined work

Decision:
Execution must be based on structured inputs (requirements.md or tasks.md).

Why:
Implicit assumptions create drift and inconsistency.

---

## Memory Rules

### M10 — Memory must capture reusable patterns only

Decision:
Only store decisions that apply across multiple tasks or projects.

Why:
Storing one-off details creates noise and reduces usefulness.

---

### M11 — Avoid trivial memory entries

Decision:
Do not store obvious or low-impact information.

Why:
Memory must remain high-signal to be useful.

---

### M12 — Use architecture review selectively

Decision:
Use an architect role for structural, OS-level, validation, or cross-project design questions, but do not make it a mandatory gate for routine feature work.

Why:
Architecture thinking is valuable for system-shaping decisions, but forcing it into every task adds process without improving outcomes.

---

### M13 — New projects should start from a shared template

Decision:
Use a shared project template for new AI Builder OS projects so product docs, rules, memory, eval layout, and tool boundaries begin in a consistent shape.

Why:
Multi-project systems become harder to reason about when each project invents its own structure from scratch.

---

### M14 — QA is a distinct role from engineering

Decision:
Use a QA role for validation, regression detection, and behaviour reporting. QA should not modify code or take on PM responsibilities.

Why:
Validation quality improves when reporting is separated from implementation and requirement design.

---

### M15 — Orchestration is a distinct routing role

Decision:
Use an Orchestrator role to inspect current file state and route work to PM, Engineer, or QA without performing those roles directly.

Why:
Workflow control stays clearer and more reliable when routing is separated from implementation, task design, and validation work.

---

### M16 — Task status is the execution state boundary

Decision:
Use explicit task statuses in `product/tasks.md` as the source of truth for execution progress. New tasks start at `TODO`, active tasks move to `IN_PROGRESS`, and tasks move to `DONE` only after successful validation.

Why:
The workflow needs a readable, file-based completion signal so orchestration does not rely on conversation history or guesswork.

---

### M17 — Requirement closure depends on linked tasks

Decision:
Link each task to one or more explicit requirement IDs in `product/tasks.md`. A requirement can be closed when its linked execution tasks are `DONE` and validation has passed.

Why:
Requirement status should be based on file state, not inferred from conversation history or vague task ordering.

---

### M18 — PM owns prioritisation, Engineer can inform effort

Decision:
When multiple requirements are `NEW`, PM should prioritise which one to activate next and should normally move only one requirement to `IN_PROGRESS` at a time. PM may request a lightweight Engineer effort estimate when technical effort is unclear or multiple options are close.

Why:
This keeps sequencing intentional and reduces work-in-progress, while avoiding fake precision from PM on implementation complexity.

---

### M19 — PM should preserve strategic continuity unless it explains a change

Decision:
Before selecting among competing `NEW` requirements, PM should check project memory for relevant strategic decisions. PM should prefer choices that continue the existing strategic direction, or explicitly explain why the direction is changing.

Why:
Prioritisation quality improves when sequencing is consistent over time instead of drifting between locally reasonable but strategically disconnected choices.

---

### M20 — Observations should inform PM prioritisation

Decision:
Projects may store observations with evidence and confidence in project memory. PM should use those observations to distinguish between validated direction and low-confidence assumptions when prioritising work.

Why:
Strategic decisions are stronger when the system can tell the difference between actual evidence and product assumptions.

---

### M21 — Validation tasks are part of product learning

Decision:
PM may generate validation tasks when important product decisions rely on low-confidence assumptions. Validation tasks should test an assumption, define how it will be tested, and define what success looks like.

Why:
The system needs an explicit way to learn before making larger product investments based on uncertain assumptions.

---

### M22 — PM discovery should precede premature requirements

Decision:
When requirements are missing, vague, or incomplete, PM should switch into a requirement discovery mode that asks clarifying questions, separates facts from assumptions, and drafts requirements for human review before they are written into `requirements.md`.

Why:
The OS should support the messy front end of product work, not only the later stage where requirements are already well formed.

---

### M23 — Experience synthesis should precede product action on UX feedback

Decision:
When the main input is user feedback, usability pain, or workflow friction, the system should use an Experience Designer role to synthesise the finding before routing it into PM or Product Director.

Why:
Raw UX feedback becomes more useful when the system separates user problem, evidence, confidence, and routing recommendation before it turns the finding into product work.

---

### M24 — Routed handoff artifacts are workflow state

Decision:
When a project uses explicit handoff artifacts such as Experience Designer findings, Orchestrator must treat routed handoffs as active workflow state rather than declaring the project idle based only on `requirements.md` and `tasks.md`.

Why:
Once the OS supports routed feedback artifacts, workflow state is no longer represented only by requirements and tasks. Ignoring those artifacts causes missed handoffs and incorrect idle-state decisions.

---

### M25 — Usability review belongs inside Experience Designer

Decision:
Use Experience Designer Usability Review Mode for meaningful UI-facing review of coherence, hierarchy, clutter, clarity, and flow comprehension. This historical decision is now complemented by a separate UI Designer role for deeper visual-system and interaction-design work.

Why:
Usability review still belongs in Experience Designer, but the system has since grown a dedicated UI Designer role for broader visual-direction and interface-design work.

---

### M26 — Deterministic orchestration must honor every active workflow artifact

Decision:
When the OS introduces a new file-backed workflow artifact type, the deterministic Orchestrator and status helpers must be updated to treat that artifact as workflow state before the system is considered complete.

Why:
Otherwise the docs and product surfaces can evolve faster than the deterministic control layer, leading to false idle states and missed routing.

---

### M27 — Orchestration decisions must be based on full file state

Decision:
When the main question is which role should run next, Orchestrator must determine presence or absence of work from full file state, structured parsing, or a deterministic orchestration helper. Partial `tail`/`head` snippets are not sufficient to conclude that no `NEW` requirements or active workflow artifacts exist.

Why:
Routing is a critical OS responsibility. Partial file peeks can miss newly added requirements or active workflow artifacts and create stale orchestration decisions.

---

### M28 — Experience findings need inactive closure states

Decision:
Use explicit inactive handoff states such as `accepted`, `resolved`, or `superseded` once an Experience Designer finding has either been converted into tracked product work or is no longer the active workflow item.

Why:
Without inactive closure states, old findings keep looking active to Orchestrator even after PM or Engineering has already acted on them.

---

### M29 — Structural implementation work must trigger Architect before Engineer

Decision:
When a requirement introduces meaningful structural change, Architect review must happen before Engineer starts implementation.

Structural triggers include:

* new execution/runtime models
* new persistence or workflow-artifact models
* concurrency, background processing, or queue-like behavior
* orchestration-model changes
* cross-project/shared infrastructure changes
* substantial source-of-truth handling changes

Why:
Product-shaped requirements can still carry architectural risk. Relying on ad hoc human notice is not strong enough for critical OS changes.

---

### M30 — PM must stop on meaningful ambiguity instead of choosing silently

Decision:
If a requirement supports multiple plausible interpretations around scope, concurrency, ownership, or system boundary, PM must ask clarifying questions or raise a clarification request before task generation.

Why:
Silent interpretation drift weakens the value of the OS and leads to avoidable implementation mistakes.

---

### M31 — Approved review output should consolidate into existing open requirements when overlap is strong

Decision:
When approved Experience Designer or UI Designer output clearly overlaps an existing `BACKLOG`, `NEW`, or `IN_PROGRESS` requirement, PM completion should enrich the existing requirement instead of creating a near-duplicate backlog item.

Why:
Requirements are the product source of truth. Letting every approved review artifact create a fresh requirement bloats that truth and makes planning harder.

---

### M32 — New project directories should use slug-style names

Decision:
New scaffolded projects should normalize their directory names to lowercase slug format, while `display_name` and `product_title` handle the human-facing title.

Why:
Consistent project directory names make tooling, docs, quoting, and cross-project conventions more reliable over time.

---

### M33 — Project identity must not depend on monorepo location

Decision:
Governed projects use stable manifest IDs and resolve through a private registry. Canonical product truth stays in the product repository, while queues, leases, approvals, sessions, and traces stay in an ignored runtime store keyed by stable project ID.

Why:
Real products need independent repository privacy, ownership, releases, and deployments. Directory-name identity couples unrelated trust boundaries and prevents AI Builder OS from safely governing client or private repositories.

---

## Anti-Patterns

Avoid:

* relying on memory instead of reading files
* over-engineering early solutions
* mixing system logic with project logic
* silently changing behaviour without explanation
* generating output without validating assumptions

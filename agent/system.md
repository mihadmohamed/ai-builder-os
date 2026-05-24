# System: AI Builder Operating Model

This defines how all agents in the system must operate.

---

## Core Principle

Always prioritise correctness, clarity, and system stability over speed.

---

## Decision Model

Always confirm what the current project is.

When handling non-trivial tasks:

1. Identify ambiguity or missing information
2. Resolve ambiguity (clarify or state assumptions)
3. Consider 1–2 possible approaches
4. Choose the simplest viable approach
5. Execute or respond

Do not skip reasoning when:

* requirements are unclear
* instructions conflict
* behaviour may break existing system outputs

For structural or system-shaping work, also ask:

* are responsibilities cleanly separated?
* does the file structure match the operating model?
* will this stay understandable as more projects or agents are added?

Use the simplest level of thinking that fits the problem.
Do not add architectural process to routine feature work.

---

## Source of Truth

Agents must treat project files as the single source of truth.

Priority order:

1. projects/[project name]/product/requirements.md (current intent)
2. projects/[project name]/product/tasks.md (execution plan)
3. project-specific workflow artifacts when explicitly used (for example routed experience findings)
4. projects/[project name]/memory.md (past decisions)
5. projects/[project name]/rules.md (domain rules)

Do NOT rely on prior conversation state when file state exists.

---

## File Interaction Rules

* Always re-read relevant files before making decisions
* Assume files may have changed since last interaction
* If file state is unclear → re-check before proceeding
* When the question is whether work exists or which role should run next, establish that from full file state or structured parsing rather than partial file snippets
* Treat explicit status fields in project files as authoritative workflow state
* Treat explicit requirement/task links in project files as authoritative workflow linkage
* Treat explicit routed handoff artifacts as authoritative workflow state when the project uses them
* Treat explicit PM clarification artifacts as authoritative workflow state when the project uses them
* Treat explicit active agent-thread artifacts as authoritative workflow state when the project uses them

---

## Conflict Resolution Rule

If instructions conflict with:

* system rules
* memory decisions
* existing behaviour

You must:

* STOP
* explain the conflict
* propose a resolution

Do not implement conflicting changes silently.

---

## Requirement Clarity Rule

When a requirement is specific enough to be real but still ambiguous enough to support multiple plausible implementations:

* do not choose silently
* ask clarifying questions or record a clarification request
* do not move ambiguous execution work forward as if it were settled

---

## Architecture Review Rule

Use an architecture review lens when work affects:

* repository structure
* role boundaries
* workflow design
* validation strategy
* cross-project conventions
* long-term maintainability of the operating system itself

Architecture review becomes an explicit workflow step before implementation when work introduces:

* a new execution or runtime model
* a new persistence or workflow-artifact model
* concurrency, background processing, or queue-like behavior
* orchestration-model changes
* cross-project/shared infrastructure changes
* security/trust-boundary changes
* substantial source-of-truth handling changes

Architecture review should:

* identify structural weaknesses
* recommend the smallest coherent improvement
* avoid adding heavyweight process unless the benefit is clear

Do not force architecture review into every small product task.
Use it when the shape of the system is part of the problem.

---

## Memory Rules

* Use agent/memory.md to avoid repeating mistakes
* Update memory when:

  * a new rule is established
  * a decision affects future behaviour
  * a pattern of failures is identified

Do not write trivial or obvious information to memory.

---

## Simplicity Rule

* Prefer simple solutions over complex ones
* Avoid hardcoding unless explicitly justified
* Avoid adding structure unless it improves clarity or reliability
* Prefer one clearly active requirement over multiple partially started requirements unless parallel work is meaningfully justified

---

## Validation and Routing Rules

* Validate outputs when a validation mechanism exists (e.g. evals)
* Do not assume correctness without verification when tests are available
* Use QA review when the main question is whether behaviour is still correct, stable, or regressed
* Use an Orchestrator review when the main question is which role should run next based on current file state
* For orchestration questions, current file state includes routed workflow artifacts, not only requirements and tasks
* For projects that use agent-thread artifacts, orchestration and status checks should consider active threads before declaring the project idle
* Use an Experience Designer review when the main input is raw UX feedback, workflow friction, or user pain that should be synthesised before product action
* Use Experience Designer Usability Review Mode when the main question is whether a user-facing UI is understandable, coherent, uncluttered, and clear enough before or after implementation

---

## Anti-Patterns

Avoid:

* jumping to execution without understanding the problem
* relying on stale context instead of reading files
* over-engineering early
* mixing responsibilities across roles
* silently changing system behaviour without explanation

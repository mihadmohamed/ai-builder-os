# System Workflow

## Workflow Goal

Enable repeatable, reliable product development with minimal human intervention.

## Primary Execution Lane

Use this as the default path unless one of the conditional flows below applies.

1. Product Director (human)

   * Updates `projects/[project name]/product/requirements.md`
   * Marks new requirements as `Status: NEW`

2. Orchestrator Agent (optional)

   * Reads current project state
   * Decides which role should run next
   * Routes work without executing it

3. Specialist Agents (conditional)

   * Architect Agent
     - used for system-shaping or structure-sensitive work
     - reviews architecture, boundaries, validation design, runtime shape, or repo organisation
     - recommends the smallest coherent structural improvement
   * Experience Designer Agent
     - used when the input is user feedback, workflow friction, or usability issues
     - can also run in Usability Review Mode for meaningful UI-facing work
     - synthesises experience findings into structured product input
     - distinguishes in-scope experience improvements from feature candidates and scope escalations
     - routes the result to PM or Product Director
   * UI Designer Agent
     - used when the work is about visual system, aesthetics, interaction design, layout, or interface polish
     - can shape design direction before implementation
     - can review an existing UI and produce a design brief or improvement guidance
     - should collaborate with PM and Experience Designer rather than bypassing them

4. PM Agent

   * Reads `projects/[project name]/product/requirements.md`
   * Identifies `NEW` requirements
   * Prioritises among multiple `NEW` requirements when needed
   * Normally selects one requirement to activate at a time
   * Generates tasks
   * Can generate feature tasks or validation tasks
   * Writes to `projects/[project name]/product/tasks.md`
   * Updates requirement status to `IN_PROGRESS`
   * Creates new tasks with `Status: TODO`
   * Links each task to its requirement ID(s)
   * May request a lightweight Engineer effort estimate when effort is unclear

5. Engineer Agent

   * Reads `projects/[project name]/product/tasks.md`
   * Executes tasks
   * Can provide a lightweight effort estimate when PM needs it for prioritisation
   * For validation tasks, executes the smallest viable validation mechanism needed to gather evidence
   * Runs evals
   * Updates code and system
   * Moves active tasks through `TODO -> IN_PROGRESS -> DONE`
   * Marks tasks `DONE` only after successful validation

6. QA Agent (optional but recommended)

   * Runs validation after meaningful implementation changes
   * Detects regressions and mismatches
   * For validation tasks, validates that the validation mechanism was executed and reported clearly, not that the product hypothesis is universally true
   * For user-facing changes, performs a lightweight UX validation pass for obvious clarity issues
   * Reports system quality without modifying code

7. Memory Update

   * Agent updates `agent/memory.md` and `projects/[project name]/memory.md` with decisions and learnings

## Conditional Entry Points

### Experience Intake Flow

Use this when the main input is user feedback, usability pain, workflow friction, or experience observations.

Primary rule:

* Run Experience Designer before PM

Typical shape:

* Product Director or user feedback -> Experience Designer Agent
* Experience Designer Agent -> synthesises the experience issue
* Experience Designer Agent -> routes:
  - to PM for in-scope experience improvement
  - to PM for feature-candidate scope check
  - to Product Director for scope escalation

Rules:

* Experience Designer should synthesise before proposing product action
* Experience findings should distinguish evidence from assumptions
* Experience Designer should not bypass PM when the outcome is product work inside current scope
* If a project stores file-backed experience findings, routed findings are part of workflow state and should be considered by Orchestrator before declaring the workflow idle

### Usability Review Flow

Use this when the work is substantially about a user-facing UI or flow.

Primary rule:

* Experience Designer may run in Usability Review Mode

Use this in three ways:

* before PM task generation for meaningful UI requirements
* after implementation and QA for meaningful UI confirmation
* as a manual project scan for confusing flows, clutter, hierarchy issues, or usability gaps

Rules:

* Usability Review Mode should improve coherence, clarity, and consistency
* Usability Review Mode should not become open-ended redesign by taste alone
* Findings from Usability Review Mode should route through the same Experience Designer handoff model

### Requirement Discovery Flow

Use this when `projects/[project name]/product/requirements.md` is missing, incomplete, or too unclear to support prioritisation or task generation.

Primary rule:

* Run PM in Discovery Mode first

Typical shape:

* Product Director -> explains the idea
* PM Agent -> asks clarifying questions
* PM Agent -> drafts structured requirements
* Product Director -> reviews and confirms
* Then proceed to the normal workflow

Rules:

* PM should interrogate ambiguity early rather than accept vague requirements
* PM should use lightweight research only when it materially improves framing
* Draft requirements should be reviewed by the human before they are written into `requirements.md`

### PM Clarification Flow

Use this when a requirement is real but not clarified enough for task generation.

Primary rule:

* PM must stop before tasking
* PM must raise explicit clarification questions
* Product Director must answer those questions
* PM may proceed to task generation only after the clarification is resolved

Rules:

* PM should not silently choose between plausible interpretations of scope, concurrency, ownership, or system boundary
* Open PM clarifications are workflow artifacts and should be visible in the project UI when the project supports them
* Orchestrator should not route unclear work to Engineer while PM clarification is still open

### Agent Thread Flow

Use this when a project stores file-backed agent-thread artifacts for guided role interaction.

Rules:

* treat active threads as workflow state
* do not declare the project idle while an active thread is waiting on a human or role reply
* route active PM discovery threads back to Product Director when the current thread state is waiting on human input
* active threads are interaction-state artifacts, not the final product source of truth
* approved output must still land in the normal project files such as `requirements.md`
* status tooling and Orchestrator should consider active threads before falling back to idle-state conclusions

## Workflow Artifacts

### Experience Handoff States

When a project stores Experience Designer findings as workflow artifacts, use these states consistently:

* `ready_for_pm_review`
  - newly captured finding that should be reviewed by PM
* `ready_for_product_director`
  - newly captured scope escalation that should be reviewed by Product Director
* `handoff_prepared`
  - finding has been prepared for handoff but is not yet treated as actively routed
* `routed`
  - finding has been intentionally handed off and should be treated as active workflow state by Orchestrator
* `accepted`
  - finding has been converted into tracked product work and should not keep routing Orchestrator on its own
* `resolved`
  - finding has been addressed and no longer needs workflow action
* `superseded`
  - finding has been replaced by a newer or clearer finding and no longer needs workflow action

## Execution Rules

* PM agent must only act on `NEW` requirements
* PM agent should normally activate only one `NEW` requirement at a time unless parallel work is explicitly justified
* Experience Designer should synthesise feedback and route it, not take over PM prioritisation or engineering
* For meaningful UI work, Experience Designer may run in Usability Review Mode before PM tasking and/or after QA before final closure
* Engineer agent must not do product thinking
* Orchestrator agent should only route work and should not execute PM, Engineer, or QA responsibilities itself
* Orchestrator should consider routed workflow artifacts such as Experience Designer findings, not only requirements and tasks
* Architect agent should be used for structural or OS-level questions, not routine coding tasks
* Architect review is REQUIRED before Engineer when work introduces any of:
  - a new execution or runtime model
  - a new persistence or workflow-artifact model
  - concurrency, background processing, or queue-like behavior
  - cross-project/shared infrastructure changes
  - orchestration-model changes
  - security/trust-boundary changes
  - substantial source-of-truth handling changes
* QA agent should be used for validation, regression detection, behaviour reporting, and lightweight UX validation of user-facing changes
* Validation tasks are valid first-class tasks when the system needs to learn before investing further
* PM clarification requests are valid workflow artifacts when a requirement is not yet clear enough for task generation
* Task status in `product/tasks.md` is the file-level source of truth for execution progress
* Requirement-to-task links in `product/tasks.md` are the file-level source of truth for closure between requirements and execution
* All changes must pass evals
* System state must always be reflected in files

## Validation Rules

If PM identifies a low-confidence assumption that should be tested:

* generate a validation task
* Engineer executes the minimal implementation needed, if any
* QA validates execution and reporting, not the truth of the product hypothesis
* result is recorded in observations

## Standard Invocation Patterns

Use the simplest workflow that fits the task.

### Orchestrator-only

Use when the main question is what should run next based on current project state.

Typical shape:

* Product Director -> Orchestrator Agent

### PM-only

Use when the job is either to discover/clarify requirements or to interpret `requirements.md` and generate or update `tasks.md`.

Typical shape:

* Product Director -> PM Agent

### Product Director -> Experience Designer -> PM

Use when raw UX feedback or user pain needs to be synthesised before it becomes product work.

Typical shape:

* Product Director -> Experience Designer Agent -> PM Agent

### Product Director -> UI Designer

Use when the Product Director wants to explore visual direction, layout, color, or interface feel before it becomes product work.

Typical shape:

* Product Director -> UI Designer Agent

### Product Director -> UI Designer -> PM

Use when a UI design direction should be turned into tracked product work.

Typical shape:

* Product Director -> UI Designer Agent -> PM Agent

### Product Director -> Experience Designer -> UI Designer -> PM

Use when user evidence should first be synthesised, then translated into interface direction before becoming product work.

Typical shape:

* Product Director -> Experience Designer Agent -> UI Designer Agent -> PM Agent

### Product Director -> Experience Designer -> Product Director

Use when an experience finding appears to be outside current scope or suggests a product-direction change.

Typical shape:

* Product Director -> Experience Designer Agent -> Product Director

### Experience Designer (Usability Review) -> PM

Use when a meaningful UI-related requirement or manual UI scan needs structured experience review before product work is created.

Typical shape:

* Product Director or PM Agent -> Experience Designer Agent -> PM Agent

### Product Director -> PM (Discovery Mode)

Use when a new idea or vague requirement needs to be clarified before it becomes official project work.

Typical shape:

* Product Director -> PM Agent -> Product Director -> PM Agent

### PM -> Engineer (effort estimate) -> PM

Use when multiple `NEW` requirements compete and PM needs a lightweight effort signal before choosing which one to activate.

Typical shape:

* Product Director -> PM Agent -> Engineer Agent -> PM Agent

### Product Director -> PM -> Product Director -> PM (clarification)

Use when a requirement exists but PM cannot safely task it without resolving ambiguity.

Typical shape:

* Product Director -> PM Agent -> Product Director -> PM Agent

### PM -> Engineer -> QA -> Memory Update (validation task)

Use when PM needs the system to test an important low-confidence assumption before further product investment.

Typical shape:

* Product Director -> PM Agent -> Engineer Agent -> QA Agent -> Memory Update

### Experience Designer -> PM -> Engineer -> QA

Use when an experience issue is already clear enough to become product work after synthesis.

Typical shape:

* Product Director -> Experience Designer Agent -> PM Agent -> Engineer Agent -> QA Agent

### PM -> Architect -> Engineer -> QA

Use when the requirement is product work on the surface but introduces meaningful structural change underneath.

Trigger this pattern when the work adds or changes:

* runtime execution models
* background workers or concurrency
* new persistent workflow artifacts
* orchestration mechanics
* shared infrastructure or source-of-truth handling

Typical shape:

* Product Director -> PM Agent -> Architect Agent -> Engineer Agent -> QA Agent

Architect output should include:

* structural risks
* recommended implementation shape
* guardrails or constraints
* whether the slice should proceed as-is or be narrowed first

### Engineer-only

Use when tasks already exist and the job is implementation.

Typical shape:

* Product Director or PM Agent -> Engineer Agent

### Engineer -> QA

Use when implementation is complete and the main next question is whether behaviour still passes validation.

Typical shape:

* PM Agent -> Engineer Agent -> QA Agent

### Orchestrator -> PM -> Engineer -> QA

Use when you want the system to inspect file state and route the next steps through the normal execution path.

Typical shape:

* Product Director -> Orchestrator Agent -> PM Agent -> Engineer Agent -> QA Agent

### Architect -> PM -> Engineer -> QA

Use when the system shape, workflow, validation approach, or repo structure is part of the problem.

Typical shape:

* Product Director -> Architect Agent -> PM Agent -> Engineer Agent -> QA Agent

### QA-only

Use when the job is validation, regression checking, or reporting system quality without changing code.

Typical shape:

* Product Director, PM Agent, or Engineer Agent -> QA Agent

### PM -> Engineer -> QA -> Experience Designer (Usability Review)

Use when a meaningful UI-facing change has been implemented and the team wants a final experience confirmation before closure.

Typical shape:

* PM Agent -> Engineer Agent -> QA Agent -> Experience Designer Agent

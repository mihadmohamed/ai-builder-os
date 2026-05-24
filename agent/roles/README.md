# Role Selection

Use this guide to choose the right AI Builder OS role for the task at hand.

## Quick Rule of Thumb

- Use **PM** when the work is about product definition, requirement clarity, or task generation.
- Use **Experience Designer** when the main input is user feedback, usability pain, or workflow friction that should be synthesised before product action.
- Use **UI Designer** when the work is about visual direction, layout, interaction design, or interface polish.
- Use **Orchestrator** when the question is which role should run next based on current file state.
- Use **Engineer** when the work is implementation.
- Use **Architect** when the shape of the system or workflow is the real problem.
- Use **QA** when the main question is whether the system still behaves correctly.

## PM

Use the PM role when the main job is to translate product intent into structured, executable work.

Typical cases:

- discovering and clarifying a new project idea
- interrogating a vague requirement before it becomes official
- identifying `NEW` requirements
- prioritising among multiple `NEW` requirements
- generating or updating `product/tasks.md`
- generating validation tasks when key decisions depend on low-confidence assumptions
- clarifying requirement scope before task generation
- stopping work to request clarification when a real requirement still has ambiguous scope, concurrency, or system-boundary semantics
- turning product intent into testable engineering tasks

Do not use PM for code changes or validation-only work.

## Experience Designer

Use the Experience Designer role when the main job is to turn UX signals into structured product input.

Typical cases:

- synthesising user feedback
- identifying workflow friction
- reviewing a user-facing UI for usability, clutter, hierarchy, scanability, or workflow friction
- distinguishing evidence from assumptions in UX findings
- deciding whether an issue is:
  - an in-scope UX improvement
  - a feature candidate
  - a scope escalation
- routing experience findings to PM or Product Director

Do not use Experience Designer for code changes, direct prioritisation, or implementation.

## UI Designer

Use the UI Designer role when the main job is to shape or review the interface itself.

Typical cases:

- discussing visual direction, color, tone, or look and feel
- shaping interaction design and layout decisions
- reviewing an existing screen for hierarchy, spacing, polish, or consistency
- proposing a stronger design direction before implementation
- collaborating with PM or Experience Designer on how a user-facing surface should feel
- shaping Streamlit-native workflows so they feel focused, legible, and well-structured rather than widget-heavy or notebook-like
- deciding when a Streamlit extra or component is justified to improve workflow clarity, navigation, or interaction quality

Do not use UI Designer for coding, direct prioritisation, or evidence-based UX synthesis work that properly belongs to Experience Designer.

## Experience Designer vs UI Designer

Choose **Experience Designer** when the problem is mostly about:

- understanding user pain
- synthesising evidence
- distinguishing UX improvement from feature work
- preparing a handoff into PM or Product Director

Choose **UI Designer** when the problem is mostly about:

- visual hierarchy
- layout and interaction direction
- interface polish
- stronger Streamlit-native design decisions before or after implementation

## Orchestrator

Use the Orchestrator role when the main job is to inspect project state and decide which role should run next.

Typical cases:

- checking whether `NEW` requirements need PM work
- deciding whether tasks should move to Engineer
- routing completed implementation to QA
- identifying whether failed validation should loop work back to Engineer
- checking whether a workflow artifact such as an experience finding or PM clarification is now the active blocking state

Do not use Orchestrator to do PM, Engineer, or QA work directly.

## Engineer

Use the Engineer role when the main job is implementation.

Typical cases:

- executing tasks from `product/tasks.md`
- giving a lightweight effort estimate when PM needs help judging complexity
- modifying code
- improving prompts, schemas, or extraction logic
- fixing regressions through implementation
- building the smallest viable mechanism for a validation task

Do not use Engineer for product planning when PM work is required.

## Architect

Use the Architect role when the shape of the system is the real problem.

Typical cases:

- repo or file-structure changes
- role boundary questions
- workflow redesign
- validation architecture changes
- multi-project conventions
- long-term maintainability review
- new runtime or execution models
- background workers or concurrency
- new workflow-state or persistence models
- security or trust-boundary changes
- substantial source-of-truth handling changes

Architect should also be triggered before engineering when a requirement introduces meaningful structural change.
Do not use Architect as a mandatory checkpoint for routine feature work.

## QA

Use the QA role when the main question is whether the system still behaves correctly.

Typical cases:

- running evals or tests
- checking for regressions
- summarising pass/fail status
- reporting system reliability
- verifying that a validation path itself is working
- doing a lightweight UX validation pass after meaningful user-facing changes

Do not use QA to modify code or generate product tasks.

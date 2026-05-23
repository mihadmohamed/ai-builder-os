# Role Selection

Use this guide to choose the right AI Builder OS role for the task at hand.

## PM

Use the PM role when the main job is to translate product requirements into executable work.

Typical cases:

- discovering and clarifying a new project idea
- interrogating a vague requirement before it becomes official
- identifying `NEW` requirements
- prioritising among multiple `NEW` requirements
- generating or updating `product/tasks.md`
- generating validation tasks when key decisions depend on low-confidence assumptions
- clarifying requirement scope
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

- discussing visual direction, colors, or look and feel
- shaping interaction design and layout decisions
- reviewing an existing screen for hierarchy, spacing, polish, or consistency
- proposing a stronger design direction before implementation
- collaborating with PM or Experience Designer on how a user-facing surface should feel
- shaping Streamlit-native workflows so they feel focused, legible, and well-structured rather than widget-heavy or notebook-like
- deciding when a Streamlit extra or component is justified to improve workflow clarity, navigation, or interaction quality

Do not use UI Designer for coding, direct prioritisation, or evidence-based UX synthesis work that properly belongs to Experience Designer.

## Orchestrator

Use the Orchestrator role when the main job is to inspect project state and decide which role should run next.

Typical cases:

- checking whether `NEW` requirements need PM work
- deciding whether tasks should move to Engineer
- routing completed implementation to QA
- identifying whether failed validation should loop work back to Engineer

Do not use Orchestrator to do PM, Engineer, or QA work directly.

## Engineer

Use the Engineer role when the main job is implementation.

Typical cases:

- executing tasks from `product/tasks.md`
- giving a lightweight effort estimate when PM needs help judging complexity
- modifying code
- improving prompts, schemas, or extraction logic
- fixing regressions through implementation

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

Do not use QA to modify code or generate product tasks.

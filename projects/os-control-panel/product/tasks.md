# Tasks — OS Control Panel

## Task 0: Establish a local validation baseline for the control panel

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Create the minimum project-local validation path needed so future UI work can be checked reliably as the project grows.

Requirements:
- Add a project-local deterministic validation runner or equivalent baseline validation path
- Add at least a narrow smoke check for the control panel application surface
- Make it clear how the engineer should validate the project after meaningful changes

Constraints:
- Keep the validation setup lightweight and local-first
- Do NOT overbuild test infrastructure before the first product slice exists
- Reuse established OS patterns where they fit the project

Validation:
- Run the project-local validation path
- Report any gaps that still remain after the baseline is added

Output:
- What validation path was added
- Why this baseline was chosen
- What is and is not covered yet

## Task 1: Build the workspace shell and summary view

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Create the first usable workspace-level UI so the operator can see the OS as a control panel rather than a collection of files.

Requirements:
- Add a workspace summary page as the primary entry point
- Show the available projects in a clear, lightweight way
- Show the most important workspace-level signals without requiring the operator to read raw markdown files
- Include role summaries for the AI Builder OS agents

Constraints:
- Keep the UI simple and internal-facing
- Do NOT build deep workflow control surfaces yet
- Keep raw traces and noisy internal debugging data out of the default workspace UI

Validation:
- Use the project-local validation path
- Confirm the workspace shell renders and the summary data loads

Output:
- What workspace summary view was added
- What agent role information is visible
- Any intentional omissions kept out of V1

## Task 2: Add the new-project creation flow

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Let the operator create a new AI Builder OS project from the UI end-to-end using the existing scaffold/template system.

Requirements:
- Add a UI flow to create a new project with:
  - project name
  - display name
  - initial idea / requirement
- Use the existing project scaffold/template mechanism rather than inventing a separate project format
- Make the created project visible in the workspace summary after creation

Constraints:
- Keep the flow local-first
- Do NOT add remote/shared project creation concerns in V1
- Do NOT ask for extra project metadata beyond the agreed V1 fields

Validation:
- Use the project-local validation path
- Verify a new project can be scaffolded from the UI with the required fields

Output:
- What project-creation flow was added
- How it connects to the existing scaffold system
- Any current limitations in the create-project experience

## Task 3: Add the project page with structured requirement editing and prioritisation

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Let the operator manage requirements in a structured UI without editing raw `requirements.md` directly.

Requirements:
- Add a project drill-down page
- Show requirements in structured cards or forms rather than raw markdown
- Support editing requirement fields needed in V1, including:
  - title
  - description
  - priority
  - status
  - effort
- Support manual prioritisation or ordering of requirements
- Support asking PM for a prioritisation recommendation

Constraints:
- Limit editing to requirements in V1
- Do NOT add memory/rules editing in this phase
- Keep the interaction clear and operator-friendly rather than building a dense admin console

Validation:
- Use the project-local validation path
- Verify requirement changes persist correctly into project files

Output:
- What requirement editing model was added
- How prioritisation works in the UI
- Any remaining rough edges in the structured editing flow

## Task 4: Add the PM discovery flow for new ideas

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Bring PM Discovery Mode into the UI so new ideas can move from rough concept to draft requirements inside the control panel.

Requirements:
- Add a hybrid PM discovery experience with:
  - initial idea input
  - PM clarifying questions
  - draft requirements for review
- Keep a lightweight discovery history model that shows:
  - the latest active draft
  - an archive link for older sessions
- Make it possible to save approved draft requirements into the project

Constraints:
- Keep the UI uncluttered even when discovery history exists
- Do NOT turn V1 into a full chat product
- Do NOT write draft requirements into `requirements.md` before human confirmation

Validation:
- Use the project-local validation path
- Verify a discovery session can produce a draft and save an approved result into project requirements

Output:
- What discovery flow was added
- How draft review and confirmation work
- How discovery history is kept lightweight

## Task 5: Add a project-level Experience Designer entry point

Type: Feature Task
Status: DONE
Requirement: R5

Goal:
Expose the Experience Designer role at the project level so the Product Director can give structured UX feedback without leaving the UI.

Requirements:
- Add an Experience Designer entry point inside the project-level UI only
- Make the entry point clearly distinct from PM discovery
- Let the Product Director describe UX pain, workflow friction, or feedback in a structured way from the selected project page

Constraints:
- Keep Experience Designer scoped to the project level in this first slice
- Do NOT trigger PM automatically from the Experience Designer flow
- Keep the interaction lightweight and consistent with the current project-detail experience

Validation:
- Use the project-local validation path
- Verify the Experience Designer flow is only available at the project level
- Manually confirm the entry point is understandable without command-line context

Output:
- What Experience Designer entry point was added
- How it is scoped to the project page
- Any remaining limitations in the first project-level entry

## Task 6: Add structured experience synthesis output and routing classification

Type: Feature Task
Status: DONE
Requirement: R5

Goal:
Help the Experience Designer produce structured findings that can feed the OS workflow cleanly.

Requirements:
- Capture and display structured Experience Designer output including:
  - user problem
  - affected user / workflow
  - evidence
  - confidence
  - severity / frequency
  - recommendation type
  - rationale
  - recommended next role
- Support recommendation types aligned with the OS:
  - UX improvement in scope
  - feature candidate
  - scope escalation

Constraints:
- Do NOT collapse Experience Designer output into PM task generation
- Keep the role boundary clear: synthesis and routing only
- Prefer structured output over free-form, noisy transcripts

Validation:
- Use the project-local validation path
- Verify the structured output renders consistently for each recommendation type

Output:
- What synthesis structure was added
- How recommendation types are represented
- Any edge cases still handled manually

## Task 7: Add a lightweight handoff path from Experience Designer findings into the OS workflow

Type: Feature Task
Status: DONE
Requirement: R5

Goal:
Let project-level Experience Designer findings move into the OS workflow without breaking role boundaries.

Requirements:
- Make it possible to keep an Experience Designer finding in the UI as a reusable project-level artifact
- Support a manual handoff path appropriate to the recommendation type:
  - in-scope improvement -> ready for PM review
  - feature candidate -> ready for PM scope check
  - scope escalation -> clearly surfaced back to Product Director
- Keep the handoff explicit rather than automatically triggering downstream roles

Constraints:
- Do NOT auto-run PM from the UI in this slice
- Do NOT silently turn every UX finding into a new requirement
- Keep the flow understandable for a single local operator

Validation:
- Use the project-local validation path
- Verify that each recommendation type leads to a clear next manual OS step

Output:
- What handoff path was added
- How the flow preserves Experience Designer vs PM role boundaries
- Any manual steps that remain intentional in V1

## Task 8: Clarify the workspace heading and top-level page framing

Type: Feature Task
Status: DONE
Requirement: R6

Goal:
Reduce confusion between the control-panel page title and the `os-control-panel` project name.

Requirements:
- Update the main workspace heading so it clearly describes the OS/workspace surface rather than repeating the project name
- Keep the new heading aligned with the local-first AI Builder OS framing
- Preserve existing functionality and layout structure while improving clarity

Constraints:
- Do NOT turn this into a broader brand redesign
- Keep the change small and readable

Validation:
- Use the project-local validation path
- Manually confirm the page heading is easier to distinguish from project names

Output:
- What heading changed
- Why the new framing is clearer

## Task 9: Reduce clutter in workspace project cards

Type: Feature Task
Status: DONE
Requirement: R6

Goal:
Make the workspace summary easier to scan by showing only the most useful high-level project signals there.

Requirements:
- Remove full task-detail clutter from workspace project cards
- Show concise project-level summary signals instead, including:
  - pending task count
  - new requirement count
- Keep deeper task detail inside the project view rather than the workspace overview

Constraints:
- Preserve the usefulness of the workspace summary
- Do NOT remove signals that help the operator understand project health at a glance

Validation:
- Use the project-local validation path
- Manually confirm project cards are easier to scan without losing key information

Output:
- What card content was simplified
- What summary signals remain visible

## Task 10: Make the agent role cards visually consistent

Type: Feature Task
Status: DONE
Requirement: R6

Goal:
Improve the visual consistency of the role-card section so it feels more polished and easier to read.

Requirements:
- Make the agent cards uniform in overall presentation and apparent size
- Preserve the current role information while improving visual consistency
- Keep the section lightweight and internal-facing

Constraints:
- Do NOT add new role content unless needed to support visual consistency
- Do NOT turn the role section into a complex marketing surface

Validation:
- Use the project-local validation path
- Manually confirm the agent cards feel visually consistent

Output:
- What was changed in the role-card presentation
- Any remaining limitations in the current layout

## Task 11: Resolve the remaining role-card visual imbalance

Type: Feature Task
Status: DONE
Requirement: R7

Goal:
Make the role-card section read as visually even so the workspace feels calmer and more polished.

Requirements:
- Adjust the role-card rendering so the cards appear visually consistent in height and alignment
- Preserve the current role information and lightweight internal-facing style
- Prefer a small layout fix over broader redesign

Constraints:
- Do NOT expand the role section into a richer feature surface
- Keep the change scoped to the remaining visual-coherence issue

Validation:
- Use the project-local validation path
- Manually confirm the role cards read as visually even in the workspace

Output:
- What caused the visual imbalance
- What was changed to resolve it

## Task 12: Change workspace project summaries to a compact card grid

Type: Feature Task
Status: DONE
Requirement: R8

Goal:
Make the workspace project summaries easier to scan by using a more compact multi-card layout instead of one full-width stacked list.

Requirements:
- Render workspace project summaries as smaller cards with sensible width
- Allow project cards to sit side by side where space allows
- Preserve the current high-level project signals while improving layout balance

Constraints:
- Keep the workspace internal-facing and lightweight
- Do NOT turn the workspace into a dense dashboard

Validation:
- Use the project-local validation path
- Manually confirm the project-summary layout feels more balanced and easier to scan

Output:
- What changed in the project-summary layout
- Why the new layout is easier to scan

## Task 13: Add clearer vertical spacing between role-card rows

Type: Feature Task
Status: DONE
Requirement: R8

Goal:
Improve the visual separation between the top and bottom rows of the role-card section.

Requirements:
- Add clear vertical spacing between role-card rows
- Preserve the balanced-row layout introduced for role-card polish
- Keep the section visually calm and consistent

Constraints:
- Keep the change small and layout-focused
- Do NOT expand the role section with new functionality

Validation:
- Use the project-local validation path
- Manually confirm the role-card rows have enough separation to read as distinct rows

Output:
- What spacing was added
- Why the updated section feels more visually balanced

## Task 14: Separate done requirements from active requirement work

Type: Feature Task
Status: DONE
Requirement: R9

Goal:
Make the Requirements view easier to scan by keeping completed items out of the main active-work path.

Requirements:
- Display unfinished requirements ahead of completed ones
- Give `DONE` requirements their own clearly secondary section or placement at the bottom
- Preserve visibility of completed work without letting it dominate the page

Constraints:
- Keep the Requirements view simple and operator-friendly
- Do NOT remove access to completed requirements entirely

Validation:
- Use the project-local validation path
- Manually confirm the Requirements page focuses attention on unfinished work first

Output:
- What changed in the Requirements-page organization
- Why the new organization is easier to use

## Task 15: Prevent direct editing of completed requirements

Type: Feature Task
Status: DONE
Requirement: R9

Goal:
Reduce accidental interaction with completed work by making `DONE` requirements non-editable in the main Requirements flow.

Requirements:
- Prevent direct editing controls for requirements with `Status: DONE`
- Keep completed requirements readable while making their closed state clear
- Preserve editing for unfinished requirements

Constraints:
- Do NOT create a complex permission model
- Keep the behaviour obvious and consistent with the rest of the page

Validation:
- Use the project-local validation path
- Manually confirm `DONE` requirements can be reviewed but not edited directly

Output:
- What edit controls changed for completed requirements
- How the closed state is communicated in the UI

## Task 16: Review and improve the active requirement-card layout

Type: Feature Task
Status: DONE
Requirement: R10

Goal:
Improve the visual balance of the active requirement cards so the Requirements page uses space more effectively without becoming harder to scan.

Requirements:
- Review the current full-width card layout for active requirements
- Implement a more balanced layout if it improves scanability and use of space
- Preserve the clarity of requirement editing and prioritisation controls

Constraints:
- Keep the change scoped to layout and presentation
- Do NOT turn the Requirements page into a dense dashboard
- Do NOT reduce readability in exchange for compactness

Validation:
- Use the project-local validation path
- Manually confirm the updated Requirements page feels more balanced and still easy to use

Output:
- What layout changed
- Why the new layout is a better use of space

## Task 17: Improve symmetry for uneven active-requirement rows

Type: Feature Task
Status: DONE
Requirement: R11

Goal:
Make the active Requirements-page layout feel more visually balanced when the number of active cards leaves a partial final row.

Requirements:
- review how partial rows of active requirement cards are rendered
- improve the layout so lone or uneven final-row cards feel less stretched and more intentional
- preserve usability and readability of the requirement-editing flow

Constraints:
- keep the change layout-focused
- do NOT sacrifice clarity for decorative symmetry
- keep the Requirements page simple and internal-facing

Validation:
- use the project-local validation path
- manually confirm partial active-card rows feel more balanced after the change

Output:
- what caused the asymmetry
- what layout adjustment improved it

## Task 18: Add staged PM Discovery intake

Type: Feature Task
Status: DONE
Requirement: R12

Goal:
Replace the flat PM Discovery intake with a staged flow that starts from the initial idea and reveals only the next relevant questions.

Requirements:
- ask for the initial idea first
- generate a smaller next-step question set based on the current project context and the PM discovery goal
- keep the interaction lightweight and easy to answer

Constraints:
- do NOT turn PM Discovery into a full chat product
- keep the flow local-first and file-backed
- preserve the existing approval boundary before writing confirmed requirements

Validation:
- use the project-local validation path
- manually confirm the PM Discovery flow no longer starts with a large flat form

Output:
- what staged PM Discovery flow was added
- how the next questions are selected

## Task 19: Add staged Experience Designer intake

Type: Feature Task
Status: DONE
Requirement: R12

Goal:
Make the Experience Designer flow progressive so the Product Director starts with the user problem and is then asked only the most relevant follow-up questions.

Requirements:
- ask for the user problem first
- generate the next relevant experience-synthesis prompts from that starting point
- keep the flow structured enough to preserve finding quality without feeling heavy

Constraints:
- do NOT collapse Experience Designer into a generic free-form chat
- preserve the existing structured finding output and routing model
- keep the interaction simple and project-aware

Validation:
- use the project-local validation path
- manually confirm the Experience Designer flow feels more progressive and less form-heavy

Output:
- what staged Experience Designer flow was added
- how structured finding quality is preserved

## Task 20: Preserve lightweight history while supporting progressive discovery

Type: Feature Task
Status: DONE
Requirement: R12

Goal:
Keep the discovery surfaces simple even after making them progressive, so history and current interaction state do not clutter the UI.

Requirements:
- preserve the latest active draft plus archive pattern for PM Discovery
- keep Experience Designer findings and in-progress intake state understandable without turning the page into a dense transcript
- make the current step obvious in both flows

Constraints:
- do NOT add a heavy conversation console
- prefer compact state and summaries over long visible transcripts

Validation:
- use the project-local validation path
- manually confirm both flows stay visually calm while supporting multi-step interaction

Output:
- what UI/state model keeps the flows lightweight
- any remaining simplifications or tradeoffs

## Task 21: Make requirement-card default expansion consistent

Type: Feature Task
Status: DONE
Requirement: R13

Goal:
Make the default expansion state of requirement cards consistent so the Requirements tab feels predictable and visually calm.

Requirements:
- review the current default-expanded behavior in the Requirements tab
- make the initial expansion state consistent across active requirement cards
- preserve the readability of requirement details without forcing one card open by default

Constraints:
- keep the change small and behavior-focused
- do NOT redesign the whole Requirements page
- preserve the existing active/completed separation

Validation:
- use the project-local validation path
- manually confirm requirement cards no longer open inconsistently by default

Output:
- what default expansion behavior changed
- why the new behavior is more consistent

## Task 22: Make PM follow-up questions depend on the submitted idea

Type: Feature Task
Status: DONE
Requirement: R14

Goal:
Improve PM Discovery so the follow-up questions are meaningfully shaped by the submitted idea instead of relying on one mostly fixed question set.

Requirements:
- inspect the initial idea before choosing the next PM questions
- tailor the follow-up prompts so they reflect the kind of idea being explored
- keep the interaction simple and relevant rather than verbose

Constraints:
- do NOT turn the flow into a full free-form chat agent
- keep the logic local-first and easy to validate
- preserve the existing draft approval boundary

Validation:
- use the project-local validation path
- manually confirm different idea types produce more relevant PM follow-up questions

Output:
- what changed in PM question selection
- why the new questions feel more idea-specific

## Task 23: Improve PM Discovery framing so it feels more like PM guidance

Type: Feature Task
Status: DONE
Requirement: R14

Goal:
Make the PM Discovery experience feel more genuinely guided by PM thinking rather than like a lightly reshuffled form.

Requirements:
- improve the PM Discovery wording and interaction framing where needed
- make the intent of each follow-up question clearer
- preserve the lightweight archive and draft flow

Constraints:
- keep the change scoped to PM Discovery only
- do NOT expand this requirement into Experience Designer work
- do NOT redesign the whole project-detail page

Validation:
- use the project-local validation path
- manually confirm the PM Discovery flow feels more guided and idea-aware

Output:
- what interaction/framing changes were made
- how the discovery flow now better reflects PM guidance

## Task 24: Add a requirement-level implementation entry point in the UI

Type: Feature Task
Status: DONE
Requirement: R15

Goal:
Let the Product Director initiate implementation from a requirement inside the control panel instead of leaving the UI to start the workflow.

Requirements:
- add an implementation entry point on eligible requirements
- make the action clearly tied to a specific requirement
- keep the control understandable and hard to trigger accidentally

Constraints:
- do NOT support launching multiple requirement implementations at once
- keep the first slice scoped to requirement-level initiation rather than full workflow editing
- preserve the file-backed source-of-truth model

Validation:
- use the project-local validation path
- manually confirm implementation can be initiated from the requirement surface

Output:
- what requirement-level entry point was added
- how the implementation action is presented in the UI

## Task 25: Enforce one active implementation flow at a time

Type: Feature Task
Status: DONE
Requirement: R15

Goal:
Preserve the project-level rule of one active implementation flow at a time when orchestration is initiated from the UI.

Requirements:
- block or disable starting a second requirement implementation while one is already active in the same project
- make the reason visible to the user
- keep the rule aligned with the PM/orchestration model of one active requirement at a time within a project

Constraints:
- do NOT add a complex queueing system in this slice
- do NOT weaken the clarified one-active-requirement-per-project discipline

Validation:
- use the project-local validation path
- manually confirm the UI prevents concurrent requirement implementations

Output:
- how the one-at-a-time rule is enforced
- how the UI explains the restriction

## Task 26: Add an orchestrated implementation execution path

Type: Feature Task
Status: DONE
Requirement: R15

Goal:
Connect the UI initiation path to a real orchestration execution flow so requirement implementation can proceed without returning to the CLI.

Requirements:
- trigger the OS workflow from the UI for the selected requirement
- preserve role boundaries within the execution path
- keep the orchestration flow grounded in the existing source-of-truth files

Constraints:
- do NOT skip PM, Engineer, or QA semantics just because the flow starts in the UI
- keep the first execution path observable and deterministic enough to debug
- prefer the smallest viable orchestration integration over a fully general runtime system

Validation:
- use the project-local validation path
- manually confirm a requirement implementation can run end-to-end from the UI path

Output:
- what orchestration execution path was added
- what boundaries or limitations still remain in the first slice

## Task 27: Display implementation outcome and errors in the UI

Type: Feature Task
Status: DONE
Requirement: R15

Goal:
Return a clear implementation summary to the Product Director after the orchestrated flow completes or fails.

Requirements:
- show a concise implementation summary in the UI after the workflow completes
- surface errors clearly when the workflow fails
- make it clear which requirement the summary or failure belongs to

Constraints:
- do NOT turn this into a full trace console
- keep the reporting high-signal and operator-friendly

Validation:
- use the project-local validation path
- manually confirm completion and error reporting are visible from the UI

Output:
- what implementation summary is shown
- how errors are surfaced back to the Product Director

## Task 28: Add file-backed requirement deletion

Type: Feature Task
Status: DONE
Requirement: R17

Goal:
Let the control panel remove eligible requirements from the project source-of-truth file without corrupting the remaining requirement document.

Requirements:
- Add a requirement deletion operation that removes a selected requirement from `product/requirements.md`
- Allow deletion only for unfinished requirements: NEW, IN_PROGRESS, and BACKLOG
- Reject deletion of DONE requirements
- Preserve the remaining requirement content, ordering, active/backlog sections, and rules text

Constraints:
- Do NOT add recycle bin, undo, or archival behavior in this first version
- Do NOT delete completed requirements
- Keep deletion scoped to requirements only

Validation:
- Add deterministic coverage for deleting eligible requirements
- Add deterministic coverage that DONE requirements cannot be deleted
- Run the project-local validation path

Output:
- What deletion operation was added
- How completed requirements are protected

## Task 29: Add a confirmed delete action to requirement cards

Type: Feature Task
Status: DONE
Requirement: R17

Goal:
Expose deletion in the Requirements UI in a way that is hard to trigger accidentally and hidden from completed requirements.

Requirements:
- Show a delete control only for unfinished requirement cards
- Require explicit confirmation before deletion is performed
- Make the successful deletion outcome visible to the operator
- Keep completed requirement cards free of delete controls

Constraints:
- Do NOT redesign the requirement editor
- Do NOT add bulk delete in this first version
- Do NOT make deletion available from completed requirement cards

Validation:
- Add deterministic coverage for delete eligibility rules where possible
- Run the project-local validation path
- Manually inspect the UI code path for confirmation and completed-requirement exclusion

Output:
- What UI control was added
- How accidental deletion is guarded against

## Task 30: Add a project-level agent workspace for PM discovery

Type: Feature Task
Status: DONE
Requirement: R18

Goal:
Replace the old PM Discovery staging surface with a project-level agent workspace that is PM-first but can expand to other agents later.

Requirements:
- Add an agent-selection surface inside the project view
- Support PM as the first concrete agent option
- Support `Requirement Discovery` as the first PM mode
- Keep the architecture open to future agent additions without requiring a UI rewrite

Constraints:
- Do NOT pretend this is already full multi-agent orchestration
- Keep the first slice scoped to PM only
- Preserve the existing file-backed project model

Validation:
- Add deterministic coverage for the new PM thread model
- Run the project-local validation path

Output:
- What agent workspace surface was added
- How the PM-first architecture stays extensible

## Task 31: Add a real PM chat thread for requirement discovery

Type: Feature Task
Status: DONE
Requirement: R18

Goal:
Turn PM discovery from a staged form into a real chat-like interaction where PM asks clarifying questions and the Product Director answers iteratively.

Requirements:
- Start the conversation from an initial idea
- Show PM follow-up messages as a thread rather than a flat question form
- Let PM ask the next relevant clarifying question
- Let the Product Director answer iteratively until PM has enough context

Constraints:
- Keep the interaction clean and operator-friendly
- Keep PM chat focused on the conversation rather than raw tracing or internal debugging detail
- Do NOT make Experience Designer part of this first slice

Validation:
- Add deterministic coverage for starting and continuing the PM chat thread
- Run the project-local validation path

Output:
- What PM chat behavior was introduced
- How the clarifying-question loop now works

## Task 32: Add PM draft generation with manual draft override

Type: Feature Task
Status: DONE
Requirement: R18

Goal:
Allow PM to decide when it has enough context to draft requirements, while still giving the Product Director a manual `Draft requirements now` control.

Requirements:
- PM should auto-draft once enough discovery context is present
- The UI should also provide a manual draft trigger
- Generated drafts should use the existing structured PM discovery output format
- The draft should stay reviewable before it is saved into `requirements.md`

Constraints:
- Do NOT require the full question set to be answered before a draft can exist
- Keep the draft path deterministic and file-backed

Validation:
- Add deterministic coverage for auto-draft and manual-draft behavior
- Run the project-local validation path

Output:
- When PM drafts automatically
- How the manual draft action works

## Task 33: Save PM chat drafts into project requirements without preserving a cluttered visible chat history

Type: Feature Task
Status: DONE
Requirement: R18

Goal:
Let reviewed PM draft output be committed into `requirements.md` while keeping the UI clean and avoiding a persistent visible chat archive.

Requirements:
- Save reviewed drafts into `product/requirements.md`
- Mark the active PM thread as complete once its draft is saved
- Avoid showing a long visible archive of past PM conversations in the main UI
- Keep the implementation compatible with future agent expansion

Constraints:
- Do NOT reintroduce the old discovery archive as the primary UX
- Do NOT lose the resulting requirement draft before approval

Validation:
- Add deterministic coverage for saving a PM thread draft into requirements
- Run the project-local validation path

Output:
- How a reviewed draft reaches `requirements.md`
- How the UI stays clean after save

## Task 34: Add file-backed agent summary data for workspace popups

Type: Feature Task
Status: DONE
Requirement: R19

Goal:
Provide concise, structured agent summary content that the workspace can render without exposing raw role, memory, or workflow files.

Requirements:
- Define a lightweight agent summary model for the existing OS roles shown on the workspace
- Include for each agent:
  - what the agent can do
  - memory or context highlights relevant to that agent
  - the agent's position in the workflow
- Keep the source of the summaries aligned with existing role/workflow/memory files where practical
- Make the summary content available through the existing workspace data path

Constraints:
- Do NOT add a second workflow source of truth
- Use concise summaries instead of raw traces or long markdown files in the popup
- Do NOT add agent execution or workflow mutation behavior

Validation:
- Add deterministic coverage for the agent summary data shape and expected role coverage
- Run the project-local validation path

Output:
- What agent summary data model was added
- How the content stays aligned with existing OS context

## Task 35: Add clickable workspace agent tiles with summary popup

Type: Feature Task
Status: DONE
Requirement: R19

Goal:
Let the Product Director click an agent tile on the workspace and read a focused summary without leaving the workspace page.

Requirements:
- Make workspace agent tiles clickable
- Open a popup/modal for the selected agent
- Show what the agent can do, relevant memory/context, and workflow position
- Provide a clear dismiss path
- Preserve the current workspace card layout and visual calm

Constraints:
- Do NOT navigate away from the workspace for this first slice
- Do NOT make the popup an execution control surface
- Do NOT add editing of role, workflow, memory, or project-rule files
- Keep the popup concise and scannable

Validation:
- Add deterministic coverage where practical for popup data rendering behavior
- Run the project-local validation path
- Manually inspect the UI code path for non-execution behavior and dismiss flow

Output:
- What workspace interaction was added
- How the popup presents the agent summary

## Task 36: Validate agent summary popup coverage and workflow boundaries

Type: Validation Task
Status: DONE
Requirement: R19

Goal:
Confirm the first version helps users understand agents while preserving the OS role and workflow boundaries.

Requirements:
- Verify every workspace agent tile has popup content
- Verify popup content covers capability, memory/context, and workflow position
- Verify clicking and dismissing the popup does not change project workflow state
- Verify no agent execution controls were added to the popup

Constraints:
- Keep validation local and deterministic where possible
- Do NOT broaden this into visual redesign beyond obvious defects introduced by the feature

Validation:
- Run the project-local validation path
- Run any scenario or unit tests added for R19
- Record any remaining UX or content limitations if found

Output:
- Which role summaries were validated
- Whether workflow boundaries were preserved

## Task 37: Simplify project navigation from the workspace

Type: Feature Task
Status: DONE
Requirement: R20

Goal:
Remove the redundant top-level Project Detail tab and let the operator open a project directly from the workspace project cards.

Requirements:
- Make each workspace project card provide a clear action to open that project
- Remove the top-level `Project Detail` tab from the primary navigation
- When a project is opened from a workspace card, show the existing project detail experience for that selected project
- Preserve the existing Requirements, Agents, and Experience Designer project-level tabs once inside a project
- Keep New Project creation available from the top-level navigation

Constraints:
- Do NOT remove the workspace summary as the primary entry point
- Do NOT change the file-backed project or requirement model
- Do NOT add multi-project workflow execution or broader navigation redesign in this task
- Keep the navigation local-first and simple

Validation:
- Add deterministic coverage for the project-card navigation state helpers where practical
- Run the project-local validation path
- Manually inspect the UI code path to confirm Project Detail is no longer a top-level tab and project cards open the project view

Output:
- What navigation changed
- How project detail remains reachable
- Whether the redundant top-level tab was removed

## Task 38: Replace fixed PM-question sequencing with a hybrid planner

Type: Feature Task
Status: DONE
Requirement: R21

Goal:
Make PM discovery decide the next question from what is still missing or unclear, instead of walking a fixed list in order.

Requirements:
- Track PM discovery against structured requirement fields under the hood
- Determine the next question from the current thread answers, not just from question index
- Stay on the same topic when the last answer is too vague to support drafting
- Move on once PM has enough detail for the current topic
- Keep the thread model ready for a later planner switch to a full live-agent mode

Constraints:
- Keep the thread file format backward-compatible where practical
- Do NOT implement the full live-agent planner in this task
- Do NOT remove the manual draft action

Validation:
- Add deterministic coverage for vague-answer follow-up behavior
- Add deterministic coverage for context-aware next-question selection
- Run the project-local validation path

Output:
- How PM now chooses the next question
- What future hook was added for the live-agent planner

## Task 39: Refresh the PM agent chat framing around the hybrid planner

Type: Feature Task
Status: DONE
Requirement: R21

Goal:
Make the PM discovery UI explain the new hybrid behavior honestly and clearly.

Requirements:
- Update the PM discovery framing so the user understands the planner is adapting to prior answers
- Keep the current PM-first agent workspace intact
- Preserve a clean review-and-save flow once PM drafts requirements

Constraints:
- Do NOT add a visible thread archive
- Do NOT imply the full live-agent mode already exists

Validation:
- Manually inspect the PM discovery UI copy path
- Run the project-local validation path

Output:
- What PM discovery copy changed
- How the UI sets expectation for the hybrid planner

## Task 40: Validate adaptive PM discovery behavior

Type: Validation Task
Status: DONE
Requirement: R21

Goal:
Confirm the hybrid PM planner behaves more intelligently while preserving deterministic draft output.

Requirements:
- Validate that vague answers trigger follow-up on the same topic
- Validate that stronger answers advance PM to the next relevant topic
- Validate that PM still produces a structured draft and save flow
- Validate that the thread artifact remains future-ready for a later live-agent planner mode

Constraints:
- Keep validation deterministic for the hybrid planner slice
- Do NOT expand this into full hosted/live-agent testing

Validation:
- Run unit coverage for the adaptive PM-thread logic
- Run the project-local eval path

Output:
- Which adaptive behaviors were validated
- Whether deterministic draft output stayed intact

## Task 41: Add a live PM new-project thread model and runtime

Type: Feature Task
Status: DONE
Requirement: R22

Goal:
Introduce a true live PM discovery path for brand-new projects, separate from the in-project hybrid planner.

Requirements:
- Add a live PM thread model for the New Project flow
- Call a live OpenAI-backed PM turn planner for that thread
- Support iterative replies and a manual draft action
- Keep the thread shape ready for future expansion without replacing the in-project hybrid PM path

Constraints:
- Do NOT replace the existing in-project hybrid PM flow in this task
- Do NOT broaden this into a full multi-agent live workspace

Validation:
- Add deterministic coverage by mocking the live PM turn planner
- Run the project-local validation path

Output:
- What live PM thread model was added
- How the live PM turn runtime is invoked

## Task 42: Make the New Project tab default to live PM discovery

Type: Feature Task
Status: DONE
Requirement: R22

Goal:
Replace the old direct scaffold form with a live PM-guided new-project flow.

Requirements:
- Start the New Project tab with project name, display name, and initial idea
- Start a live PM conversation from that context
- Show the live PM conversation as a chat thread
- Let the user answer iteratively or force a draft
- Preserve a simple reset path

Constraints:
- Keep the surface clean and local-first
- Keep this flow focused on the active thread rather than a long visible archive

Validation:
- Manually inspect the New Project UI path
- Run the project-local validation path

Output:
- What changed in the New Project tab
- How the live PM conversation behaves there

## Task 43: Create projects from reviewed live PM drafts

Type: Feature Task
Status: DONE
Requirement: R22

Goal:
Make reviewed live PM drafts create the project cleanly instead of falling back to raw placeholder requirement text.

Requirements:
- Use the reviewed draft title as the seeded `R1` title
- Use the reviewed draft body as the seeded `R1` description
- Preserve the shared scaffold path for project creation

Constraints:
- Do NOT change the file-backed project template model beyond what is needed to seed the first requirement
- Do NOT add multiple drafted requirements in this slice

Validation:
- Add deterministic coverage where practical for reviewed-draft creation behavior
- Run the project-local validation path

Output:
- How reviewed live drafts seed the new project
- What changed in the scaffold path

## Task 44: Validate the split between live new-project PM and hybrid in-project PM

Type: Validation Task
Status: DONE
Requirement: R22

Goal:
Confirm the new live PM path improves brand-new project discovery without collapsing the existing hybrid PM workspace.

Requirements:
- Validate the New Project tab uses the live PM flow
- Validate the in-project PM workspace still uses the hybrid planner
- Validate reviewed live drafts still produce a clean project scaffold

Constraints:
- Keep validation deterministic by mocking the live PM runtime
- Do NOT attempt end-to-end network validation in the local test suite

Validation:
- Run unit coverage for the live PM thread flow
- Run the project-local eval path

Output:
- Which live-path behaviors were validated
- Whether the hybrid/live split stayed intact

## Task 45: Add lifecycle-derived implementation progress metadata

Type: Feature Task
Status: DONE
Requirement: R23

Goal:
Make implementation runs expose clear progress values and one-line stage explanations derived from the existing run lifecycle.

Requirements:
- Add deterministic helpers for implementation progress percentage and status explanation
- Cover queued, running, completed, failed, and unknown states
- Keep the progress approximate and lifecycle-derived rather than time-derived
- Preserve backward compatibility for existing implementation run records

Constraints:
- Do NOT introduce a new implementation runtime model
- Do NOT add precise remaining-time estimates
- Do NOT weaken the one-active-run-per-project lock

Validation:
- Add unit coverage for implementation progress metadata
- Run the project-local validation path

Output:
- Which progress values and explanations are exposed
- Whether existing run records remain compatible

## Task 46: Show implementation progress in requirement cards

Type: Feature Task
Status: DONE
Requirement: R23

Goal:
Update the requirement card implementation controls so active implementation is visibly in progress and explains what is happening.

Requirements:
- Show a progress bar on the requirement card after implementation starts
- Show a concise one-line explanation for the current implementation stage
- Show locked-state context on other eligible requirement cards while a project implementation is active
- Preserve completed and failed summary/error display

Constraints:
- Keep the UI refresh-based for this slice
- Keep implementation logs out of the requirement card surface
- Do NOT add multi-run controls

Validation:
- Add deterministic coverage where practical for UI-facing progress metadata
- Run the project-local validation path
- Manually inspect the implementation UI path if feasible

Output:
- What changed in the implementation card UI
- How active, locked, completed, and failed states appear

## Task 47: Define project preview availability and launch metadata

Type: Feature Task
Status: DONE
Requirement: R24

Goal:
Create a small, deterministic project-preview model so the control panel can decide whether a project can be opened for interactive testing.

Requirements:
- Detect whether a project has a previewable local application entry point
- Expose preview availability, target command, URL, and user-facing status text through workspace helpers
- Keep preview metadata derived from existing project files rather than introducing a separate source of truth
- Support Streamlit-based local projects as the first previewable application type

Constraints:
- Do NOT introduce hosted or remote preview infrastructure in this slice
- Do NOT add deep health diagnostics beyond basic preview availability
- Do NOT assume every AI Builder OS project has a runnable web UI
- Keep the model extensible for other preview runtimes later

Validation:
- Add unit coverage for previewable and non-previewable project detection
- Run the project-local validation path

Output:
- What preview metadata is exposed
- Which project types are previewable in the first slice
- Any runtime types intentionally deferred

## Task 48: Add project preview launch controls to the control panel

Type: Feature Task
Status: DONE
Requirement: R24

Goal:
Let users open a previewable executed project from the control panel in a new browser tab for testing and demos.

Requirements:
- Add a clear `Preview project` action for selected projects that have a previewable local app
- Start or reuse the local preview server needed for that project before opening the preview URL
- Open the preview URL in a new browser tab
- Show concise status or error feedback when preview launch is unavailable or fails
- Preserve existing project navigation, requirement management, and implementation controls

Constraints:
- Preserve the local-first control-panel model
- Do NOT add a full process manager or trace console
- Do NOT block the UI with long-running foreground preview commands
- Avoid significant lag by launching previews through a lightweight background process

Validation:
- Add deterministic coverage for launch command construction and preview state handling where practical
- Run the project-local validation path
- Manually inspect the preview button path if feasible

Output:
- Where the preview action appears
- How the preview process is launched or reused
- What feedback appears for available and unavailable projects

## Task 49: Validate project preview behavior across project states

Type: Validation Task
Status: DONE
Requirement: R24

Goal:
Confirm the project preview flow works for runnable projects and fails clearly for projects without a previewable application.

Requirements:
- Validate that a previewable project exposes an enabled preview action
- Validate that a non-previewable project explains why preview is unavailable
- Validate that preview launch preserves the existing control-panel workflow state
- Validate that the new behavior remains browser-compatible by using standard links/new-tab behavior

Constraints:
- Keep validation local and deterministic where possible
- Do NOT require remote hosting or external browser automation for this slice
- Do NOT expand validation into deep project health diagnostics

Validation:
- Run unit tests for preview metadata and launch behavior
- Run the scenario eval path
- Record any manual preview checks that could not be automated

Output:
- Which preview states were validated
- Whether browser/new-tab behavior has any remaining manual validation gap

## Task 50: Generalize the agent workspace foundation beyond PM

Type: Feature Task
Status: DONE
Requirement: R25

Goal:
Turn the `Agents` tab into a shared multi-agent workspace foundation instead of a PM-only special case.

Requirements:
- Support a shared agent selector and mode selector model for multiple agents
- Keep PM working as a live requirement-discovery chat
- Reuse the existing file-backed agent-thread store
- Preserve the distinction between conversation state, workflow state, and execution state

Constraints:
- Do NOT reintroduce separate bespoke project tabs for each role
- Do NOT break the existing PM live discovery flow
- Keep the architecture extensible for later QA and Engineer surfaces

Validation:
- Add deterministic coverage for the expanded agent workspace configuration
- Run the project-local validation path

Output:
- Which agents and modes are supported in the first shared workspace slice
- How the shared workspace avoids PM-only hard-coding

## Task 51: Reintroduce Experience Designer through the shared Agents workspace

Type: Feature Task
Status: DONE
Requirement: R25

Goal:
Expose Experience Designer as a live agent inside the shared `Agents` workspace and reconnect it to the existing experience-finding workflow.

Requirements:
- Add Experience Designer with:
  - `Feedback Synthesis`
  - `Usability Review`
- Use a live chat flow rather than the old removed project tab
- Let Experience Designer draft one structured finding at a time
- Save reviewed findings into the existing experience-finding artifact model

Constraints:
- Preserve the existing recommendation-type and handoff-state model
- Do NOT reintroduce a standalone Experience Designer tab

Validation:
- Add deterministic coverage for drafting and saving an Experience Designer finding
- Run the project-local validation path

Output:
- How Experience Designer appears inside `Agents`
- How findings move from thread draft to workflow artifact

## Task 52: Add UI Designer as a first-class agent workspace surface

Type: Feature Task
Status: DONE
Requirement: R25

Goal:
Add a UI Designer agent that can discuss visual direction, aesthetics, interaction design, layout, and interface polish.

Requirements:
- Add UI Designer with:
  - `Design Direction`
  - `UI Review`
- Use a live chat flow and let the agent draft one design brief at a time
- Keep the first slice grounded in the shared thread model
- Keep the UI Designer role distinct from Experience Designer

Constraints:
- Do NOT turn UI Designer into PM or Engineer
- Do NOT introduce a large new design-artifact system in this first slice

Validation:
- Add deterministic coverage for drafting and archiving a UI Designer brief
- Run the project-local validation path

Output:
- Which UI Designer modes are available
- How design briefs are surfaced in the first slice

## Task 53: Add Orchestrator to the Agents workspace as a code-driven control surface

Type: Feature Task
Status: DONE
Requirement: R25

Goal:
Expose Orchestrator inside the shared `Agents` workspace without turning it into a freeform live-chat persona.

Requirements:
- Add Orchestrator to the agent selector
- Show the current next role, next action, and why
- Reuse the deterministic workflow logic already used by the OS control layer
- Keep the surface honest about being code-driven and authoritative

Constraints:
- Do NOT make Orchestrator a freeform live chat in this slice
- Keep the logic aligned with the existing file-backed workflow rules

Validation:
- Add deterministic coverage for Orchestrator’s in-app recommendation behavior
- Run the project-local validation path

Output:
- What Orchestrator shows inside the agent workspace
- How it stays aligned with the OS control layer

## Task 54: Add a workflow inbox surface to the control panel

Type: Feature Task
Status: DONE
Requirement: R26

Goal:
Give the Product Director one inbox surface for active workflow state across the OS.

Requirements:
- Add a top-level `Inbox` surface
- Show active items across the OS, including:
  - approvals
  - PM clarifications
  - waiting agent threads
  - routed experience findings
  - active implementation runs
- Support filtered views for:
  - waiting
  - blocked
  - routed
  - running

Constraints:
- Keep the inbox file-backed and local-first
- Do NOT replace the underlying workflow artifacts
- Keep the first slice concise and operator-friendly

Validation:
- Add deterministic coverage for inbox item collection
- Run the project-local validation path

Output:
- Which workflow states are surfaced in the inbox
- Which filter buckets are supported in the first slice

## Task 55: Add explicit approval artifacts and actions for draft transitions

Type: Feature Task
Status: DONE
Requirement: R26

Goal:
Turn important draft transitions into durable approval objects rather than button side effects.

Requirements:
- Add file-backed approval artifacts
- Support approval requests for:
  - PM requirement drafts
  - Experience Designer findings
  - UI Designer design briefs
- Support explicit approve and reject actions
- On approval, persist the reviewed output into its correct destination

Constraints:
- Keep the approval model small and explicit in the first slice
- Do NOT require full multi-user permissioning in this phase

Validation:
- Add deterministic coverage for approval request, approval, and rejection flows
- Run the project-local validation path

Output:
- Which draft transitions use approvals
- How approval resolution affects workflow state

## Task 56: Align orchestration and status tooling with the approval layer

Type: Validation Task
Status: DONE
Requirement: R26

Goal:
Keep the deterministic OS control layer aligned with the new approval and inbox model.

Requirements:
- Treat open approvals as active workflow state in Orchestrator
- Surface approval counts in project/workspace status tooling
- Preserve the existing workflow-state contract for clarifications, findings, threads, and runs

Constraints:
- Keep the control layer deterministic
- Do NOT introduce a second interpretation of workflow state

Validation:
- Run the project-local validation path
- Run deterministic project status and orchestrator checks

Output:
- How approvals affect routing
- What status tooling now reports

## Task 57: Detect durable ambiguity in live PM discovery

Type: Feature Task
Status: DONE
Requirement: R33

Goal:
Allow the live PM discovery agent to raise a durable clarification automatically when a materially blocking ambiguity should not be silently assumed.

Requirements:
- Extend the live PM turn model to support a clarification outcome
- Let PM use that outcome selectively for structurally meaningful ambiguity
- Persist the clarification into the existing PM clarification store without requiring manual creation

Constraints:
- Do NOT turn every normal follow-up question into a durable clarification
- Keep the PM thread grounded in the existing file-backed workflow model

Validation:
- Add deterministic coverage for auto-generated clarification creation
- Run the project-local validation path

Output:
- How PM distinguishes a durable clarification from an ordinary next-turn question
- What gets written when PM blocks on ambiguity

## Task 58: Resume blocked PM threads from Inbox clarification answers

Type: Feature Task
Status: DONE
Requirement: R33

Goal:
Let the Product Director answer a PM-generated clarification from the Inbox and continue the blocked PM discovery thread cleanly.

Requirements:
- Surface the clarification questions in the Inbox
- Allow the Product Director to answer a thread-linked clarification directly there
- Resolve the clarification and resume the linked PM thread after the answer is submitted

Constraints:
- Keep the first slice single-reply and local-first
- Preserve the existing manual resolve behavior for non-thread clarifications

Validation:
- Add deterministic coverage for answering and resuming a blocked PM thread
- Run the project-local validation path

Output:
- How Inbox answers resume PM discovery
- How clarification resolution affects thread state

## Task 59: Align PM clarification messaging with the automatic flow

Type: Validation Task
Status: DONE
Requirement: R33

Goal:
Keep the control-panel surfaces honest and coherent once durable PM clarifications are created automatically.

Requirements:
- Update UI messaging so blocked PM threads point the Product Director to Inbox
- Keep Inbox/orchestration wording meaningful for both requirement-linked and thread-linked clarifications
- Preserve deterministic workflow-state reporting

Constraints:
- Do NOT remove the requirement-page clarification controls in this slice
- Keep the workflow state model compatible with existing tests and status tooling

Validation:
- Run the project-local validation path

Output:
- How PM clarification state is described across the UI and deterministic workflow layer

## Task 60: Add full approval review details to Inbox approval cards

Type: Feature Task
Status: DONE
Requirement: R31

Goal:
Let the Product Director inspect the real underlying approval content before approving or rejecting it.

Requirements:
- Add a review surface inside Inbox approval cards
- Show the full draft content for:
  - PM requirement drafts
  - Experience Designer findings
  - UI Designer design briefs

Constraints:
- Keep the first slice compact and local-first
- Reuse the existing approval payloads rather than introducing a separate review store

Validation:
- Add deterministic coverage for approval review content
- Run the project-local validation path

Output:
- What information is visible before approval
- How different approval types are rendered

## Task 61: Keep Inbox approval review aligned with existing approval actions

Type: Feature Task
Status: DONE
Requirement: R31

Goal:
Improve approval reviewability without changing the underlying approval flow semantics.

Requirements:
- Keep approve and reject actions in the same Inbox card
- Preserve existing approval resolution behavior after adding review details
- Ensure the review surface remains truthful to the stored artifact

Constraints:
- Do NOT add a second approval workflow
- Do NOT hide the underlying approval type or source agent

Validation:
- Run the project-local validation path

Output:
- How review details coexist with approve and reject actions

## Task 62: Record the approval reviewability improvement in product state

Type: Validation Task
Status: DONE
Requirement: R31

Goal:
Keep product files and docs aligned after making Inbox approvals reviewable.

Requirements:
- Update tracked product state for the completed slice
- Keep docs and review lists aligned with the new behavior

Constraints:
- Keep the change tightly scoped to approval reviewability

Validation:
- Run the project-local validation path

Output:
- Which product/workflow records changed for the slice

## Task 63: Auto-run PM completion after approved review artifacts

Type: Feature Task
Status: DONE
Requirement: R34

Goal:
Turn approved Experience Designer findings and UI Designer reviews into real workflow outcomes automatically instead of stopping at artifact approval.

Requirements:
- After approving an Experience Designer finding, run a PM completion step automatically
- After approving a UI Designer review, run the same PM completion step automatically
- Let PM completion choose between:
  - create a backlog requirement now
  - request Product Director confirmation that the review should stay out of scope

Constraints:
- Keep the completion logic visible and file-backed
- Do NOT hide the resulting backlog requirement or scope confirmation from the Product Director

Validation:
- Add deterministic coverage for the backlog path
- Add deterministic coverage for the scope-confirmation path
- Run the project-local validation path

Output:
- What PM completion now does after approval
- How each branch is persisted in workflow state

## Task 64: Make scope-confirmation outcomes actionable in Inbox

Type: Feature Task
Status: DONE
Requirement: R34

Goal:
Ensure the out-of-scope branch still ends in a clear Product Director decision rather than a dead-end approval.

Requirements:
- Add a scope-confirmation approval type for PM completion outcomes
- Show the PM rationale and fallback backlog requirement in Inbox
- Let the Product Director either:
  - confirm out of scope
  - send the item to backlog instead

Constraints:
- Keep the UI language explicit about the decision being made
- Reuse the existing approval surface rather than inventing a separate queue

Validation:
- Add deterministic coverage for Inbox labels and fallback backlog behavior
- Run the project-local validation path

Output:
- How out-of-scope confirmation appears to the Product Director
- What happens when the Product Director sends the item to backlog instead

## Task 65: Align review-artifact state with automatic completion

Type: Validation Task
Status: DONE
Requirement: R34

Goal:
Keep approved review artifacts and their downstream workflow state consistent after adding PM completion automation.

Requirements:
- Mark Experience Designer findings resolved once PM completion finishes them
- Preserve approved UI review output while still driving a downstream outcome
- Keep approval history, backlog changes, and thread state aligned

Constraints:
- Do NOT leave approved reviews stranded in a half-complete routed state

Validation:
- Run the project-local validation path

Output:
- How experience findings, UI review threads, and approvals stay aligned after completion

## Task 66: Detect UI and experience triggers in requirement implementation routing

Type: Feature Task
Status: DONE
Requirement: R44

Goal:
Teach the OS to recognize when pending implementation work is meaningfully about usability/experience or UI design, not just engineering execution.

Requirements:
- Add shared trigger detection for:
  - experience/usability-heavy requirements
  - UI/visual-heavy requirements
- Keep the trigger logic lightweight and deterministic
- Reuse the same trigger logic across the control panel and deterministic orchestration helper

Constraints:
- Do NOT remove the existing Architect trigger path for structural work
- Keep the heuristic conservative enough that obvious user-facing work is routed correctly without turning every requirement into a design review

Validation:
- Add deterministic coverage for experience-trigger routing
- Add deterministic coverage for UI-trigger routing
- Run the project-local validation path

Output:
- What trigger types were added
- How the OS decides which design agent should run before Engineer

## Task 67: Route pending UI and experience work to the right design agent before Engineer

Type: Feature Task
Status: DONE
Requirement: R44

Goal:
Make the real workflow route UI-heavy work to UI Designer and experience-heavy work to Experience Designer before engineering starts.

Requirements:
- Update the deterministic Orchestrator helper to route:
  - experience-heavy pending work -> Experience Designer
  - UI-heavy pending work -> UI Designer
- Update the in-app Orchestrator to use the same routing behavior
- Preserve Architect precedence for structural requirements

Constraints:
- Keep routing explainable in the user-facing `why` text
- Do NOT skip straight to Engineer when a design-agent review is clearly warranted

Validation:
- Add deterministic coverage for the new routing branches
- Run the project-local validation path

Output:
- How pending implementation work is now routed
- How the role precedence works across Architect, Experience Designer, UI Designer, and Engineer

## Task 68: Align the implementation prompt with design-agent routing

Type: Validation Task
Status: DONE
Requirement: R44

Goal:
Make the background implementation runner honest about when UI Designer or Experience Designer must be part of the workflow.

Requirements:
- Update the requirement implementation prompt so relevant requirements explicitly mention:
  - do not skip Experience Designer
  - do not skip UI Designer
- Keep the prompt aligned with deterministic Orchestrator behavior rather than inventing a second workflow

Constraints:
- Keep the prompt focused and requirement-specific
- Do NOT hard-code design-agent guidance onto unrelated requirements

Validation:
- Add deterministic coverage for prompt guidance on a requirement that triggers both design-agent paths
- Run the project-local validation path

Output:
- What extra guidance the implementation runner now includes
- How the prompt stays aligned with the control-layer routing rule

## Task 69: Replace blind agent dropdowns with guided selection surfaces

Type: Feature Task
Status: DONE
Requirement: R45

Goal:
Help the Product Director choose the right agent intentionally instead of relying on blind dropdowns.

Requirements:
- Replace agent dropdown-first selection with a more explorable surface
- Show enough explanation for each agent to support confident choice
- Keep the existing agent workflows intact underneath

Constraints:
- Keep the surface lightweight and local-first
- Do NOT turn the agent workspace into a separate documentation browser

Validation:
- Run the project-local validation path

Output:
- What changed in agent selection
- How users now understand the available agents up front

## Task 70: Make mode selection more self-explanatory

Type: Feature Task
Status: DONE
Requirement: R45

Goal:
Make agent modes feel intentional and understandable at the moment of choice.

Requirements:
- Show mode descriptions at the moment of selection
- Preserve the existing mode model while making it easier to understand
- Keep the mode decision lightweight enough not to bog down the workflow

Constraints:
- Do NOT broaden this into the inferred-mode work tracked separately

Validation:
- Run the project-local validation path

Output:
- What changed in mode selection
- How the user learns the meaning of each mode

## Task 71: Rework Inbox hierarchy around workflow state groups

Type: Feature Task
Status: DONE
Requirement: R46

Goal:
Make the Inbox easier to scan by grouping items according to workflow state rather than presenting one long same-weight list.

Requirements:
- Group inbox workflow items by state
- Preserve approval actions and existing workflow detail
- Keep waiting, blocked, routed, and running work readable at a glance

Constraints:
- Keep the Inbox focused on workflow coordination
- Do NOT turn the Inbox into a second general-purpose workspace

Validation:
- Run the project-local validation path

Output:
- How Inbox grouping changed
- What now scans more clearly

## Task 72: Strengthen approval-card hierarchy without changing approval semantics

Type: Feature Task
Status: DONE
Requirement: R46

Goal:
Make approval requests feel more obviously actionable and distinct from lower-priority workflow items.

Requirements:
- Improve approval-card hierarchy and labeling
- Keep review details and approve/reject actions intact
- Preserve the truthful mapping between approval type and workflow meaning

Constraints:
- Do NOT invent a second approval workflow

Validation:
- Run the project-local validation path

Output:
- What changed in approval presentation
- How the Inbox now distinguishes approvals from other workflow states

## Task 73: Refine project-card composition and action framing

Type: Feature Task
Status: DONE
Requirement: R47

Goal:
Make project cards feel more like real entry points into work and less like generic status boxes.

Requirements:
- Improve the hierarchy of project identity, state, and action
- Preserve compact two-column layout
- Keep actions obvious without making the cards noisy

Constraints:
- Keep the visual language restrained
- Do NOT broaden this into a full workspace redesign

Validation:
- Run the project-local validation path

Output:
- What changed in the project cards
- Why the new composition feels more intentional

## Task 74: Reduce repetitive framing across core control-panel surfaces

Type: Validation Task
Status: DONE
Requirement: R47

Goal:
Reduce the sense that every screen is made of repeated same-weight bordered blocks.

Requirements:
- Remove or soften repetition where possible in the updated workspace, projects, and inbox surfaces
- Keep the product calm and legible rather than decorative

Constraints:
- Prefer focused hierarchy changes over sweeping restyles

Validation:
- Run the project-local validation path

Output:
- What repetitive framing was reduced
- How the updated surfaces feel lighter and easier to scan

## Task 75: Surface open approval requests on the workspace

Type: Feature Task
Status: DONE
Requirement: R29

Goal:
Let the Product Director see pending approval decisions from the Workspace page without first navigating to Inbox.

Requirements:
- Add a workspace-level approval section when open approvals exist
- Show a concise summary for each open approval, including project, source agent, title, and summary
- Keep longer approval details available through progressive disclosure rather than making the Workspace noisy
- Preserve the existing Inbox approval surface and approval workflow semantics

Constraints:
- Do NOT create a second approval data model
- Do NOT change what approve or reject means for any approval type
- Keep the Workspace page responsive by using the existing lightweight approval store

Experience Designer guidance:
- The approval section should reduce missed decisions by making waiting approvals visible at the point where the operator starts work
- The section should not become a second Inbox; it should focus only on decision-ready approvals

UI Designer guidance:
- Place the approval section near the top of Workspace Summary, after the high-level metrics and before the agent cards
- Use compact hierarchy: clear section title, small metadata, concise summary, and hidden full draft detail

Validation:
- Add deterministic coverage for workspace approval filtering and summary metadata
- Run the project-local validation path

Output:
- What workspace approval visibility was added
- How the surface stays distinct from the full Inbox

## Task 76: Add direct workspace approval actions

Type: Feature Task
Status: DONE
Requirement: R29

Goal:
Let the Product Director approve pending requests directly from the Workspace page.

Requirements:
- Add approve actions to each workspace approval item
- Preserve the existing reject action where it already exists for approval requests
- Reuse existing approval labels so scope confirmations keep their distinct outcome language
- Rerun the page after a decision so resolved approvals disappear from the workspace list

Constraints:
- Do NOT bypass existing approval handlers
- Do NOT add approval actions for non-approval inbox items in this requirement
- Do NOT broaden the Workspace page into full workflow-state management

Experience Designer guidance:
- The user should be able to resolve a simple approval from the Workspace with the same confidence as in Inbox
- Full draft detail should remain accessible before approving to avoid accidental decisions based on too little context

UI Designer guidance:
- Keep action buttons close to the corresponding approval summary
- Avoid visually over-weighting reject/destructive actions compared with the primary approval path

Validation:
- Add deterministic coverage that the workspace uses the same approval button labels as Inbox
- Run the project-local validation path

Output:
- What direct workspace approval actions were added
- How action semantics remain aligned with Inbox

## Task 77: Add a sprint planning model for backlog requirements

Type: Feature Task
Status: DONE
Requirement: R50

Goal:
Introduce a first-class project sprint model so backlog requirements can be grouped into an intentional execution batch.

Requirements:
- Add durable sprint state per project
- Allow backlog requirements to be added to a sprint
- Allow sprint items to be removed and reordered before sprint execution begins

Constraints:
- Keep Sprint V1 to one sprint plan per project
- Do NOT introduce project-internal parallel execution

Validation:
- Run the project-local validation path

Output:
- What sprint state was added
- How backlog requirements now move into a sprint plan

## Task 78: Add sprint controls to the requirements UI

Type: Feature Task
Status: DONE
Requirement: R50

Goal:
Make sprint planning and execution accessible from the control panel without forcing the operator into direct file editing.

Requirements:
- Show sprint state in the requirements surface
- Let the Product Director add backlog items into a sprint from the UI
- Show sprint ordering and provide clear sprint actions

Constraints:
- Keep the UI truthful and restrained
- Do NOT hide the distinction between backlog planning and active execution

Validation:
- Run the project-local validation path

Output:
- What sprint controls were added in the UI
- How the requirements surface now supports sprint planning

## Task 79: Launch the first sprint requirement immediately and keep execution sequential

Type: Feature Task
Status: DONE
Requirement: R50

Goal:
Ensure starting a sprint turns into real implementation work rather than just changing labels.

Requirements:
- Starting a sprint should activate and launch the first requirement immediately
- Only one implementation run should remain active per project
- Sprint progression should advance requirement by requirement in sprint order

Constraints:
- Preserve the existing one-active-implementation-per-project rule
- Do NOT implement parallel sprint execution in V1

Validation:
- Run the project-local validation path

Output:
- How sprint start triggers real implementation
- How sequential execution is enforced

## Task 80: Block sprint progression visibly when a requirement needs intervention

Type: Validation Task
Status: DONE
Requirement: R50

Goal:
Prevent the sprint from silently skipping or looping when a requirement run finishes in a state that still needs attention.

Requirements:
- Surface a blocked sprint state when the current requirement is not ready to advance
- Require explicit continuation after the operator resolves the issue
- Keep the current requirement visible so the blocker is understandable

Constraints:
- Prefer clear operator control over aggressive auto-retry behavior

Validation:
- Run the project-local validation path

Output:
- How sprint blocking is surfaced
- How the operator resumes controlled progression

## Task 81: Separate top-level and project-level navigation presentation

Type: Feature Task
Status: DONE
Requirement: R35

Goal:
Make the two navigation levels feel visibly distinct so the Product Director can tell whether they are moving across the whole control panel or inside a selected project.

Requirements:
- Keep the existing top-level sections and project-level sections intact
- Give the top-level navigation an explicit main-navigation label
- Change project-level navigation away from the same horizontal tab-like presentation used by top-level navigation
- Preserve the existing Workspace, Projects, Inbox, New Project, Requirements, and Agents destinations

Constraints:
- Do NOT restructure the broader information architecture
- Do NOT remove existing project entry, requirement, agent, inbox, or new-project flows
- Keep the change restrained and consistent with the existing Streamlit control-panel style

Experience Designer guidance:
- The interaction should answer "am I navigating the whole OS or this project?" at a glance
- Project navigation should sit close to project identity and avoid looking like a duplicate of the global navigation

UI Designer guidance:
- Use placement, orientation, and labels to distinguish hierarchy before adding decorative styling
- Keep the selected project section readable without adding a heavy card-within-card layout

Validation:
- Add deterministic coverage for the navigation labels/orientation contract
- Run the project-local validation path

Output:
- What changed in the navigation hierarchy
- How the update reduces dual-level confusion

## Task 82: Preserve project workflow access after navigation changes

Type: Feature Task
Status: DONE
Requirement: R35

Goal:
Ensure the revised navigation keeps the same project workflows reachable and understandable.

Requirements:
- Confirm Requirements remains the default project section
- Confirm Agents remains reachable from the project-level navigation
- Keep back-to-projects behavior unchanged
- Keep pending agent focus and project-open state behavior compatible with the revised navigation

Constraints:
- Do NOT introduce a new workflow state model
- Do NOT change the agent mode or requirement editing surfaces beyond what is needed for navigation clarity

Experience Designer guidance:
- The revised flow should reduce navigation uncertainty without making common project actions slower

UI Designer guidance:
- Keep the project nav compact enough that Requirements and Agents content remain the primary focus

Validation:
- Add deterministic coverage for default project-section behavior and pending agent focus compatibility where practical
- Run the project-local validation path

Output:
- Which existing flows were preserved
- Any intentional limits in the navigation update

## Task 83: Validate and close the navigation usability slice

Type: Validation Task
Status: DONE
Requirement: R35

Goal:
Verify the R35 navigation update and close the requirement state only after validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R35 DONE only if all linked tasks are DONE and validation passes

Constraints:
- Keep validation local and deterministic
- Do NOT claim survey-based success metrics are met without user-testing evidence

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 152: Define repo-link alignment for the public showcase

Type: Design Task
Status: DONE
Requirement: R70

Goal:
Make the public showcase resilient to public-repo link changes without requiring ad hoc code edits.

Requirements:
- Avoid burying the public repo target in multiple hardcoded strings
- Keep local and deployed showcase links easy to align through one explicit configuration point
- Make the handoff obvious for publication time

Constraints:
- Keep the handoff lightweight and configuration-driven
- Keep the current showcase behavior working locally

Validation:
- Add deterministic coverage for the configurable repo URL

Output:
- Clean public-repo link alignment model

## Task 153: Implement configurable public repo links and documentation

Type: Feature Task
Status: DONE
Requirement: R70

Goal:
Let the showcase point at the final public GitHub repo through one explicit configuration point and document that handoff clearly.

Requirements:
- Add a single public-repo URL setting for the showcase
- Use that setting for:
  - workspace repo links
  - project-folder GitHub links
- Document the setting in the root README and showcase README

Constraints:
- Preserve a sensible default while allowing the final public repo target to be set explicitly
- Keep the public visitor experience unchanged aside from link correctness

Validation:
- Showcase tests cover repo URL override behavior

Output:
- Configurable public repo links
- Clear publication-time handoff docs

## Task 154: Validate and close R70

Type: Validation Task
Status: DONE
Requirement: R70

Goal:
Close R70 only after the repo-link configuration path is working and documented.

Requirements:
- Run the showcase test path
- Keep root and showcase docs aligned
- Record the handoff decision in project memory

Validation:
- `.venv/bin/python -m unittest showcase.tests.test_app`

Output:
- Validation results
- Requirement closure state

## Task 149: Define the public Streamlit showcase shape

Type: Design Task
Status: DONE
Requirement: R69

Goal:
Create a public-facing Streamlit app concept that explains AI Builder OS clearly without using the raw operator control panel as the first public impression.

Requirements:
- Keep the operator control panel separate from the public showcase
- Explain:
  - what the OS is
  - how the workflow works
  - what projects exist in the workspace
  - how someone can try it locally
- Keep the experience simple enough for first-time visitors

Constraints:
- Do not turn the showcase into a fake live control panel
- Keep the public story honest about what is local-first and what remains an internal operator workflow

Validation:
- The showcase structure should be documented and implemented as a dedicated Streamlit app entrypoint

Output:
- Clear public showcase structure

## Task 150: Build the public Streamlit showcase app

Type: Feature Task
Status: DONE
Requirement: R69

Goal:
Implement a polished public Streamlit showcase app that introduces AI Builder OS and its example projects.

Requirements:
- Add a dedicated Streamlit showcase app outside the operator control panel
- Include sections for:
  - overview
  - workflow
  - projects
  - how to try it
- Add supporting showcase documentation
- Update root docs so the showcase has a clear local run path

Constraints:
- Keep the showcase lighter and more curated than the operator control panel
- Avoid requiring live model access just to use the showcase

Validation:
- Add lightweight deterministic coverage for the showcase app helpers

Output:
- Public showcase Streamlit app

## Task 151: Validate and close R69

Type: Validation Task
Status: DONE
Requirement: R69

Goal:
Close R69 only after the showcase app, docs, and lightweight validation all work cleanly.

Requirements:
- Run the OS Control Panel validation path
- Run the showcase test path
- Keep the public-showcase scope aligned with the requirement and supporting project context

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- `.venv/bin/python -m unittest showcase.tests.test_app`

Output:
- Validation results
- Requirement closure state

## Task 146: Define the public repo readiness slice

Type: Design Task
Status: DONE
Requirement: R68

Goal:
Turn public publication into an explicit product slice so the repo can become a high-quality showcase rather than a private operating directory with a README.

Requirements:
- Define what “public-ready” means for this workspace
- Separate public-repo readiness from the later public Streamlit showcase app
- Capture the need for:
  - clearer repo story
  - public-safe state review
  - setup quality
  - validation clarity
  - media/demo checklist

Constraints:
- Do not start building the showcase app in this slice
- Keep the repo honest about what is local-first and what is still evolving

Validation:
- Update requirement framing to reflect the public-repo readiness split

Output:
- Clear public-repo readiness scope

## Task 147: Improve public repo narrative and publication process guidance

Type: Feature Task
Status: DONE
Requirement: R68

Goal:
Make the workspace easier to understand and safer to publish by tightening the repo narrative and clarifying the publication process.

Requirements:
- Improve the root README so a visitor can understand:
  - what AI Builder OS is
  - what the control panel is
  - what the example projects demonstrate
  - how to run meaningful surfaces locally
- Document the publication process clearly enough that repo curation and publication checks can be performed intentionally
- Clarify in project/docs language that operational `data/` is not the canonical product backlog
- Preserve the distinction between the operator control panel and the later public showcase app

Constraints:
- Avoid pretending the repo is already a hosted multi-user product
- Keep the docs grounded in the real implementation

Validation:
- Review the updated README and publication-process guidance for internal consistency

Output:
- Stronger public-facing repo narrative
- Clear publication-process guidance

## Task 148: Validate and close R68

Type: Validation Task
Status: DONE
Requirement: R68

Goal:
Close R68 only after the public repo readiness docs are in place and the repo still validates cleanly.

Requirements:
- Run the OS Control Panel validation path
- Run workspace project-structure validation
- Record the public-repo readiness decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- `python tools/validate_project_structure.py`

Output:
- Validation results
- Requirement closure state

## Task 107: Establish R54 navigation experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R54

Goal:
Constrain the broad navigation-clarity requirement into a focused, implementable navigation improvement before engineering changes.

Requirements:
- Use Experience Designer guidance to identify the main workflow problem as orientation cost between workspace-level navigation and project-level navigation
- Use UI Designer guidance to make navigation labels task-oriented and visually distinct without adding a new navigation model
- Preserve existing Workspace, project selection, Inbox, project creation, Requirements, and Agents behavior
- Keep the first implementation slice focused on existing navigation surfaces rather than broad UI redesign

Constraints:
- Do NOT add full workflow execution control, deep task inspection, or backend navigation semantics
- Do NOT introduce a third-party UI dependency
- Do NOT claim the 20% task-completion success metric from deterministic validation alone
- Keep the design compatible with native Streamlit reruns and existing session-state routing

Experience Designer guidance:
- User problem: the current top-level navigation makes users spend extra effort locating where to open a project, create a project, inspect the inbox, or switch within a selected project
- Affected workflow: opening the control panel, choosing the right workspace section, then moving inside a selected project
- Evidence: R54 explicitly reports navigation clarity and efficiency problems, and prior project memory says Workspace should stay orienting while Inbox remains action-focused
- Confidence: Medium, based on explicit requirement language and repeated prior navigation/Workspace clarity work, but without new measured task-completion data
- Recommendation: make workspace-level destinations read as tasks, keep project-level navigation visibly separate, and preserve the current bounded V1 surface area

UI Designer guidance:
- Rename ambiguous top-level destinations so the route labels communicate the job: workspace overview, project opening, workflow inbox, and project creation
- Keep top-level navigation horizontal and project navigation vertical so hierarchy is visible at a glance
- Keep the project-level navigation compact in the left column and avoid adding decorative navigation cards
- Use native Streamlit controls and small helper functions for deterministic validation rather than custom navigation components

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for top-level labels, destination intent, and project-level navigation separation

Output:
- R54 usability and UI direction for implementation
- Explicit limits that keep navigation work inside a focused UI slice

## Task 108: Improve main and project navigation clarity

Type: Feature Task
Status: DONE
Requirement: R54

Goal:
Make the existing navigation easier to understand and faster to use by clarifying destination labels and preserving a visible distinction between workspace-level and project-level movement.

Requirements:
- Rename top-level navigation destinations from generic section names to task-oriented labels where needed
- Keep Workspace and Inbox available as stable top-level destinations
- Keep project opening separate from project creation in the top-level navigation
- Keep Requirements and Agents as project-level destinations shown only inside a selected project
- Preserve session-state routing from Workspace cards, Inbox thread links, and project open/back actions

Constraints:
- Do NOT reintroduce a top-level Project Detail tab
- Do NOT change project file parsing, workflow artifact state, sprint behavior, or approval behavior
- Do NOT remove the existing project preview or Back to projects controls
- Do NOT add custom JavaScript navigation

Validation:
- Add or update deterministic unit tests for navigation labels, label intent, and project-level navigation separation
- Run the project-local validation path

Output:
- Updated navigation labels/helper functions
- Validation evidence that routing structure remains bounded and distinct

## Task 109: Validate and close R54

Type: Validation Task
Status: DONE
Requirement: R54

Goal:
Close R54 only after the focused navigation clarity slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R54 DONE only if linked R54 tasks are DONE and validation passes
- Record any reusable navigation design decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat the 20% task-completion improvement as a future user-feedback metric, not deterministic proof
- Treat remaining open questions about exact confusing elements and post-launch satisfaction as future research input rather than blockers for this scoped slice

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 84: Restructure the requirements page around priority focus

Type: Feature Task
Status: DONE
Requirement: R36

Goal:
Make the Requirements page easier to scan by showing the most important unfinished work before lower-priority or planning-only detail.

Requirements:
- Separate unfinished requirements into clear priority/workflow groups instead of one noisy active-and-backlog list
- Put high-priority and in-progress/new requirements ahead of lower-priority backlog requirements
- Preserve existing requirement editing, ordering, sprint planning, clarification, deletion, and implementation controls
- Add concise metadata labels so each requirement card communicates status, priority, and effort before the user expands it

Constraints:
- Do NOT change requirement storage or backend data structures
- Do NOT remove completed-requirement reference visibility
- Keep the Streamlit layout restrained and native-component-first

Experience Designer guidance:
- The page should answer "what needs attention first?" before exposing every editable field
- Treat the 20% satisfaction score as a post-implementation feedback target, not a deterministic validation claim

UI Designer guidance:
- Prefer grouping, labels, and progressive disclosure over decorative styling
- Avoid adding a third-party Streamlit component unless native layout cannot support the interaction

Validation:
- Add deterministic coverage for requirement grouping, priority ordering, and card metadata
- Run the project-local validation path

Output:
- What grouping model was added
- How priority work is made easier to find

## Task 85: Preserve requirements workflow controls in the cleaner layout

Type: Feature Task
Status: DONE
Requirement: R36

Goal:
Ensure the cleaner Requirements page does not make existing project-management actions harder to reach.

Requirements:
- Keep PM prioritisation recommendation visible without competing with the primary requirement groups
- Keep sprint planning visible but secondary to the requirement focus area
- Keep active implementation and PM clarification warnings prominent when they exist
- Preserve the default collapsed editing behavior so long descriptions do not dominate the page

Constraints:
- Do NOT introduce a new workflow state model
- Do NOT change the one-active-implementation-per-project rule
- Do NOT claim survey-based satisfaction improvement without separate user feedback

Experience Designer guidance:
- Reduce clutter while preserving the operator's ability to act from the same page

UI Designer guidance:
- Use concise section titles and captions so the hierarchy is self-explanatory without instructional copy overload

Validation:
- Add or update tests for the workflow-control placement helpers where practical
- Run the project-local validation path

Output:
- Which existing workflows were preserved
- Any intentional limits in the layout update

## Task 86: Validate and close the R36 requirements-page usability slice

Type: Validation Task
Status: DONE
Requirement: R36

Goal:
Close R36 only after deterministic validation passes and the workflow state points to no remaining R36 implementation work.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R36 DONE only if linked R36 tasks are DONE and validation passes

Constraints:
- Keep validation local and deterministic
- Treat satisfaction-score improvement as a future feedback measurement outside this deterministic closure

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 87: Establish R40 workspace and inbox experience direction

Type: Feature Task
Status: DONE
Requirement: R40

Goal:
Use Experience Designer and UI Designer guidance to make the workspace and inbox feel more intentional before implementation changes are made.

Requirements:
- Treat the Workspace first read as orientation, not a dense dashboard
- Treat Inbox as a workflow queue grouped around action state and decision urgency
- Preserve existing approval, clarification, routed-item, running-work, project-opening, and preview actions
- Use a consistent card anatomy for workflow items: type/status cue, title, metadata, summary/detail, then action
- Keep helper text concise and tied to the user's immediate decision

Constraints:
- Do NOT add a new persistence model or backend workflow behavior
- Do NOT duplicate the full Inbox inside Workspace
- Do NOT claim measured satisfaction improvement without separate user feedback
- Prefer native Streamlit layout and small CSS helpers over new third-party UI dependencies

Experience Designer guidance:
- Reduce the feeling of clutter by separating orientation, decisions, and reference material into clear sections
- Keep actionable workflow items visually stronger than informational agent or project reference cards
- Make empty states calm and clear so the operator understands whether work is waiting or not

UI Designer guidance:
- Use restrained section headings, compact metadata, and consistent card spacing
- Keep cards visually related across Workspace and Inbox without making every surface identical
- Preserve responsive two-column layouts where useful, with single-card rows left aligned instead of stretched

Validation:
- Review the implemented Workspace and Inbox surfaces for preserved workflow actions and clearer hierarchy
- Run the project-local validation path

Output:
- Design guidance applied to the implementation
- Any intentional limits in the UI simplification

## Task 88: Refine the Workspace surface hierarchy

Type: Feature Task
Status: DONE
Requirement: R40

Goal:
Make the Workspace tab a calmer orientation surface with clear top-level signals and concise decision-ready approval visibility.

Requirements:
- Replace the loose workspace stack with clearer sections for operating snapshot, awaiting approval, and agent reference
- Keep workspace metrics visible but visually grouped as the first-read operating snapshot
- Keep open approval cards compact and decision-ready without hiding full review detail
- Preserve the existing approval actions and project/workflow boundaries

Constraints:
- Do NOT move project drill-down management into Workspace
- Do NOT remove agent summaries
- Do NOT introduce backend changes

Validation:
- Unit test helper output for the workspace approval section title/metadata where practical
- Run the project-local validation path

Output:
- Workspace hierarchy changes
- Preserved actions and intentional omissions

## Task 89: Refine the Inbox workflow queue hierarchy

Type: Feature Task
Status: DONE
Requirement: R40

Goal:
Make Inbox easier to scan by clarifying filters, metrics, workflow-state groups, and item-card structure.

Requirements:
- Present Inbox controls as queue filters rather than a generic form block
- Keep metrics focused on work waiting, blocked, routed, and running
- Render approval and workflow item cards with consistent metadata and status/type cues
- Preserve clarification answer forms, approval actions, and thread-opening actions
- Keep empty states specific to the active filter/project selection

Constraints:
- Do NOT change approval semantics or workflow item generation
- Do NOT hide blocked or routed workflow state
- Do NOT add heavy custom UI dependencies

Validation:
- Add or update deterministic unit tests for Inbox helper text/card metadata where practical
- Run the project-local validation path

Output:
- Inbox hierarchy changes
- Validation evidence that workflow actions remain available

## Task 90: Validate and close the R40 workspace and inbox UI slice

Type: Validation Task
Status: DONE
Requirement: R40

Goal:
Close R40 only after deterministic validation passes and the workflow state has no remaining R40 implementation work.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R40 DONE only if linked R40 tasks are DONE and validation passes

Constraints:
- Treat satisfaction and efficiency measurement as future user feedback, not deterministic proof
- Keep validation local and reproducible

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 91: Add explicit sprint completion confirmation

Type: Feature Task
Status: DONE
Requirement: R51

Goal:
Give sprint execution a clear completion handoff instead of leaving the final sprint state ambiguous.

Requirements:
- When all sprint requirements are done, the sprint should become visibly ready to close
- The Product Director should explicitly confirm sprint completion
- Confirmation should clear the active sprint so a new one can be planned

Constraints:
- Do NOT silently auto-clear the sprint the moment the last requirement becomes DONE
- Preserve Sprint V1 as a project-local sequential flow

Validation:
- Run the project-local validation path

Output:
- How sprint completion is surfaced
- What happens when completion is confirmed

## Task 92: Move sprint planning to the top of the requirements workflow

Type: Feature Task
Status: DONE
Requirement: R51

Goal:
Make sprint state one of the first things the Product Director sees on the requirements page.

Requirements:
- Render the sprint panel above the main requirement stack
- Keep alerts and recommendations intact while making sprint state easier to see

Constraints:
- Do NOT disrupt the existing project-level navigation model

Validation:
- Run the project-local validation path

Output:
- New sprint placement
- Any resulting section-order changes

## Task 93: Convert completed requirements into a compact archive

Type: Feature Task
Status: DONE
Requirement: R51

Goal:
Stop completed requirements from turning the requirements page into a long scroll of stale cards.

Requirements:
- Replace the long completed-requirements stack with a compact archive surface
- Keep completed requirement detail available on demand
- Preserve completed work as read-only reference material

Constraints:
- Do NOT remove completed requirements from the project source of truth
- Prefer compact progressive disclosure over a second long card list

Validation:
- Run the project-local validation path

Output:
- What compact archive pattern replaced the old stack
- How completed detail is still accessible

## Task 94: Redesign the project preview control as a compact utility card

Type: Feature Task
Status: DONE
Requirement: R51

Goal:
Make the project preview control feel like a deliberate utility surface instead of a large detached button block.

Requirements:
- Present preview status, action, and link in a tighter utility layout
- Preserve the ability to start preview locally and open it in a new tab

Constraints:
- Do NOT change project preview semantics or introduce remote preview behavior

Validation:
- Run the project-local validation path

Output:
- Updated preview control layout
- Preserved preview behavior

## Task 95: Establish R39 Workspace and Inbox simplification direction

Type: Feature Task
Status: DONE
Requirement: R39

Goal:
Use Experience Designer and UI Designer guidance to constrain R39 to a focused usability and visual-hierarchy pass before implementation.

Requirements:
- Treat Workspace as an orientation surface that should make waiting decisions clear without duplicating the full Inbox
- Treat Inbox as an action queue where approval, waiting, blocked, routed, and running states are visually distinct
- Preserve all existing approval actions, clarification replies, thread-opening actions, project-opening actions, and preview behavior
- Prefer clearer status cues, concise metadata, and consistent workflow-card anatomy over broad redesign

Constraints:
- Do NOT add new features or workflow semantics
- Do NOT claim survey-based satisfaction or completion-time improvement from deterministic validation
- Do NOT introduce a new UI dependency for this slice

Experience Designer guidance:
- Reduce perceived clutter by making each workflow card answer what kind of attention it needs before showing detail
- Keep the user's next decision visible without hiding review detail or workflow state
- Avoid making Workspace a second Inbox

UI Designer guidance:
- Use a restrained, consistent status-cue treatment across Workspace and Inbox cards
- Keep card metadata compact and predictable
- Preserve the native Streamlit layout model and responsive behavior

Validation:
- Carry this guidance into the Engineer task
- Run deterministic helper tests for the new UI hierarchy helpers where practical

Output:
- Design constraints for the R39 implementation
- Intentional limits that keep the work within the existing product scope

## Task 96: Refine Workspace and Inbox workflow-card intentionality

Type: Feature Task
Status: DONE
Requirement: R39

Goal:
Make Workspace approval cards and Inbox workflow cards feel more intentional and easier to scan without changing workflow behavior.

Requirements:
- Add a reusable workflow-card attention cue that maps approval, waiting, blocked, routed, and running states to clear user-facing labels
- Render the cue consistently in Workspace approval cards, Inbox approval cards, and Inbox workflow item cards
- Keep existing titles, summaries, review details, and actions available
- Keep existing Inbox filters and queue metrics intact

Constraints:
- Do NOT alter approval, rejection, clarification, or thread-routing semantics
- Do NOT remove full review detail from approval cards
- Do NOT add new persistent data

Validation:
- Add or update unit tests for attention-cue label mapping and rendered workflow-card header markup
- Run the project-local validation path

Output:
- Updated UI hierarchy helpers and rendering
- Confirmation that workflow actions remain available

## Task 97: Validate and close the R39 UI simplification slice

Type: Validation Task
Status: DONE
Requirement: R39

Goal:
Close R39 only after deterministic validation passes and linked R39 tasks are complete.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R39 DONE only if linked R39 tasks are DONE and validation passes

Constraints:
- Treat survey-based satisfaction and time-on-task improvement as future user-feedback validation, not deterministic proof
- Keep validation local and reproducible

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 98: Establish R52 Workspace role-card experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R52

Goal:
Constrain the Workspace page role-card improvement to a focused usability and visual-hierarchy pass before implementation.

Requirements:
- Use Experience Designer guidance to keep the Workspace role section easy to scan and immediately understandable for PM, Engineer, Designer, QA, Architect, and Orchestrator responsibilities
- Use UI Designer guidance from the saved design brief to maintain uniform card width, clearer role hierarchy, consistent spacing, stronger card separation, and more visible summary actions
- Preserve the existing agent summaries, popup behavior, and Workspace role set
- Keep the change scoped to the Workspace page visual design and layout

Constraints:
- Do NOT add new workflow semantics or new agent execution behavior
- Do NOT alter the source role definitions or popup summary content
- Do NOT introduce a new UI dependency for this slice
- Treat survey satisfaction and support-question reductions as future user-feedback metrics, not deterministic validation claims

Experience Designer guidance:
- The role-card section should answer who each agent is and why the user would open its summary before requiring detailed reading
- Visual balance matters because asymmetrical role cards reduce trust and slow scanability
- The Workspace should stay an orientation surface, not become a documentation browser

UI Designer guidance:
- Role cards should have equal column width within every row, including incomplete rows
- Role labels should read as distinct metadata, not compete with the agent display title
- Card backgrounds, borders, and summary actions should create clear affordances while staying restrained
- Native Streamlit layout is sufficient; no third-party component is needed

Validation:
- Carry this guidance into the Engineer task
- Add or update deterministic unit tests for role-card markup and row layout helpers where practical

Output:
- R52 design constraints for implementation
- Explicit limits that keep the work inside visual/layout improvement scope

## Task 99: Refine Workspace role-card visual hierarchy and symmetry

Type: Feature Task
Status: DONE
Requirement: R52

Goal:
Make Workspace role cards more visually even and easier to scan while preserving existing role summary behavior.

Requirements:
- Render role-card rows with fixed row width so incomplete rows do not stretch remaining cards
- Update role-card markup and styling to improve hierarchy between role name, display title, and summary
- Improve role-card visual separation through restrained background, border, and spacing treatment
- Make the agent summary action more visible while keeping the existing popup behavior
- Preserve all existing agent role cards and summary content

Constraints:
- Do NOT change project navigation, Inbox behavior, requirements workflow, or implementation controls
- Do NOT change the meaning of any role or summary popup section
- Keep the layout responsive and compatible with native Streamlit reruns

Validation:
- Add or update deterministic unit tests for role-card markup, role-card row weights, and summary action behavior
- Run the project-local validation path

Output:
- Updated Workspace role-card UI
- Validation evidence that existing role summaries still open through the same action path

## Task 100: Validate and close R52

Type: Validation Task
Status: DONE
Requirement: R52

Goal:
Close R52 only after deterministic validation passes and linked R52 tasks are complete.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R52 DONE only if linked R52 tasks are DONE and validation passes

Constraints:
- Keep validation local and reproducible
- Do NOT claim survey or support-question metric improvement from deterministic tests

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 101: Establish R53 role-card button experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R53

Goal:
Constrain the Workspace role-card button improvement to a focused usability and interaction-polish pass before implementation.

Requirements:
- Use Experience Designer guidance to make the summary action feel attached to each agent card instead of floating below it
- Use UI Designer guidance to place the action directly after the agent description with consistent alignment across cards
- Preserve the existing agent role cards, summary popup behavior, row symmetry, and card dimensions
- Keep the design responsive using native Streamlit layout and local CSS only

Constraints:
- Do NOT change backend logic, role definitions, summary popup content, or navigation semantics
- Do NOT introduce a new UI dependency for this slice
- Do NOT claim post-implementation user feedback improvement from deterministic validation

Experience Designer guidance:
- User problem: the current action placement weakens the connection between each agent description and its summary action, slowing scan-and-act behavior on the Workspace
- Affected workflow: Product Director and team members reviewing Workspace agent summaries
- Evidence: R53 records that users struggle to identify and engage with agent summaries because action buttons are poorly positioned
- Confidence: Medium, based on explicit requirement evidence but without measured post-change feedback
- Recommendation: keep the action inside the card rhythm, immediately after the description, so each card reads as label, title, summary, action

UI Designer guidance:
- The card should use a flex column so summaries occupy the flexible middle area and actions align along the card bottom
- The action row should be visually inside the card using a small top margin and full-width button-style link treatment
- Button styling should improve accessibility through consistent target size, visible border, clear focus/hover affordance, and restrained primary color
- Mobile behavior should remain a single-column/Streamlit-native stacked layout with no action overflow

Validation:
- Carry this guidance into the Engineer task
- Add or update deterministic tests for role-card markup and style hooks where practical

Output:
- R53 design constraints for implementation
- Explicit limits that keep the work inside card interaction and styling scope

## Task 102: Move Workspace role-card summary actions inside cards

Type: Feature Task
Status: DONE
Requirement: R53

Goal:
Make each Workspace agent summary action visually and structurally part of its card while preserving existing summary popup behavior.

Requirements:
- Render the summary action inside the role-card container directly below the agent summary
- Keep action placement and alignment uniform across all role cards
- Preserve the existing action label text and popup content
- Improve the action styling for accessibility and scanability while maintaining current card dimensions and row symmetry

Constraints:
- Do NOT change role-card ordering, role definitions, or summary dialog content
- Do NOT alter Workspace project cards, Inbox cards, Requirements views, or agent workspace flows
- Keep the implementation compatible with Streamlit reruns and native layout behavior

Validation:
- Add or update deterministic unit tests for the internal action markup, styling hooks, and existing label behavior
- Run the project-local validation path

Output:
- Updated Workspace role-card markup and styling
- Validation evidence that summary actions remain available and consistently labelled

## Task 103: Validate and close R53

Type: Validation Task
Status: DONE
Requirement: R53

Goal:
Close R53 only after deterministic validation passes and linked R53 tasks are complete.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R53 DONE only if linked R53 tasks are DONE and validation passes

Constraints:
- Keep validation local and reproducible
- Treat user-feedback ease-of-use improvement as a future feedback metric, not deterministic proof

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 104: Establish R48 experience and UI simplification direction

Type: Feature Task
Status: DONE
Requirement: R48

Goal:
Constrain the broad Workspace and Inbox simplification requirement into an implementable usability and visual direction before engineering changes.

Requirements:
- Use Experience Designer guidance to identify the main workflow problem as excess visual weight and weak grouping across Workspace approvals and Inbox workflow items
- Use UI Designer guidance to simplify the shared workflow-card treatment and make Inbox sections easier to scan
- Preserve existing Workspace, Inbox, approval, clarification, routed-finding, and active-run behavior
- Keep the first implementation slice focused on existing surfaces rather than introducing new workflow features

Constraints:
- Do NOT add full workflow execution control, manual state editing, or deep task inspection
- Do NOT change approval, inbox, sprint, requirement, or agent-thread data semantics
- Do NOT add a third-party UI dependency for this simplification pass
- Do NOT claim measured user-feedback improvement from deterministic validation

Experience Designer guidance:
- User problem: the Workspace and Inbox currently make operational items feel heavier than their content warrants, increasing scan effort before the Product Director can decide what needs attention
- Affected workflow: opening the control panel, checking approvals, and triaging the Workflow Inbox
- Evidence: R48 explicitly asks for broader visual simplification, more intentional hierarchy, card grouping, button spacing reassessment, and less excessive border/shadow treatment
- Confidence: Medium, based on explicit requirement language and repeated prior workspace/inbox polish work, but without new measured usability evidence
- Recommendation: reduce card visual weight, make section grouping do more of the comprehension work, and keep action cues honest about real workflow state

UI Designer guidance:
- Use the existing shared workflow card header as the visual anchor for Workspace approvals and Inbox items
- Introduce a restrained workflow-card styling hook so bordered Streamlit containers read lighter and more intentional
- Use compact section labels for Inbox groups that include item counts and attention state before the list starts
- Keep accent color limited to state cues and primary actions, with whitespace and grouping carrying the simplified design

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for workflow-card styling hooks and Inbox section label helpers

Output:
- R48 usability and UI direction for implementation
- Explicit limits that keep the broad initiative inside a focused simplification slice

## Task 105: Simplify Workspace approval and Inbox workflow card hierarchy

Type: Feature Task
Status: DONE
Requirement: R48

Goal:
Make Workspace approval cards and Inbox workflow items feel lighter, more grouped, and easier to scan while preserving existing workflow behavior.

Requirements:
- Add a shared workflow-card visual hook used by Workspace approval cards, Inbox approval cards, and Inbox workflow-item cards
- Reduce the perceived weight of workflow cards through restrained background, border, shadow, and spacing treatment
- Add compact Inbox section labels that communicate the section name, item count, and attention state
- Preserve existing approval actions, review details, thread links, clarification reply forms, and item metadata
- Keep state cue colors sparing and tied to the existing attention labels

Constraints:
- Do NOT change workflow item ordering, filtering behavior, status buckets, or action handlers
- Do NOT introduce new navigation or card selection behavior
- Do NOT hide required approval review details or clarification questions
- Keep the implementation compatible with native Streamlit layout and reruns

Validation:
- Add or update deterministic unit tests for workflow-card markup, style hooks, and Inbox section label helpers
- Run the project-local validation path

Output:
- Updated Workspace approval and Inbox card styling/section hierarchy
- Validation evidence that the shared card helpers still expose the existing metadata and attention labels

## Task 106: Validate and close R48

Type: Validation Task
Status: DONE
Requirement: R48

Goal:
Close R48 only after the focused simplification slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R48 DONE only if linked R48 tasks are DONE and validation passes
- Record any reusable design decision in project memory

Constraints:
- Keep validation local and reproducible
- Do NOT claim broad initiative completion beyond the implemented Workspace and Inbox simplification slice
- Treat any remaining preference questions from R48 as future design input, not blockers for this scoped slice

Validation:
- `venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 110: Establish R56 navigation experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R56

Goal:
Constrain the main-navigation redesign into a focused usability and visual direction before implementation.

Requirements:
- Use Experience Designer guidance to prioritize the top-level jobs: Workspace overview, opening project work, clearing Inbox items, and creating a new project
- Use UI Designer guidance to make the main navigation read as a deliberate control surface rather than a plain horizontal radio group
- Keep the existing top-level destinations and project-level section navigation intact
- Define responsive behavior that remains clear on narrow screens without adding a separate navigation model

Constraints:
- Do NOT redesign non-navigation surfaces outside the minimum needed to frame the main navigation
- Do NOT change backend workflow state, project data, Inbox semantics, or requirement persistence
- Do NOT add a third-party UI dependency for this navigation slice
- Do NOT claim measured user-survey or usage-stat improvement from deterministic validation

Experience Designer guidance:
- User problem: team members need faster orientation and task access at the top of the control panel, but the current main navigation feels like a generic tab strip rather than an intentional workflow entry point
- Affected workflow: opening the control panel, moving between workspace overview, project work, Inbox triage, and new-project creation
- Evidence: R56 explicitly identifies main navigation clarity, intuitiveness, and quick access to workspaces, projects, Inbox, and project creation as the problem space
- Confidence: Medium, based on explicit requirement evidence and repeated prior navigation findings, but without post-change timing or survey data
- Recommendation: preserve the four current destinations while improving hierarchy, labels, and immediate visual affordance so users can choose their next workflow without reading surrounding content first

UI Designer guidance:
- Use Streamlit's native segmented-control pattern for the top-level navigation because it communicates mutually exclusive destinations more intentionally than a plain horizontal radio group
- Place the navigation in a restrained main-navigation block with a short label, clear selected state, and stable full-width behavior
- Keep labels task-oriented and familiar: Workspace, Open Project, Inbox, Create Project
- Keep project-level navigation visually distinct as the existing vertical project-section control
- Use local CSS hooks only for spacing, border, and selected-state polish; native Streamlit behavior remains the interaction source of truth

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for the main-navigation labels, control choice, helper metadata, and project-level navigation separation

Output:
- R56 experience and UI direction for implementation
- Explicit limits that keep the work inside main-navigation redesign scope

## Task 111: Redesign the main navigation control

Type: Feature Task
Status: DONE
Requirement: R56

Goal:
Make the control panel's top-level navigation clearer, more intentional, and easier to use while preserving current destinations.

Requirements:
- Replace the plain horizontal top-level radio interaction with a native Streamlit segmented-control navigation
- Add a restrained main-navigation visual wrapper or styling hook that makes the navigation feel like a first-class control
- Preserve the existing four top-level destinations:
  - Workspace
  - Open Project
  - Inbox
  - Create Project
- Preserve legacy session-state normalization from old labels into current labels
- Keep project-detail navigation separate and visibly distinct from the main navigation
- Preserve existing routing behavior for opening projects, returning to project list, Inbox, and new-project creation

Constraints:
- Do NOT change the requirement editor, Inbox item behavior, approval actions, sprint behavior, agent flows, or project creation logic
- Do NOT add a sidebar navigation or a second competing top-level navigation model
- Do NOT introduce external Streamlit components
- Keep the implementation deterministic and unit-testable through app helper functions

Validation:
- Add or update unit tests for the segmented-control helper, labels, descriptions, and legacy label normalization
- Run the project-local validation path

Output:
- Updated top-level navigation UI
- Validation evidence that navigation labels and routing helpers remain stable

## Task 112: Validate and close R56

Type: Validation Task
Status: DONE
Requirement: R56

Goal:
Close R56 only after deterministic validation passes and linked R56 tasks are complete.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R56 DONE only if linked R56 tasks are DONE and validation passes
- Record the reusable navigation design decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat survey feedback, navigation usage statistics, and task-time reduction as future product metrics, not deterministic proof

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 113: Establish R55 Open Project experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R55

Goal:
Constrain the broad Open Project page improvement into a focused, implementable usability and visual direction before engineering changes.

Requirements:
- Use Experience Designer guidance to identify the main workflow problem as scan-and-select friction when choosing which project to open
- Use UI Designer guidance to improve the Open Project page's hierarchy, card anatomy, and action placement without changing project data or navigation semantics
- Keep the page focused on choosing a project and seeing enough status at a glance to make that choice confidently
- Preserve existing project opening, preview, missing-structure visibility, and selected-project detail behavior

Constraints:
- Do NOT add new project management functionality beyond clearer presentation of existing project summary data
- Do NOT change project parsing, requirement/task storage, Inbox behavior, or agent workflows
- Do NOT add a third-party UI dependency
- Do NOT claim survey, user-testing, or navigation-time success from deterministic validation alone

Experience Designer guidance:
- User problem: users selecting a project currently see a plain grid of similarly weighted cards, so the page does not strongly support quick comparison or confident next action
- Affected workflow: moving from the main navigation into Open Project, scanning available projects, deciding which project needs attention, then opening or previewing it
- Evidence: R55 explicitly reports frustration and disengagement on the Open Project page, and current cards expose counts but do not summarize the next likely work item
- Confidence: Medium, based on explicit requirement language and current UI structure, but without direct post-change user-testing evidence
- Recommendation: keep the page narrow in purpose, make each card communicate health, work signals, and next work before actions, and keep the primary Open action visually dominant

UI Designer guidance:
- Add a restrained Open Project page intro that explains the selection job without becoming a marketing section
- Give project cards a consistent internal anatomy: status cue, project name, concise metadata, two stable signal columns, next-work summary, then actions
- Keep card styling lightweight and compatible with the existing workflow-card grammar instead of introducing a separate decorative card system
- Make the Open action primary and the Preview action secondary while preserving equal card widths and responsive two-column behavior
- Use native Streamlit containers, columns, and buttons with local CSS hooks only for hierarchy, spacing, and scanability

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for Open Project page helper text, project-card anatomy, next-work summaries, and styling hooks

Output:
- R55 experience and UI direction for implementation
- Explicit limits that keep the work inside the Open Project page UI slice

## Task 114: Refine the Open Project page card hierarchy

Type: Feature Task
Status: DONE
Requirement: R55

Goal:
Make the Open Project page easier to scan and more visually intentional while preserving current project-opening behavior.

Requirements:
- Add concise page-level helper copy for the Open Project selection workflow
- Add reusable project-card markup/helpers for a consistent status cue and card anatomy
- Summarize the next visible work signal using existing project data, prioritizing new requirements before pending tasks and falling back to structure or idle state
- Keep New requirements and Pending tasks as stable side-by-side signals
- Keep the Open project button as the primary action and Preview as the secondary action
- Preserve missing-path detail for projects with structure issues

Constraints:
- Do NOT alter project discovery, project file parsing, requirement/task semantics, or preview startup behavior
- Do NOT remove the existing selected-project detail path
- Do NOT add custom JavaScript or external UI components
- Keep helper functions deterministic and unit-testable

Validation:
- Add or update unit tests for Open Project helper copy, project-card status labels, next-work summary behavior, and CSS hooks
- Run the project-local validation path

Output:
- Updated Open Project page presentation
- Validation evidence that existing routing behavior remains stable

## Task 115: Validate and close R55

Type: Validation Task
Status: DONE
Requirement: R55

Goal:
Close R55 only after the focused Open Project UI slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R55 DONE only if linked R55 tasks are DONE and validation passes
- Record any reusable Open Project page design decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat survey ratings, user-testing feedback, and navigation-time reduction as future product metrics, not deterministic proof
- Treat the remaining open questions from R55 as future research input rather than blockers for this scoped slice

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

## Task 116: Establish R58 two-layer navigation experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R58

Goal:
Constrain the two-layer navigation clarity improvement into a focused usability and visual direction before engineering changes.

Requirements:
- Use Experience Designer guidance to define the usability problem as weak visual differentiation between workspace-level navigation and project-level section navigation
- Use UI Designer guidance to make the main navigation and project navigation read as separate hierarchy levels while preserving the current navigation structure
- Keep the existing top-level destinations and project-level sections intact
- Preserve the current task-oriented labels and segmented-control main navigation
- Keep the secondary navigation clearly scoped to the selected project

Constraints:
- Do NOT rethink the overall navigation model or add a new navigation hierarchy
- Do NOT change backend workflow state, project data, Inbox semantics, requirement persistence, or agent workflows
- Do NOT add a third-party UI dependency
- Do NOT claim user-satisfaction, usability-test, or task-completion improvement from deterministic validation alone

Experience Designer guidance:
- User problem: users can struggle to tell whether they are using workspace-level navigation or selected-project section navigation because both controls sit near each other without enough hierarchy and scope cues
- Affected workflow: moving from the workspace-level control panel into a selected project, then switching between Requirements and Agents inside that project
- Evidence: R58 explicitly reports insufficient visual differentiation in the current two-layer navigation structure, and prior navigation work preserved the hierarchy while improving labels
- Confidence: Medium, based on explicit requirement evidence and repeated navigation clarity work, but without fresh usability-test evidence
- Recommendation: preserve the two-layer model, but add stronger scope language, visual separation, and hierarchy cues so users can identify the current navigation layer before choosing an option

UI Designer guidance:
- Treat the main navigation as the global workspace control with a concise level label and destination descriptors
- Treat project navigation as a secondary local control with a visible selected-project scope marker and compact section options
- Use native Streamlit controls and local CSS hooks for hierarchy, spacing, border treatment, and selected-state context
- Avoid decorative redesign; the improvement should be clearer level distinction, not a new visual theme
- Keep the layout responsive by maintaining the existing side-by-side project detail structure and allowing secondary labels to wrap cleanly on narrow widths

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for navigation level labels, scope helper text, CSS hooks, and preservation of the existing navigation destinations

Output:
- R58 experience and UI direction for implementation
- Explicit limits that keep the work inside two-layer navigation clarity scope

## Task 117: Refine two-layer navigation visual differentiation

Type: Feature Task
Status: DONE
Requirement: R58

Goal:
Make the workspace-level and project-level navigation layers easier to distinguish while preserving current routing behavior.

Requirements:
- Add or refine helper functions that expose explicit navigation level labels and scope descriptions
- Make the main navigation communicate that it controls workspace-level destinations
- Make the project navigation communicate that it controls sections inside the selected project
- Add local CSS hooks that visually separate the secondary project navigation from the main navigation
- Preserve the existing top-level destinations:
  - Workspace
  - Open Project
  - Inbox
  - Create Project
- Preserve the existing project-level sections:
  - Requirements
  - Agents

Constraints:
- Do NOT alter routing semantics, project opening behavior, requirement editing, Inbox behavior, or agent flows
- Do NOT add external Streamlit components or custom JavaScript
- Do NOT rename destinations in a way that breaks existing session-state normalization
- Keep helper functions deterministic and unit-testable

Validation:
- Add or update unit tests for the new navigation hierarchy helpers and styling hooks
- Run the project-local validation path

Output:
- Updated navigation presentation
- Validation evidence that navigation hierarchy and destinations remain stable

## Task 118: Validate and close R58

Type: Validation Task
Status: DONE
Requirement: R58

Goal:
Close R58 only after the focused navigation hierarchy slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R58 DONE only if linked R58 tasks are DONE and validation passes
- Record any reusable navigation hierarchy decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat user satisfaction, usability testing, and task completion rates as future product metrics, not deterministic proof
- Treat remaining open questions from R58 as future research input rather than blockers for this scoped slice

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

Post-implementation Experience Designer review:
- User problem reviewed: the two navigation layers needed clearer hierarchy and scope cues without changing the underlying navigation model
- Evidence checked: implementation now names the main layer as workspace-level navigation and the selected-project layer as project-level navigation, with deterministic tests covering helper copy and styling hooks
- Confidence: Medium; deterministic checks confirm the intended UI structure, while direct user satisfaction and guided usability evidence remain future metrics
- Recommendation: close the scoped R58 implementation because the in-scope usability improvement is represented in the UI helpers, styling hooks, and validation coverage

## Task 119: Establish R57 agent and mode selection experience and UI direction

Type: Feature Task
Status: DONE
Requirement: R57

Goal:
Constrain the agent and mode selection usability problem into a focused, implementable experience and design direction before engineering changes.

Requirements:
- Use Experience Designer guidance to define the usability problem as avoidable context switching between the chosen agent and the relevant mode choices
- Use UI Designer guidance to place agent identity, selected-agent context, and mode choice close enough that users can understand the relationship before entering a thread
- Preserve the existing agent set:
  - PM
  - Experience Designer
  - UI Designer
  - Orchestrator
- Preserve each agent's current modes and thread-starting behavior
- Keep the work scoped to the Agents project section selection surface

Constraints:
- Do NOT change agent workflow semantics, thread persistence, mode names, approval flows, Inbox behavior, or backend planner behavior
- Do NOT add a third-party UI dependency, custom JavaScript, or a broader interface redesign
- Do NOT claim usability-test time reduction or satisfaction-score improvement from deterministic validation alone

Experience Designer guidance:
- User problem: users must choose an agent and then interpret separate mode options with too much visual distance between the selected role and the mode decision
- Affected workflow: opening a project, entering Agents, selecting PM/Experience Designer/UI Designer/Orchestrator, choosing the mode, then starting or continuing the relevant thread
- Evidence: R57 explicitly reports difficulty quickly and intuitively selecting agents and modes because the current layout creates unnecessary visual distance
- Confidence: Medium, based on explicit requirement language and current UI structure, but without fresh usability-test timing data
- Recommendation: keep the existing two-step decision model but make selected-agent context persistent and place mode options inside a nearby action area so users can confirm "who" and "how" together

UI Designer guidance:
- Treat agent selection as a compact role picker and selected-agent summary, not a distant grid followed by disconnected mode cards
- Add an agent-workspace context shell with restrained styling hooks for selector layout, selected-agent summary, and mode cards
- Make selected state visible through copy and structure, while preserving native Streamlit buttons and rerun behavior
- Keep mode cards compact, equal-weight, and responsive, with descriptions close to their choice buttons
- Prefer native Streamlit columns/containers and local CSS hooks over new components

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for selected-agent context copy, mode summary behavior, styling hooks, and preservation of existing agent/mode option sets

Output:
- R57 experience and UI direction for implementation
- Explicit limits that keep the work inside the Agents selection layout slice

## Task 120: Refine agent and mode selection layout proximity

Type: Feature Task
Status: DONE
Requirement: R57

Goal:
Make the Agents section easier to scan and use by tightening the relationship between selected agent context and mode selection while preserving existing behavior.

Requirements:
- Add deterministic helper functions for agent workspace caption, selected-agent summary, selected-agent mode summary, and markup hooks
- Render selected-agent context between the agent picker and mode choices so the next choice is visually tied to the chosen agent
- Update the agent selector and mode selector card markup to use local CSS hooks for hierarchy, proximity, selected state, and scanability
- Preserve existing session-state keys, agent options, mode options, and chat rendering paths
- Keep single-mode agents deterministic by setting their mode state while still showing concise mode context

Constraints:
- Do NOT change thread lifecycle functions, project selection behavior, Inbox focus behavior, requirement/task parsing, or agent role definitions
- Do NOT rename modes or agents
- Do NOT add external Streamlit components, custom JavaScript, or non-local styling dependencies
- Keep helper functions deterministic and unit-testable

Validation:
- Add or update unit tests for helper copy, selected-agent/mode markup, CSS hooks, and the unchanged option sets
- Run the project-local validation path

Output:
- Updated Agents selection presentation
- Validation evidence that agent and mode routing behavior remains stable

## Task 121: Validate and close R57

Type: Validation Task
Status: DONE
Requirement: R57

Goal:
Close R57 only after the focused Agents selection layout slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Mark R57 DONE only if linked R57 tasks are DONE and validation passes
- Record any reusable Agents selection layout decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat usability-test speed and satisfaction-score changes as future product metrics, not deterministic proof
- Treat remaining open questions from R57 as future research input rather than blockers for this scoped slice

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

Post-implementation Experience Designer review:
- User problem reviewed: agent and mode selection needed stronger proximity and context without changing the underlying two-step workflow
- Evidence checked: implementation now keeps selected-agent context directly beside the mode decision through deterministic helper copy and styling hooks
- Confidence: Medium; deterministic checks confirm the intended UI structure, while direct usability-test timing and satisfaction evidence remain future metrics
- Recommendation: close the scoped R57 implementation because the in-scope usability improvement is represented in the Agents selection layout and validation coverage

## Task 122: Establish R59 project control panel layout direction

Type: Feature Task
Status: DONE
Requirement: R59

Goal:
Constrain the broad Project Control Panel layout issue into a focused, implementable experience and UI direction before engineering changes.

Requirements:
- Use Experience Designer guidance to define the usability problem as weak first-screen orientation inside an opened project, especially around preview access and the relationship between project work and agent assignment
- Use UI Designer guidance to make the project header, preview action, and agent assignment entry points scan as one coherent project-control area
- Prioritize the selected project identity, preview availability, current local section, and available agent assignments without introducing a new project-management model
- Keep the existing project-level sections:
  - Requirements
  - Agents
- Keep the existing agent set and modes:
  - PM
  - Experience Designer
  - UI Designer
  - Orchestrator

Constraints:
- Do NOT redesign the whole control panel, global navigation, requirements editing, agent thread lifecycle, implementation execution, or persistence model
- Do NOT add backend agent assignment functionality; treat assignment as the existing act of choosing an agent and mode inside the Agents section
- Do NOT add third-party UI dependencies, custom JavaScript, or a new navigation system
- Do NOT claim measured survey, analytics, or satisfaction improvements from deterministic validation alone

Experience Designer guidance:
- User problem: once a project is opened, users need a clearer control area that helps them orient, preview the project, and move into the right agent workflow without scanning separate stacked regions
- Affected workflow: opening a project from the workspace, checking project preview availability, then deciding whether to work in Requirements or assign work to PM, Experience Designer, UI Designer, or Orchestrator through the Agents section
- Evidence: R59 explicitly reports project-control layout frustration and asks for faster access to project previews and agent assignments; current rendering places preview above the project navigation/content split and does not summarize agent assignment options at the project-control level
- Confidence: Medium, based on requirement text and current UI structure, but without fresh analytics or survey data
- Recommendation: preserve current routing and agent behavior, but add a compact project-control header that groups preview access and agent-assignment orientation close to project identity and local navigation

UI Designer guidance:
- Treat the opened-project top area as a utility header rather than another large card stack
- Show project identity, path, preview state, and agent assignment options with restrained native Streamlit layout and local CSS hooks
- Move preview access into the same control band as project identity so it is immediately available without occupying a separate full-width block
- Add an agent-assignment summary that names the current agent options and points users to the Agents section without creating a duplicate agent launcher
- Keep responsive behavior simple: a primary project summary column plus compact utility columns that stack naturally on narrow widths

Validation:
- Carry this guidance into the Engineer task
- Add deterministic tests for project-control helper copy, preview placement hooks, agent-assignment summary hooks, and preservation of the existing project sections and agent options

Output:
- R59 experience and UI direction for implementation
- Explicit limits that keep the work inside project-control layout clarity scope

## Task 123: Refine opened-project control header layout

Type: Feature Task
Status: DONE
Requirement: R59

Goal:
Make the opened project page easier to scan by grouping project identity, preview access, and agent assignment orientation into a compact control header.

Requirements:
- Add deterministic helper functions for project-control heading copy, project path metadata, preview summary copy, agent-assignment summary copy, and markup hooks
- Render a compact project-control header at the top of the opened project view
- Keep preview start/open behavior available in that header
- Add a compact agent-assignment orientation summary that lists the available project agents and clarifies that assignment happens in the Agents section
- Keep project-level navigation and content routing unchanged
- Preserve existing session-state keys, preview runtime behavior, agent options, mode options, and requirement editing paths

Constraints:
- Do NOT change project selection behavior, preview process management, requirements persistence, agent thread persistence, Inbox behavior, or orchestration routing
- Do NOT add automatic agent assignment or new backend ownership state
- Do NOT rename Requirements, Agents, PM, Experience Designer, UI Designer, or Orchestrator
- Keep helper functions deterministic and unit-testable

Validation:
- Add or update unit tests for helper copy, markup hooks, preview summary behavior, agent-assignment summary behavior, and unchanged project sections/agent options
- Run the project-local validation path

Output:
- Updated opened-project control header presentation
- Validation evidence that preview and agent routing behavior remain stable

## Task 124: Validate and close R59

Type: Validation Task
Status: DONE
Requirement: R59

Goal:
Close R59 only after the focused project-control layout slice is implemented and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Run the deterministic Orchestrator helper after implementation
- Perform a post-implementation Experience Designer review for the meaningful UI-facing change
- Mark R59 DONE only if linked R59 tasks are DONE and validation passes
- Record any reusable project-control layout decision in project memory

Constraints:
- Keep validation local and reproducible
- Treat survey satisfaction, analytics, and reported-issue reduction as future product evidence, not deterministic proof
- Treat remaining open questions from R59 as future research input rather than blockers for this scoped slice

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`
- `python3 tools/orchestrator_status.py os-control-panel`

Output:
- Validation results
- Requirement closure state

Post-implementation Experience Designer review:
- User problem reviewed: the opened-project control area needed clearer first-screen orientation for project preview and agent assignment without changing the project workflow model
- Evidence checked: implementation now groups project identity, path, preview state/action, and agent assignment orientation in one compact project-control header, with deterministic tests covering copy, markup hooks, and preservation of existing project sections and agent options
- Confidence: Medium; deterministic checks confirm the intended UI structure, while direct survey, analytics, and reported-issue evidence remain future product metrics
- Recommendation: close the scoped R59 implementation because the in-scope layout improvement is represented in the project-control header and validation coverage

## Task 125: Define Architect and QA workspace surfaces

Type: Design Task
Status: DONE
Requirement: R60

Goal:
Add Architect and QA into the shared agent workspace in a way that is useful, truthful, and consistent with the rest of the OS.

Requirements:
- Keep Architect as a deterministic structural review surface in this slice
- Keep QA as a deterministic validation-review surface in this slice
- Reuse the existing shared agent selection model rather than inventing a separate location for these roles
- Make the scope and limits of both roles explicit in the UI

Constraints:
- Do NOT pretend Architect or QA are live-chat agents if they are not
- Keep the first slice grounded in current file state and existing validation tooling

Validation:
- Add deterministic coverage for the expanded agent set and role-specific mode descriptions

Output:
- Clear Architect and QA workspace shape

## Task 126: Implement Architect and QA panels in Agents

Type: Feature Task
Status: DONE
Requirement: R60

Goal:
Expose Architect and QA as usable project-level surfaces inside `Agents`.

Requirements:
- Add Architect to the shared agent selector with an `Architecture Review` mode
- Add QA to the shared agent selector with a `Validation Review` mode
- Architect should show current structural hotspots and guardrails derived from project state
- QA should run the existing validation path and show summary, failures, confidence, and raw output
- Preserve PM, Experience Designer, UI Designer, and Orchestrator behavior

Constraints:
- Keep both surfaces deterministic and local-first
- Reuse the existing project eval runner path for QA

Validation:
- Add or update unit tests for the expanded agent list, Architect/QA mode descriptions, Architect snapshot behavior, and QA review behavior
- Run the project-local validation path

Output:
- Architect and QA surfaces in `Agents`

## Task 127: Validate and close R60

Type: Validation Task
Status: DONE
Requirement: R60

Goal:
Close R60 only after the new Architect and QA surfaces behave coherently and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm the shared agent workspace still reads coherently after adding Architect and QA
- Record any reusable role-surface decision in project memory

Validation:
- `python3 projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 128: Design an implementation-run inspection surface

Type: Design Task
Status: DONE
Requirement: R61

Goal:
Define a compact project-level run-observability surface that makes background implementation work inspectable without turning the requirements page into another long workflow log.

Requirements:
- Show recent implementation runs for the selected project in one dedicated place
- Keep sprint planning visually ahead of run history so sprint control stays primary
- Make active, completed, failed, and stale runs clearly distinguishable
- Let the Product Director open one run at a time to inspect its details

Constraints:
- Reuse the existing file-backed implementation run model
- Keep the UI compact and recent-first

Validation:
- Add deterministic coverage for run-inspection helpers

Output:
- Clear run-history panel shape for the requirements page

## Task 129: Implement recent run history and detail inspection

Type: Feature Task
Status: DONE
Requirement: R61

Goal:
Expose recent implementation runs inside the requirements workflow so sprint execution and failed runs no longer feel opaque.

Requirements:
- Add a project-level implementation-runs panel to the requirements page
- Show recent runs with status, linked requirement, and timestamps
- Allow each run to be expanded for summary, error state, and available log/output references
- Show output/log previews when files exist
- Keep the latest requirement-card implementation state intact

Constraints:
- Do not build the full workflow timeline yet
- Keep the panel compact enough that it does not drown out active requirement work

Validation:
- Add deterministic coverage for run inspection, status classification, and artifact previews

Output:
- Recent implementation run history and detail inspection in the UI

## Task 130: Validate and close R61

Type: Validation Task
Status: DONE
Requirement: R61

Goal:
Close R61 only after the run-observability surface is usable and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm recent implementation runs are inspectable from the requirements page
- Record the observability decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 131: Define truthful workflow timeline coverage

Type: Design Task
Status: DONE
Requirement: R62

Goal:
Define a workflow timeline that answers “where did this go?” using only artifact history the OS can honestly reconstruct.

Requirements:
- Use durable workflow artifacts rather than inferred requirement history
- Cover approvals, clarifications, findings, agent-thread transitions, and implementation runs
- Make approval outcomes explicit so the timeline can show what an approved review turned into
- Keep the surface recent-first and project-scoped in this first slice

Constraints:
- Do not invent requirement transition history the OS never recorded
- Keep the timeline inspectable without turning the requirements page into another giant log

Validation:
- Add deterministic coverage for outcome capture and timeline ordering

Output:
- Clear truthful workflow-timeline model

## Task 132: Implement workflow timeline and artifact outcome history

Type: Feature Task
Status: DONE
Requirement: R62

Goal:
Expose a project-level workflow timeline that shows what happened to important artifacts after creation, approval, clarification, routing, and implementation.

Requirements:
- Add a workflow timeline panel to the requirements page
- Show recent events for:
  - agent threads
  - approvals and approval outcomes
  - PM clarifications
  - experience findings
  - implementation runs
- Persist approval outcome references so the timeline can point to backlog requirements or scope confirmations truthfully
- Distinguish open attention from recorded and completed history

Constraints:
- Keep the first version project-level rather than requirement-by-requirement
- Reuse existing file-backed workflow stores rather than adding a new event ledger

Validation:
- Add deterministic coverage for approval outcome persistence, clarification resolution timestamps, and timeline event assembly

Output:
- Recent workflow timeline and artifact outcome history in the UI

## Task 133: Validate and close R62

Type: Validation Task
Status: DONE
Requirement: R62

Goal:
Close R62 only after the timeline answers common workflow-history questions and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm the requirements page now exposes both implementation-run history and broader workflow history
- Record the observability decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 134: Define the project quality-signal surface

Type: Design Task
Status: DONE
Requirement: R63

Goal:
Define a quality dashboard that makes validation health visible in the control panel without collapsing it into workflow history or implementation state.

Requirements:
- Show the latest deterministic validation result for a project
- Keep the quality signal clearly separate from implementation runs and workflow timeline
- Preserve QA as an explicit review surface while giving the project page its own persistent quality read
- Record when the validation was last run

Constraints:
- Reuse the existing deterministic validation runner
- Keep the first slice project-scoped rather than workspace-global

Validation:
- Add deterministic coverage for persisted quality review records

Output:
- Clear project-level quality dashboard shape

## Task 135: Implement persisted quality reviews and dashboard surface

Type: Feature Task
Status: DONE
Requirement: R63

Goal:
Expose a trustworthy quality signal in the control panel and persist QA review results so they remain visible after the transient agent interaction ends.

Requirements:
- Persist deterministic QA review results for each project
- Show the latest quality signal in the requirements page with:
  - pass/fail summary
  - failing cases
  - confidence statement
  - last-run timestamp
- Update the QA agent surface to reuse the persisted quality review record
- Keep raw validation output inspectable

Constraints:
- Do not merge quality state into implementation-run state
- Keep the quality panel compact and readable

Validation:
- Add deterministic coverage for pass/fail persistence and latest-review lookup

Output:
- In-app quality dashboard and persisted QA review history

## Task 136: Validate and close R63

Type: Validation Task
Status: DONE
Requirement: R63

Goal:
Close R63 only after validation health is visible in-product and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm the quality signal remains distinct from implementation and workflow state
- Record the quality-surface decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 137: Define requirement-level manual verification state

Type: Design Task
Status: DONE
Requirement: R64

Goal:
Define a lightweight manual verification model that lives with each requirement and supports signoff without waiting for the later guided test-card workflow.

Requirements:
- Store verification state per requirement
- Let a requirement hold multiple manual verification checks
- Track pass/fail/not-run plus notes per check
- Derive a clear signoff state from the recorded checks

Constraints:
- Keep this slice requirement-level, not workspace-global
- Do not depend on the future guided test-card interaction from R65

Validation:
- Add deterministic coverage for verification-plan persistence and signoff-state calculation

Output:
- Clear requirement-level verification state model

## Task 138: Implement manual verification editing and signoff summaries in the UI

Type: Feature Task
Status: DONE
Requirement: R64

Goal:
Expose manual verification directly inside requirement detail so signoff evidence stays attached to the work being reviewed.

Requirements:
- Show a manual verification section in requirement detail
- Let the Product Director add verification checks
- Let the Product Director record:
  - pass
  - fail
  - notes
- Show a signoff summary derived from the current checks
- Keep verification editable for completed requirements without reopening product-content editing

Constraints:
- Keep the UI compact and local-first
- Preserve the completed-requirement archive model

Validation:
- Add deterministic coverage for add/update/remove flows and signoff states

Output:
- Requirement-level manual verification and signoff evidence in the control panel

## Task 139: Validate and close R64

Type: Validation Task
Status: DONE
Requirement: R64

Goal:
Close R64 only after manual verification is visibly tied to requirements and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm manual verification state is available for active and completed requirements
- Record the signoff-model decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 140: Define the guided verification-card pattern

Type: Design Task
Status: DONE
Requirement: R65

Goal:
Define a guided manual-testing pattern that keeps the selected verification check visible while the Product Director moves through relevant project surfaces.

Requirements:
- Let the user pick a requirement-level verification check to guide
- Keep the guided card visible at the project level rather than burying it back inside one requirement expander
- Preserve requirement-level ownership of the underlying verification state
- Avoid turning the guided card into a separate heavyweight workflow system

Constraints:
- Build on top of the requirement-level verification model from R64
- Keep the first slice inside the selected project rather than floating across the whole workspace

Validation:
- Add deterministic coverage for guided-card state selection and clearing

Output:
- Clear guided verification-card pattern for the control panel

## Task 141: Implement pinned guided verification card in project detail

Type: Feature Task
Status: DONE
Requirement: R65

Goal:
Make manual testing easier by letting one selected verification check stay visible while the Product Director navigates the project.

Requirements:
- Add a `Guide this check` action to manual verification checks
- Show the selected check in a pinned guided card at the project-detail level
- Let the guided card:
  - show the current instructions
  - record pass/fail/not-run
  - capture notes
  - jump back into the Requirements section
  - be cleared when no longer needed
- Keep the card requirement-level rather than introducing a separate testing object

Constraints:
- Keep the guided card project-scoped
- Reuse the same verification data store and signoff logic as R64

Validation:
- Add deterministic coverage for guided-card selection and clearing behavior

Output:
- Guided test-card flow for manual verification

## Task 142: Validate and close R65

Type: Validation Task
Status: DONE
Requirement: R65

Goal:
Close R65 only after the guided card remains useful while navigating the project and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm the guided card stays visible at the project level while the Product Director moves through the project
- Record the guided-testing interaction decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 143: Define the cleaner project-section split

Type: Design Task
Status: DONE
Requirement: R66

Goal:
Separate project planning, delivery inspection, and quality review into clearer sections so the Requirements page stops carrying too many different jobs.

Requirements:
- Keep `Requirements` centered on sprint planning, requirement editing, and requirement-level verification
- Move implementation and workflow-history inspection into a dedicated `Delivery` section
- Move deterministic validation signal into a dedicated `Quality` section
- Preserve the existing project-scoped guided verification flow

Constraints:
- Do not remove or weaken the new observability and quality capabilities
- Keep the project navigation simple and local-first

Validation:
- Add deterministic coverage for the updated project-section labels

Output:
- Clear project information architecture for planning, delivery, and quality

## Task 144: Move observability and quality surfaces into dedicated project sections

Type: Feature Task
Status: DONE
Requirement: R66

Goal:
Reduce conceptual overload on the Requirements page by giving execution history and quality review their own homes.

Requirements:
- Add `Delivery` and `Quality` to project navigation
- Move:
  - implementation runs
  - workflow timeline
  out of `Requirements` and into `Delivery`
- Move deterministic validation signal out of `Requirements` and into `Quality`
- Leave sprint planning, structured requirements, and requirement-level manual verification inside `Requirements`

Constraints:
- Preserve existing run-history, workflow-timeline, and quality functionality
- Keep manual verification attached to requirements rather than moving it into project-wide quality

Validation:
- Run the project-local validation path

Output:
- Cleaner project navigation with dedicated delivery and quality surfaces

## Task 145: Validate and close R66

Type: Validation Task
Status: DONE
Requirement: R66

Goal:
Close R66 only after the project UI separates planning, delivery, and quality cleanly and deterministic validation passes.

Requirements:
- Run the project-local validation path
- Confirm the project navigation exposes `Requirements`, `Agents`, `Delivery`, and `Quality`
- Record the information-architecture decision in project memory

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 152: Define the residual workspace redesign boundary

Type: Design Task
Status: DONE
Requirement: R49

Goal:
Turn the broad workspace redesign theme into a bounded residual design-debt container so future UI review work has one clear place to consolidate.

Requirements:
- Record what remains beyond the already completed workspace, navigation, inbox, project-control, and role-card slices
- State that R49 is not a mandate for another broad visual overhaul without new evidence
- Preserve R49 as the consolidation point for future approved workspace visual-review findings that share this theme
- Distinguish residual visual direction from distinct product problems that should become separate requirements

Constraints:
- Do not reopen completed requirements R45, R47, R48, R52, R54, R57, R58, or R59
- Do not introduce a new workflow model, visual system dependency, or implementation surface
- Keep the outcome file-backed in product state or project memory

Validation:
- Confirm the requirement text and memory describe the residual boundary clearly

Output:
- A clear residual workspace redesign boundary for future PM and design routing

## Task 153: Update the R49 product record with Experience and UI Designer guidance

Type: Feature Task
Status: DONE
Requirement: R49

Goal:
Apply the Experience Designer and UI Designer guidance to the R49 product record without making unnecessary UI code changes.

Requirements:
- Add a concise R49 note that future work must identify what remains beyond shipped slices before implementation
- Add a concise R49 note that broad redesign work should be decomposed into focused, evidence-backed slices before engineering
- Keep the note aligned with the local-first control panel and existing Streamlit constraints

Constraints:
- Do not change production UI unless the residual review identifies a concrete, bounded screen problem
- Do not create duplicate workspace redesign requirements
- Keep the requirement understandable from `requirements.md` alone

Validation:
- Run the project-local validation path after file-backed state updates

Output:
- Updated R49 source-of-truth text

## Task 154: Validate and close R49

Type: Validation Task
Status: DONE
Requirement: R49

Goal:
Close R49 once it functions as the residual broad workspace redesign container and validation passes.

Requirements:
- Run the project-local validation path
- Confirm no active R49 engineering task remains
- Record the R49 consolidation decision in project memory
- Mark R49 DONE only after validation succeeds

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 155: Define the balanced Inbox card layout direction

Type: Design Task
Status: DONE
Requirement: R43

Goal:
Use Experience Designer and UI Designer review to turn the open Inbox layout question into a focused implementation direction.

Requirements:
- Preserve the Inbox as a grouped workflow queue for approvals, waiting items, blocked items, routed artifacts, and active runs
- Reduce repeated full-width cards by presenting inbox cards in a balanced two-column grid where space allows
- Keep approval details, PM clarification questions, thread links, and workflow-state cues readable inside each card
- Preserve current grouping by workflow state so scanability improves without hiding state meaning

Constraints:
- Do not redesign the full control panel visual system
- Do not change the underlying Inbox workflow model or file-backed state
- Use native Streamlit layout primitives and existing card styling hooks

Validation:
- Add deterministic coverage for the Inbox card row layout helpers and styling hooks

Output:
- Inbox design direction: grouped workflow sections with balanced two-column card rows and left-aligned incomplete rows

## Task 156: Implement balanced Inbox card rows

Type: Feature Task
Status: DONE
Requirement: R43

Goal:
Make Inbox workflow cards easier to scan by rendering approval and workflow-item cards in balanced rows rather than one long full-width stack.

Requirements:
- Add reusable Inbox card row helpers
- Render open approval requests in balanced Inbox card rows
- Render grouped waiting, blocked, routed, and running workflow items in balanced Inbox card rows
- Preserve existing card contents, review controls, clarification forms, thread links, and status styling

Constraints:
- Keep changes scoped to the Inbox layout and deterministic tests
- Preserve existing workflow behavior and source-of-truth files
- Avoid adding new UI dependencies

Validation:
- Run the project-local validation path

Output:
- Balanced Inbox card layout for approvals and workflow items

## Task 157: Validate and close R43

Type: Validation Task
Status: DONE
Requirement: R43

Goal:
Close R43 only after the Inbox layout change passes deterministic validation and the requirement source of truth is updated.

Requirements:
- Run the project-local validation path
- Confirm Inbox card layout helpers create balanced two-column rows
- Confirm existing workflow card styling and Inbox grouping remain covered
- Mark R43 DONE only after validation succeeds

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`

Output:
- Validation results
- Requirement closure state

## Task 158: Define the private reflection-helper interaction

Type: Design Task
Status: DONE
Requirement: R72

Goal:
Turn the interactive-reflection concept into a small, testable workflow shape inside the OS before implementation begins.

Requirements:
- Define the trigger moment for the first reflection-helper slice
- Define the minimum clarifying-question sequence
- Define the output shape for a structured reflection draft
- Define where the draft should be written in the private reflection layer

Constraints:
- Keep the first slice narrow and private-first
- Do not design a full reflection dashboard
- Avoid introducing public-facing workflow surfaces

Validation:
- Review the resulting interaction shape against the Reflection V2 design note
- Confirm the scope is small enough for a first implementation slice

Output:
- Reflection-helper interaction shape
- Minimal question flow
- Draft output contract
- Product artifact: `projects/os-control-panel/product/reflection-helper-interaction-R72.md`

## Task 159: Build the local interactive reflection helper

Type: Feature Task
Status: DONE
Requirement: R72

Goal:
Implement the first usable reflection-helper flow so the OS can help turn raw signals into stronger structured reflection drafts.

Requirements:
- Add a local-only reflection helper entry point
- Accept a raw signal as input
- Ask a small number of clarifying questions in sequence
- Produce a structured reflection draft with clearer fields
- Save the draft into the private reflection layer without exposing it publicly

Constraints:
- Keep the implementation local-first and private-first
- Do not require a broad new navigation surface for the first slice
- Prefer the smallest useful interaction over a more ambitious reflection system

Validation:
- Run the project-local validation path
- Manually confirm the helper can turn one raw signal into a stronger reflection draft

Output:
- Working local reflection-helper flow
- Private saved reflection draft
- Project-local validation path passed after implementation

## Task 160: Validate and close R72

Type: Validation Task
Status: DONE
Requirement: R72

Goal:
Close R72 only after the first reflection-helper slice works reliably enough to support repeated use.

Requirements:
- Run the project-local validation path
- Confirm the helper asks clarifying questions rather than only storing the original note
- Confirm the output is saved into the private reflection layer
- Confirm the flow stays private-first and out of public repo surfaces
- Mark R72 DONE only after validation succeeds

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- Manual reflection-helper walkthrough

Output:
- Automated validation passed through the project-local eval runner
- The first manual walkthrough confirmed the helper worked and saved drafts into the private reflection layer
- A follow-on bounded dynamic-questioning slice was required before closure
- Validation completed successfully after the dynamic follow-on was tested manually

## Task 161: Add bounded dynamic questioning to the reflection helper

Type: Feature Task
Status: DONE
Requirement: R72

Goal:
Improve the reflection helper so it asks context-specific follow-up questions while still producing a structured private reflection draft.

Requirements:
- Replace the fixed follow-up sequence with context-sensitive questioning based on the raw signal and prior answers
- Keep the interaction bounded so it remains lightweight rather than becoming an open-ended journal chat
- Preserve the current private-first draft output shape or evolve it in a compatible way
- Make it clear when the helper is reasoning about the signal and preparing the next question

Constraints:
- Keep this local-first and private-first
- Keep operator reflection content out of public repo or showcase surfaces
- Avoid turning the helper into a generic agent chat without a structured end state

Validation:
- Run the project-local validation path
- Manually confirm that two materially different signals produce meaningfully different follow-up questions
- Manually confirm the final output still saves as a structured reflection draft

Output:
- Working bounded dynamic reflection-helper flow
- Evidence that questioning adapts to context instead of reusing the same fixed prompts
- Product artifact: `projects/os-control-panel/product/reflection-helper-dynamic-questioning-R72.md`

## Task 162: Define the private concept-learning helper interaction

Type: Design Task
Status: DONE
Requirement: R73

Goal:
Turn the interactive-learning concept into a small, testable workflow shape inside the OS before implementation begins.

Requirements:
- Define the trigger moment for the first concept-learning slice
- Define the minimum clarification sequence
- Define the output shape for a stronger concept note draft
- Define where the draft should be written in the private learning layer

Constraints:
- Keep the first slice narrow and private-first
- Do not design a full learning dashboard
- Keep the helper grounded in implementation context rather than generic study

Validation:
- Review the resulting interaction shape against the Learning V2 design note
- Confirm the scope is small enough for a first implementation slice

Output:
- Concept-learning helper interaction shape
- Minimal clarification flow
- Draft output contract
- Product artifact: `projects/os-control-panel/product/concept-learning-helper-interaction-R73.md`

## Task 163: Build the local interactive concept-learning helper

Type: Feature Task
Status: DONE
Requirement: R73

Goal:
Implement the first usable concept-learning helper so the OS can help turn concept exposure into stronger contextual understanding.

Requirements:
- Add a local-only concept-learning helper entry point
- Accept a concept or unfamiliar term as input
- Ask a small number of clarifying questions in sequence
- Produce a stronger concept note draft tied to implementation and product implication
- Save the draft into the private learning layer without exposing it publicly

Constraints:
- Keep the implementation local-first and private-first
- Do not require a broad new navigation surface for the first slice
- Prefer the smallest useful interaction over a more ambitious learning system

Validation:
- Run the project-local validation path
- Manually confirm the helper can turn one fuzzy concept into a stronger concept note draft

Output:
- Working local concept-learning helper flow
- Private saved concept note draft
- Project-local validation path passed after implementation

## Task 164: Validate and close R73

Type: Validation Task
Status: DONE
Requirement: R73

Goal:
Close R73 only after the first concept-learning helper slice works reliably enough to support repeated use.

Requirements:
- Run the project-local validation path
- Confirm the helper clarifies the concept rather than only storing the term
- Confirm the output is saved into the private learning layer
- Confirm the flow stays private-first and out of public repo surfaces
- Mark R73 DONE only after validation succeeds

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- Manual concept-learning helper walkthrough

Output:
- Automated validation passed through the project-local eval runner
- Manual walkthrough confirmed the helper can structure and save a concept note draft
- Manual walkthrough also showed that the helper asks for learning inputs without teaching or explaining enough in context
- The bounded teaching/explainer follow-on was delivered, and the older helper-era slice is now complete as a foundation
- The active frontier has moved into the broader live learning-agent initiative under `R74`

## Task 165: Add bounded concept teaching to the learning helper

Type: Feature Task
Status: DONE
Requirement: R73

Goal:
Improve the concept-learning helper so it teaches or explains the concept in context before asking the operator to finalize a concept note draft.

Requirements:
- Add a bounded explanation step after the operator provides the concept and current confusion
- Explain what the concept is, why it exists, and what nearby distinction matters
- Connect the explanation to implementation context in the OS where possible
- Keep the interaction bounded so it remains lightweight rather than becoming an open-ended tutor chat
- Preserve the current private-first concept note draft output or evolve it in a compatible way

Constraints:
- Keep this local-first and private-first
- Do not turn the helper into a generic study system detached from current work
- Avoid unbounded chat or overly broad teaching loops

Validation:
- Run the project-local validation path
- Manually confirm the helper teaches something useful before requesting final note fields
- Manually confirm the final output still saves as a structured concept note draft

Output:
- Working bounded concept-teaching flow
- Evidence that the helper improves understanding rather than only collecting note inputs
- Product artifact: `projects/os-control-panel/product/concept-learning-explainer-R73.md`
- Project-local validation path passed after implementation

## Task 166: Define the holistic learning-layer initiative shape

Type: Design Task
Status: DONE
Requirement: R74

Goal:
Turn the learning-layer initiative into a clear product shape so learning work can stay coherent across explanation, recommendation, and build-to-learn pathways.

Requirements:
- Define the major learning capability tracks needed beyond the current helper slice
- Clarify how built-in concept teaching, new-concept capture, concept recommendation, and build-to-learn should connect
- Define what makes the learning layer feel first-class rather than like scattered helper tools

Constraints:
- Keep the initiative grounded in the operator's trajectory and end goals
- Do not collapse the whole learning system into a single narrow helper requirement

Validation:
- Review the resulting initiative shape against the current product direction
- Confirm it creates a coherent next-phase learning program for the OS

Output:
- Holistic learning-layer initiative shape
- Product artifact: `projects/os-control-panel/product/learning-layer-initiative-R74.md`

## Task 167: Add concept recommendation and next-learning prompts

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Help the OS propose which concepts should be learned next so the operator is not limited to concepts they already know to ask about.

Requirements:
- Identify candidate next concepts based on current OS capabilities, current work, and stated trajectory
- Surface recommended next concepts inside the private learning layer or helper flow
- Explain why each recommended concept matters now

Constraints:
- Keep recommendations grounded and finite
- Avoid generic laundry lists of AI terminology

Validation:
- Run the project-local validation path
- Manually confirm the OS can suggest useful next concepts rather than random buzzwords

Output:
- Working concept recommendation flow
- Evidence that the OS can propose useful next learning steps
- Automated validation passed through the project-local eval runner

## Task 168: Add build-to-learn concept pathways

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Let the OS support learning concepts that are not yet implemented by turning them into bounded build-to-learn pathways.

Requirements:
- Allow a concept to be marked as something to learn by building
- Define a bounded path from concept -> implementation experiment -> learning note
- Preserve a link between the built experiment and the resulting learning artifact

Constraints:
- Keep the first slice lightweight and bounded
- Avoid spawning broad speculative projects without a learning objective

Validation:
- Run the project-local validation path
- Manually confirm at least one concept can be framed as a build-to-learn pathway

Output:
- Working build-to-learn pathway model
- Evidence that learning-by-building is captured intentionally
- Manual walkthrough confirmed the first build-to-learn cut works cleanly enough to carry forward
- Product artifact: `projects/os-control-panel/product/build-to-learn-pathways-R74.md`

## Task 169: Validate and close R74

Type: Validation Task
Status: DONE
Requirement: R74

Goal:
Close R74 only after the learning layer feels like a coherent first-class OS capability rather than a loose collection of helpers.

Requirements:
- Validate the integrated teaching, concept capture, concept recommendation, and build-to-learn behavior
- Confirm the learning layer supports concepts already present, newly introduced concepts, and concepts not yet implemented
- Confirm the capability feels aligned with the operator's trajectory and end goal
- Mark R74 DONE only after the initiative reaches a V3-or-better learning experience

Validation:
- `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- Manual learning-layer walkthrough

Output:
- Validation results
- Initiative closure state
- R74 remains open while the broader learning-agent and concept-management scope stays active
- Outcome captured: `R74` remains open because the initiative expanded into the live tutoring-agent and concept-management phase rather than stopping at the earlier integrated-helper cut

## Task 170: Define the learning agent model and Feynman operating pattern

Type: Design Task
Status: DONE
Requirement: R74

Goal:
Define the next-phase learning agent so the OS can guide concept understanding actively rather than only exposing helper flows.

Requirements:
- Define how the learning agent should use the operator's background, current trajectory, and learned concepts
- Define the Feynman-style learning loop for the agent:
  - explain simply
  - ask for re-explanation in plain language
  - detect weak spots or jargon dependence
  - route back into clarification or build-to-learn when understanding is shallow
- Define how the learning agent should decide when to teach, when to ask follow-up questions, and when to suggest building
- Keep the model bounded enough to implement incrementally in the local-first UI

Constraints:
- Keep the model grounded in actual OS learning work, not generic tutoring theory
- Avoid designing an open-ended conversational companion without concept-state discipline

Validation:
- Review the resulting model against the operator's stated end goal of jargon-free understanding and credible explanation

Output:
- Product artifact: `projects/os-control-panel/product/learning-agent-model-R74.md`
- A concrete operating model for the next implementation slice
- The next implementation slice is concept lifecycle management so learning state can be edited, advanced, and reopened intentionally

## Task 171: Add concept lifecycle management

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Let the operator manage concepts intentionally over time rather than only create new notes.

Requirements:
- Support concept states such as:
  - upcoming
  - in progress
  - learned
  - reopened / needs-refresh
- Allow the operator to:
  - mark a concept learned
  - move a concept back into the learning backlog
  - edit concept understanding and open questions
  - capture new doubts or follow-up questions after a concept was previously considered learned
- Preserve concept history rather than overwriting understanding invisibly

Constraints:
- Keep the first lifecycle model simple enough to reason about in the UI
- Do not collapse all learning state into one flat notes file without inspectable structure

Validation:
- Run the project-local validation path
- Manually confirm a concept can move through more than one state without losing context

Output:
- Working concept lifecycle management flow
- Evidence that concepts can be revisited and reopened intentionally

## Task 172: Add concept relationship and dependency guidance

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Help the operator understand how concepts connect so learning compounds instead of fragmenting.

Requirements:
- Allow concepts to reference related concepts, nearby distinctions, and likely prerequisites
- Surface at least a lightweight relationship view for current learning concepts
- Help the OS suggest when a concept should be learned before or after another one

Constraints:
- Keep the first slice light and useful rather than attempting a heavy knowledge graph upfront
- Prefer a concept relationship model that supports explanation and sequencing over visual spectacle

Validation:
- Run the project-local validation path
- Manually confirm at least one concept can be understood in relation to others more clearly than before

Output:
- Working concept relationship guidance
- Evidence that learning order and adjacency are clearer
- The Learning tab now surfaces prerequisite, related, often-confused-with, and next concept relationships in the concept detail view
- Validation passed through the project-local eval runner and manual walkthroughs confirmed the relationship layer is useful enough for this first slice

## Task 173: Add background-aware next-learning guidance

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make next-concept suggestions more personal and trajectory-aware instead of only capability-driven.

Requirements:
- Capture the operator's background and current learning posture in a reusable form for the learning layer
- Use that context when recommending what to learn next
- Explain why a concept matters for this operator specifically, not just in general

Constraints:
- Keep the first slice private-first and editable
- Avoid pretending to know the operator better than the explicit captured context allows

Validation:
- Run the project-local validation path
- Manually confirm at least one recommendation feels more tailored because of background-aware context

Output:
- Working background-aware recommendation support
- Evidence that the learning layer can personalize concept guidance meaningfully
- Product artifact: `projects/os-control-panel/product/background-aware-learning-guidance-R74.md`
- A private learning profile now personalizes recommendation framing and why-now guidance
- Validation passed through the project-local eval runner and manual review confirmed recommendations feel more personally grounded

## Task 174: Pull build-to-learn back into concept management

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Close the current gap where build-to-learn exists as a path, but not yet as a full loop back into concept understanding.

Requirements:
- Link build-to-learn pathways back into the related concept record
- Allow a completed or partially completed build-to-learn experiment to update concept state, open questions, and current understanding
- Make it visible when a concept was learned partly by building rather than only by explanation

Constraints:
- Keep the first slice inspectable and file-backed
- Do not auto-mark concepts learned without explicit human confirmation

Validation:
- Run the project-local validation path
- Manually confirm one concept can move from recommended -> build-to-learn -> updated concept state

Output:
- Working pull-through from build-to-learn into concept management
- Evidence that learning-by-building feeds the concept system rather than floating beside it
- Product artifact: `projects/os-control-panel/product/build-to-learn-concept-management-R74.md`
- Evolution framing: `projects/os-control-panel/product/build-to-learn-evolution-R74.md`
- Build-to-learn now has a dedicated `Builds` surface with concept <-> build linking in both directions
- Completed build capture can now flow back into concept understanding and unresolved questions without auto-marking a concept learned

## Task 175: Add a persistent learning-agent session with Feynman-style understanding checks

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Turn the learning layer from a set of connected helpers into a true bounded learning-agent session that can stay with one concept, check understanding over multiple turns, and guide the next learning move.

Requirements:
- Support one persistent active learning-agent session for a concept
- Allow the session to begin from a recommendation, concept manager, or related learning surface
- Use a Feynman-style loop:
  - explain simply
  - ask the operator to explain it back simply
  - detect weak understanding
  - choose the next move
- Preserve enough session state that the operator can continue without restarting the concept each turn
- Allow the operator to request follow-up clarification inside the session, including:
  - explain it more simply
  - clarify a specific confusion
  - give another example
  - compare it to a nearby concept
- Route cleanly into:
  - more explanation
  - nearby distinction
  - concept-state update
  - build-to-learn

Constraints:
- Keep the session bounded and easy to resume
- Avoid turning the learning layer into an open-ended tutor chat
- Keep the first slice private-first, file-backed, and inspectable
- Do not auto-mark a concept learned

Validation:
- Run the project-local validation path
- Manually confirm one concept can stay active across more than one learning turn without losing context
- Manually confirm the Feynman explanation-back check changes the next move meaningfully
- Manually confirm the operator can ask a follow-up clarification question without breaking or abandoning the session

Output:
- Working persistent learning-agent session
- Evidence that learning guidance now feels session-based rather than helper-fragmented
- Product artifact: `projects/os-control-panel/product/persistent-learning-agent-session-R74.md`
- Current gaps:
  - operator-initiated follow-up clarification inside the session is now implemented as bounded clarification moves
  - the next refinement is to decide how much further lifecycle progression should move into the live agent as follow-on work rather than leaving that question inside this task
- Validation:
  - bounded clarification moves are now available inside the active session
  - project-local validation passed at `186/186`

## Task 176: Strengthen compounding guidance across concepts

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make the learning layer compound over time so concept progress changes what the OS recommends next, how it sequences adjacent concepts, and what should be reopened or deepened.

Requirements:
- Use concept state, concept relationships, build-to-learn outcomes, and recent learning activity to improve what the OS suggests next
- Help the operator understand:
  - what concept should come next
  - what adjacent concept is now more relevant
  - what unresolved edge should be revisited
  - what concept relationship became clearer because of recent learning
- Move beyond isolated recommendations toward a lightweight cumulative learning map

Constraints:
- Keep the first slice lightweight and file-backed rather than building a heavy curriculum engine
- Prefer clear progression logic over visual complexity
- Do not bury the operator in too many simultaneous "next" suggestions

Validation:
- Run the project-local validation path
- Manually confirm the next-learning guidance changes meaningfully after concept progress or build-to-learn outcomes
- Manually confirm at least one reopened concept affects what the OS recommends next

Output:
- Working compounding guidance across concepts
- Evidence that the learning layer now builds on prior learning rather than only presenting isolated concept prompts
- Delivered through the live tutoring-agent compounding slice in `Task 188`

## Task 177: Show concepts implemented in the OS

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Help the operator learn by seeing how a concept is actually implemented in the OS, not only by reading explanations about it.

Requirements:
- Allow the learning layer to show where a concept appears in the OS
- Surface useful implementation anchors such as:
  - relevant files
  - concrete examples or cases
  - related outputs or artifacts
  - a simple explanation of how those pieces relate to one another
- Make the walkthrough useful for retention, not just as a file list

Constraints:
- Keep the first slice inspectable and local-first
- Prefer a small number of relevant implementation anchors over dumping too much repo detail at once
- Keep the explanation in plain language tied to the operator's learning goal

Validation:
- Run the project-local validation path
- Manually confirm at least one concept (for example `Evals`) can be learned more concretely by seeing its implementation in the OS

Output:
- Working concept-implementation walkthrough flow
- Evidence that concepts can be learned by seeing them in action inside the OS
- Delivered through the live tutoring-agent implementation-walkthrough slice in `Task 187`

## Task 178: Simplify the learning layer around the live agent

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Retire or demote older helper-era learning flows so the learning layer feels agent-centered rather than like a collection of competing tools.

Requirements:
- Make the persistent learning-agent session the primary learning path
- Retire the concept helper from the main user-facing flow or reduce it to a fallback/internal tool
- Simplify concept manager so it behaves primarily like a concept library and continuation surface, not a heavy record editor
- Reduce the prominence of manual concept maintenance in favor of agent-led progression
- Preserve concept/build linkage, concept relationships, and inspectable state without making them compete with the live session

Constraints:
- Keep the system private-first, local-first, and file-backed
- Do not remove manual control entirely; keep a lower-emphasis maintenance path for edge cases
- Avoid introducing another top-level learning mode while simplifying

Validation:
- Run the project-local validation path
- Manually confirm the learning layer feels more coherent after the agent-centered cleanup
- Manually confirm the main user path now clearly favors:
  - start/resume learning session
  - open concept
  - open build

Output:
- A more coherent agent-centered learning layer
- Reduced duplication between older helpers and the live learning session
- Product artifact: `projects/os-control-panel/product/learning-agent-centered-cleanup-R74.md`
- Workflow guidance artifact: `projects/os-control-panel/product/learning-agent-centered-workflow-R74.md`
- Architect audit artifact: `projects/os-control-panel/product/learning-layer-architecture-audit-R74.md`
- Progress note: the older concept-helper UI path has now been retired from the main learning experience so `Learn next` stays fully agent-centered
- Progress note: inline manual concept maintenance has now been removed from the normal concept view so concept progression is owned by the live agent in the primary flow
- The concept page now behaves primarily as a read-and-route surface rather than a heavy manual editor
- Remaining deeper cleanup has been split into follow-on architecture tasks instead of leaving this simplification task artificially open

## Task 179: Re-baseline R74 product truth

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Bring `R74` task and requirement truth back into alignment with the current implementation so Architect, Orchestrator, and workflow state remain trustworthy.

Requirements:
- Review the current `R74` slices that are already substantially implemented
- Mark completed slices done where the product and validation support closure
- Rewrite stale task notes so they describe the current live-agent-centered product truth
- Preserve an honest record of what is still incomplete rather than collapsing everything into one broad `IN_PROGRESS` blob

Constraints:
- Keep the update grounded in actual product behavior, not optimism
- Do not close open work simply to make the board look cleaner
- Prefer fewer clearer active tasks over many stale half-active ones

Validation:
- Manually confirm the Architect snapshot is more trustworthy after the task-state cleanup
- Manually confirm the active learning-layer tasks describe the current frontier rather than already-shipped work

Output:
- Re-baselined `R74` task truth
- Cleaner active frontier for the learning initiative
- Evidence that workflow-state reasoning is now more trustworthy
- Completed learning slices are now marked done and the active frontier is narrowed to persistent session refinement plus follow-on architectural cleanup
- Product artifact: `projects/os-control-panel/product/learning-layer-architecture-audit-R74.md`

## Task 180: Split learning state into explicit layers

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Reduce architectural ambiguity in the learning layer by separating recommendation state, concept state, learning-session state, and build-to-learn state more explicitly.

Requirements:
- Stop overloading one derived concept record with meanings that belong to different learning layers
- Make it explicit when the UI is showing:
  - recommendation framing
  - persisted concept understanding
  - active learning-session output
  - build-to-learn state
- Keep the composition inspectable and file-backed without pretending the sources are one underlying state object

Constraints:
- Prefer evolutionary refactors over a large rewrite
- Preserve current user-facing functionality while clarifying the model
- Keep the live learning agent as the center of gravity

Validation:
- Run the project-local validation path
- Manually confirm recommendation-only concepts no longer read like answered learning state
- Manually confirm concept views feel more truthful about what is inferred versus what was actually learned

Output:
- Clearer learning-state model boundaries
- Reduced UI confusion caused by overloaded derived records
- Stronger alignment between product semantics and stored state
- Product artifact: `projects/os-control-panel/product/learning-state-layering-R74.md`
- Recommendation, concept, session, and build state are now composed explicitly for the learning surfaces rather than blurred through one overloaded derived record
- Concept detail rendering now reads from the layered model and validation passed at `187/187`

## Task 181: Thin concept manager into a read-and-route surface

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make Concept manager a lighter library and continuation surface while the live learning agent owns progression logic.

Requirements:
- Reduce view-level orchestration logic in Concept manager
- Keep the page focused on:
  - current concept state
  - linked build state
  - relationships
  - lifecycle history
  - clear routing back into the learning agent
- Move progression decisions and concept-shaping behavior further into the learning agent where appropriate

Constraints:
- Do not reintroduce helper-era parallel workflows
- Preserve file-backed inspectability
- Keep the concept page calm and easy to scan

Validation:
- Run the project-local validation path
- Manually confirm the concept page feels more like a reading-and-routing surface than a hidden orchestration layer
- Manually confirm the live learning agent remains the obvious primary path

Output:
- Simpler concept manager architecture
- Reduced regression risk from UI cleanup work
- Stronger alignment between the concept page and the live-agent operating model
- Workflow artifact: `projects/os-control-panel/product/learning-concept-manager-read-route-R74.md`
- Concept manager now behaves as a calmer read-and-route surface with the live agent as the dominant continuation path
- Validation passed at `188/188` and manual review confirmed the page feels acceptable

## Task 182: Define the live tutoring-agent architecture

Type: Design Task
Status: DONE
Requirement: R74

Goal:
Define the true model-generated tutoring agent as the next core architecture of the learning layer.

Requirements:
- Define the tutoring agent as a single-agent-first system
- Define its:
  - model role
  - tool surface
  - instruction surface
  - concept-state responsibilities
- Define how it should own:
  - teaching
  - clarification
  - explanation-back
  - progression guidance
  - build-to-learn routing
- Keep the architecture grounded in the existing file-backed learning system

Constraints:
- Do not decompose into multiple learning agents yet
- Do not reintroduce helper-era parallel flows
- Keep the design inspectable and local-first

Validation:
- Review the resulting architecture against the current R74 live-agent goal

Output:
- Product artifact: `projects/os-control-panel/product/live-tutoring-agent-initiative-R74.md`
- A concrete architecture for the model-generated tutoring-agent phase
- The architecture now defines:
  - agent inputs and structured outputs
  - tool contracts
  - session vs durable concept-state boundaries
  - progression ownership
  - build-to-learn and implementation-walkthrough integration
  - guardrail and eval expectations

## Task 183: Add model-generated teaching and clarification

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Replace the remaining deterministic teaching and clarification core with true model-generated tutoring responses.

Requirements:
- Replace static concept-teaching and clarification logic with model-generated responses
- Make the generated response use:
  - concept
  - learning profile
  - current concept state
  - active session context
  - exact operator clarification ask
  - related concepts and nearby distinctions
- Preserve the bounded learning-session shape instead of becoming a generic open chat

Constraints:
- Keep the tutoring practical and concise
- Keep concept-specific grounding strong
- Avoid hallucinated implementation details or free-floating tutoring verbosity

Validation:
- Run the project-local validation path
- Manually confirm two different clarification questions for the same concept produce meaningfully different teaching responses

Output:
- A true model-generated clarification and teaching loop
- Reduced reliance on deterministic helper-era response logic

## Task 184: Add tutoring-agent instructions and guardrails

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make the tutoring agent reliable by giving it strong instructions and explicit guardrails.

Requirements:
- Add explicit tutoring instructions for:
  - simple explanation
  - jargon discipline
  - Feynman-style explanation-back
  - staying on the current concept
  - choosing the next move responsibly
- Add guardrails for:
  - concept drift
  - false certainty
  - premature `learned` progression
  - unbounded build-to-learn suggestions
  - invented OS implementation claims

Constraints:
- Keep the guardrails product-focused rather than safety-theater
- Preserve a calm, supportive tutoring voice

Validation:
- Run the project-local validation path
- Manually confirm the agent stays anchored to the selected concept through multiple turns

Output:
- Stronger tutoring instructions
- Explicit tutoring guardrails

## Task 185: Add human hand-back and uncertainty behavior

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Let the tutoring agent hand control back cleanly when the learning situation is too ambiguous, too broad, or too risky to press forward automatically.

Requirements:
- Add explicit hand-back behavior when:
  - the concept is too broad
  - the learning goal is underspecified
  - the agent is uncertain
  - the proposed build step is too large or risky
- Make the hand-back feel supportive and clear rather than like a failure

Constraints:
- Keep the intervention lightweight
- Avoid unnecessary interruptions when the agent can continue responsibly

Validation:
- Manually confirm at least one ambiguous concept flow returns cleanly to the operator instead of bluffing forward

Output:
- Working human hand-back behavior inside the tutoring workflow

## Task 186: Make concept progression fully agent-owned

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make the tutoring agent the owner of concept progression across upcoming, in progress, build-to-learn, learned, and reopened states.

Requirements:
- Let the agent propose and confirm concept progression changes
- Make the agent own the normal transitions between:
  - upcoming
  - in progress
  - build-to-learn
  - learned
  - reopened
- Preserve file-backed inspectability of each transition

Constraints:
- Do not hide state changes
- Keep the progression model understandable in the UI

Validation:
- Run the project-local validation path
- Manually confirm the agent can move a concept through more than one state without falling back to helper-era manual logic

Output:
- Agent-owned concept progression workflow

## Task 187: Integrate implementation walkthroughs into the tutoring agent

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Let the tutoring agent show how concepts are implemented in the OS so learning is tied to real examples, files, evals, and behavior.

Requirements:
- Let the agent retrieve and explain implementation anchors for a concept
- Support examples such as:
  - relevant files
  - eval cases
  - build pathways
  - related outputs or artifacts
- Keep the walkthrough explanatory, not just a file dump

Constraints:
- Prefer a small number of meaningful anchors
- Keep the explanation tied to the learner's current goal and concept state

Validation:
- Run the project-local validation path
- Manually confirm one concept such as `Evals` can be explained through its implementation in the OS

Output:
- Working concept-implementation walkthroughs inside the tutoring flow
- Progress on existing `Task 177` through the live-agent model

## Task 188: Strengthen compounding guidance through the tutoring agent

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make the tutoring agent compound learning over time by changing what it recommends, revisits, compares, and deepens based on prior concept progress.

Requirements:
- Use concept state, relationships, build outcomes, and recent learning history to shape next recommendations
- Help the agent explain:
  - what should come next
  - what adjacent concept is now more relevant
  - what should be reopened
  - what relationship became clearer because of recent learning

Constraints:
- Keep the first slice lightweight and inspectable
- Avoid overwhelming the operator with too many simultaneous next steps

Validation:
- Run the project-local validation path
- Manually confirm the tutoring agent changes what it recommends after meaningful learning progress

Output:
- Stronger compounding guidance through the live tutoring agent
- Progress on existing `Task 176` through the live-agent model

## Task 189: Add tutoring-agent evaluation coverage

Type: Validation Task
Status: DONE
Requirement: R74

Goal:
Give the tutoring agent a reliable eval layer so the live model-driven learning behavior can be trusted, improved, and debugged.

Requirements:
- Add evaluation coverage for:
  - teaching quality
  - clarification quality
  - Feynman understanding checks
  - concept progression decisions
  - build-to-learn routing decisions
  - recommendation quality
- Preserve fast local validation where possible

Constraints:
- Do not rely on vibes alone to validate tutoring quality
- Keep evals targeted and inspectable rather than bloated

Validation:
- Run the project-local validation path
- Confirm the tutoring-agent evals meaningfully distinguish stronger and weaker learning behavior

Output:
- Tutoring-agent eval coverage
- Stronger confidence in the live-agent learning core

## Task 190: Evaluate manager-pattern decomposition after the single tutoring agent is strong

Type: Design Task
Status: BACKLOG
Requirement: R74

Goal:
Only after the single tutoring agent is strong, decide whether a manager pattern or agents-as-tools architecture would improve the learning layer.

Requirements:
- Review whether specialized sub-agents would genuinely improve:
  - implementation walkthroughs
  - build-to-learn planning
  - concept graph reasoning
  - tutoring-quality review
- Compare the added clarity against the risk of fragmentation

Constraints:
- Do not introduce manager-pattern decomposition before the single-agent tutoring model is already strong and validated

Keep this task tied to the delivered single-agent tutoring model unless a future requirement explicitly reopens manager-pattern decomposition.

Validation:
- Architectural review against the delivered single-agent tutoring system

Output:
- A clear yes/no recommendation on manager-pattern decomposition
- Product artifact: `projects/os-control-panel/product/live-tutoring-agent-initiative-R74.md`

## Task 191: Simplify the Learning tab around the current learning move

Type: Feature Task
Status: DONE
Requirement: R75

Goal:
Make the Learning tab calmer and faster to navigate by orienting the first screen around the operator's current learning move instead of presenting multiple learning tools at equal weight.

Requirements:
- Use Experience Designer guidance to prioritize:
  - resuming an active learning session when one exists
  - starting the featured next concept when no session is active
  - finding and opening a concept from the concept library
- Use UI Designer guidance to strengthen hierarchy across `Learn next`, `Concepts`, and `Profile` without changing the existing top-level grid or visual identity
- Keep the primary learning action visually dominant and move secondary explanation or actions behind progressive disclosure where appropriate
- Reduce repeated headings, nested bordered containers, and same-weight action rows that make the Learning tab feel visually dense
- Preserve all existing learning capabilities, private file-backed state, and routing between recommendations, sessions, concept management, build-to-learn, and profile editing
- Preserve keyboard-operable native Streamlit controls and readable contrast

Constraints:
- Do not add new learning features or content types
- Do not change the existing brand palette, typography, top-level navigation model, or layout grid
- Prefer native Streamlit components; do not add a third-party UI dependency for this pass
- Keep R74 learning-agent and concept-management behavior intact

Validation:
- Add focused deterministic coverage for the Learning tab hierarchy and routing helpers
- Run `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- Perform a lightweight post-implementation usability and UI review for clarity, scanability, keyboard-operable controls, and preservation of the primary workflows

Output:
- A calmer Learning tab with a clear current/next learning action
- Existing learning workflows preserved
- Validation and post-implementation review results
- Experience and UI guidance: `projects/os-control-panel/product/learning-tab-ui-guidance-R75.md`
- Active learning sessions now take precedence over unfinished helper drafts
- Featured recommendation now exposes one primary action and progressively discloses secondary routes
- Other recommendations now use compact rows instead of repeated nested cards
- Validation: 176/176 unit tests and 184/184 project eval checks passed
- Live Streamlit socket smoke was blocked by the managed sandbox's port-binding restriction

## Task 192: Define and implement the shared bounded-agent runtime

Type: Feature Task
Status: DONE
Requirement: R76

Goal:
Create one runtime contract for live model-backed OS roles.

Requirements:
- Compose runtime instructions from canonical role and workflow documents
- Add explicit maximum-step, retry, timeout, and hand-back controls
- Preserve typed structured outputs
- Record inspectable run metadata and completion state

Validation:
- Add focused unit coverage for prompt composition, limits, retries, and trace persistence

Output:
- Superseded by the genuine OpenAI Agents SDK runtime in `src/agents_runtime/`
- All model-backed roles route through `Runner`; the former custom loop and `src/agent_runtime.py` have been removed

## Task 193: Add risk-rated project-context tools for live roles

Type: Feature Task
Status: DONE
Requirement: R76

Goal:
Let bounded agents dynamically gather relevant project context through a small standardized tool surface.

Requirements:
- Add read-only tools for project summary, requirements, tasks, memory, rules, and active workflow state
- Add tool descriptions and risk ratings
- Limit tools by role
- Keep write and execution actions behind human approval

Validation:
- Confirm unknown or disallowed tools are rejected
- Confirm tool output is bounded and traceable

Output:
- Role-allowlisted project summary, requirements, tasks, memory, rules, and active-workflow readers
- High-risk write and execution definitions remain approval-gated and unavailable

## Task 194: Add layered live-agent guardrails and human hand-back

Type: Feature Task
Status: DONE
Requirement: R76

Goal:
Protect live turns from known input, output, and execution failures.

Requirements:
- Add relevance, prompt-injection, sensitive-data, and input-length checks
- Add output grounding and structured completion checks
- Add clear human-hand-back behavior for blocked or repeatedly failing runs
- Assign tool risk levels and approval requirements

Validation:
- Add positive and negative guardrail cases

Output:
- Input length, relevance, prompt-injection, and sensitive-data checks
- Structured output, unsupported action-claim, and tool-authorization checks
- Retry, timeout, step-budget, and explicit human-hand-back behavior

## Task 195: Add bounded live manager review to Orchestrator

Type: Feature Task
Status: DONE
Requirement: R76

Goal:
Support manager-style interpretation without replacing deterministic routing authority.

Requirements:
- Keep deterministic routing as the policy source of truth
- Let Workflow Review mode request a bounded live manager interpretation
- Restrict manager output to known roles and non-mutating recommendations
- Surface agreement or disagreement with deterministic routing

Validation:
- Confirm live manager review cannot mutate state or name unsupported roles

Output:
- User-triggered live Workflow Review with typed known-role output
- Deterministic recommendation remains visible and authoritative

## Task 196: Add trace grading and live-agent quality evaluation

Type: Validation Task
Status: DONE
Requirement: R76

Goal:
Evaluate the quality and safety of real live-agent runs rather than only mocked workflow mechanics.

Requirements:
- Persist model-call, tool-use, guardrail, completion, and hand-back trace events
- Add deterministic trace-quality grading
- Add a live eval runner that can grade captured traces and optionally execute configured live cases
- Cover question relevance, grounding, tool discipline, completion, and approval compliance

Validation:
- Demonstrate that clean and intentionally invalid traces receive different grades

Output:
- Redacted JSONL traces for model, tool, guardrail, completion, error, and hand-back events
- `tools/live_eval_runner.py` grades captured traces
- Clean and incomplete trace fixtures receive different grades

## Task 197: Validate and close R76

Type: Validation Task
Status: DONE
Requirement: R76

Goal:
Verify the completed bounded live-agent operating model and close its product state.

Validation:
- Run the complete project validation baseline
- Run the live-agent trace evaluation path
- Confirm existing PM, Experience Designer, UI Designer, learning-agent, Orchestrator, QA, Architect, and Engineer paths remain intact

Output:
- Full project validation: 203/203 passing
- Real bounded PM turn and captured-trace evaluation: 1/1 passing
- R76 closed as DONE

## Task 198: Build the Operations dashboard read model

Type: Feature Task
Status: DONE
Requirement: R77

Goal:
Aggregate existing trace, workflow, quality, implementation, approval, and learning data into one deterministic dashboard read model.

Requirements:
- Summarize live runs from redacted traces, including legacy partial traces
- Aggregate per-role performance and per-tool usage
- Aggregate project workflow health, quality, oversight, learning, and activity signals
- Keep all source data read-only

Validation:
- Add focused aggregation tests for clean, failed, hand-back, tool-using, and legacy runs

Output:
- Added `src/operations_dashboard.py` for trace, role-performance, and tool-usage aggregation
- Added `operations_dashboard_snapshot()` to join operational and file-backed workspace state

## Task 199: Add Agent Operations, Quality, and Performance dashboards

Type: Feature Task
Status: DONE
Requirement: R77

Goal:
Make live-agent behavior and reliability inspectable across roles and projects.

Requirements:
- Add recent run inspection with project and role filters
- Add trace quality and failure signal summaries
- Add per-role completion, hand-back, retry, step, and tool metrics

Validation:
- Confirm empty and mixed trace histories render without failure

Output:
- Added filtered run inspection, trace-quality summary, and per-role performance comparison

## Task 200: Add Workflow Health and Human Oversight dashboards

Type: Feature Task
Status: DONE
Requirement: R77

Goal:
Show where work is moving, blocked, stale, or waiting for a human decision.

Requirements:
- Summarize requirements, tasks, approvals, clarifications, routed findings, and active implementations
- Surface current pending approvals and approval-gated high-risk capabilities
- Preserve existing approval actions in Inbox rather than duplicating mutations

Validation:
- Confirm project filters and attention counts match file-backed workflow state

Output:
- Added project workflow-health comparison and read-only human-oversight views
- Existing Inbox remains the mutation surface for approval decisions

## Task 201: Add Tool Usage, Learning Progress, and System Activity dashboards

Type: Feature Task
Status: DONE
Requirement: R77

Goal:
Expose capability usage, learning movement, and a unified operational timeline.

Requirements:
- Summarize tool calls, roles, failures, and unused registered tools
- Reuse concept and learning-session state for progress signals
- Merge recent agent-run and workflow events into a chronological activity view

Validation:
- Confirm dashboards handle missing tools, no active learning session, and projects without activity

Output:
- Added registered/unused/denied tool comparison
- Added learning-state and active-session summary
- Added merged live-agent and workflow activity timeline

## Task 202: Validate and close R77

Type: Validation Task
Status: DONE
Requirement: R77

Goal:
Verify all eight dashboards and close the requirement.

Validation:
- Run the complete project validation baseline
- Smoke-test the Streamlit Operations surface
- Confirm existing Workspace, Learning, Open Project, Inbox, Create Project, and project-detail flows remain intact

Output:
- Full project validation: 210/210 passing
- Operations AppTest: eight tabs, eight data tables, zero exceptions
- Local Streamlit endpoint: HTTP 200
- Added visible board descriptions and hover help for every Operations table column
- Post-description validation: 222/222 passing
- R77 closed as DONE

## Task 203: Define all eight executable eval contracts

Type: Feature Task
Status: DONE
Requirement: R78

Goal:
Create reusable evaluators and deterministic fixtures for output quality, tool selection, workflow, memory, safety, cost, latency, and reliability.

Validation:
- Confirm every eval type has a passing fixture and at least one negative threshold test

Output:
- Added `src/eval_framework.py`, `evals/eval_cases.json`, and an eight-dimension capability runner

## Task 204: Capture cost and latency evidence in live-agent traces

Type: Feature Task
Status: DONE
Requirement: R78

Goal:
Record token usage, estimated model spend, model-call duration, tool duration, and end-to-end run duration without breaking legacy trace readers.

Validation:
- Confirm measured values reach both the returned run result and persisted trace

Output:
- Captured tokens, estimated cost, model duration, tool duration, and total duration with legacy compatibility

## Task 205: Complete tool-selection and memory evaluation

Type: Validation Task
Status: DONE
Requirement: R78

Goal:
Detect missing, unnecessary, unauthorized, or misordered tools and verify required memory recall, stale-memory rejection, and deliberate memory retrieval.

Validation:
- Add positive and negative evaluator cases

Output:
- Added exact, missing, unnecessary, unauthorized, ordering, recall, stale-memory, and retrieval checks

## Task 206: Add Eval Coverage to Operations

Type: Feature Task
Status: DONE
Requirement: R78

Goal:
Explain which eval types exist, which projects and agents they cover, and what each measurement checks.

Validation:
- Confirm the board has a description and hover help for every column

Output:
- Added the ninth Operations board with complete project, agent, eval-type, and implementation mapping

## Task 207: Integrate capability evals into the project runner

Type: Validation Task
Status: DONE
Requirement: R78

Goal:
Run all eight eval dimensions alongside unit and workflow scenario coverage.

Validation:
- Confirm one command reports the combined total and fails when any capability eval fails

Output:
- Main project runner now executes unit, workflow scenario, and capability eval layers

## Task 208: Validate and close R78

Type: Validation Task
Status: DONE
Requirement: R78

Goal:
Run focused, full-suite, and UI smoke validation, then record the final evidence.

Output:
- Focused validation: 21/21
- Capability evals: 8/8
- Full project validation: 244/244
- Operations AppTest: nine boards, nine data tables, zero exceptions
- R78 closed as DONE

## Task 212: Build a normalized eval-case inspection catalog

Type: Feature Task
Status: DONE
Requirement: R79

Goal:
Read existing JSON, replay-backed, scenario, and code-defined eval cases into one read-only inspection model.

Validation:
- Confirm every evaluated project contributes cases and all eight eval types remain represented

Output:
- Added a 57-case catalog spanning every evaluated project and all eight eval types

## Task 213: Add Eval Coverage case drill-down

Type: Feature Task
Status: DONE
Requirement: R79

Goal:
Add project and eval-type filters, case selection, expected-behavior details, source details, and a collapsed full-payload inspector.

Validation:
- Confirm the Operations board renders with empty and populated filters

Output:
- Added project and eval-type filters, case selection, expected/source details, and full-payload inspection

## Task 214: Validate and close R79

Type: Validation Task
Status: DONE
Requirement: R79

Goal:
Run focused, full-suite, and Streamlit interaction validation and record the final evidence.

Output:
- Focused validation: 13/13
- Full project validation: 246/246
- Streamlit filtered-case interaction: zero exceptions
- R79 closed as DONE

## Task 218: Add complete agent-role quality coverage

Type: Feature Task
Status: DONE
Requirement: R80

Goal:
Preserve all configured agent roles in quality and performance aggregation even before live traces exist.

Validation:
- Confirm all eight roles appear with correct execution and evidence states

Output:
- All eight configured roles remain visible with execution-mode and evidence-state labels

## Task 219: Clarify no-trace states in Operations

Type: Feature Task
Status: DONE
Requirement: R80

Goal:
Distinguish missing live evidence from failed quality and avoid zero-percent completion labels for roles with no runs.

Validation:
- Confirm project and role tables use explicit no-trace/no-run labels

Output:
- Added `NO LIVE TRACES`, `No captured live runs`, `Uses separate validation path`, and `No runs` states

## Task 220: Validate and close R80

Type: Validation Task
Status: DONE
Requirement: R80

Goal:
Run focused, full-suite, and Streamlit rendering validation.

Output:
- Focused validation: 17/17
- Full project validation: 249/249
- Streamlit role-table render: two eight-row tables, zero exceptions
- R80 closed as DONE

## Task 221: Define the Learning Agent deployment phases

Type: Product Task
Status: DONE
Requirement: R81

Goal:
Define the invite-only pilot, database-backed beta, and production deployment phases with explicit exit criteria.

Output:
- Added `projects/learning-agent/deployment-phases.md`
- Explicitly treated `projects/learning-agent` as a hosted wrapper around canonical learning behavior in `os-control-panel`

## Task 222: Extract the standalone hosted Learning Agent

Type: Feature Task
Status: DONE
Requirement: R81

Goal:
Expose only the external Learning Agent experience through a dedicated hosted wrapper Streamlit entry point.

Output:
- Added `projects/learning-agent/src/app.py` using the external V2 release profile
- Kept learning behavior delegated to `projects/os-control-panel`

## Task 223: Add hosted authentication and user isolation

Type: Feature Task
Status: DONE
Requirement: R81

Goal:
Add OIDC identity, invite allowlisting, per-user learning storage, and per-user agent traces while preserving local behavior.

Validation:
- Confirm two users cannot read or overwrite each other's profile or traces

Output:
- Added OIDC and local authentication modes, an optional invited-email allowlist, and stable hashed tenant identifiers
- Scoped hosted learning profiles, sessions, concept state, notes, build-to-learn records, and agent traces by authenticated user
- Preserved the existing local private-data and trace paths when no hosted user context is active
- Added isolation tests covering independent learner profiles and agent traces

## Task 224: Add deployment packaging

Type: Feature Task
Status: DONE
Requirement: R81

Goal:
Package the hosted app for Railway and Render with Docker, health checks, persistent storage, and secret configuration.

Output:
- Added Dockerfile, start script, Railway configuration, Render blueprint, Streamlit configuration, and secrets template

## Task 225: Validate pilot deployment readiness

Type: Validation Task
Status: DONE
Requirement: R81

Goal:
Run isolation, app-render, project-eval, and container-build checks and record any credential-dependent steps that remain.

Validation:
- Hosted Learning Agent AppTest passed with zero exceptions and no Operations surface
- Targeted hosted/runtime suite passed: 226/226
- Full project eval passed: 262/262
- Python compilation, shell syntax, and diff whitespace checks passed
- Docker is not installed in the local environment, so the image build remains to be exercised by Railway or Render
- Live OIDC sign-in, persistent-volume restart/redeploy, DNS, and external smoke testing remain credential-dependent deployment checks

Output:
- Pilot application and deployment package are ready to connect to a single-replica Railway or Render service

## Task 228: Polish the hosted Learning Agent surface for invited external learners

Type: Feature Task
Status: DONE
Requirement: R81

Goal:
Tighten the hosted wrapper so invited learners immediately understand what the product is, how the guided flow works, and what the privacy and pilot boundaries are.

Validation:
- Confirm the hosted sign-in and invite-only states explain the product and the pilot boundary clearly
- Confirm the hosted wrapper introduces the profile -> learning plan -> learn next flow without exposing wider OS language
- Confirm privacy and support/contact guidance remain visible in the hosted shell
- Confirm the wrapper still delegates canonical learning behavior to `projects/os-control-panel`

Output:
- Workflow artifact: `projects/os-control-panel/product/hosted-learning-agent-pilot-polish-workflow-R81.md`
- Access strategy: `projects/os-control-panel/product/hosted-learning-agent-pilot-access-strategy-workflow-R81.md`
- Hosted wrapper now includes clearer learner-facing shell copy and pilot framing
- Hosted wrapper tests cover the new onboarding shell

## Task 229: Add the hosted pilot pre-launch checklist and operator runbook

Type: Product Task
Status: DONE
Requirement: R81

Goal:
Give the external Learning Agent pilot a concrete launch discipline so the wrapper can be provisioned, smoke-tested, and invited safely without relying on memory or scattered notes.

Validation:
- Confirm the hosted project includes an explicit pre-launch checklist
- Confirm the runbook covers env vars, OIDC, invite allowlisting, persistent storage, smoke tests, and invite readiness
- Confirm the hosted README points operators to the runbook

Output:
- Workflow artifact: `projects/os-control-panel/product/hosted-learning-agent-launch-readiness-workflow-R81.md`
- Added `projects/learning-agent/pilot-launch-checklist.md`
- Tightened `projects/learning-agent/README.md` with launch-readiness references

## Task 230: Add a hosted pilot preflight validator

Type: Feature Task
Status: DONE
Requirement: R81

Goal:
Reduce operator error before deployment by adding a machine-checkable preflight step for the invite-only hosted pilot configuration.

Validation:
- Confirm the hosted project includes a runnable preflight validator
- Confirm the validator checks the required invite-only pilot env vars and boundary assumptions
- Confirm the validator distinguishes hard failures from softer warnings
- Confirm the hosted README tells operators how to run it before inviting learners

Output:
- Workflow artifact: `projects/os-control-panel/product/hosted-learning-agent-preflight-validator-workflow-R81.md`
- Added `projects/learning-agent/src/preflight.py`
- Added hosted preflight tests and README/checklist references

## Task 231: Add a top-level hosted pilot launch plan checklist

Type: Product Task
Status: DONE
Requirement: R81

Goal:
Give the team one simple launch-plan view that shows the full path to real pilot users, current status, and the next execution gate.

Validation:
- Confirm the hosted project includes a top-level launch plan checklist
- Confirm the checklist distinguishes launch phases from the lower-level pre-launch runbook
- Confirm the hosted README points operators to the launch plan first and the detailed runbook second

Output:
- Workflow artifact: `projects/os-control-panel/product/hosted-learning-agent-launch-plan-workflow-R81.md`
- Added `projects/learning-agent/pilot-launch-plan.md`
- Tightened `projects/learning-agent/README.md` with launch-plan-first guidance

## Task 232: Clean duplicate task IDs and restore workflow/architecture hygiene after pilot launch

Type: Product Task
Status: BACKLOG
Requirement: R82

Goal:
After the first hosted Learning Agent pilot launches, clean duplicate task identifiers and tighten any workflow or architectural drift that the pilot deliberately left for later.

Validation:
- Confirm duplicate task identifiers are removed from `projects/os-control-panel/product/tasks.md`
- Confirm Orchestrator and Architect outputs remain trustworthy after the cleanup
- Confirm the cleanup is recorded as evolutionary hygiene rather than a broad redesign

Output:
- Post-pilot workflow and architecture hygiene pass for task identity and launch-deferred cleanup

Treat this as workflow and architecture hygiene rather than as a broad redesign driver.

## Task 209: Define concept families and hierarchy-aware learning progression

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make concept hierarchy a first-class part of the learning journey so parent concepts can scaffold child concepts instead of leaving the learning layer as a mostly flat concept list.

Validation:
- Define initial parent-level concept families and child mappings for the current learning catalog
- Confirm the hierarchy is used as learning structure, not just a decorative UI layer

Output:
- Product artifact: `projects/os-control-panel/product/concept-hierarchy-learning-initiative-R74.md`
- Workflow artifact: `projects/os-control-panel/product/concept-hierarchy-workflow-R74.md`
- Initial concept-family model implemented in the learning layer
- Current families defined:
  - `Evals`
  - `Context and capability systems`
- Family placement now distinguishes gateway and specialized concepts for the current catalog

## Task 210: Make recommendations hierarchy-aware

Type: Feature Task
Status: BACKLOG
Requirement: R74

Goal:
Update recommendation logic so the OS can prefer parent-first progression where appropriate and explain why a child concept is being surfaced now.

Use this task when hierarchy-aware recommendation behavior is being actively refined.

Validation:
- Confirm parent concepts are recommended ahead of children where the family structure makes that the better learning path
- Confirm child concepts can still surface when the user already has enough parent context

Output:
- Hierarchy-aware recommendation behavior in the learning layer

## Task 211: Make tutoring and concept pages hierarchy-aware

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Let the tutoring agent and concept surfaces use concept-family structure directly so the learner can see where a concept sits, how it relates to siblings, and whether it is broader or narrower than nearby concepts.

Validation:
- Confirm live tutoring comparisons explicitly reference family structure when helpful
- Confirm concept and session surfaces expose hierarchy cleanly without flattening the journey back into a long taxonomy page
- Confirm concept-page navigation is driven by concept-family hierarchy rather than status buckets

Output:
- Hierarchy-aware tutoring and concept-surface behavior
- Workflow artifact: `projects/os-control-panel/product/hierarchy-based-learning-navigation-workflow-R74.md`
- Concept-page navigation now follows concept families and nested concept hierarchy
- Session and concept hierarchy sections now share one family-tree model instead of drifting apart

## Task 212: Define the V2 external learning release profile

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Define a clean external V2 release profile that focuses the product on a curated concept-learning catalog for the external release.

Validation:
- Confirm the external profile clearly excludes reflection and build-to-learn from the user-facing product
- Confirm the internal profile preserves those capabilities for future V3 work

Output:
- Product artifact: `projects/os-control-panel/product/v2-external-learning-release-mode-R74.md`
- Release-profile decision for:
  - `internal_v2`
  - `external_v2`
- Outcome captured: use a small explicit release profile seam instead of scattered long-lived feature flags

## Task 213: Gate reflection and build-to-learn behind the V2 release profile

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Hide reflection and build-to-learn surfaces from the external V2 release without deleting the broader internal capability.

Validation:
- Confirm Workspace does not show reflection in external V2 mode
- Confirm Learning does not show `Builds` or build actions in external V2 mode
- Confirm internal V2 mode still exposes the current broader surfaces

Output:
- Release-profile-aware UI and routing behavior for reflection and build-to-learn
- External V2 mode now hides:
  - Workspace reflection helper
  - Learning `Builds` navigation
  - build-to-learn actions in recommendations and concept pages
  - build-to-learn progression as a tutoring next move

## Task 214: Complete the curated external V2 concept catalog

Type: Feature Task
Status: BACKLOG
Requirement: R74

Goal:
Define the curated external V2 concept catalog, identify any missing concepts, and implement them in the OS before release so the tutoring experience can teach a rich built concept set.

- Significant catalog work is already delivered.
- This task should only add catalog work that materially improves the external tutoring surface.

Validation:
- Confirm the external V2 catalog is explicit and finite
- Confirm any concept exposed in the external V2 experience has real OS implementation support
- Confirm tutoring and concept pages continue to support implementation walkthroughs for the curated catalog

Output:
- Curated external V2 concept catalog and gap-closure plan for missing concepts
- Product artifact: `projects/os-control-panel/product/external-v2-concept-catalog-R74.md`
- Workflow artifact: `projects/os-control-panel/product/external-v2-catalog-expansion-workflow-R74.md`
- Approved governing concept truth for runtime trial: `projects/os-control-panel/product/concept-governing-truth-R74.md`

## Task 215: Expand the evals family into a complete external V2 learning track

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Implement the missing eval-family concepts so the external V2 release can teach `Evals` as a serious concept system rather than a partial cluster.

Validation:
- Confirm the learning layer includes:
  - `Tool Selection Evals`
  - `Workflow Evals`
  - `Memory Evals`
  - `Safety Evals`
  - `Cost Evals`
  - `Latency Evals`
  - `Reliability Evals`
- Confirm each concept has hierarchy placement, implementation anchors, and tutoring support

Output:
- Completed external V2 eval-family concept set
- Workflow artifact: `projects/os-control-panel/product/evals-family-workflow-R74.md`
- Validation: `.venv/bin/python -m unittest projects.os-control-panel.tests.unit.test_workspace` passed (`209 tests`)
- Validation: `.venv/bin/python projects/os-control-panel/tools/scenario_eval_runner.py` passed (`14/14`)

## Task 216: Add the missing family gateways for external V2

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Add the missing family-level concepts that make the external V2 learning journey feel like a map of AI agent systems rather than a handful of terms.

Validation:
- Confirm the learning layer includes first-class gateway concepts for:
  - `Agents`
  - `Workflows`
  - `Tool use`
  - `Function calling`
- Confirm each gateway concept has meaningful family structure and implementation grounding

Output:
- New family gateways for workflow systems and capability access
- Implemented gateways:
  - `Agents`
  - `Workflows`
  - `Tool use`
  - `Function calling`

## Task 217: Split context/capability structure for external V2

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Refine the current mixed `Context and capability systems` family into cleaner learning families so the catalog teaches context, retrieval, and capability access without blurring them together.

Validation:
- Confirm `MCP` no longer relies on a muddled family placement
- Confirm the catalog has clearer family structure for:
  - context and knowledge
  - tool and capability access
- Confirm the tutoring and hierarchy views stay coherent after the split

Output:
- Cleaner external V2 family structure for context/knowledge vs tool/capability concepts
- `MCP` moved into `Tool and capability access`
- `RAG` and retrieval concepts now live under `Context and knowledge systems`

## Task 218: Make the external V2 learning journey profile-first and agent-owned

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Shift the external V2 learning workflow from a concept browser into an agent-owned personalized learning plan that starts from the learner profile.

Validation:
- Confirm `Profile` is the first Learning tab in the external V2 surface
- Confirm the profile captures the learner's current understanding of AI Builder OS
- Confirm implementation walkthroughs can use that OS-understanding level to adapt context depth
- Confirm the `Concepts` tab no longer behaves like a free-roam map and instead shows the agent-owned current plan step with broader family context

Output:
- Workflow artifact: `projects/os-control-panel/product/profile-first-agent-plan-workflow-R74.md`
- External V2 Learning navigation now starts with `Profile`
- External V2 `Concepts` now renders an agent-owned personalized learning plan instead of a browseable concept map

## Task 226: Tighten the external V2 learning flow around profile, plan, and active learning

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Tighten the external V2 learning experience so the learner can move through a clearer agent-owned flow: lightweight structured profile setup, a clean forward-only learning plan, and a simpler active learning surface.

Validation:
- Confirm the learner profile uses bounded option-based answers instead of open-ended prompts
- Confirm PM guidance shaped the profile option semantics and UX/UI guidance shaped the control types and layout
- Confirm the `Concepts` tab is renamed to `Learning plan`
- Confirm the `Learning plan` page shows progress and current position in the plan without exposing concept hierarchy, related concepts, or free-roam concept management
- Confirm the learner can move from `Learning plan` into `Learn next` through the current plan step only
- Confirm the `Learn next` active-session surface removes the `Capture what is clearer now` section
- Confirm the `Learn next` active-session surface includes a direct `Mark learned` action and stays visually focused on teaching, clarification, implementation grounding, and completion

Output:
- Workflow artifact: `projects/os-control-panel/product/external-v2-learning-flow-tightening-workflow-R74.md`
- External V2 learning profile now uses structured options and lighter input controls
- External V2 `Learning plan` is now the named plan surface and no longer behaves like a concept detail page
- External V2 `Learn next` no longer asks for a written recap before continuing and supports direct concept completion

## Task 227: Generate an explicit teaching strategy from profile before live tutoring

Type: Feature Task
Status: DONE
Requirement: R74

Goal:
Make profile-driven personalization inspectable and more obviously meaningful by having the learning agent derive an explicit teaching strategy before teaching, clarifying, or explaining implementation.

Validation:
- Confirm the learning runtime derives a structured teaching strategy from the saved learner profile
- Confirm the teaching strategy is passed into live teaching, clarification, and implementation turns
- Confirm the teaching strategy explicitly covers explanation entry point, explanation order, OS-context depth, example style, and coaching style
- Confirm profile changes can change the generated teaching strategy without changing the governing concept truth

Output:
- Workflow artifact: `projects/os-control-panel/product/profile-derived-teaching-strategy-workflow-R74.md`
- Runtime teaching strategy generation now sits between profile loading and live tutoring turns
- Live tutoring payloads now include an explicit teaching strategy alongside governing truth and concept context

## Task 233: Add a first-pass project state and next-step orientation layer

Type: Feature Task
Status: DONE
Requirement: R83

Goal:
Make the project-detail page easier to operate by showing the current workflow state, the best next move, and the most relevant section before the operator has to choose where to go.

Requirements:
- Add a lightweight project-state panel near the top of the project-detail page
- Reuse the existing deterministic orchestrator recommendation as the source of truth for the suggested next move
- Show concise grounded project signals including:
  - open approvals
  - PM clarifications
  - active agent threads
  - active implementation runs
  - latest quality status
- Let the operator jump directly into the suggested project section from that panel

Constraints:
- Do not create a second workflow model beside the real OS workflow state
- Do not expand this pass into deeper execution controls
- Keep the UI concise and project-level rather than turning it into an operations dashboard

Validation:
- Confirm the project-detail page renders the new orientation layer without exceptions
- Confirm the suggested section uses existing workflow state and recommendation logic
- Run a syntax check on the updated Streamlit app module

Output:
- First-pass project orientation layer inside the project-detail page
- Product truth extended with `R83`

## Task 234: Add the GitHub publication policy gate

Type: Feature Task
Status: DONE
Requirement: R84

Goal:
Create a reusable policy layer that reviews GitHub publication payloads before any draft can enter the external-publication workflow.

Validation:
- Confirm canonical requirement summaries are allowed
- Confirm private paths, runtime state, trace files, local temp paths, secrets, and private-planning language are blocked
- Confirm low-risk contact information is redacted

Output:
- Added `projects/os-control-panel/src/github_publication.py`
- Added policy unit coverage

## Task 235: Add GitHub delivery draft approvals

Type: Feature Task
Status: DONE
Requirement: R84

Goal:
Let the OS prepare GitHub issue, PR-description, and eval-summary drafts from canonical or sanitized OS evidence, then send safe drafts through the existing Inbox approval flow.

Validation:
- Confirm a requirement can create a GitHub issue-draft approval
- Confirm approval review shows target, policy status, title, body, and external-write boundary
- Confirm approving the draft publishes to GitHub when credentials are configured

Output:
- Added GitHub publication request helpers in the workspace layer
- Added Delivery UI actions for GitHub publication drafts
- Added Inbox preview and approval labels for GitHub publication drafts

## Task 236: Register GitHub publishing as an approval-gated capability

Type: Feature Task
Status: DONE
Requirement: R84

Goal:
Make the eventual GitHub write action visible as a high-risk capability that must remain behind explicit approval.

Validation:
- Confirm Operations includes `publish_to_github` among high-risk approval-gated capabilities

Output:
- Registered `publish_to_github` in the bounded runtime tool catalog as a blocked high-risk write capability

## Task 237: Publish approved GitHub drafts end to end

Type: Feature Task
Status: DONE
Requirement: R84

Goal:
When a human approves a policy-passing GitHub publication draft, publish it to GitHub and write the resulting GitHub URL back to the approval record.

Validation:
- Confirm approved issue drafts call the GitHub issue API
- Confirm approved eval-summary drafts publish as GitHub issues
- Confirm approved PR-description drafts update the open PR for the current branch when one exists
- Confirm failed GitHub configuration or API calls leave the approval open
- Confirm the Inbox reports the published GitHub URL after success

Output:
- Added credential-driven GitHub REST publishing
- Wired GitHub publication approval to publish on approval
- Added publish success and failure unit coverage

## Task 238: Add release delivery approval gate

Type: Feature Task
Status: DONE
Requirement: R85

Goal:
Replace manual-only GitHub drafting with an OS-native completion gate that prepares one release approval bundle when a requirement is ready to become DONE.

Validation:
- Confirm manual `DONE` transitions create a release delivery approval and keep the requirement open
- Confirm completed sprint implementation pauses for release delivery approval
- Confirm the approval contains implementation, quality, GitHub issue, commit message, included-file, and excluded-file details
- Confirm approval marks the requirement DONE and records GitHub/git delivery outputs

Output:
- Added release delivery approval creation from requirement completion
- Added release delivery execution on approval
- Added git change planning with private/runtime exclusions
- Added Inbox review support for release delivery bundles
- Added focused release delivery tests

## Task 239: Add UI runtime as explicit workflow truth

Type: Feature Task
Status: DONE
Requirement: R86

Goal:
Make the intended UI runtime part of canonical OS workflow truth so the system can distinguish Streamlit-native work from explicitly selected web-app work.

Requirements:
- Add a bounded UI runtime field that supports:
  - `streamlit`
  - `web_app`
- Default the runtime to `streamlit`
- Support choosing the runtime at the project level and overriding it at the requirement level when needed
- Persist the runtime in a place that current workflow surfaces and agents can reliably read

Constraints:
- Keep the first version simple; do not expand into multiple frontend framework enums yet
- Do not hide the runtime choice inside prompts or undocumented metadata

Validation:
- Confirm newly created projects default to `streamlit`
- Confirm a project or requirement can explicitly select `web_app`
- Confirm the saved runtime can be read back consistently in workflow surfaces

Output:
- Canonical UI runtime field in OS workflow truth
- Default runtime behavior for existing and new projects
- Project-level runtime persisted in `product/ui-runtime.json`
- Requirement-level runtime override captured in `product/requirements.md`

## Task 240: Make UI Designer and Engineer runtime-aware

Type: Feature Task
Status: DONE
Requirement: R86

Goal:
Teach the UI Designer and Engineer paths to preserve current Streamlit behavior by default while intentionally switching to web-app behavior when the runtime requires it.

Requirements:
- Keep current Streamlit-oriented behavior as the default for UI Designer and Engineer
- When runtime is `web_app`, route UI Designer and Engineer prompts, guidance, and implementation assumptions through web-app behavior instead of Streamlit assumptions
- Make the selected runtime visible in the relevant UI/agent context so the operator can see what mode the work is in

Constraints:
- Do not create a separate frontend agent role
- Do not let `web_app` behavior leak into ordinary Streamlit projects

Validation:
- Confirm Streamlit projects continue to behave as before
- Confirm explicitly selected `web_app` projects or requirements switch the active assumptions for UI Designer and Engineer

Output:
- Runtime-aware agent behavior for UI Designer and Engineer
- Visible runtime context in the project workflow
- Engineer implementation prompts now read the effective runtime profile
- UI Designer prompts and operator copy now stay aligned with the selected runtime

## Task 241: Vendor frontend-only web-app capability into a local OS plugin

Type: Feature Task
Status: DONE
Requirement: R86

Goal:
Bring in a bounded local plugin capability so explicitly selected `web_app` work can use frontend-focused guidance without making the whole OS dependent on a generic external plugin.

Requirements:
- Create an OS-local plugin or equivalent local capability bundle for web-app work
- Vendor only the frontend-focused skills needed for the first slice:
  - frontend app builder
  - frontend testing/debugging
  - React best practices
  - shadcn best practices
- Exclude Stripe and database capabilities from this first integration slice
- Make the plugin available only when runtime-aware routing says it should be used

Constraints:
- Keep the vendored capability local and reviewable
- Do not import unused payment or database capability in the first pass
- Do not make this plugin mandatory for Streamlit work

Validation:
- Confirm the local plugin installs or resolves correctly in the Codex environment
- Confirm runtime-aware web-app work can access the vendored frontend capability
- Confirm Streamlit work remains unaffected when the plugin is not selected

Output:
- Local OS-owned frontend capability bundle
- Bounded plugin usage for explicit web-app work
- Repo-owned `web-app-frontend` capability bundle added under `agent/capabilities/`
- Live agents can inspect the runtime capability profile through a bounded read-only tool

## Task 242: Add project type capability profiles

Type: Feature Task
Status: DONE
Requirement: R86

Goal:
Turn the existing runtime choice into a first-class project type capability profile that controls project creation, preview, release expectations, and deployment provider defaults.

Requirements:
- Present the runtime choice as project type in the operator UI
- Preserve the selected project type through live PM discovery and reviewed-draft creation
- Scaffold web app projects with a Vercel-compatible Next.js starter
- Preview web app projects through `npm run dev`
- Add project-type capability guidance to Engineer implementation prompts
- Add project type, deployment provider, and release expectation to release delivery approvals
- Add web-app capability-pack guidance from the Vercel plugin concepts
- Add web-app release readiness checks for package scripts, route entry, shadcn/ui config, Vercel config, env documentation, browser verification, and preview deployment verification

Constraints:
- Keep Vercel as a capability behind `web_app`, not as a new dashboard
- Do not change existing Streamlit project defaults
- Keep the persisted `product/ui-runtime.json` shape compatible with existing projects
- Do not import payments, database provisioning, or marketplace installation as active behavior until a project explicitly needs them

Validation:
- Confirm live PM project threads preserve `web_app`
- Confirm reviewed-draft creation passes `web_app` to scaffolding
- Confirm web app preview uses `npm run dev`
- Confirm release approvals expose Vercel as the web-app deployment provider
- Confirm Engineer prompts include web-app capability guidance
- Confirm release approvals expose web-app readiness checks

Output:
- Project runtime capability profiles
- Web app/Next.js scaffold files
- Runtime-aware local preview routing
- Project-type UI wording
- Release approval deployment capability metadata
- Vercel plugin-derived web-app capability pack
- Web app release readiness checks

## Task 243: Record Vercel preview deployment after web-app release

Type: Feature Task
Status: DONE
Requirement: R86

Goal:
After an approved web-app release pushes to GitHub, look up the matching Vercel deployment for the pushed commit and record the preview URL/status on the release approval.

Requirements:
- Query Vercel deployments after GitHub push for `web_app` releases
- Match deployments by commit SHA and branch
- Support `AI_BUILDER_OS_VERCEL_TOKEN` or `VERCEL_TOKEN`
- Support optional `AI_BUILDER_OS_VERCEL_TEAM_ID`
- Support optional project-specific `AI_BUILDER_OS_VERCEL_PROJECT_<PROJECT_SLUG>` mapping
- Record lookup status, preview URL, deployment id, ready state, inspector URL, and detail on the approval

Constraints:
- Do not fail GitHub/code delivery if Vercel is not configured
- Do not require Vercel for Streamlit projects
- Keep the lookup as release metadata, not as a separate dashboard

Validation:
- Confirm missing Vercel token records `not_configured`
- Confirm Vercel API query uses project, commit SHA, branch, and team id
- Confirm approved web-app releases record Vercel preview metadata

Output:
- Credential-driven Vercel deployment lookup
- Release approval Vercel preview metadata
- Focused Vercel lookup tests

## Task 244: Enforce Railway and Vercel deployment defaults by project type

Type: Feature Task
Status: DONE
Requirement: R87

Goal:
Make deployment provider selection follow the OS project-type model: Streamlit/Python-service projects default to Railway, while Next.js/React web-app projects default to Vercel.

Requirements:
- Set the Streamlit project capability profile default deployment provider to Railway
- Keep the web-app project capability profile default deployment provider as Vercel
- Show the default deployment capability near project type in the project detail surface
- Add Streamlit release readiness checks for Railway-compatible hosted Python service delivery
- Keep Vercel preview lookup scoped to `web_app` releases

Constraints:
- Do not replace Railway with Vercel globally
- Do not add a separate deployment dashboard
- Do not make Streamlit releases perform Vercel lookup

Validation:
- Confirm Streamlit release approvals use Railway as the deployment provider
- Confirm Streamlit release readiness includes Railway checks
- Confirm web-app release approvals and Vercel lookup behavior remain unchanged

Output:
- Project-type deployment defaults
- Railway readiness checks for Streamlit projects
- Visible default deployment capability in project detail
- Focused provider-default tests

## Task 245: Enforce Playwright browser verification before web-app release

Type: Feature Task
Status: DONE
Requirement: R88

Goal:
Make rendered-browser verification mandatory for `web_app` release delivery so Vercel-bound approvals require evidence from a real Playwright run.

Requirements:
- Add a repo-owned Playwright verification runner for web app projects
- Start `npm run dev` locally for the target project
- Open the app in Chromium at desktop and mobile viewports
- Capture screenshots into the project product folder
- Record console errors, page errors, horizontal overflow, and visible interaction click results
- Write structured browser-verification evidence to `product/browser-verification.json`
- Fail web-app release readiness when evidence is missing or failing
- Block web-app release approval creation and approval execution until the evidence passes

Constraints:
- Do not require this gate for Streamlit/Railway releases
- Do not treat Vercel preview lookup as local browser QA
- Keep the verification artifact reviewable and file-backed

Validation:
- Confirm web-app readiness fails without Playwright evidence
- Confirm web-app readiness passes with passing evidence
- Confirm web-app release approval is blocked without passing evidence
- Confirm existing Streamlit/Railway release behavior remains unaffected

Output:
- `tools/verify_web_app.py`
- Browser-verification release gate for web apps
- Product-file browser QA evidence
- Focused Playwright-gate tests

## Task 246: Connect approved Figma references to web app delivery

Type: Feature Task
Status: DONE
Requirement: R89

Goal:
Give Figma-enabled web app projects a bounded, requirement-level design context that agents can read and release delivery can verify.

Requirements:
- Add code-first, Figma-referenced, and Figma-managed project modes
- Store Figma file metadata and requirement-to-frame references in `product/ui-runtime.json`
- Preserve unknown runtime configuration when project type or Figma context changes
- Expose design references through the existing project capability context tool
- Require an approved requirement frame for Figma-enabled web app release delivery
- Show Figma reference metadata in release approval review

Constraints:
- Keep code-first projects unaffected
- Do not store Figma credentials
- Do not add a standalone Figma dashboard
- Do not represent stored references as live connector data
- Do not automate Figma writes in this slice

Validation:
- Confirm runtime and Figma metadata survive round trips
- Confirm agents receive bounded design context
- Confirm approved mappings pass release readiness and missing mappings fail
- Confirm the Streamlit app renders with the new project controls

Output:
- Backward-compatible Figma project configuration
- Requirement-to-frame mapping controls
- Agent-readable design context
- Figma-aware web app release readiness

## Task 247: Make Figma requirement-level and preserve code-first delivery

Type: Feature Task
Status: DONE
Requirement: R90

Goal:
Use Figma where it materially improves design control without making limited MCP capacity block ordinary web-app work.

Requirements:
- Keep Code First as the default design mode
- Treat mappings in Figma Referenced mode as requirement-level opt-ins
- Keep Figma Managed as the strict project-wide design contract
- Cache synced evidence and avoid automatic repeat reads
- Explain all three modes in the project UI
- Preserve mandatory Playwright verification independently of Figma

Validation:
- Confirm an unmapped Figma Referenced requirement follows code-first release readiness
- Confirm a mapped requirement still requires approved matching evidence
- Confirm Code First ignores Figma release gating
- Confirm the updated Electrical Services Website passes Playwright and reaches release approval

Output:
- Requirement-scoped Figma governance
- Clear mode guidance
- Unblocked code-first PM workflow

## Task 248: Put Figma design contracts inside Requirements

Type: Feature Task
Status: DONE
Requirement: R91

Goal:
Make Figma design state understandable and actionable from the requirement that owns it.

Requirements:
- Remove requirement mapping controls from project state
- Keep only project design policy and shared file metadata in project state
- Show design-contract status on each web-app requirement
- Edit frame mapping and approval from the requirement card
- Show cached Figma evidence and screenshot beside requirement execution state
- Preserve design history for completed requirements
- Count mapped requirements on the Requirements page
- Let blocked sprints focus the current requirement

Validation:
- Confirm the Electrical Services Requirements page shows R1 as Figma Ready
- Confirm unmapped requirements show Code First
- Confirm the Figma Mapped metric reflects stored mappings
- Confirm focused tests and Streamlit app rendering pass

Output:
- Requirement-owned Figma workflow
- Visible design-contract lifecycle
- Direct sprint recovery path

## Task 249: Infer and distribute OpenAI runtime decisions

Type: Feature Task
Status: DONE
Requirement: R92

Goal:
Turn product requirement context into a durable, agent-readable OpenAI runtime decision without requiring manual technology selection.

Requirements:
- Infer whether OpenAI runtime capability is needed from requirement intent
- Select Responses API, Agents SDK, Apps SDK, Realtime API, or no runtime
- Record capabilities, credentials, rationale, confidence, and review consequences
- Synchronize metadata on requirement writes
- Expose decisions to all relevant agents through project capability context
- Include the active decision in Engineer implementation instructions
- Show the result read-only within Requirements

Validation:
- Confirm non-AI requirements select no OpenAI runtime
- Confirm research requirements select Responses API with web search
- Confirm multi-agent requirements select Agents SDK
- Confirm ChatGPT app requirements select Apps SDK
- Confirm requirement edits refresh stale decisions
- Confirm the capability context tool returns recorded decisions

Output:
- Automatic OpenAI capability classifier
- Durable requirement runtime contracts
- Agent and UI integration

## Task 250: Add stable project manifests and a private project registry

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Separate project identity from physical repository location.

Architecture contract:
- `product/standalone-project-architecture.md`

Requirements:
- Add a stable project ID and project manifest schema
- Support embedded_showcase, managed_standalone, and attached_repository modes
- Represent visibility, ownership, repository, default branch, and workspace path explicitly
- Store registry state outside the public Git repository
- Auto-discover and register existing embedded projects for backward compatibility

Constraints:
- Do not store credentials or private runtime data in manifests
- Do not require existing projects to migrate immediately
- Reject paths that escape approved registered workspace roots

Validation:
- Confirm stable IDs survive renames and registry reloads
- Confirm embedded projects remain discoverable
- Confirm external paths resolve only through registered entries
- Confirm registry state is excluded from Git

## Task 251: Route the controller and workspace through project locations

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Remove direct repository-root/projects/name assumptions from governed operations.

Requirements:
- Resolve canonical product files through the project registry
- Route control-plane history, hashing, locking, claims, queues and snapshots through stable project IDs
- Route workspace requirements, tasks, previews, QA, capability metadata and implementation commands through resolved project paths
- Preserve runtime-state separation using the stable project ID

Constraints:
- Preserve current embedded behavior
- Do not broaden filesystem access beyond registered project roots
- Do not move lease tokens or operational state into Git

Validation:
- Confirm embedded and external fixtures return equivalent snapshots
- Confirm canonical history is appended in the target repository
- Confirm operational state remains under the configured runtime root
- Confirm path traversal and unregistered paths are rejected

## Task 252: Add standalone repository creation and attachment workflows

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Let operators create or attach independently governed GitHub repositories.

Requirements:
- Extend creation with embedded showcase, create standalone, and attach existing choices
- Capture GitHub owner, repository name, visibility, ownership and default branch
- Scaffold standalone repositories with canonical product files and project manifest
- Represent repository creation, visibility changes, pushes and attachment as approval-gated actions
- Run publication policy checks before external GitHub writes

Constraints:
- Default new standalone repositories to private
- Never place a nested Git repository inside AI Builder OS
- Never record credentials in project truth or public history
- Keep GitHub failure recoverable without corrupting registry state

Validation:
- Confirm private is the default
- Confirm create and attach previews are reviewable before execution
- Confirm failed GitHub actions leave a resumable state
- Confirm attached repositories are validated before registration

## Task 253: Expose repository location and privacy in Streamlit

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Make repository placement, privacy and deployment ownership understandable in the operator UI.

Requirements:
- Show project mode, visibility, repository owner and deployment provider in project summaries
- Add create-standalone and attach-existing flows
- Keep showcase creation as an explicit choice
- Distinguish canonical project files from runtime operational state
- Show external-action approval and failure states

Constraints:
- Public showcase surfaces contain approved portable project metadata only
- Preserve the existing embedded-project workflow
- Keep client showcase permission off by default

Validation:
- Confirm all three project modes render clearly
- Confirm private/client defaults are visible before creation
- Confirm existing projects remain navigable

## Task 254: Package the Codex-native workflow for standalone repositories

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Make the deterministic AI Builder OS workflow reusable from Codex chats opened on standalone repositories.

Requirements:
- Provide a valid Codex plugin bundle containing the workflow skill and deterministic MCP configuration
- Add standalone project AGENTS.md and manifest templates
- Resolve the active project from its manifest or registry entry
- Keep Codex-native execution as the default
- Preserve the explicit API-billed Agents SDK boundary

Constraints:
- Do not require OpenAI API use for normal Codex implementation
- Do not grant a chat write access to unrelated registered repositories
- Keep project-specific canonical history in the target repository

Validation:
- Validate the plugin manifest and skill
- Confirm a standalone fixture can list, inspect, claim and record evidence
- Confirm SDK tools remain explicit opt-in

## Task 255: Add multi-repository migration and isolation verification

Type: Validation Task
Status: DONE
Requirement: R93

Goal:
Prove that standalone projects are isolated without regressing embedded projects.

Requirements:
- Add registry, resolver, manifest, path-safety and runtime-isolation tests
- Add standalone create and attach tests with GitHub calls mocked
- Add control-plane and Codex contract tests for external projects
- Add publishing-policy tests that prevent client/private leakage
- Document migration and recovery procedures

Constraints:
- Do not require live GitHub or Vercel credentials in unit tests
- Keep tests deterministic
- Preserve existing Agents SDK contract coverage

Validation:
- Run focused unit and contract suites
- Validate project structures and plugin manifests
- Run public-content policy checks

## Task 256: Migrate Wright Sparks to a private standalone repository

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Move Wright Sparks source and canonical product history to an independent private repository without changing its public production domain.

Requirements:
- Audit the existing subtree for sensitive or unsuitable public content
- Create a private standalone GitHub repository
- Preserve relevant source and product history
- Register the standalone repository with AI Builder OS
- Connect its release workflow and Vercel project to the new GitHub repository
- Verify preview and production before removing the embedded source

Constraints:
- Do not rewrite AI Builder OS public history unless the audit finds material confidentiality risk
- Keep the current production domain stable
- Public registry and showcase files contain approved portable project metadata only

Validation:
- Confirm the GitHub repository is private
- Confirm local and remote main contain the migrated project
- Confirm Vercel production deploys from the standalone repository
- Confirm the public site remains healthy

## Task 257: Replace embedded Wright Sparks source with a sanitized showcase

Type: Feature Task
Status: DONE
Requirement: R93

Goal:
Retain public demonstration value without keeping the client source project inside AI Builder OS.

Requirements:
- Remove the active embedded Wright Sparks source after standalone production is verified
- Add an explicitly sanitized showcase entry with approved screenshots and outcome summary
- Ensure OS discovery does not treat the showcase as a governed client project
- Document that future implementation and history live in the private repository

Constraints:
- Do not include private repository identifiers, client-only product history, credentials or unpublished requirements
- Do not break other embedded examples
- Do not remove historical public Git objects without a separate confidentiality decision

Validation:
- Confirm public-content policy passes
- Confirm Wright Sparks is governed through the private registered workspace
- Confirm the public OS repository contains only sanitized showcase material

## Task 258: Define the canonical typed PM contract

Type: Feature Task
Status: DONE
Requirement: R94

Goal:
Replace the conflicting PM role definitions with one complete proposal-only contract.

Requirements:
- Define typed discovery, requirement, prioritisation, and task-plan decisions
- Make the canonical PM role file authoritative for Codex, Streamlit, and Agents SDK
- Remove direct product-file writes and silent instruction truncation
- Keep specialist consultations advisory and attributable

Validation:
- Confirm every PM surface exposes the same authority and modes
- Confirm the full role contract reaches SDK agents
- Confirm conflicting legacy write instructions are absent

## Task 259: Add deterministic PM proposal and approval operations

Type: Feature Task
Status: DONE
Requirement: R94

Goal:
Make PM product-state changes reviewable, idempotent, and controller-owned.

Requirements:
- Submit typed proposals with source-state fingerprints
- Approve or reject an exact proposal revision
- Validate stale state, duplicates, status transitions, and task links
- Apply approved requirement, task, status, and intent changes under the project lock
- Record durable proposal and approval history

Validation:
- Confirm rejected and stale proposals do not change canonical files
- Confirm retries do not duplicate product state
- Confirm conversational approval records actor, source, proposal ID, and revision

## Task 260: Connect Codex and Agents SDK PM adapters

Type: Feature Task
Status: DONE
Requirement: R94

Goal:
Let both model backends produce and apply the same PM decision contract.

Requirements:
- Add model-free PM proposal MCP tools for Codex
- Add an approval-gated Agents SDK PM application tool
- Add Engineer and QA consultation tools to PM
- Remove implementation-oriented asset tools from PM
- Preserve resumable SDK approval state and traces

Validation:
- Confirm Codex proposal operations never instantiate the SDK runtime
- Confirm SDK approval resumes the exact pending proposal
- Confirm specialists remain advisory and PM retains decision ownership

## Task 261: Align Streamlit PM and backend usage visibility

Type: Feature Task
Status: DONE
Requirement: R94

Goal:
Make the execution backend and billing boundary clear before PM work starts.

Requirements:
- Keep READY_FOR_CODEX as the default Streamlit path
- Keep live API PM explicitly enabled and labelled
- Adapt live PM output to the shared typed contract
- Record available API token and model-request usage
- Label Codex usage as plan/credits without estimated token counts

Validation:
- Confirm queued work does not require an API key
- Confirm API mode warns before execution
- Confirm SDK usage and trace identifiers are inspectable

## Task 262: Add PM contract and behaviour verification

Type: Validation Task
Status: DONE
Requirement: R94

Goal:
Prevent contract drift and verify the PM’s decision boundaries.

Requirements:
- Add contract parity, controller, approval, billing-boundary, and prompt-completeness tests
- Add deterministic behavioural cases for ambiguity, prioritisation, validation work, specialist consultation, and stale state
- Keep live SDK evaluation explicitly opt-in

Validation:
- Run focused PM, controller, Agents SDK, Codex contract, and workspace suites
- Run broader unit regression tests
- Confirm normal verification consumes no OpenAI API tokens

## Task 263: Add typed PM work requests and proposal lineage

Type: Feature Task
Status: DONE
Requirement: R95

Goal:
Carry operational PM intent losslessly through the Codex queue and proposal lifecycle.

Requirements:
- Define versioned prioritisation and task-plan request payloads
- Extend Codex work requests compatibly with structured payload and proposal result references
- Link PM proposals to originating work requests and parent revisions

Constraints:
- Existing stored work requests must load without migration
- Do not duplicate canonical product state in runtime records

Validation:
- Verify typed round trips and legacy record loading
- Verify proposal and request lineage is deterministic and idempotent

## Task 264: Enforce operational PM mode invariants

Type: Feature Task
Status: DONE
Requirement: R95

Goal:
Reject unsafe prioritisation and task-plan proposals before canonical writes.

Requirements:
- Validate eligible NEW prioritisation candidates and exact single activation
- Block activation while another requirement is IN_PROGRESS
- Validate task-plan target, task links, task status, rationale, and evidence

Constraints:
- Preserve exact-revision and stale-source protections
- Do not weaken existing proposal validation

Validation:
- Cover stale candidates, concurrent activation, invalid links, duplicates, and valid bundles

## Task 265: Build the Requirements PM Workbench

Type: Feature Task
Status: DONE
Requirement: R95

Goal:
Let operators initiate prioritisation and task planning beside canonical requirements.

Requirements:
- Add Prioritise work and Plan tasks forms with eligibility guidance
- Default to Prepare for Codex
- Expose API execution only when enabled and after a billing warning
- Keep discovery and manual requirement editing intact

Constraints:
- Avoid duplicating the workbench in Agents
- Keep the surface compact and explain blocked states

Validation:
- Verify eligibility, defaults, backend labels, and request creation in Streamlit

## Task 266: Unify PM proposal review and continuation

Type: Feature Task
Status: DONE
Requirement: R95

Goal:
Review, approve, reject, and continue PM decisions without duplicate approval paths.

Requirements:
- Render exact proposal changes, evidence, assumptions, consultations, and backend in Inbox
- Approve Codex proposals through the controller
- Resume API approvals through the same serialized SDK RunState
- Continue NEEDS_INPUT decisions with linked revisions

Constraints:
- Never apply an SDK-owned proposal directly while its run is paused
- Keep controller operations model-free

Validation:
- Verify Codex approval, SDK pause and resume, rejection, and clarification continuation

## Task 267: Verify operational PM modes and token boundaries

Type: Validation Task
Status: DONE
Requirement: R95

Goal:
Prevent workflow, approval, and billing regressions in operational PM modes.

Requirements:
- Add controller, UI, Codex contract, and scripted SDK cases
- Cover prioritisation, active-work blocking, task planning, uncertainty-driven validation work, and specialist consultation
- Keep live API evaluation opt-in

Constraints:
- Normal verification must not use OPENAI_API_KEY
- Preserve unrelated Learning Agent failure baseline

Validation:
- Run focused unit and deterministic eval suites
- Run broad regression tests and publishing policy checks

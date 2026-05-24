# Product: OS Control Panel

## Problem

AI Builder OS currently operates through files, prompts, and command-line workflows. That makes it powerful, but slower and less intuitive to use when starting new projects, capturing requirements, prioritising work, and understanding what the agents are doing. A local UI is needed to make the OS easier to operate without replacing the underlying file-based system.

## Goal

Build a local-first control panel for AI Builder OS that helps the operator create new projects, discover and draft requirements through PM interaction, and edit and prioritise requirements.

## User

- Primary V1 user: the Product Director operating the OS locally
- Secondary later: invited collaborators
- Future later: external/shared users

## Core User Flow

Operator opens the workspace UI -> starts a new project through live PM discovery or opens an existing project -> enters the project-level agent workspace when working inside an existing project -> uses PM discovery to shape requirements -> reviews draft requirements -> confirms and edits requirements in structured UI -> prioritises work without reading raw project files

## Core Functionality

### Input

- Project name
- Display name
- Initial idea / requirement
- Requirement fields such as title, description, priority, status, and effort
- PM discovery conversation inputs from the operator

### Output

- Workspace summary of projects
- Structured requirement drafts from PM agent discovery
- Structured requirement cards/forms
- PM prioritisation recommendations
- Static role cards describing the available agents

### Persistence

- Persist project state through the existing AI Builder OS file structure
- Save approved requirements into `product/requirements.md`
- Persist active agent-thread state in a lightweight file-backed way when the project uses guided agent interaction

### UI / API / Automation

- Workspace summary page is the primary entry point
- Project drill-down page supports:
  - requirements
  - agent workspace
  - prioritisation
- PM requirement discovery should run as a PM-first chat flow:
  - idea input
  - PM clarifying questions in-thread
  - draft requirements for review
- V1 is view-first for orchestration and does not need to trigger full agent execution from the UI

## Constraints

- Must be an internal, local-first tool in V1
- Must build on the existing AI Builder OS structure rather than replace it
- Must keep the UI simple and avoid clutter from long PM conversations
- Must edit only requirements in V1, not project memory or rules
- Must use structured requirement cards/forms rather than raw markdown editing as the primary requirement-editing experience
- Must present concise summaries instead of raw agent traces or heavy debugging surfaces in V1
- Must not turn V1 into a full execution IDE or workflow-control console

## Success Criteria

- A new project can be started from the UI end-to-end in about 10 minutes
- The operator can scaffold a new project from the UI using:
  - project name
  - display name
  - initial idea
- The operator can run PM discovery in the UI and receive:
  - clarifying questions in a PM chat thread
  - a structured draft requirement set for review
- Approved requirements can be saved into the project
- Requirements can be edited through structured cards/forms
- Requirements can be prioritised through:
  - manual ordering
  - editing `Priority`, `Status`, and `Effort`
  - asking PM for a recommendation
- The UI provides:
  - a workspace summary page
  - static role cards for all agents
  - PM requirement drafts
  - PM prioritisation decisions

## Current Limitations

- V1 is local-first only
- V1 does not provide full agent execution control
- V1 does not treat task inspection as a primary feature
- V1 does not include editing of project memory or rules
- V1 should keep PM discovery lightweight, focused on the active PM thread and the reviewed draft rather than a visible archive
- V1 keeps visible PM chat history lightweight and focused on the active thread rather than a large visible archive
- Engineer summaries and QA summaries are not primary V1 outputs

## Out of Scope

- Remote/shared multi-user access in V1
- Full PM -> Engineer -> QA workflow control from the UI
- Deep task inspection as a primary V1 feature
- Manual workflow-state editing
- Editing project memory or rules in V1
- Engineer summaries and QA summaries as primary V1 outputs
- Full raw agent traces or internal debugging consoles

# Product Requirements

## Active Requirements

### R1 — Build the local-first OS control panel

Status: DONE
Priority: HIGH
Effort: M
Description:
Build a local-first UI for AI Builder OS that helps the operator create new projects, run PM discovery, and edit and prioritise requirements from a workspace-first control panel.

### R5 — Experience Designer UI Intro

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement
- Project-level UI feedback should be captured inside the product surface rather than forcing operators back to the command line.

Target user
- Product Directors and operators shaping the OS through hands-on project feedback.

Core job-to-be-done
- Give structured experience feedback from inside the selected project so it can flow through the OS workflow.

Success criteria
- Smaller project-level UX feedback can be captured and routed without falling back to the CLI.

Constraints
- The Experience Designer needs to be exposed only at the project level.

Out of scope
- No automatic triggering of Product Manager agent. As long as the Designer role completes its scope that is fine.

Assumptions
- Existing requirement IDs in this project: R1, R2, R3, R4

Open questions
- Which parts of this draft should become a new requirement versus a refinement of existing requirements?

### R6 — Improve workspace UI clarity

Status: DONE
Priority: HIGH
Effort: S
Description:
Improve the clarity of the workspace experience so the control panel is easier to scan and less visually confusing during everyday use.

This requirement covers:
- renaming the main workspace heading so it is clearly distinct from the `os-control-panel` project name
- reducing clutter in workspace project cards by showing summary counts instead of full task detail
- making the agent role cards visually consistent in size and presentation

Why now:
- this requirement comes from a routed Experience Designer finding with high confidence
- the issues are in-scope UX improvements to existing surfaces rather than new feature work

### R7 — Finish workspace role-card visual polish

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Resolve the remaining visual-coherence issue in the workspace role-card section so the cards read as visually even and the workspace feels more polished.

This requirement covers:
- fixing the uneven visual presentation of the agent role cards
- preserving the current role content while improving layout consistency

Why now:
- this requirement comes from a manual Experience Designer usability review
- the issue is a small in-scope UX improvement on an existing surface rather than new feature work

### R8 — Improve workspace layout balance

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Refine the workspace layout so the summary surfaces feel more balanced and easier to scan.

This requirement covers:
- changing workspace project cards from a full-width stacked layout to a more compact card grid with sensible width
- adding clearer vertical separation between the top and bottom rows of the agent role cards

Why now:
- this requirement comes from an accepted Experience Designer finding
- the issue is an in-scope workspace-layout polish improvement on an existing surface

### R9 — Improve requirement-page focus on active work

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Make the Requirements view easier to use by focusing attention on unfinished work and reducing accidental interaction with completed requirements.

This requirement covers:
- moving `DONE` requirements into their own lower-priority section or otherwise placing them below active work
- preventing direct editing of requirements that are already `DONE`

Why now:
- this requirement comes from a routed Experience Designer finding with high confidence
- the issue is an in-scope usability improvement to an existing project-management surface

### R10 — Improve requirement-card layout balance

Status: DONE
Priority: LOW
Effort: S
Description:
Refine the Requirements-page card layout so it uses the available space more intentionally and feels more visually balanced.

This requirement covers:
- reviewing whether full-width requirement cards are the best use of the current page width
- improving the layout of the active requirement cards in a way that is more aesthetically balanced while preserving clarity

Why now:
- this requirement comes from an Experience Designer visual-review finding
- the issue is an in-scope UI polish improvement on an existing surface rather than new feature work

### R11 — Improve requirement-card symmetry

Status: DONE
Priority: LOW
Effort: S
Description:
Refine the active Requirements-page layout so it feels more visually even when the number of active cards does not fill a complete row.

This requirement covers:
- improving the visual symmetry of the active requirement-card layout
- avoiding awkward lone-card rows that feel stretched or visually imbalanced

Why now:
- this requirement comes from a new Experience Designer finding after the two-column layout was introduced
- the issue is a small in-scope aesthetic polish improvement on an existing surface

### R12 — Make discovery flows dynamic and question-driven

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Improve the PM Discovery and Experience Designer flows so they ask for information progressively instead of presenting a large flat form up front.

This requirement covers:
- collecting the initial user problem or idea first
- generating only the next relevant questions or question set based on project context and role intent
- keeping the interaction simple so the Product Director provides only information that is actually needed

Why now:
- this requirement comes from an Experience Designer feature-candidate finding
- the issue affects the quality and usability of the core control-panel workflows, but still fits the current project scope

### R13 — Make requirement-card expansion behavior consistent

Status: DONE
Priority: LOW
Effort: S
Description:
Remove the inconsistent default-expanded state in the Requirements tab so requirement cards behave predictably and the page feels calmer.

This requirement covers:
- reviewing the default expansion behavior of requirement cards in the Requirements tab
- making the initial card state consistent across the requirement list
- preserving readability while avoiding one card drawing accidental attention by default

Why now:
- this requirement comes from an Experience Designer in-scope UX finding
- the issue is a small usability and polish refinement on an existing project-management surface

### R14 — Add interactive PM discovery flow

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Problem statement
- To make the discovery process more interactive with the PM

Target user
- Product Directors or operators using PM discovery to shape a new requirement.

Core job-to-be-done
- Let PM discovery respond to the submitted idea instead of asking the same static questions each time.

Success criteria
- The PM questions are relevant to the idea submitted.

Constraints
- We can start with just this form and move to experience designer if this works.

Out of scope
- Improving the Experience designer form.

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R2, R3, R4

Open questions
- Which parts of this draft should become a new requirement versus a refinement of existing requirements?

### R15 — Allow initiation of requirement implementation

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- Requirement implementation still depends on the CLI, which breaks the operator workflow inside the control panel.

Target user
- Operators managing requirement implementation from the control panel.

Core job-to-be-done
- Start requirement implementation directly from the UI.

Success criteria
- Requirement implementation can be initiated from the control panel without using the CLI.

Constraints
- Let me initiate implementation of only one requirement at a time within a project. Once that requirement is done, another requirement implementation in the same project can be initiated.

Out of scope
- Implementation of multiple concurrent requirements within the same project.

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R2, R3, R4

Open questions
- Which parts of this draft should become a new requirement versus a refinement of existing requirements?

### R17 — Delete Requirements

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Problem statement
- Operators need to remove unfinished requirements that are no longer useful, without creating risk around completed history.
The delete button should not be visible for completed requirements.

Target user
- Operators managing the requirements list.

Core job-to-be-done
- Keep the requirements list accurate without damaging completed history.

Success criteria
- Get a confirmation dialogue to make sure.
- Deleting an eligible requirement removes it from the file-backed requirements list.
- Completed requirements cannot be deleted from the main Requirements flow.

Constraints
- Only unfinished requirements are eligible for deletion: NEW, IN_PROGRESS, and BACKLOG.
- Require an explicit confirmation step before deleting.
- Preserve the existing file-backed requirements format and ordering for remaining requirements.

Out of scope
- Recycle bin and undo of deletes, etc

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R16, R3, R2, R4
- Initial idea entered: Add the ability to delete requirements.

Open questions
- None for the first version.

### R18 — Add PM chat-based requirement discovery

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- The current guided PM Discovery experience does not feel like a real PM interaction. It behaves more like a structured intake form than an agent conversation, which makes requirement discovery feel stiff and limits its usefulness for shaping ideas properly.

Target user
- Primary: Product Director operating the OS inside a project.

Core job-to-be-done
- Allow the user to open a PM chat inside a project, choose `Requirement Discovery Mode`, describe an idea, answer PM clarifying questions, and review draft requirements before saving them into `requirements.md`.

Success criteria
- The user can select the PM agent inside a project.
- The user can select `Requirement Discovery Mode`.
- The user can start a true chat thread with PM inside the project.
- PM can ask clarifying questions based on the idea provided.
- The user can answer iteratively in chat.
- PM can decide when it has enough context to draft requirements.
- The UI also provides a manual `Draft requirements now` action.
- PM drafts one or more requirement drafts for review.
- Draft requirements can be reviewed before being committed.
- Approved drafts can then be saved into `requirements.md`.
- The architecture is PM-first but supports adding other agents later, starting with Experience Designer.

Constraints
- This first slice covers PM only.
- This first slice covers discovery only.
- The UI should stay clean and should not keep a full visible conversation history.
- Save flow should create draft requirement(s) for review first, then confirm into `requirements.md`.
- The architecture should support later agent expansion without needing a major UI rewrite.

Out of scope
- Experience Designer chat in this requirement.
- PM refinement mode for existing requirements.
- PM prioritisation chat mode.
- Requirement clarification chat mode.
- Full multi-agent chat orchestration.
- Full persistent conversation history UI.

Assumptions
- The PM chat can use the existing PM discovery principles already defined in the OS.
- A lightweight active-thread model is enough even though the full conversation should not clutter the UI.
- Requirement drafts may map to one or more saved requirements.

Open questions
- None for the first PM-first slice.

### R19 — Let users click the agent tile in the workspace to open a popup that show a summary of what the agent does. Summary should show what the agent can do, whats in memory and its position in the workflow.

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- Let users click the agent tile in the workspace to open a popup that show a summary of what the agent does. Summary should show what the agent can do, whats in memory and its position in the workflow.

Target user
- Me

Core job-to-be-done
- Understand each agent from the workspace without opening raw role, memory, or workflow files.

Success criteria
- Workspace agent tiles are clickable.
- Clicking an agent tile opens a focused popup/modal for that agent.
- The popup explains what the agent can do in the OS.
- The popup shows a concise memory/context summary relevant to that agent.
- The popup explains the agent's position in the workflow.
- The popup can be dismissed without changing workflow state.

Constraints
- This is an informational UI surface only.
- Do not trigger agent execution from the popup.
- Use concise summaries instead of raw internal traces or long source files in the popup.
- Use existing file-backed role, memory, and workflow context where practical.
- Keep the workspace visually calm and avoid cluttering the agent tile cards.

Out of scope
- Editing agent role definitions, memory, workflow files, or project rules.
- Running agents or changing workflow state from the popup.
- A full documentation browser or raw markdown viewer.
- Remote/shared access behavior.

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R17, R18, R3, R2, R4
- Initial idea entered: Let users click the agent tile in the workspace to open a popup that show a summary of what the agent does. Summary should show what the agent can do, whats in memory and its position in the workflow.

Open questions
- None for the first informational popup slice.

### R20 — Improve navigation to projects

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- the project tab at the top is not needed if the projects cards can be clicked to navigate to the project

Target user
- Me

Core job-to-be-done
- in navigation

Success criteria
- Define what success looks like for the first version.

Constraints
- remove the project details tab from the top and allow users to clock the project card to navigate

Out of scope
- Clarify what should not be included in the first version.

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R17, R18, R19, R3, R2, R4
- Initial idea entered: Tidy up navigation on the workflow page

Open questions
- Which parts of this draft should become a new requirement versus a refinement of existing requirements?

### R21 — Make PM discovery conversationally adaptive

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- The PM discovery chat still behaves too much like a structured questionnaire. It does not reliably process previous answers, skip questions that are already covered, or ask sharper follow-up questions when an answer is vague.

Target user
- Me

Core job-to-be-done
- Shape a new requirement by talking to PM in a way that feels responsive to what I have already said, without losing the structured draft output that the OS needs.

Success criteria
- PM discovery no longer walks a fixed question list in order.
- PM uses the current thread context to decide which requirement field is still missing or unclear.
- PM asks a follow-up question on the same topic when the previous answer is too vague.
- PM moves to the next most relevant question when it has enough detail for the current topic.
- PM decides when there is enough context to draft requirements based on field quality, not just answer count.
- The thread model is prepared for a future planner switch to a full live-agent mode.
- Manual `Draft requirements now` remains available.

Constraints
- Keep the current file-backed thread artifact model.
- Keep the save path into `requirements.md` deterministic.
- Do not implement the full live-agent mode in this requirement.
- Do not turn the UI into a long visible conversation archive.

Out of scope
- Full live-agent PM discovery.
- Experience Designer chat overhaul.
- Hosted or remote execution concerns.

Assumptions
- Live PM can replace the hybrid planner cleanly now that it is working well in the New Project flow.

Open questions
- None for the current live-PM slice.

### R22 — Add live PM discovery as the default new-project flow

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- The New Project tab currently starts from a local scaffold form with very little context. This is exactly where PM has the least local knowledge, so it should default to a live PM agent that can reason in real time and shape the first requirement before the project is created.

Target user
- Me

Core job-to-be-done
- Start a brand-new project by talking to a live PM agent, then create the project from a reviewed requirement draft instead of seeding it from a raw idea.

Success criteria
- The New Project tab defaults to a live PM discovery flow.
- The user can enter project name, display name, and an initial idea to start the live PM conversation.
- PM can ask follow-up questions in a true live agent mode.
- The user can answer iteratively or force a draft manually.
- PM can draft the first requirement for the project.
- The reviewed draft can create the project and seed `R1` with both the drafted title and drafted body.
- The existing project-level PM workspace remains available and should align with the live PM discovery model.

Constraints
- Keep project creation file-backed through the shared scaffold path.
- Require an OpenAI-backed live PM runtime for the New Project flow.
- Do not turn this slice into a full multi-agent live workspace yet.

Out of scope
- Live Experience Designer in the New Project tab.
- Hosted or multi-user execution concerns.

Assumptions
- A live PM agent is most valuable where there is the least existing project context.
- One drafted initial requirement is enough to seed a brand-new project in this first live slice.

Open questions
- None for the first live new-project slice.

### R23 — Implementation progress.

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- UI-initiated implementation needs clearer progress feedback so operators can tell that work is active and understand its current stage.

Target user
- Operators running requirement implementation across projects.

Core job-to-be-done
- Make UI-initiated requirement implementation feel visibly active and easier to interpret while the background worker is running.

Success criteria
- When implementation is started from a requirement card, the same card shows a progress bar immediately.
- The running requirement card shows a concise one-line explanation of the current implementation stage.
- Progress state advances deterministically across the existing run lifecycle: queued, running, completed, and failed.
- A different requirement card explains that implementation is locked while another requirement is active.
- Completed or failed runs keep the existing summary/error outcome visible.

Constraints
- Build on the existing file-backed implementation run artifact.
- Keep progress approximate and status-derived; do not claim exact elapsed or remaining time.
- Preserve the one-active-run-per-project lock.
- Keep the UI local-first and refresh-based for this slice.

Out of scope
- Real-time streaming logs.
- Precise duration estimates.
- Full multi-agent trace display.
- Multiple concurrent implementation runs in the same project.

Assumptions
- Existing requirement IDs in this project: R1, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R17, R18, R19, R20, R21, R22, R3, R2, R4
- The first version can represent progress by lifecycle stage rather than measuring actual implementation completion.

Open questions
- None for the first progress-visibility slice.

### R24 — Project preview

Status: DONE
Priority: HIGH
Effort: L
Description:
### Problem statement
Users need a way to quickly access and test executed projects to evaluate their functionality, conduct demos, and verify the overall health of projects without navigating away from the control panel interface.

### Target user
Product managers, developers, and quality assurance professionals who need to evaluate project implementations and performance.

### Core job-to-be-done
Enable users to click a button that opens an executed project in a new tab for testing and demonstration purposes.

### Success criteria
- A functional button that opens the executed project in a new tab.
- The new tab reflects real-time project status and allows for interaction/testing.
- Users report increased efficiency in conducting demos and testing implementations.

### Constraints
- The functionality must work across all major browsers.
- There should be no significant lag in loading the project when opening the new tab.

### Out of scope
- In-depth project health diagnostics beyond basic functionality checks.
- Editing features for the other tabs or panels during demo/testing sessions.

### Assumptions
- Users are familiar with navigating web tabs and expect a seamless transition between the control panel and the executed project.
- The executed projects are hosted in a way that can be accessed through standard web links.

### Open questions
- What specific projects or types of implementations will users need to preview? 
- Are there any security or access considerations we need to account for when opening projects in a new tab?

### R25 — Phase 1 multi-agent workspace foundation

Status: DONE
Priority: HIGH
Effort: L
Description:
### Problem statement
The current `Agents` workspace is still too PM-centric to act as a real agent workflow surface. Product work, experience synthesis, UI design direction, and workflow control are still split across old patterns or absent from the shared workspace, which makes the control panel feel incomplete as the operating surface for the OS.

### Target user
Product Director operating AI Builder OS through the control panel.

### Core job-to-be-done
Expand the `Agents` tab into a shared multi-agent workspace foundation that supports PM, Experience Designer, UI Designer, and Orchestrator without falling back to bespoke tabs or one-off surfaces.

### Success criteria
- The `Agents` tab supports:
  - PM
  - Experience Designer
  - UI Designer
  - Orchestrator
- PM continues to work as a live requirement-discovery chat
- Experience Designer is reintroduced through `Agents`, not as a standalone project tab
- Experience Designer supports:
  - `Feedback Synthesis`
  - `Usability Review`
- Experience Designer can save a reviewed finding into the existing workflow-artifact model
- UI Designer supports:
  - `Design Direction`
  - `UI Review`
- UI Designer can produce a durable design brief inside the shared agent-thread model
- Orchestrator is available in the `Agents` tab as a code-driven workflow authority surface
- The agent workspace architecture is shared rather than hard-coded as PM-only

### Constraints
- Keep PM live and intact while adding the shared workspace foundation
- Reuse the existing file-backed agent-thread model rather than introducing a separate chat store
- Keep Orchestrator authoritative and code-driven rather than making it a freeform live chat
- Do not reintroduce a bespoke Experience Designer project tab

### Out of scope
- Workflow inbox
- Approval objects
- QA agent surface
- Engineer agent surface
- Hosted multi-user agent control

### Assumptions
- Experience Designer findings should remain workflow artifacts, not casual notes
- UI Designer can be useful in the first slice even if its design briefs remain thread-backed rather than becoming a new product artifact type immediately
- The shared `Agents` workspace is the right long-term home for role-based interaction

### Open questions
- Should UI Designer eventually write to a dedicated design-artifact store instead of only the shared thread model?
- How much run/trace visibility should be embedded directly in each agent panel versus a later workflow inbox or observability view?

### R26 — Phase 2 workflow inbox and approval layer

Status: DONE
Priority: HIGH
Effort: L
Description:
### Problem statement
The control panel now has multiple kinds of workflow state, but too much of that state is still implicit or scattered. Draft approvals, blocked clarifications, routed findings, and active runs need one durable place where the Product Director can see what is waiting, what is blocked, and what needs explicit approval.

### Target user
Product Director operating AI Builder OS through the control panel.

### Core job-to-be-done
Add a workflow inbox and explicit approval layer so the Product Director can review, approve, reject, and inspect active workflow items without guessing where state is hiding.

### Success criteria
- The top-level UI includes an `Inbox` surface
- The inbox shows active workflow items across the OS, including:
  - approvals
  - PM clarifications
  - waiting agent threads
  - routed experience findings
  - active implementation runs
- The inbox supports filtered views for:
  - waiting
  - blocked
  - routed
  - running
- PM requirement drafts become explicit approval requests before they are written into `requirements.md`
- Experience Designer findings can be sent for approval before they are written into the workflow-artifact model
- UI Designer design briefs can be sent for approval as reviewed outputs
- Approving or rejecting a request updates durable workflow state
- Orchestrator and status tooling treat open approvals as active workflow state

### Constraints
- Keep the approval model file-backed and local-first
- Do not replace existing requirement, clarification, finding, or run artifacts
- Do not turn approvals into hidden side effects; they must be visible in the inbox
- Keep Orchestrator code-driven and aligned with the same file-backed state

### Out of scope
- Full token-level tracing
- Hosted notification systems
- Multi-user approval permissions
- Formal architect signoff objects for every structural change
- Rich implementation-run debugging consoles

### Assumptions
- The highest-value first approvals are draft-to-artifact transitions, not every possible workflow step
- Open approvals should route back to Product Director before further automation continues
- A single inbox surface is a better first operator experience than spreading approval controls across multiple tabs

### Open questions
- Which approval types should become first-class beyond draft approvals in a later slice?
- How much run detail should move from the inbox into a later observability surface?

### R29 — Enhance Approval Visibility on Workspace Page

Status: DONE
Priority: HIGH
Effort: L
Description:
**Problem statement**  
The current process requires users to navigate to their inbox to check for pending approvals, leading to inefficiency and missed opportunities for timely decisions.

**Target user**  
Users who need to manage and approve requests within the control panel on a regular basis.

**Core job-to-be-done**  
Users want to quickly access and approve pending requests without having to navigate away from the workspace page.

**Success criteria**  
- Users can see a list of items awaiting approval directly on the workspace page.  
- Each item displays a concise summary sufficient for approval decisions.  
- Users can approve requests directly from the workspace interface, improving efficiency.

**Constraints**  
- The solution must integrate seamlessly with existing control panel features.  
- It should maintain performance and responsiveness of the workspace page.

**Out of scope**  
- Any changes to the approval workflow beyond visibility and direct action on the workspace page.

**Assumptions**  
- Users have a need to approve multiple items and can make quick decisions based on summaries.

**Open questions**  
- What specific details would be essential in the summary for each approval item?  
- Are there different types of approvals that require distinct handling?

### R33 — Automate durable PM clarifications from live discovery

Status: DONE
Priority: HIGH
Effort: M
Description:
Move PM clarification handling out of manual requirement bookkeeping and into the live PM discovery flow so PM can automatically raise durable Inbox clarifications when a materially blocking ambiguity is detected.

Success criteria:
- PM live discovery can request a durable clarification automatically when the ambiguity is materially blocking
- Auto-generated clarifications appear in the Inbox without manual creation by the Product Director
- Clarification questions are visible in the Inbox
- Answering a thread-linked clarification from the Inbox resumes the blocked PM discovery thread
- Requirement-page clarification tooling remains available for explicit manual use when needed

Reason:
- During post-test review, the Product Director clarified that the low-value part of the feature was manual routing, not clarification itself.
- PM should own ambiguity detection and durable clarification creation when the implementation or requirement shape would otherwise be guessed.

### R34 — Complete approved review workflows automatically

Status: DONE
Priority: HIGH
Effort: M
Description:
When the Product Director approves Experience Designer findings or UI Designer reviews, the workflow should continue automatically to a real completion state instead of stopping at “approved”. Approved review work should be run through PM automatically so it either lands in the requirements backlog or comes back as an explicit out-of-scope confirmation.

Success criteria:
- Approving an Experience Designer finding automatically triggers a PM completion step
- Approving a UI Designer review automatically triggers the same PM completion step
- PM completion ends in exactly one of:
  - a new backlog requirement added to `requirements.md`
  - an explicit Product Director confirmation that the approved review should stay out of scope
- Scope confirmations are visible and actionable in the Inbox
- Experience findings that complete through PM are marked resolved so the workflow does not stall in a half-routed state
- UI reviews no longer stop at “approved and archived” with no actionable downstream outcome

Reason:
- During manual use, the Product Director clarified that approving review work should mean “continue the OS workflow to a result”, not just “persist the reviewed artifact”.
- The existing behavior was uneven: Experience findings were saved but still needed manual PM pickup, while approved UI reviews had no meaningful downstream completion path at all.

### R44 — Route UI and experience-heavy implementation work through the right design agents

Status: DONE
Priority: HIGH
Effort: M
Description:
The requirement implementation workflow currently routes structural work through Architect, but it does not reliably bring in UI Designer for UI-heavy requirements or Experience Designer for experience-heavy requirements. That leaves user-facing implementation work vulnerable to skipping the design and usability shaping that the OS says should happen before engineering.

Success criteria:
- Pending implementation work with meaningful experience/usability triggers routes to Experience Designer before Engineer
- Pending implementation work with meaningful UI/visual triggers routes to UI Designer before Engineer
- The deterministic Orchestrator helper and the in-app Orchestrator use the same routing rule
- The requirement implementation prompt explicitly tells the background workflow not to skip Experience Designer or UI Designer when the requirement is relevant
- UI-related work can feed UI design requirements or constraints into the workflow before engineering begins

Reason:
- The Product Director asked for explicit confirmation that UI Designer and Experience Designer are actually wired into the requirement implementation workflow for the kinds of work they should shape.
- The previous implementation path relied on PM/Engineer/Architect but did not enforce the design-agent layer for user-facing work.

### R45 — Make agent selection intentional and explorable

Status: DONE
Priority: HIGH
Effort: M
Description:
The current agent workspace still makes the Product Director choose agents and modes too blindly through dropdowns. The control panel should make those choices more intentional by showing the available agents and modes with enough explanation to choose confidently before entering a thread.

Success criteria:
- Agent selection no longer depends on a blind dropdown-first flow
- The Product Director can understand what each agent is for before choosing it
- Mode selection is explained clearly enough to support intentional choice
- The new surface remains compatible with the existing PM, Experience Designer, UI Designer, and Orchestrator workflows

Reason:
- UI Designer review concluded that agent selection is one of the highest-leverage improvements because the current flow hides too much at the moment of choice.

### R46 — Improve Inbox hierarchy and scanability

Status: DONE
Priority: HIGH
Effort: M
Description:
The Inbox works functionally, but it still feels visually heavy and too stacked. It should make waiting, blocked, routed, and running work easier to scan by using clearer hierarchy and stronger grouping rather than presenting everything as same-weight cards.

Success criteria:
- Inbox items are grouped more clearly by workflow state
- Approval requests and workflow items feel more distinct in priority and purpose
- The Product Director can scan the Inbox faster without losing detail or actions
- The Inbox remains a workflow surface rather than turning into a second workspace

Reason:
- UI Designer review identified the Inbox as usable but still too visually monotonous and same-weighted.

### R47 — Make project entry surfaces feel more intentional

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Project cards and project-level framing should feel more like meaningful entry points into live work and less like generic status boxes. The workspace and projects surfaces should reduce repetitive framing and improve identity, hierarchy, and action clarity.

Success criteria:
- Project cards feel more intentional and easier to scan
- Project identity, attention signals, and primary actions are more clearly separated
- Workspace and project surfaces reduce unnecessary repeated framing where possible
- The UI remains calm and restrained rather than becoming more decorative

Reason:
- UI Designer review identified repeated full-width bordered structure and flat project-card composition as meaningful quality issues even though the workflow already functions.

### R27 — Rename Experience Designer `Visual Review` to `Usability Review`

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Rename the Experience Designer mode currently labeled `Visual Review` to `Usability Review` so the role boundary is clearer against UI Designer `UI Review`.

Success criteria:
- The Experience Designer mode label changes from `Visual Review` to `Usability Review`
- The wording makes the distinction clearer between:
  - Experience Designer usability/clarity review
  - UI Designer visual/interface review
- Related UI copy and supporting docs stay aligned

Reason:
- During manual verification, the Product Director identified that `Visual Review` overlaps too much with UI Designer `UI Review` at the naming layer even though the intended responsibilities are different.

### R31 — Make inbox approval items reviewable before approval

Status: DONE
Priority: HIGH
Effort: S
Description:
Improve the Inbox so approval items can be opened and reviewed in full before the Product Director approves or rejects them.

Success criteria:
- Inbox approval items can be clicked or expanded
- The Product Director can read the full underlying draft before approving
- This works for at least:
  - PM requirement drafts
  - Experience Designer findings
  - UI Designer design briefs

Reason:
- During manual verification, the Product Director found that inbox approval cards currently expose only a one-line summary, which is not enough to make an informed approval decision.

### R35 — Improve Dual-Level Navigation for Enhanced Usability

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: Users find the dual-level navigation confusing when accessing projects, particularly when switching between requirements and agent sections due to their similar horizontal layout. This leads to inefficiency and frustration.

**Target user**: Project managers and users who frequently navigate through the project's requirements and agent sections.

**Core job-to-be-done**: Users need to efficiently navigate between projects and associated components without confusion to manage their tasks effectively.

**Success criteria**: 
1. Reduction in user-reported confusion regarding navigation (target a 50% decrease based on feedback surveys).
2. Improved task completion times for switching between project sections (measured through user testing).
3. Increased user satisfaction ratings on navigation aspects in future feedback sessions.

**Constraints**: The navigation must remain consistent with the overall design language of the OS control panel and accommodate all existing user flows without introducing new barriers.

**Out of scope**: Any changes to the overall layout of the site beyond navigation (e.g., restructuring the information architecture or content hierarchy).

**Assumptions**: The simplification of navigation will lead to a clearer user experience and will be positively received based on existing user feedback.

**Open questions**: What specific visual elements can we implement to clearly distinguish between navigation levels? What are the technical limitations of modifying the navigation structure at this stage?

### R50 — Add sequential sprint planning and execution

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement
- Backlog requirements are currently a flat list with no project-level execution container, which makes it awkward to commit intentionally to a set of work and run it through implementation in a clear order.

Target user
- Product Director using the OS control panel to plan and execute a coherent batch of project work.

Core job-to-be-done
- Move backlog requirements into a sprint, order them intentionally, and start a sequential sprint that implements one requirement at a time within the project.

Success criteria
- Backlog requirements can be added into a project sprint from the UI.
- Sprint items can be reordered before the sprint starts.
- Starting a sprint immediately promotes and launches the first requirement.
- Sprint execution respects the existing one-active-implementation-per-project rule.
- When one sprint requirement finishes cleanly, the next sprint requirement starts automatically on the next app cycle.
- If a sprint requirement needs intervention, the sprint becomes visibly blocked instead of silently skipping ahead.

Constraints
- Sprint V1 should stay sequential within a project.
- Sprint V1 should not introduce parallel requirement execution inside a project.
- Backlog requirements should remain non-implementable until explicitly activated by the sprint flow or by manual status change.

Out of scope
- Parallel sprint lanes.
- Automatic PM-authored sprint ordering.
- Cross-project sprint coordination.

Assumptions
- The Product Director wants to choose sprint contents manually and retain direct control over sprint order.
- Sequential execution is the safest first implementation because it preserves the current project-level implementation lock.

Open questions
- Should a future sprint version support explicit dependency markers between requirements?
- Should sprint progress eventually surface more prominently in workspace and inbox summaries?

### R36 — Improve Requirements Page Layout for Enhanced Usability

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: Users are overwhelmed by the noisy layout of the requirements page, making it difficult to discern priority tasks and manage requirements efficiently.

**Target user**: Project managers and team members who use the requirements page to track and prioritize project tasks.

**Core job-to-be-done**: Enable users to quickly identify and focus on high-priority requirements to enhance efficiency in managing project timelines.

**Success criteria**: 
- Redesign the requirements page layout to reduce clutter and clearly highlight priority tasks.
- Achieve a user satisfaction score improvement of at least 20% in post-implementation feedback.

**Constraints**: Redesign must be completed within current project timelines and budget, and should maintain integration with existing project workflows.

**Out of scope**: Any changes to back-end functionality or data storage solutions that are not directly related to the user interface layout.

**Assumptions**: It is assumed users prefer a cleaner, less cluttered interface and that visual cues can effectively guide them to prioritize tasks.

**Open questions**: What specific visual cues can be added to signal priority? How will we measure the impact of this change on user workflow efficiency?

### R40 — Enhance Workspace and Inbox UI for Intentionality and Simplicity

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem Statement**  
Current workspace and inbox UI lacks intentionality and visual clarity, leading to user frustration due to overwhelming visual clutter and ineffective navigation.  
  
**Target User**  
Professionals and teams managing workflows and communications within the application.  
  
**Core Job-to-be-Done**  
Enable users to efficiently navigate and interact with content cards and inbox items while maintaining focus on tasks without distraction.  
  
**Success Criteria**  
- Implement a unified card design with balanced size and spacing.  
- Provide a clearer visual hierarchy, reducing clutter, with defined purposes for UI elements.  
- Increase user satisfaction and efficiency, measured by user feedback and usability testing.  
  
**Constraints**  
- Design must be responsive across devices.  
- Must adhere to accessibility standards.  
  
**Out of Scope**  
- Extensive redesign of functionalities beyond the workspace and inbox UI will not be included in this update.  
- Changes to backend systems or data management processes are not part of this requirement.  
  
**Assumptions**  
- Users prefer a minimalist aesthetic that prioritizes functionality and ease of navigation.  
- The proposed design elements will be feasible to implement without causing delays in the delivery timeline.  
  
**Open Questions**  
1. Are there specific actions you want to prioritize within the cards that might influence their design further?  
2. What types of content will be most commonly displayed in the inbox that should dictate card size or layout?  
3. Do you have preferred styles or examples of cards or layouts from other applications that resonate with your vision of simplicity?

### R51 — Improve sprint closure and requirements page density

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement
- The requirements page currently makes sprint completion ambiguous, leaves completed sprint items hanging around in the active sprint context, and uses too much vertical space for completed work and the project preview utility.

Target user
- Product Director using the OS control panel to manage active project work and close sprints confidently.

Core job-to-be-done
- Know clearly when a sprint is complete, confirm sprint closure intentionally, and review the requirements page without it turning into a long scroll of stale or low-priority content.

Success criteria
- A sprint becomes visibly complete before it is cleared.
- The Product Director can confirm sprint completion explicitly.
- After confirmation, the active sprint is cleared so a new sprint can be planned.
- The sprint panel appears near the top of the requirements page.
- Completed requirements are shown in a compact archive rather than a long stack of cards.
- The project preview control feels like a compact utility surface instead of an oversized banner button.

Constraints
- Keep Sprint V1 sequential and project-local.
- Preserve the existing one-active-implementation-per-project rule.
- Keep completed requirements available for reference even after compacting them.

Out of scope
- Sprint history analytics.
- Drag-and-drop sprint planning.
- Broad visual redesign of the entire project page.

Assumptions
- Sprint completion should be explicit rather than silently auto-cleared.
- Completed requirements should remain accessible without competing visually with active work.

Open questions
- Should sprint completion preserve a dedicated history artifact after closure?
- Should the completed archive eventually support search or recency sorting?

### R39 — Enhance UI Intentionality and Simplicity in Workspace and Inbox

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
Current workspace and inbox designs may feel cluttered and lack intentional use of visual hierarchy, leading to user frustration and inefficiencies.  

**Target user**  
Professional users and teams managing workflows and communications within the application, requiring efficient navigation and interaction with content.  

**Core job-to-be-done**  
To create a workspace and inbox UI that is intentionally designed to allow users to focus on their tasks with a clear, symmetric layout that minimizes visual clutter and emphasizes important interactions.  

**Success criteria**  
- Increased user satisfaction ratings based on usability tests.  
- Reduction in task completion times as measured in user feedback sessions.  
- Positive feedback on visual hierarchy and intentionality in design.  

**Constraints**  
The design must be responsive across devices and adhere to accessibility standards, ensuring usability remains high despite the visual simplification.  

**Out of scope**  
Adding new features to the application not covered in the design brief. Any major overhauls of underlying functionality outside aesthetic adjustments and layout improvements.  

**Assumptions**  
Users are seeking a more organized workspace and inbox experience and are willing to adapt to a more minimalistic design approach.  

**Open questions**  
- What specific actions should be prioritized in the card designs?  
- What common content types will inform card layouts and sizes?  
- Are there existing designs from other applications that align with the proposed simplification?

### R52 — Enhance Workspace Page UI for Improved Clarity and Usability

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
The current workspace page lacks visual clarity and usability, making it difficult for team members to quickly identify roles and responsibilities. The visual hierarchy is poor, resulting in a cluttered interface that diminishes user experience.  

**Target user**  
Team members, including PMs, Engineers, Designers, QAs, and Architects, who need to easily access and comprehend their roles and related summaries.  

**Core job-to-be-done**  
Team members require a more intuitive interface that allows for quick navigation and understanding of workspace roles and responsibilities.  

**Success criteria**  
- Increased user satisfaction ratings regarding the workspace page layout by at least 20% in usability surveys.  
- Reduction in user questions related to identifying roles and accesses by 30% within three months post-launch.  

**Constraints**  
The layout must maintain responsiveness across devices, ensuring legibility and usability are upheld at various screen sizes while implementing design changes.  

**Out of scope**  
Any changes beyond improving the visual design and layout of the workspace page, including functional overhauls or new feature additions, are out of scope for this improvement initiative.  

**Assumptions**  
Current brand guidelines will be followed, and there is no additional functionality change requested apart from design improvements.  

**Open questions**  
- What specific color palette should be used to maintain consistency with existing design elements? Are there any brand guidelines to adhere to?

### R53 — Enhance Card Interaction with Internal Buttons

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem Statement**: Users struggle to quickly identify and engage with agent summaries due to poorly positioned action buttons within each card, affecting usability and visual clarity.

**Target User**: Team members accessing role summaries for various agents.

**Core Job-to-be-Done**: Improve identification and accessibility of agent summaries through better button placement within each respective card.

**Success Criteria**: 1) Action buttons are repositioned inside each card directly below the agent's descriptions;
2) All buttons maintain uniform alignment across cards;
3) Button sizes/styles are improved for accessibility;
4) User feedback is collected post-implementation indicating a higher ease of use rating.

**Constraints**: Maintain existing card dimensions; all design changes must adhere to current branding guidelines.

**Out of Scope**: Changes to the overall card design or dimensions beyond button placement and styling; any functionality change involving backend logic.

**Assumptions**: Users will respond positively to the new button placement and find it more intuitive; existing user demographics will remain consistent.

**Open Questions**: 1) Should button colors be adjusted for visibility?
2) What specific padding or spacing guidelines apply for button integration?
3) How will we ensure consistent interaction across various devices, particularly mobile?

### R48 — Launch a broader workspace and inbox visual simplification initiative

Status: DONE
Priority: LOW
Effort: L
Description:
**Design goal**  
Elevate the workspace and inbox UI to create a more intentional, symmetrical design that exhibits simplicity, ensuring elements have distinct purposes and a cohesive visual hierarchy.  

**User and context**  
The primary users are professionals or teams managing workflows and communications through the application. They need to navigate and interact with various content cards and inbox items efficiently while maintaining focus on their tasks without visual clutter.  

**Visual direction**  
Adopt a minimalist color palette with a focus on whitespace to enhance clarity and make elements stand out. Utilize accent colors sparingly for call-to-action buttons and essential highlights. Transition from a flat design to one that employs subtle shadows and depth, particularly for cards to signify interaction and importance.  

**Layout and interaction guidance**  
1. Ensure all cards are uniform in size and spacing, creating a balanced feel.  
2. Reassess the button placements within the cards; consider using icons or visual cues that convey their functionality without overcrowding the card design.  
3. Introduce a slight elevation to selected cards within the inbox to create a layered effect, allowing users to focus on one card at a time while retaining context.  

**Surface changes**  
- Remove excessive border or shadowing from the inbox cards to enhance simplicity.  
- Introduce card grouping or distinct section breaks within the inbox to demarcate different types of content, utilizing visual dividers or color blocks.  
- Reassess padding and margin around the buttons to ensure they feel integral without dominating the card's identity.  

**Constraints**  
The design must maintain responsiveness across different devices and screen sizes, ensuring that simplicity and symmetry are preserved without compromising the usability of buttons and interactive elements. Additionally, considerations for accessibility standards must be adhered to.  

**Open questions**  
1. Are there specific actions you want to prioritize within the cards that might influence their design further?  
2. What types of content will be most commonly displayed in the inbox that should dictate card size or layout?  
3. Do you have preferred styles or examples of cards or layouts from other applications that resonate with your vision of simplicity?

### R54 — Improve Main Navigation Clarity and Efficiency

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: The current main navigation lacks clarity and efficiency, causing users to struggle with locating sections and leading to delays in task completion.

**Target user**: Users of the os-control-panel who rely on efficient navigation to perform their tasks.

**Core job-to-be-done**: Users need to navigate the platform quickly and easily to complete their tasks without frustration or delays.

**Success criteria**: Implementation of a simplified navigation structure that increases the task completion rate by at least 20% within the first month after launch, as validated by user feedback and testing.

**Constraints**: The new design must adhere to existing branding guidelines and be compatible with current platform features.

**Out of scope**: Changes to the overall user interface design outside of navigation improvements; any backend modifications not related to navigation.

**Assumptions**: Users will respond positively to the proposed changes and appreciate the simplified navigation structure; sufficient resources will be available for user testing and implementation.

**Open questions**: What specific elements of the current navigation are most confusing to users? How will we measure user satisfaction post-implementation?

### R56 — Main Navigation UI Redesign

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
Existing main navigation lacks clarity and intuitiveness, hindering efficient user workflows for team members managing projects in the control panel.  

**Target user**  
Team members utilizing the control panel for project management.  

**Core job-to-be-done**  
Users need quick and easy access to workspaces, projects, inbox, and new project creation to enhance efficiency in their workflow.  

**Success criteria**  
- Clear and intuitive navigation interface that significantly reduces time spent navigating.  
- Positive user feedback on accessibility and aesthetic appeal in user surveys post-implementation.  
- Increase in usage statistics of navigation elements, demonstrating improved usability.  

**Constraints**  
- Must adhere to existing branding guidelines and color schemes.  
- Design must maintain compatibility with previous UI elements to ensure a cohesive experience.  

**Out of scope**  
- Any functionalities unrelated to navigation, including backend integrations or non-navigation UI features.  

**Assumptions**  
- Users prioritize efficiency and intuitive design in their navigation experience.  

**Open questions**  
- What specific functionalities should be emphasized in the new navigation?  
- Which key user tasks are the top priority for integration into the redesigned navigation?  
- How will responsive behaviors be optimized for different screen sizes in this navigation redesign?

### R55 — UI Improvement for Open Project Page

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: The current 'Open Project' page lacks visual appeal and usability, leading to user frustration and disengagement.

**Target user**: Project managers and team members who frequently navigate projects and require clear visibility of project status and tasks.

**Core job-to-be-done**: Users need to effortlessly navigate between projects while being provided with clear information at a glance, thereby enhancing the overall user experience.

**Success criteria**:
1. Increased user satisfaction ratings post-implementation as measured by surveys.
2. Reduction in navigation time or clicks to access important project information.
3. Positive feedback from user testing sessions regarding the new design.

**Constraints**:
1. Must adhere to existing brand guidelines.
2. User testing feedback must inform design decisions.
3. Must be feasible within the limitations of our current technology stack.

**Out of scope**: Changes unrelated to the 'Open Project' page design, such as adding new functionalities not addressed in the brief.

**Assumptions**: Users value an aesthetically pleasing interface and will respond positively to an improved design that focuses on usability and accessibility.

**Open questions**:
1. What specific user feedback do we have regarding the current interface?
2. Are there brand colors or elements we must adhere to or avoid in the redesign?
3. What functionalities are critical for users to access quickly on this page?

### R58 — Enhance Two-Layer Navigation Clarity

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem Statement:** Users find it challenging to navigate and understand the current two-layer navigation structure due to insufficient visual differentiation. 

**Target User:** Users of the project interface who require clarity in navigating hierarchical navigation options. 

**Core Job-to-be-Done:** Enable users to intuitively identify their navigation level and easily access available options in both main and secondary navigation layers. 

**Success Criteria:**  
1. Increased user satisfaction with the navigation structure as measured by feedback and usability testing.  
2. A clearer distinction between primary and secondary navigation levels as evidenced by usability assessments.  
3. Improved task completion rates without confusion over navigation options during guided user testing sessions. 

**Constraints:** 
- Must align with existing design standards to ensure consistency.  
- The structure of navigation hierarchy must remain intact and not altered fundamentally. 

**Out of Scope:**  
- Any changes that involve rethinking the overall navigation strategy or structure beyond these UI enhancements.  

**Assumptions:**  
- Users are familiar with digital navigation and can articulate their needs for clarity in navigation structures.  

**Open Questions:**  
- Are there existing branding guidelines for color usage?  
- What specific feedback has been collected from users regarding current navigation issues?  
- Can we expect any additional user training or onboarding needs following these changes?

### R57 — Enhance Agent and Mode Selection Layout for Improved Usability

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
Users find it difficult to quickly and intuitively select agents and modes due to the existing layout that creates unnecessary visual distance between these options, hindering usability.  

**Target user**  
Users who need to select agents and modes efficiently, particularly those who may not be familiar with the interface options.  

**Core job-to-be-done**  
Ensure that users can easily and quickly select their preferred agent and mode through an improved layout that enhances clarity and context.  

**Success criteria**  
- Users report a decrease in time taken to select agents and modes in usability tests.  
- Increased satisfaction scores regarding the clarity of the selection process in user feedback.  

**Constraints**  
- Design must adhere to existing branding guidelines and accessibility standards.  
- Implementation should not significantly increase load times or code complexity.  

**Out of scope**  
- Any major redesign of the overall interface that diverges from the focus on agent and mode selection.  
- Changes that would require additional backend functionality not currently planned.  

**Assumptions**  
- Users will benefit from enhanced proximity and visual context between selection elements.  
- Feedback from previous usability tests accurately represents user pain points in the selection process.  

**Open questions**  
- What specific user personas struggle with the current layout?  
- What feedback have users provided about agent and mode selection in previous tests?

### R59 — Improve Project Control Panel Layout

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
The current layout of the Project Control Panel lacks clarity and usability, leading to inefficient navigation and user frustration.  

**Target user**  
Project managers and agents navigating the Project Control Panel who require efficient access to project previews and agent assignments.  

**Core job-to-be-done**  
Users need to quickly view project previews and manage agent assignments without excessive effort or confusion.  

**Success criteria**  
- Increased user satisfaction scores from surveys after implementation.  
- Reduced time taken to access project previews and manage assignments, measured through user analytics.  
- Fewer reported issues regarding navigation and layout.  

**Constraints**  
- Must adhere to existing branding guidelines.  
- Need to be responsive across various screen sizes.  
- Accessibility standards must be met for all features.  

**Out of scope**  
- Major redesign of the entire Project Control Panel interface.  
- Changes to unrelated sections of the product not impacting the Project Control Panel directly.  

**Assumptions**  
- Users are open to changes in layout for improved experience.  
- The repositioning will not conflict with back-end functionalities.  

**Open questions**  
- What specific information should be prioritized within the Project Preview card?  
- Are there additional elements that require repositioning for better workflow?  
- How do users currently interact with the layout and what pain points have they identified?

### R60 — Add Architect and QA surfaces to the shared agent workspace

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**  
The control panel already exposes PM, Experience Designer, UI Designer, and Orchestrator, but Architect and QA still live mostly in docs and terminal tooling. That leaves a gap between the workflow model the OS claims to support and the role surfaces available inside the product.

**Target user**  
Product Director using the control panel to understand structural risk and validation status without leaving the shared agent workspace.

**Core job-to-be-done**  
Inspect architecture-sensitive project state and run a grounded QA validation review from the same shared agent workspace used for the other core roles.

**Success criteria**  
- Architect is available in the shared `Agents` workspace with a clear deterministic review surface.
- QA is available in the shared `Agents` workspace with a deterministic validation surface.
- The Architect surface highlights active structural hotspots and guardrails rather than pretending to be a generic chat.
- The QA surface can run the project validation path and show a clear reliability summary.
- The shared agent selection model remains coherent after adding Architect and QA.

**Constraints**  
- Keep both surfaces deterministic and honest about their limits.
- Do not turn Architect or QA into fake live-chat personas in this slice.
- Reuse the existing project validation path rather than inventing a second QA mechanism.

**Out of scope**  
- Fully conversational Architect threads.
- Fully conversational QA threads.
- Hosted execution or distributed validation infrastructure.

**Assumptions**  
- The control panel benefits from exposing the full workflow shape more truthfully, even when some roles are review surfaces rather than live chats.

**Open questions**  
- Should Architect or QA eventually gain deeper artifact history or run timelines once observability work lands?

### R61 — Add implementation run history and detail inspection

Status: DONE
Priority: HIGH
Effort: M
Description:
Create a real run-observability surface for requirement implementation so the Product Director can inspect active and historical runs without guessing from scattered workflow clues.

Success criteria:
- The UI shows recent implementation runs for the current project.
- The Product Director can open a run and inspect:
  - status
  - timestamps
  - linked requirement
  - summary
  - error state if any
  - available log/output references
- Active, completed, failed, and stale runs are visually distinguishable.
- Sprint-related execution no longer feels opaque when a run is in flight or stuck.

Reason:
- The current workflow has real background run state, but too little in-app visibility into what happened or why a run is still active.

### R62 — Add workflow timeline and artifact outcome history

Status: DONE
Priority: HIGH
Effort: L
Description:
Add a truthful workflow timeline that shows how a requirement or review moved through roles, approvals, clarifications, and state transitions so the OS becomes inspectable instead of merely stateful.

Success criteria:
- The Product Director can inspect a timeline for meaningful workflow items such as:
  - requirements
  - approvals
  - experience findings
  - UI reviews
  - PM clarifications
- The timeline shows:
  - which role acted
  - what artifact was created
  - what approval or routing happened next
  - what final outcome was produced
- “Where did this go?” questions can be answered from the UI without reading raw JSON files.

Reason:
- The OS now completes more work automatically, which is good, but the resulting workflow narrative is still hard to see.

### R63 — Add an in-app quality dashboard

Status: DONE
Priority: HIGH
Effort: M
Description:
Expose validation health directly in the control panel so quality is a visible control-plane concern rather than something only reachable through CLI runners.

Success criteria:
- The UI shows the latest deterministic validation result for a project.
- The Product Director can inspect:
  - pass/fail summary
  - failing cases if any
  - confidence statement
  - when the validation was last run
- The quality surface is clearly separate from implementation state and workflow state.

Reason:
- QA is now present in the agent workspace, but the OS still lacks a dedicated quality surface that makes validation history and status easy to trust.

### R64 — Add requirement-level manual verification and signoff

Status: DONE
Priority: HIGH
Effort: L
Description:
Bring the manual verification process into the control panel so requirement signoff can be tracked in-product instead of through external notes and chat updates.

Success criteria:
- A requirement can have a manual verification plan visible in the UI.
- The Product Director can step through individual verification checks and record:
  - pass
  - fail
  - notes
- Verification progress is tied to the requirement itself.
- Requirement closure/signoff can reference that verification evidence explicitly.

Reason:
- Manual verification proved genuinely valuable, but doing it outside the UI was too painful and easy to lose track of.

### R65 — Add guided test-card flow for manual verification

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Add a guided testing mode where a selected manual test card can stay with the user while they work through the UI, helping them know the current step, what to verify next, and how to record the result.

Success criteria:
- The user can pick a manual verification test case from the UI.
- The chosen test case remains visible while the user navigates the relevant surface.
- The card helps the user:
  - understand the current step
  - know what to verify next
  - record pass/fail without losing context
- The guided card supports requirement-level verification rather than acting as a separate floating workflow system.

Reason:
- During post-test review, the Product Director identified that a guided hovering test-card pattern could make manual testing much more usable and less error-prone.

### R66 — Reorganize project sections around planning, delivery, and quality

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Move project-wide observability and quality surfaces out of the Requirements page so the project UI stays easier to scan and conceptually cleaner.

Success criteria:
- `Requirements` focuses on:
  - sprint planning
  - structured requirements
  - requirement-level manual verification and signoff
- `Delivery` becomes the home for:
  - implementation runs
  - workflow timeline
- `Quality` becomes the home for:
  - deterministic validation signal
- The project UI feels less busy and less conceptually overloaded than when all of those surfaces were stacked into `Requirements`

Reason:
- The new observability and quality features were useful, but placing them on the Requirements page made the page feel too busy and mixed together planning, execution history, and validation concerns.

### R68 — Prepare AI Builder OS for a public GitHub showcase

Status: DONE
Priority: HIGH
Effort: L
Description:
Prepare the workspace and its documentation for publication as a public repository that reflects high engineering and product quality rather than a private in-progress operating directory.

Success criteria:
- The public repo tells a clear story about what AI Builder OS is and how the projects fit together.
- Public-facing docs are tightened so a visitor can understand:
  - what the OS does
  - what the control panel does
  - what the projects demonstrate
  - how to run at least one meaningful surface locally
- Local-only operational residue is either removed from the public repo narrative or clearly separated from durable source-of-truth files.
- The repo includes a clean publication checklist covering:
  - public-safe data/state
  - README quality
  - screenshots or demo media
  - setup instructions
  - validation instructions
- The resulting repository is something the Product Director would be comfortable using as a public GitHub showcase.

Reason:
- The repository now needs a polished public-facing presentation in addition to internal product iteration.

### R69 — Build a public Streamlit showcase for AI Builder OS

Status: DONE
Priority: HIGH
Effort: L
Description:
Create a public-facing Streamlit showcase that explains and demonstrates AI Builder OS in a polished, shareable way without exposing the raw operator control panel as the primary public demo.

Success criteria:
- The workspace has a dedicated public showcase app that can be deployed independently from the repo.
- The showcase explains:
  - what AI Builder OS is
  - how the agent workflow operates
  - what the main project surfaces are
  - what example projects demonstrate
- The showcase remains honest about what is real, local-first, or still evolving.
- The showcase is visually stronger and more curated than the operator control panel.
- The showcase can be deployed from the public repo with a clear Streamlit deployment path.

Reason:
- The control panel is useful for operation, but it is not the best primary public demo surface for explaining the OS to new visitors.

### R70 — Align the public showcase with the final public GitHub repo

Status: DONE
Priority: HIGH
Effort: S
Description:
Prepare the public showcase so its repository links and publication instructions can point cleanly at the final public GitHub destination without requiring ad hoc code edits at publish time.

Success criteria:
- The showcase repo links can be redirected to the final public GitHub repo through one explicit configuration point.
- Showcase documentation explains how to set that public repo target.
- The publication checklist includes the repo-link alignment step.
- The current placeholder repo links remain usable until the final public repo exists.

Reason:
- The showcase is ready before the final public GitHub destination is finalized, so link alignment needs a clean handoff path instead of hidden hardcoded edits.

### R71 — Final showcase polish and Streamlit publish readiness

Status: NEW
Priority: HIGH
Effort: M
Description:
Do the final UX and deployment polish needed to make the public Streamlit showcase feel finished and ready for public publishing.

Success criteria:
- The showcase pages feel visually consistent, calm, and intentional across sections.
- The main public actions are obvious and audience-appropriate.
- The final public GitHub repo links are correct.
- The Streamlit publishing path is documented clearly enough to execute without guesswork.

Reason:
- The showcase now exists and tells the right story, but it still needs one final polish-and-publish pass before it should be treated as the public front door.

## Backlog (Not yet prioritised)

### R3 — Add deeper workflow execution controls

Status: BACKLOG
Priority: MEDIUM
Effort: L
Description:
Allow the UI to move beyond view-first workflow visibility into selectively triggering orchestration or agent execution from the control panel.

### R2 — Support remote/shared access

Status: BACKLOG
Priority: MEDIUM
Effort: L
Description:
Extend the OS Control Panel beyond local-first operation so invited collaborators can use it remotely with an appropriate sharing and access model.

### R4 — Add a lightweight next-action recommendation surface

Status: BACKLOG
Priority: MEDIUM
Effort: S
Description:
Show a lightweight next recommended action in the control panel without turning V1 into a full orchestration console.

### R43 — Improve Inbox card layout balance

Status: BACKLOG
Priority: MEDIUM
Effort: M
Description:
Problem statement
- The current full-width inbox cards create visual clutter and make it harder to scan workflow items quickly.

Target user
- Product Director using the OS control panel Inbox to manage approvals and active workflow items.

Core job-to-be-done
- Review workflow items efficiently without the Inbox feeling visually heavy or repetitive.

Success criteria
- Inbox items are easier to scan at a glance.
- Card layout feels more balanced and less monotonous.
- Layout changes preserve clarity for approvals, waiting items, and routed workflow state.

Constraints
- Keep the Inbox local-first and workflow-focused.
- Preserve readability of item details and actions.

Out of scope
- Broad redesign of the entire control panel visual system.

Assumptions
- Better balance and hierarchy in the Inbox will improve scanability and reduce perceived clutter.

Open questions
- Should Inbox cards use multiple columns, stronger grouping, or denser summaries?

### R49 — Launch a broader workspace visual redesign initiative

Status: BACKLOG
Priority: LOW
Effort: L
Description:
Residual workspace-level visual direction that remains after the narrower navigation, inbox, project-control, and role-card improvements already shipped through R45, R47, R48, R52, R54, R57, R58, and R59.

Success criteria:
- Any future workspace redesign work clearly identifies what still remains beyond the already-completed simplification and layout slices.
- The requirement acts as the single residual container for broader workspace redesign ideas instead of spawning overlapping backlog duplicates.
- Future approved UI reviews that still belong to this theme should consolidate here unless they truly introduce a distinct product problem.

Reason:
- Earlier design-review completion paths created broad overlapping workspace/UI initiatives. This requirement now serves as the remaining broad workspace-design container instead of competing with completed narrower slices.

---

## Rules

* Only requirements with Status: NEW should be converted into tasks
* Requirements move from:
  NEW → IN_PROGRESS → DONE
* PM agent must NOT generate tasks for DONE items

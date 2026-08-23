# Product: OS Control Panel

## Problem

AI Builder OS currently operates through files, prompts, and command-line workflows. That makes it powerful, but slower and less intuitive to use when starting new projects, capturing requirements, prioritising work, and understanding what the agents are doing. A local UI is needed to make the OS easier to operate without replacing the underlying file-based system.

## Goal

Build a local-first control panel for AI Builder OS that helps the operator create projects, shape requirements through agent-guided workflows, inspect delivery and quality state, and operate the OS without leaving the underlying file-based system behind.

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
- Structured requirement cards/forms and sprint planning surfaces
- Shared agent surfaces for live and deterministic role workflows
- Delivery and quality inspection surfaces grounded in file-backed project state

### Persistence

- Persist project state through the existing AI Builder OS file structure
- Save approved requirements into `product/requirements.md`
- Persist active agent-thread state in a lightweight file-backed way when the project uses guided agent interaction

### UI / API / Automation

- Workspace summary page is the primary entry point
- Project drill-down page supports:
  - requirements
  - agent workspace
  - delivery inspection
  - quality review
- PM requirement discovery should run as a PM-first chat flow:
  - idea input
  - PM clarifying questions in-thread
  - draft requirements for review
- Deterministic Architect, QA, and Orchestrator surfaces should complement the live PM, Experience Designer, and UI Designer flows
- The control panel may trigger scoped implementation or validation actions when they stay aligned with the underlying workflow model

## Constraints

- Must remain a local-first operator tool in the current product slice
- Must build on the existing AI Builder OS structure rather than replace it
- Must keep the UI simple and avoid clutter from long conversational history or overloaded project surfaces
- Must preserve file-backed product truth instead of replacing it with hidden UI-only state
- Must use structured requirement cards/forms rather than raw markdown editing as the primary requirement-editing experience
- Must present concise summaries instead of raw agent traces or heavy debugging surfaces in the default UI
- Must not turn the control panel into a full execution IDE or workflow-control console
- Must not collapse the operator surface into the public showcase app

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
  - a shared agent workspace with live and deterministic role surfaces
  - PM requirement drafts
  - delivery and quality inspection surfaces grounded in project state

## Current Limitations

- The control panel is still local-first only
- The control panel does not provide unrestricted full-agent execution control
- Editing project memory or rules is not a primary in-product workflow
- PM discovery should stay lightweight, focused on the active PM thread and the reviewed draft rather than a visible archive
- Visible PM chat history should stay lightweight and focused on the active thread rather than a large visible archive
- The operator surface should prefer summaries and grounded inspection over raw internal traces or debugging consoles

## Out of Scope

- Remote/shared multi-user access in the current slice
- Unrestricted PM -> Engineer -> QA workflow control from the UI
- Manual workflow-state editing that bypasses durable artifacts
- Editing project memory or rules as a primary workflow
- Full raw agent traces or internal debugging consoles as the main operator experience

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
Product Directors and operators navigating the project detail surface who need quick access to project identity, preview access, and local workflow context.  

**Core job-to-be-done**  
Users need to quickly orient themselves inside a project and reach the relevant project controls without excessive effort or confusion.  

**Success criteria**  
- The project control area clearly communicates project identity and available utility actions.  
- Preview access is easy to reach without overpowering the main project workflow.  
- The layout causes less navigation friction and fewer reported usability issues.  

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
- The publication process is documented clearly enough that public-safe data/state, README quality, demo media, setup instructions, and validation instructions can be reviewed before a public refresh.
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
- Repo-link alignment is part of the publication process for the showcase.
- The showcase can point cleanly at the final public repo without hidden code edits.

Reason:
- The showcase is ready before the final public GitHub destination is finalized, so link alignment needs a clean handoff path instead of hidden hardcoded edits.

### R71 — Final showcase polish and Streamlit publish readiness

Status: DONE
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

### R49 — Launch a broader workspace visual redesign initiative

Status: DONE
Priority: LOW
Effort: L
Description:
Residual workspace-level visual direction that remains after the narrower navigation, inbox, project-control, and role-card improvements already shipped through R45, R47, R48, R52, R54, R57, R58, and R59.

Experience Designer guidance:
- Treat the residual issue as experience-debt consolidation rather than a fresh mandate to redesign the workspace again.
- Future work must name the concrete user workflow friction that remains after the shipped simplification slices.
- If the evidence points to a distinct workflow problem, PM should split that into a focused requirement instead of keeping it hidden inside R49.

UI Designer guidance:
- Treat native Streamlit structure, clear hierarchy, restrained spacing, and existing card/navigation patterns as the default design system.
- Do not add a new visual system, component dependency, or broad restyle unless a focused review shows that native Streamlit patterns cannot solve the specific usability issue cleanly.
- Decompose any future workspace visual work into small, reviewable slices with a stated affected surface and validation path before engineering.

Success criteria:
- Any future workspace redesign work clearly identifies what still remains beyond the already-completed simplification and layout slices.
- The requirement acts as the single residual container for broader workspace redesign ideas instead of spawning overlapping backlog duplicates.
- Future approved UI reviews that still belong to this theme should consolidate here unless they truly introduce a distinct product problem.

Reason:
- Earlier design-review completion paths created broad overlapping workspace/UI initiatives. This requirement now serves as the remaining broad workspace-design container instead of competing with completed narrower slices.

### R43 — Improve Inbox card layout balance

Status: DONE
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

### R72 — Add a private interactive reflection helper

Status: DONE
Priority: HIGH
Effort: M
Description:
Add a private-first reflection helper to the OS so raw signals can be clarified into stronger structured reflections instead of being captured as one-shot notes only.

Success criteria:
- The OS provides a local-only reflection workflow that starts from a raw signal.
- The helper asks a small set of clarifying questions rather than only storing the original note.
- The interaction helps separate:
  - observation
  - interpretation
  - implication
  - confidence
- The result can be saved as a stronger reflection draft in the private reflection layer.
- The workflow feels lightweight enough to use repeatedly during normal OS use.
- The questioning should be context-specific enough that the helper feels like reflective assistance rather than a static form.

Constraints:
- Keep this private-first and local-only in the first slice.
- Keep raw operator reflection content out of public showcase or public-facing repo surfaces.
- Do not overbuild a broad reflection dashboard before the helper pattern is proven useful.
- Prefer a narrow workflow that improves refinement over a large storage or analytics surface.
- Keep any future live-agent interaction bounded so the helper still produces a structured reflection draft rather than becoming an unbounded journal chat.

Reason:
Real usage showed that the value of the reflection layer came from back-and-forth clarification. The next useful step is to make that clarification behavior part of the OS itself.

Validation note:
- The first implemented slice proved that in-product reflection capture is useful and that structured private draft saving works.
- The bounded dynamic-questioning follow-on made the helper meaningfully more context-specific while keeping it lightweight.
- Manual validation confirmed the dynamic helper was better enough to carry forward as the V2 reflection pattern.

### R73 — Add a private interactive concept-learning helper

Status: DONE
Priority: HIGH
Effort: M
Description:
Add a private-first concept-learning helper to the OS so concepts encountered during building can be clarified in context rather than being noted and forgotten.

Success criteria:
- The OS provides a local-only learning workflow that starts from a concept or unfamiliar term.
- The helper clarifies what the concept is, why it exists, and where it appears in the OS.
- The interaction connects concept -> implementation -> product implication.
- The result can be saved into the private learning layer as a stronger concept note or draft.
- The workflow feels useful for credibility-building rather than generic note-taking.
- The helper should actively teach or explain in context before asking the operator to crystallize the learning note.

Constraints:
- Keep this private-first and local-only in the first slice.
- Do not turn the helper into a generic study tool detached from implementation.
- Prefer a bounded helper flow over a large learning dashboard.
- Keep any future teaching/explainer behavior bounded so the helper still converges toward a saved concept note rather than becoming an open-ended tutor chat.

Reason:
Real usage showed that credibility requires a concept learning layer, not just reflection. The next useful step is to make concept clarification part of using the OS itself.

Validation note:
- The first implemented slice proved that in-product concept-note capture is useful and that structured private draft saving works.
- Manual validation also showed that clarification prompts alone do not feel like learning.
- R73 was the proving slice for in-product concept learning.
- Its teaching and clarification responsibilities have now been absorbed into the broader live learning-agent initiative under `R74`.
- The older helper-era requirement is therefore complete as a delivered foundation rather than the active learning frontier.

### R75 — Learning Tab UI Improvement Implementation

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: Users find the current Learning tab cumbersome and visually overwhelming, making it difficult to efficiently navigate learning materials.

**Target user**: Individuals using the os-control-panel for engaging with various learning materials, ranging from beginners to advanced learners.

**Core job-to-be-done**: Users need a streamlined interface that allows for quick access to information, enabling them to focus on learning without distractions.

**Success criteria**:
1. Increased user engagement and satisfaction scores for the Learning tab post-implementation.
2. Reduction in reported user frustrations related to navigation and visual clutter on the Learning tab.
3. Positive feedback from usability testing sessions with target users before and after changes.

**Constraints**:
- The existing color palette and typography must remain consistent with the brand.
- Accessibility standards must be upheld, specifically regarding contrast ratios and keyboard navigation.
- The overall layout grid system needs to stay intact to ensure integration with other tabs and features.

**Out of scope**:
- Major redesigns that deviate from the existing brand identity are not included.
- Adding new features or content types that are not currently part of the Learning tab's functionality.

**Assumptions**:
- Users will respond positively to simplified navigation and a calmer interface.
- The removal of visual clutter will effectively enhance usability and focus.

**Open questions**:
- Resolved from the current R74 implementation and review artifacts: prioritize resuming an active learning session, starting the featured recommendation, and finding/opening a concept.
- Documented pain points are cognitive overload, excessive vertical navigation, multiple same-weight tools, and loss of orientation when moving between recommendations, sessions, concept management, build-to-learn, and profile context.

**Validation note**:
- Experience Designer and UI Designer guidance was captured before implementation in `product/learning-tab-ui-guidance-R75.md`.
- Active-session routing, featured recommendation hierarchy, and compact secondary recommendations were implemented without changing learning-state semantics.
- 176/176 unit tests and 184/184 project eval checks passed.
- Live Streamlit socket smoke was unavailable because the managed sandbox prohibits local port binding.

### R76 — Complete the bounded live-agent operating model

Status: DONE
Priority: HIGH
Effort: XL
Description:
Complete the missing agent foundations across AI Builder OS so live model-backed roles operate through one inspectable, bounded runtime instead of isolated model calls.

Success criteria:
- PM, Experience Designer, UI Designer, and the learning agent use canonical role instructions plus shared runtime guardrails.
- Live roles can dynamically request a small set of read-only project-context tools before producing a final structured response.
- Every live run has explicit step, retry, timeout, and human-hand-back limits.
- Tool definitions carry risk ratings and action tools remain behind explicit human approval.
- Inputs receive deterministic relevance, prompt-injection, sensitive-data, and length checks before model execution.
- Outputs receive structured validation and grounding checks before they are accepted.
- Orchestrator keeps deterministic routing as authority and can use a bounded live manager review for ambiguous workflow interpretation without silently mutating project state.
- Live-agent calls and tool use produce inspectable trace records without exposing hidden reasoning.
- The project has live-agent quality and trace evaluation coverage that can distinguish acceptable runs from guardrail, routing, and completion failures.
- Runtime prompts are composed from canonical role documents so documented and executed behavior do not drift silently.

Constraints:
- Preserve deterministic routing, file-backed product truth, and existing approval boundaries.
- Do not give conversational agents unrestricted filesystem or command execution.
- Do not let the live manager bypass deterministic policy or directly mutate workflow state.
- Keep all write actions reversible or human-approved.
- Preserve existing live-agent UI flows and current R74 tutoring work.

Reason:
The OS currently contains one full execution agent and several bounded model interactions. It needs shared tools, run controls, layered guardrails, traceability, live-quality evaluation, and prompt alignment before broader autonomy can be trusted.

Validation note:
- PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator Workflow Review now use the shared bounded runtime.
- Canonical prompts compose the system, workflow, role, turn, tool, and runtime-boundary instructions.
- Read-only tools are role-allowlisted and risk-rated; write and execution tools remain approval-gated and unavailable to automatic model tool use.
- Input, output, tool-authorization, retry, timeout, step-budget, and human-hand-back controls are active.
- Redacted model-call, model-response, tool, completion, error, and hand-back traces are persisted for evaluation.
- Orchestrator Next Step remains deterministic; Workflow Review adds an advisory live manager review that cannot mutate state.
- Full validation passed with 195 unit tests plus 8 scenarios: 203/203.
- A real bounded PM model turn completed and its captured-trace evaluation passed: 1/1.

### R77 — Add operational dashboards for agents and workflow health

Status: DONE
Priority: HIGH
Effort: L
Description:
Add one coherent Operations area that turns existing agent traces, workflow artifacts, quality records, implementation runs, approvals, and learning state into useful operating dashboards.

Success criteria:
- Agent Operations shows recent live runs, status, duration, attempts, steps, tools, guardrails, and hand-backs.
- Agent Quality shows trace-eval status and completion, hand-back, error, and guardrail signals by role and project.
- Workflow Health shows requirements, tasks, blocked work, stale work, approvals, clarifications, routed findings, and active implementation.
- Human Oversight shows pending approvals, their source and risk context, and high-risk capabilities that remain approval-gated.
- Agent Performance compares completion rate, hand-back rate, retries, steps, and tool use by role.
- Tool Usage shows invocation volume, role usage, denials/errors, and unused registered tools.
- Learning Progress shows learned, in-progress, upcoming, active-session, clarification, build-to-learn, and hand-back signals.
- System Activity provides one recent chronological view across live-agent runs and file-backed workflow events.
- Dashboard calculations use existing file-backed sources and do not introduce a second source of truth.
- Empty, partial, and legacy trace data render safely.

Constraints:
- Keep the interface quiet, operational, and optimized for scanning.
- Reuse existing navigation, metrics, filters, cards, and workflow terminology.
- Do not surface internal analytical text or unredacted sensitive data.
- Do not add write actions to analytical dashboards beyond existing approval controls.
- Keep project-level Delivery and Quality views intact.

Reason:
The bounded agent runtime is now functional, but its evidence is spread across several surfaces. Operators need a single place to understand what agents are doing, whether they are reliable, where workflow is blocked, and when human attention is required.

Validation note:
- Added a top-level Operations destination with all eight requested dashboards.
- Dashboard data is joined from existing redacted traces, requirements, tasks, approvals, clarifications, findings, implementation runs, quality reviews, learning state, and workflow events.
- Legacy and partial traces are handled without breaking the surface.
- Focused aggregation tests cover completed, hand-back, legacy, retry, tool, denied-tool, navigation, and workflow-join cases.
- Full project validation passed: 210/210.
- Streamlit AppTest rendered Operations with all eight tabs, eight data tables, and zero exceptions.
- The running local server returned HTTP 200.
- Every Operations board now includes a plain-language purpose description, and every table column includes hover help explaining the value it represents.
- Post-description validation passed: 222/222.

### R78 — Complete the agent evaluation system

Status: DONE
Priority: HIGH
Effort: L
Description:
Complete the OS evaluation system so output quality, tool selection, workflow, memory, safety, cost, latency, and reliability are all explicit, executable evaluation dimensions rather than partial checks or operational telemetry.

Success criteria:
- Output-quality contracts can require grounded content and reject forbidden or unsupported content.
- Tool-selection evals detect missing, unnecessary, unauthorized, and incorrectly ordered tool calls.
- Workflow evals continue to validate routing, handoffs, state cleanup, and terminal outcomes.
- Memory evals verify required recall, stale-memory rejection, persistence, and deliberate memory-tool use.
- Safety evals continue to validate injection resistance, authorization, redaction, bounded execution, and human hand-back.
- Live-agent traces capture input tokens, output tokens, estimated model cost, model-call latency, tool latency, and end-to-end duration.
- Cost and latency evals enforce explicit per-run budgets and fail when measurements are absent.
- Reliability evals enforce minimum sample sizes and pass-rate thresholds across repeated outcomes.
- One project eval command executes all eight evaluation dimensions.
- Operations shows an Eval Coverage board explaining which projects and agents use each eval type.

Constraints:
- Preserve existing deterministic workflow authority and approval boundaries.
- Keep legacy traces readable when newer cost and timing fields are absent.
- Do not surface internal prompt text or unredacted sensitive content.
- Keep model pricing isolated and replaceable as provider pricing changes.

Reason:
The first agent runtime established trace integrity and guardrails, but tool choice and memory remained partial while cost and latency were telemetry-only. A complete evaluation system is required before agent autonomy or model usage expands.

Validation note:
- Added reusable evaluators and explicit fixtures for all eight evaluation dimensions.
- Tool-selection grading detects missing, unnecessary, unauthorized, and incorrectly ordered calls.
- Memory grading checks required facts, stale facts, and required memory-tool use.
- Live traces now capture model tokens, estimated cost, model-call latency, tool latency, and end-to-end duration.
- Model pricing has a replaceable environment configuration through `AI_BUILDER_OS_MODEL_PRICING_JSON`.
- Agent Operations now displays token and estimated-cost evidence; Eval Coverage maps every eval type to projects, agents, and concrete checks.
- Focused validation passed: 21/21.
- Capability evals passed: 8/8.
- Full project validation passed: 244/244.
- Streamlit AppTest rendered all nine Operations boards and nine data tables with zero exceptions.

### R79 — Add eval-case drill-down to Operations

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Let operators inspect the concrete fixtures behind Eval Coverage instead of seeing only a summary of which evaluation dimensions exist.

Success criteria:
- Eval Coverage shows the number of configured eval cases.
- Cases can be filtered by project and eval type.
- Each case exposes its title, agent or component, description, expected behavior, case ID, and source fixture.
- The full case payload can be opened on demand without cluttering the default board.
- The catalog includes OS capability contracts, OS workflow scenarios, ParentMate replay fixtures, Career Guidance cases, Dream Translator cases, and code-defined Trip Planner cases.

Constraints:
- Read directly from existing fixtures and runners rather than creating a duplicate eval database.
- Do not execute eval suites merely to render the dashboard.
- Keep large payloads collapsed until requested.

Reason:
Coverage summaries are useful for orientation, but practical debugging and review require direct access to the cases that define expected behavior.

Validation note:
- Added a normalized read-only catalog over existing JSON fixtures, workflow scenarios, replay-backed email pairs, and code-defined planner assertions.
- The catalog exposes 57 cases across os-control-panel, ParentMate, Career Guidance, Dream Translator, and Trip Planner.
- All eight eval types remain represented in the inspectable case catalog.
- Eval Coverage now supports project and eval-type filters, a case selector, expected-behavior details, source details, and a collapsed full-payload view.
- Focused validation passed: 13/13.
- Full project validation passed: 246/246.
- Streamlit interaction validation filtered ParentMate output-quality cases, selected a fixture, and rendered three detail code blocks plus the full-payload expander with zero exceptions.

### R80 — Show the complete agent roster in quality dashboards

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Keep every configured OS agent visible in Agent Quality and Agent Performance, even when a role has not yet produced a bounded live trace.

Success criteria:
- PM, Experience Designer, UI Designer, Learning Agent, Architect, Orchestrator, Engineer, and QA always appear.
- Each role shows its execution mode.
- Bounded live roles with no runs show `No captured live runs`.
- Architect, Engineer, and QA state that they use separate validation paths.
- Completion displays `No runs` rather than a misleading zero-percent quality score when no evidence exists.
- Projects without a live trace stream display `NO LIVE TRACES` rather than `NEEDS ATTENTION`.

Constraints:
- Do not fabricate run evidence for inactive roles.
- Preserve actual trace-derived metrics when runs exist.
- Keep live-trace quality distinct from deterministic and execution validation.

Reason:
Evidence-only rendering hid configured agents and made the dashboard appear incomplete. Operators need the full roster and an honest explanation of what evidence exists for each role.

Validation note:
- Agent Quality and Agent Performance now always show PM, Experience Designer, UI Designer, Learning Agent, Architect, Orchestrator, Engineer, and QA.
- Each role identifies its execution mode and whether live traces or a separate validation path provide its evidence.
- Roles without runs display `No runs`; bounded live roles explicitly display `No captured live runs`.
- Projects without a trace stream now display `NO LIVE TRACES` rather than a false failure signal.
- Focused validation passed: 17/17.
- Full project validation passed: 249/249.
- Streamlit AppTest rendered both complete eight-row role tables with zero exceptions.

### R81 — Deploy the Learning Agent for an invite-only external pilot

Status: DONE
Priority: HIGH
Effort: XL
Description:
Create an authenticated, user-isolated hosted wrapper for the external V2 Learning Agent experience that can be shared externally without exposing the wider AI Builder OS.

Success criteria:
- A hosted wrapper Streamlit entry point exposes only the external V2 Learning Agent experience.
- The hosted release uses the external V2 learning profile.
- OIDC authentication provides a stable identity for every learner.
- An optional email allowlist can support trusted cohorts without being the only access path.
- Learning profiles, sessions, concept state, notes, and agent traces are isolated per authenticated user.
- Existing local OS learning data continues to use its current private paths.
- The app has Docker, Railway, and Render deployment configuration with health checks and secrets guidance.
- Persistent hosted state survives restart and redeploy in the single-replica pilot.
- The interface explains the hosted privacy boundary and provides a data-contact route.
- The hosted wrapper gives external learners a clear product shell that explains what the Learning Agent is, how the guided flow works, and what to expect from the pilot.
- The hosted project includes a concrete pre-launch checklist and pilot operator runbook covering env vars, auth, allowlisting, persistence, smoke checks, and invite readiness.
- The hosted project includes a machine-checkable preflight validator for the invite-only pilot configuration.
- The hosted project includes a top-level launch plan checklist that shows the full path from scope freeze to first invited learners.
- The database-backed beta and production deployment phases are documented.

Constraints:
- Keep the pilot to one application replica while hosted state remains file-backed.
- Keep the hosted surface limited to learning and exclude Operations, project management, and implementation surfaces.
- Never commit OpenAI or OIDC credentials.
- Do not claim the deployment is live until hosting credentials, DNS, and the external service are configured.

Reason:
The Learning Agent is valuable beyond the private OS, but the current local application assumes one learner and one filesystem. External use requires a deliberately separate hosted surface and a real tenancy boundary, while keeping canonical learning behavior owned by `os-control-panel`.

Validation note:
- Hosted external-V2 wrapper entry point, OIDC/local authentication modes, invited-email allowlisting, and per-user learning/tracing isolation are implemented.
- Railway, Render, Docker, health-check, persistent-volume, Streamlit, secrets, and operator guidance are present under `projects/learning-agent`.
- Hosted AppTest passed with zero exceptions and without exposing Operations.
- Targeted hosted/runtime validation passed: 226/226.
- Full project validation passed: 262/262.
- Real Railway deployment, OIDC sign-in, persistent-volume restart/redeploy behavior, guest-mode entry, and authenticated user isolation were later verified externally.
- The hosted Learning Agent project now counts as delivered infrastructure for the current OS surface.

### R83 — Tighten the project-level operator loop

Status: DONE
Priority: HIGH
Effort: M
UI Runtime: streamlit
Description:
Make the project-detail page feel more like one coherent operating loop instead of a set of adjacent sections.

Success criteria:
- Opening a project immediately shows the current workflow state in plain language.
- The operator can see the best next move without having to infer it from multiple panels.
- The project page clearly points the operator toward the most relevant section for the current state.
- Project-level workflow signals such as approvals, clarifications, active threads, active runs, and quality status are visible without leaving the project page.
- The added orientation layer stays lightweight and does not turn the project surface into a workflow console.

Constraints:
- Reuse existing OS workflow truth and recommendation logic instead of inventing a parallel status model.
- Keep the current four-section structure: Requirements, Agents, Delivery, Quality.
- Do not expand this work into deeper workflow execution controls.
- Prefer concise summaries and recommended movement over dense dashboards.

Reason:
The OS already has real workflow state, but the project-detail experience still asks the operator to choose a section before the page has properly oriented them. Tightening this loop should make the existing system feel calmer, more legible, and more intentional without changing the underlying workflow model.

### R84 — Add a policy-gated GitHub delivery publication layer

Status: DONE
Priority: HIGH
Effort: M
Description:
Add a GitHub integration slice as a publication layer that can prepare delivery artifacts from canonical OS truth, preserve the local public/private boundary, and publish approved artifacts to GitHub after explicit human approval.

Success criteria:
- The OS can draft a GitHub issue body from a canonical requirement.
- The OS can draft a GitHub pull request description from a sanitized implementation-run summary.
- The OS can draft a GitHub evaluation summary from the current deterministic quality review.
- Every GitHub publication draft passes through a policy checker before it can become an approval request.
- The policy checker blocks ignored private paths, local runtime state, trace internals, local temp paths, secrets, and private-planning language.
- Low-risk contact information is redacted from publication payloads.
- GitHub publication drafts appear in the existing Inbox approval flow for human preview.
- Approving a GitHub issue or evaluation-summary draft publishes it to GitHub when `AI_BUILDER_OS_GITHUB_TOKEN`, `GITHUB_TOKEN`, or `GH_TOKEN` is configured.
- Approving a GitHub PR-description draft updates the open PR for the current branch when a matching PR exists.
- Successful publication records the GitHub URL, reference id, and publication state on the approval record.
- Failed GitHub configuration or API calls leave the approval open and show a setup/publish error.
- The GitHub publishing action is represented as a high-risk, approval-required capability.

Constraints:
- Do not bypass the existing local publication policy.
- Do not publish raw agent traces, implementation logs, runtime state, private planning, local secrets, or local-only notes.
- Do not auto-close issues, auto-merge PRs, or mutate GitHub state beyond approved issue creation, evaluation-summary issue creation, or PR description updates.
- Keep publishing credential-driven and explicit; do not silently publish without approval.

Reason:
Codex can already push and raise PRs on request, but AI Builder OS needs GitHub delivery state to become part of its operating model. The first safe step is not raw write access; it is a policy-gated publication draft path that keeps the OS's local privacy boundary intact.

Validation note:
- Added reusable GitHub publication policy and draft builders.
- Added Delivery actions for issue, PR-description, and eval-summary drafts.
- Added Inbox preview support for GitHub publication approvals.
- Added approval-resolution behavior that publishes approved drafts to GitHub through the GitHub REST API and records the resulting URL.
- Added `publish_to_github` as a high-risk approval-gated capability.

### R85 — Gate requirement completion through release delivery approval

Status: DONE
Priority: HIGH
Effort: M
Description:
Bake GitHub publication and code delivery into the OS requirement lifecycle so an attempted move to `DONE` creates one release approval bundle instead of requiring a separate manual Delivery draft flow.

Success criteria:
- When a requirement is marked `DONE` from the Requirements UI, the OS creates a release delivery approval and keeps the requirement in its prior status until approval.
- When a completed sprint implementation is continued, the sprint pauses on a release delivery approval instead of treating completion as an ambiguous block.
- The release approval shows requirement details, implementation summary, quality summary, GitHub issue content, approved files to commit, excluded files, branch, and proposed commit message.
- Approving the release marks the requirement `DONE`, publishes the GitHub issue, commits the approved public files, pushes the branch, and records GitHub/git outputs on the approval.
- Private paths, local runtime state, implementation logs, trace files, env files, and secret-like files are excluded from the commit plan.
- Failed GitHub or git delivery leaves the approval unresolved and shows the error to the operator.

Constraints:
- Do not silently mark a requirement `DONE` when external delivery approval is required.
- Do not stage ignored local/private/runtime files.
- Do not push code without an explicit human approval from Inbox.
- Keep the manual Delivery draft actions available as escape hatches, but make release approval the main workflow.

Reason:
The OS should behave like a delivery operating system, not a pile of manual publishing buttons. Completion is the natural moment to gather product truth, implementation evidence, quality evidence, GitHub artifacts, and code delivery into one reviewable decision.

Validation note:
- Added release delivery approval creation from `DONE` transitions.
- Added sprint completed-implementation release gate.
- Added approval execution for requirement completion, GitHub issue publishing, git commit, and push.
- Added Inbox review details and approval labels for release delivery.
- Added focused release-delivery unit coverage.

### R86 — Add project type capability profiles

Status: DONE
Priority: HIGH
Effort: M
Description:
Classify projects as either Streamlit apps or web apps at creation time, then let the OS use that classification as a capability profile for scaffolding, preview, implementation guidance, release expectations, and deployment provider defaults.

Success criteria:
- New-project creation asks for project type before live PM discovery starts.
- The selected project type survives live PM discovery and reviewed-draft project creation.
- Streamlit app projects keep the existing Streamlit preview and hosted-Python expectations.
- Web app projects scaffold a Vercel-compatible Next.js starter and preview through `npm run dev`.
- Engineer implementation prompts include project-type capability guidance.
- Release delivery approvals include project type, default deployment provider, and release expectation.
- Web app capability profiles include Next.js, shadcn/ui, browser verification, Vercel deployment/env/log readiness, AI SDK/AI Elements, storage, auth, functions, and observability decision points.
- Web app release approvals include readiness checks for package scripts, Next.js route entry, shadcn/ui config, Vercel config, environment-variable documentation, browser verification, and Vercel preview verification.
- Approved web app release deliveries look up the matching Vercel deployment by pushed commit and branch, then record preview URL/status metadata on the approval.
- Project cards and requirement metadata expose project type without adding a separate Vercel dashboard.

Constraints:
- Keep Vercel as a web-app capability, not as a standalone dashboard surface.
- Do not force current Streamlit projects into a web-app deployment shape.
- Preserve existing `product/ui-runtime.json` compatibility while presenting the concept as project type in the UI.
- Keep the first version bounded to `streamlit` and `web_app`; do not over-model framework variants before they are needed.

Reason:
AI Builder OS needs to decide how a project should be built and delivered before implementation starts. Streamlit and Vercel-backed web apps have different scaffolds, preview commands, validation expectations, and release paths, so project type should be a native OS capability profile.

Validation note:
- Added project runtime capability profiles for Streamlit apps and web apps.
- Added web-app/Next.js scaffold files for web app projects.
- Added web app preview routing through `npm run dev`.
- Added project-type selection to new project creation and reviewed draft creation.
- Added project-type release metadata and Engineer prompt guidance.
- Added Vercel plugin-derived web-app capability pack guidance.
- Added web-app release readiness checks to release approvals.
- Added Vercel preview deployment lookup after approved web-app release push.
- Added focused runtime, preview, release, and prompt tests.

### R87 — Enforce deployment provider defaults by project type

Status: DONE
Priority: HIGH
Effort: S
Description:
Make deployment provider selection a native project-type rule so Streamlit/Python-service work defaults to Railway and Next.js/React web-app work defaults to Vercel.

Success criteria:
- Streamlit projects use Railway as the default deployment capability.
- Web app projects use Vercel as the default deployment capability.
- Release delivery approvals expose the provider default from the project capability profile.
- Streamlit release readiness checks refer to Railway service compatibility rather than Vercel preview behavior.
- Web app release readiness and preview lookup remain Vercel-specific.
- The project detail surface shows the default deployment capability beside the selected project type.

Constraints:
- Do not replace Railway with Vercel globally.
- Do not force Streamlit projects into a Vercel-shaped workflow.
- Do not add a separate deployment dashboard for this rule.
- Keep provider choice derived from project type unless a future explicit override is introduced.

Reason:
Railway and Vercel are both useful, but for different OS project shapes. Railway is the right default for Streamlit, Python services, workers, and backend-style deployments. Vercel is the right default for browser-native Next.js/React web apps with preview deployments.

Validation note:
- Streamlit runtime profile now defaults to Railway.
- Web app runtime profile remains Vercel-backed.
- Added Streamlit/Railway release readiness checks.
- Added project-detail default deployment capability copy.
- Added focused tests for Streamlit/Railway and web-app/Vercel separation.

### R88 — Require Playwright browser verification for web app releases

Status: DONE
Priority: HIGH
Effort: M
Description:
Move web-app release readiness from advisory browser QA language to an enforced Playwright evidence gate before Vercel-bound release approval.

Success criteria:
- The repo includes a Playwright-based web-app verification runner.
- The runner starts the web app dev server, opens real browser pages, captures desktop and mobile screenshots, records console/page errors, checks horizontal overflow, and exercises visible interaction targets.
- Browser verification writes structured evidence into the project `product/` folder.
- Web app release readiness fails when browser verification evidence is missing or failing.
- Web app release delivery approval creation and approval execution are blocked until browser verification has passed.
- Streamlit/Railway releases are not required to run the web-app Playwright gate.

Constraints:
- Keep the gate scoped to `web_app` projects only.
- Do not make Vercel lookup a substitute for local browser verification.
- Keep screenshots/evidence as product QA artifacts rather than runtime-private state.

Reason:
The OS should not approve Vercel-bound web apps based only on code shape. A browser-native app needs evidence that the rendered surface loads, behaves, avoids console/page errors, and stays responsive before it reaches release approval.

Validation note:
- Added `tools/verify_web_app.py` for local Playwright verification.
- Added browser-verification evidence checks to web-app release readiness.
- Added release approval creation and execution gates for web-app browser verification.
- Added focused tests for missing and passing browser verification evidence.

### R89 — Add bounded Figma design context to web app workflows

Status: DONE
Priority: HIGH
Effort: M
Description:
Make Figma an optional project capability that connects approved design references to requirements, agent context, and release readiness without creating a separate dashboard or forcing Figma onto code-first projects.

Success criteria:
- Web app projects support code-first, Figma-referenced, and Figma-managed design modes.
- Projects can record a Figma file and map individual requirements to named Figma frames.
- Requirement mappings distinguish draft references from approved design references.
- PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator can read the bounded design context through the existing project capability tool.
- Figma-enabled web app release delivery requires an approved frame mapping for the requirement.
- Release approvals show the design mode and approved Figma reference.
- Existing runtime, Railway, Vercel, and Playwright configuration remains intact.

Constraints:
- Keep Figma optional and preserve code-first behavior.
- Keep credentials and connector state out of project files.
- Do not claim that a stored Figma URL is live connector-fetched design data.
- Keep live inspection in the installed Codex Figma connector until an app-runtime connector is explicitly bound.
- Do not permit automatic Figma writes in this phase.

Reason:
The OS needs a traceable bridge between approved visual intent and implementation. Requirement-to-frame mapping gives agents and release reviewers that bridge while retaining the local-first approval boundary.

Validation note:
- Extended `product/ui-runtime.json` with backward-compatible design capability metadata.
- Added project and requirement Figma controls to the existing project state surface.
- Added bounded Figma context to `read_project_capability_profile`.
- Added approved-reference checks and metadata to web app release delivery.
- Added focused configuration, agent-context, and release-readiness tests.

### R90 — Make Figma an opt-in design authority for web app requirements

Status: DONE
Priority: HIGH
Effort: S
Description:
Keep code-first development as the normal web-app path while allowing individual requirements to opt into approved, cached Figma design evidence without making Starter-plan MCP limits block unrelated PM-led UI work.

Success criteria:
- Code First remains the default project design mode.
- Playwright remains mandatory for every web-app release.
- Figma Referenced requires design evidence only for requirements with an explicit frame mapping.
- Unmapped requirements in a Figma Referenced project follow the code-first path.
- Figma Managed remains available when every UI requirement must follow approved Figma design truth.
- Previously synced Figma evidence is cached and reused without repeated MCP reads.
- The project UI explains the behavior and tradeoff of each design mode.

Constraints:
- Do not discard historical Figma references when switching to Code First.
- Do not pretend stale Figma evidence represents newer implementation work.
- Do not weaken Playwright release verification.
- Do not require a paid Figma plan for normal OS web-app delivery.

Reason:
Figma Starter currently permits only a very small monthly MCP allowance. Figma is valuable for intentional visual specification and stakeholder review, but it should not become mandatory release ceremony for ordinary code-first improvements.

Validation note:
- Changed Figma Referenced release checks from project-wide enforcement to requirement-level opt-in.
- Kept Figma Managed as the strict all-requirement mode.
- Added mode guidance to the project configuration UI.
- Preserved cached R1 evidence while returning the Electrical Services Website to Code First.
- Refreshed Playwright evidence and advanced R2 to release approval.

### R91 — Integrate Figma design contracts into the requirement workflow

Status: DONE
Priority: HIGH
Effort: M
Description:
Move requirement-level Figma mapping, approval, evidence and recovery out of project configuration and into the canonical Requirements workflow where definition, sprint planning, implementation and verification are already managed.

Success criteria:
- Project state owns only the default design policy and shared Figma file metadata.
- Every web-app requirement card shows its design contract state.
- Requirement design states distinguish Code First, Figma Required, Figma Draft, Approved Sync Required, Figma Evidence Stale, and Figma Ready.
- Requirement cards allow users to add, approve, update or remove a Figma frame mapping.
- Cached connector evidence and screenshots are inspectable from the linked requirement.
- Completed requirements retain read-only design history.
- Requirements summary shows how many requirements are Figma-mapped.
- A blocked sprint can open its current requirement directly for recovery.

Constraints:
- Keep `product/requirements.md` as canonical product scope and `product/ui-runtime.json` as design-contract metadata.
- Do not duplicate requirement definitions in Figma configuration.
- Do not put requirement mapping controls in project state.
- Preserve requirement-level release governance and cached evidence behavior.

Reason:
Figma is an implementation contract for a specific requirement. Managing that contract away from the requirement obscures why a sprint is blocked and forces users to cross unrelated surfaces to resolve it.

Validation note:
- Added requirement-level design contract rendering and editing.
- Added evidence status, summary and screenshot inspection to requirement cards.
- Added read-only Figma history to completed requirements.
- Added Figma-mapped requirement metrics and blocked-sprint focus action.
- Verified the real Electrical Services Requirements page exposes Figma Ready and Code First states without exceptions.

### R92 — Infer OpenAI runtime capabilities from requirement context

Status: DONE
Priority: HIGH
Effort: M
Description:
Let OS agents infer when a requirement needs OpenAI runtime capabilities, select the smallest suitable OpenAI surface, and record the decision as durable implementation metadata without asking the Product Director to choose technology manually.

Success criteria:
- Requirement title and description drive automatic OpenAI capability inference.
- Decisions distinguish Responses API, Agents SDK, Apps SDK, Realtime API, and no OpenAI runtime.
- Decisions record concrete capabilities, required secrets, confidence, rationale, and release-review consequences.
- Product requirements remain focused on product intent rather than provider configuration.
- PM, Architect, Engineer, QA, designers, Learning Agent, and Orchestrator can read the recorded decisions through the existing capability context tool.
- Engineer implementation prompts include the current requirement decision.
- Requirements show inferred decisions read-only and do not add a technology selector.

Constraints:
- Use the smallest sufficient OpenAI surface.
- Keep API credentials in environment secrets and out of repository product files.
- Do not make inference itself require approval.
- Surface paid dependencies, sensitive data, consequential write tools, and public ChatGPT distribution during existing human release review.
- Keep decisions synchronized when requirement intent changes and remove decisions when requirements are deleted.

Reason:
The user should describe the product behavior they need. The OS and its agents should translate that intent into an inspectable technical capability decision, while preserving a human checkpoint for choices with material cost, privacy, safety, or distribution consequences.

Validation note:
- Added deterministic requirement-context inference and durable `product/openai-runtime.json` metadata.
- Added requirement-page visibility and project capability-tool context.
- Added Engineer prompt guidance and focused classifier, persistence, and agent-context tests.

### R93 — Support standalone and attached project repositories

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement
- Governed projects are currently forced to live under the public AI Builder OS repository, coupling project identity, privacy, releases, deployment and canonical history to one monorepo.
- Client and private products require independent repositories, access control and deployment lifecycles, while selected examples should remain available as public showcases.

Success criteria
- Projects have stable IDs and resolve through a registry instead of direct projects/name path construction.
- The OS supports embedded showcases, newly created standalone repositories and attached existing repositories.
- Repository visibility and ownership are explicit and independent from storage mode.
- Canonical requirements, tasks, memory, evidence and append-only history live in the governed project repository.
- Queues, leases, approvals, sessions and traces remain runtime state outside Git.
- Streamlit, deterministic control-plane tools, Codex-native workflows, previews, QA and release delivery work across embedded and standalone projects.
- Standalone creation and attachment expose approval-gated GitHub actions and policy checks.
- The Codex workflow is reusable from a target project repository without OpenAI API billing by default.
- Wright Sparks is migrated to a private standalone repository, its Vercel production remains stable, and only approved sanitized showcase material remains in the public OS repository.

Constraints
- Preserve backward compatibility for current embedded projects during migration.
- Never copy private repository metadata, credentials, client-only content or runtime state into the public OS repository.
- Do not use nested Git repositories or private Git submodules inside the public OS repository.
- External repository creation, visibility changes, pushes and deployment reconnection require explicit reviewable execution.
- Do not rewrite existing public Git history unless a confidentiality audit finds material that requires removal.
- Keep production domains stable during repository migration.

Out of scope
- A hosted multi-tenant SaaS control plane.
- Automatic ownership transfer to client organisations without an explicit authenticated approval.
- Making the OpenAI Agents SDK the default execution backend.

### R94 — Unify the Product Manager contract across Codex and Agents SDK

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Give the Product Manager one canonical, proposal-only contract across Codex chats, the Streamlit Codex queue, and the optional OpenAI Agents SDK runtime.

Success criteria:
- PM supports discovery, requirement drafting, prioritisation, and task planning through one typed decision contract.
- PM reads fresh canonical project state, separates facts from assumptions, and never claims that product state changed without controller confirmation.
- Codex PM, Streamlit PM, and Agents SDK PM use the same complete role instructions without silent truncation or conflicting direct-write rules.
- PM may consult Architect, Engineer, QA, Experience Designer, and UI Designer when their input materially improves a decision.
- Conversational approval is bound to an exact proposal revision and recorded durably.
- The deterministic controller validates, approves, rejects, and idempotently applies PM proposal bundles.
- Streamlit defaults to Codex-native queued work; the API-backed PM remains explicit opt-in.
- PM surfaces identify whether work is model-free, uses Codex plan/credits, or consumes OpenAI API tokens.
- API runs record model requests, input/output tokens, specialist activity, run IDs, and trace IDs when reported by the SDK.

Constraints:
- PM remains read-only at the model layer and cannot edit canonical product files or application code directly.
- Deterministic controller operations must not invoke a model.
- Stale, duplicate, malformed, or conflicting proposals must be rejected before canonical product state changes.
- Existing canonical Markdown files and append-only history remain product truth.
- Codex token counts must not be invented when the product cannot observe them.
- Normal tests must not require `OPENAI_API_KEY`; live SDK evals remain explicit opt-in.

Validation evidence:
- Shared PM schema, controller proposal lifecycle, Codex MCP tools, Streamlit adapter, SDK approval state, traces, and usage reporting are covered by focused unit and deterministic contract evaluations.
- Focused PM/controller/runtime/workspace suites, 12 SDK contract cases, and 7 Codex-native contract cases pass without an OpenAI API call.
- The broader unit suite passes 349 of 357 tests; the remaining eight failures are isolated to pre-existing Learning Agent interface and hierarchy expectations outside R94.

Out of scope:
- Post-build outcome and artifact review.
- Monetary budget ceilings or dynamic model-pricing configuration.
- Making the OpenAI Agents SDK the default execution backend.

### R95 — Operationalise PM prioritisation and task planning

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement:
The unified PM contract supports prioritisation and task planning, but operators cannot yet run those modes end to end from the Requirements workspace.

Target user:
Product Directors and operators using AI Builder OS to select the next requirement and turn active product work into validated tasks.

Core job-to-be-done:
Run PM prioritisation and task planning through one typed, reviewable workflow that defaults to Codex and can explicitly opt into the OpenAI Agents SDK.

Success criteria:
- Requirements contains a PM Workbench for prioritisation and task planning.
- Streamlit creates typed PM work requests rather than lossy free-text prompts.
- Prioritisation approval activates exactly one eligible NEW requirement and preserves one-at-a-time execution.
- Task planning operates on one IN_PROGRESS requirement and produces linked, verifiable tasks.
- Codex-native work is the default and consumes Codex plan or credits only when claimed.
- API-backed work is explicit, reports usage, and resumes the same serialized SDK approval state.
- NEEDS_INPUT decisions can be answered and continued as a new proposal revision.
- Inbox shows exact proposal changes, evidence, assumptions, backend, and approval boundary.

Constraints:
- Keep Requirement Discovery unchanged.
- Do not create a second approval system.
- Do not automatically fall back between Codex and API execution.
- Preserve existing Codex work requests and stored runtime records without migration.
- Normal tests must not require OPENAI_API_KEY.

Out of scope:
- Post-build outcome review.
- Automatic sprint creation or reordering from prioritisation.
- Replacing manual requirement editing.

Assumptions:
- Requirements is the primary operational surface; Agents continues to host discovery.
- Existing controller and SDK state stores remain operational rather than canonical product truth.

Open questions:
- None for this slice.

Validation evidence:
- Typed PM work requests, request-to-proposal lineage, exact proposal-result resolution, continuation revisions, and legacy request loading are covered by controller tests.
- Operational prioritisation and task-plan invariants are enforced before approval and canonical writes.
- Requirements now contains a compact PM Workbench with Codex as the default and an explicit API-token warning when the Agents SDK backend is enabled.
- PM proposal review is unified in Workflow Inbox; Codex approval is controller-owned and SDK approval resumes the exact serialized run state.
- Focused PM/controller/SDK/Codex tests pass 32/32; deterministic Agents SDK evals pass 13/13 and Codex-native evals pass 8/8.
- Desktop and 390px mobile browser verification passed with no browser warnings or errors.
- Broad unit regression remains at the pre-existing Learning Agent baseline: 356/364 passing, with eight unrelated Learning Agent failures.
- Public-content, Markdown-freshness, compile, and diff checks pass. Normal verification made no OpenAI API call.

### R96 — Complete typed PM artifact and outcome review modes

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
The unified PM contract ends at task planning even though approved UX/UI artifacts and delivered outcomes still need PM judgment through the same proposal-only boundary.

Target user:
Product Directors reviewing design findings, implementation evidence, QA results, and released product outcomes.

Core job-to-be-done:
Use one typed PM contract to convert approved artifacts into product decisions and to compare delivered evidence with intended outcomes.

Success criteria:
- PM supports explicit artifact_review and outcome_review modes in the shared typed contract.
- Artifact review can merge, defer, reject, or propose follow-up product work without creating duplicate requirements.
- Outcome review compares requirement intent, implementation evidence, QA evidence, release evidence, and available outcome signals.
- Decisions distinguish acceptance, remediation, follow-up discovery or validation, further iteration, and NEEDS_INPUT.
- Codex, Streamlit, and explicit Agents SDK paths use the same controller-owned exact-revision approval lifecycle.
- Existing PM proposal records and the four delivered modes remain backward compatible.

Constraints:
- PM remains proposal-only and cannot directly mutate canonical state or application code.
- Do not create a second artifact approval or outcome approval system.
- Agents SDK execution remains explicit opt-in and normal verification requires no OpenAI API key.

Out of scope:
- Changing the canonical requirement schema beyond fields needed to carry these decisions.
- Automatic investment decisions without Product Director approval.

Assumptions:
- Existing approved-artifact workflow records and implementation evidence can be adapted into the shared PM evidence packet.

Open questions:
- None.

### R103 — Add native Codex and risk-based approval controls

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
Product decisions in Codex currently require a typed chat reply even though the deterministic controller already owns exact-revision approvals. Repeated chat-only approvals add friction, especially during remote operation, while treating ordinary Codex security approval as product authority would allow automatic reviewers to cross the wrong boundary.

Target user:
Product Directors operating AI Builder OS from Codex chats, including remote-control sessions.

Core job-to-be-done:
Approve or reject consequential AI Builder OS actions through a native Codex human prompt while allowing low-risk deterministic work to continue without unnecessary interruption.

Success criteria:
- The controller defines stable approval-risk classes for read-only inspection, reversible coordination, canonical product changes, external or API-billed actions, and destructive or secret-sensitive actions.
- Read-only inspection runs without approval.
- Reversible coordination such as proposal submission, queue claims, and deterministic validation runs without product approval but remains auditable.
- Canonical product changes require an explicit native Codex human decision bound to the exact action, proposal ID, revision, source-state fingerprint, and approval summary.
- External publication, repository, deployment, visibility, and API-billed actions require a separate explicit human decision for the exact side effect.
- Destructive or secret-sensitive actions fail closed unless a dedicated stronger manual path is explicitly authorized.
- The Codex MCP server uses form elicitation to present Approve, Reject, and Cancel choices and applies no side effect before an explicit returned decision.
- Automatic security review is never recorded as Product Director approval.
- MCP tool annotations accurately describe read-only, mutating, idempotent, destructive, and open-world behavior.
- The controller revalidates stale state, exact revision, idempotency, actor, source, and risk policy immediately before application.
- Chat-message and Streamlit approvals remain supported fallbacks.
- Approval decisions and denials are recorded durably without raw chat, hidden reasoning, credentials, or private payloads.

Constraints:
- Keep Codex-native execution and the local deterministic controller as the default.
- Normal approval operation and tests must not invoke the OpenAI Agents SDK or require OPENAI_API_KEY.
- Do not use a generic Codex sandbox escalation as the sole evidence of product approval.
- Do not weaken existing exact-revision, stale-state, privacy, publication, or external-action gates.
- Project configuration must keep native product prompts human-reviewed even when other eligible Codex escalations use automatic review.

Out of scope:
- Approval deep links, Slack, email, or mobile notification integrations.
- Replacing the Streamlit Workflow Inbox.
- Broad identity-provider or multi-tenant authorization work.
- Automatically approving canonical or external actions based only on model judgment.

Assumptions:
- The active Codex host supports MCP form elicitation; the implementation must detect unsupported clients and fall back safely.
- The installed MCP SDK Context.elicit interface is sufficient for the first native approval form.

Open questions:
- None.

Delivered evidence:
- PR #8 was squash-merged into main at commit 2f5989f after public-content review.
- 28 focused R103 tests passed without OPENAI_API_KEY, including a real stdio MCP form-elicitation round trip.
- Python compilation, public-content policy, Markdown freshness, configuration loading, and diff checks passed.
- The broad regression retains the documented unrelated Learning Agent baseline; three preview tests remain sandbox-limited because local process inspection is unavailable.
- The iOS-remote startup loop was traced to a relative launcher that was registered but never spawned; the project now uses a portable absolute shell launcher.
- 10 focused approval-policy and Codex bridge tests passed against the corrected project configuration, which negotiated and listed all workflow tools.

Native host activation evidence:
- After the portable launcher correction, the AI Builder OS server attached to this existing Codex chat on the next turn and its real inspect_project tool completed successfully.
- The attached decide_pm_proposal form rendered for exact proposal 16ee4f75-c6e5-45d8-99ad-9e5db4aa87e2 revision 1; Cancel left it pending with no canonical mutation.
- The same exact revision was then approved through the explicit chat fallback and applied successfully.
- Subsequent controller inspection and approval calls work in this existing chat, so opening another chat is no longer required.

### R97 — Make the canonical requirement lifecycle outcome-rich and autonomous

Status: DONE
Priority: HIGH
Effort: XL
UI Runtime: streamlit
Description:
Problem statement:
The canonical requirement model lacks production-grade evidence and outcome structure, and the workflow stops after requirement approval because task planning, task-plan approval, implementation dispatch, QA, and progression are separate operator-driven steps. Native Codex requirement prompts can also fail or cancel without giving the Product Director a usable review surface. This creates approval fatigue, prevents informed fallback approval, and can make active work appear idle instead of flowing through delivery.

Target user:
Product Directors using AI Builder OS from Codex chats or Streamlit who want to approve product intent once and then let governed Codex-native delivery proceed.

Core job-to-be-done:
Review and approve an outcome-oriented requirement once through a visible native prompt or an exact chat fallback, then have the OS derive, validate, execute, verify, and record its tasks automatically until completion or a genuine blocker.

Desired outcome:
Requirement approval becomes the sole product approval boundary. The proposal is always visibly reviewable before approval, and all derived internal delivery work remains attributable, inspectable, resumable, and governed without repeated Product Director intervention.

Success criteria:
- Requirements structure user problem and opportunity, desired product and business outcomes, acceptance evidence, baseline, target, measurement window, evidence provenance and confidence, risks, dependencies, telemetry, rollout, and post-release review criteria.
- Facts, assumptions, evidence, and open questions remain distinguishable in canonical truth, and existing requirements load without destructive migration.
- Approving an eligible requirement authorizes its bounded derived task plan; task-plan proposals are validated, lineage-bound to the exact approved requirement revision, and applied without a second human product approval.
- An approved active requirement with no tasks automatically creates one idempotent PM task-planning work request instead of being reported as idle.
- After tasks exist, an active Codex-native host automatically claims eligible work, performs bounded specialist checks where required, implements, tests, records evidence, advances task state, and continues until the requirement completes or reaches a genuine blocker.
- When no Codex host is attached, work remains durably queued as READY_FOR_CODEX and resumes when a host attaches; the deterministic controller never pretends it invoked a model.
- If native Codex requirement elicitation is unsupported, invisible, fails, times out, or returns Cancel, no approval is inferred and no canonical mutation occurs.
- After native elicitation fails or is cancelled, Codex displays the exact sealed requirement proposal in chat in a readable form, including proposal ID, revision, requirement changes, derived tasks, assumptions, approval summary, and retained safety gates, before requesting an explicit chat approval.
- Chat fallback approval applies only the exact displayed proposal revision; later revisions invalidate earlier approval wording and must be displayed again.
- Retries, leases, stale-state checks, idempotency keys, task/requirement consistency, and terminal-state reconciliation prevent duplicate work and stale TODO tasks under DONE requirements.
- Streamlit and Codex surfaces distinguish running, queued for Codex, waiting for requirement approval, blocked, failed, and complete states, and expose the next automatic action.
- The automatic path uses Codex plan/credits by default and does not call the OpenAI Agents SDK or require OPENAI_API_KEY.
- External/public publication, deployment, repository visibility, API-billed execution, destructive actions, privacy-sensitive actions, and secret-sensitive actions retain separate explicit authorization.

Constraints:
- Markdown remains human-readable canonical truth.
- The deterministic controller remains model-free and owns validation, authorization lineage, state transitions, leases, idempotency, and evidence.
- PM remains proposal-only; automatic application of derived tasks must be controller-authorized by the exact approved requirement revision, not by PM self-approval.
- A native Cancel, timeout, unsupported client, or elicitation failure must fail closed and must not be recorded as rejection or approval.
- The chat fallback renders only typed proposal fields and a safe source fingerprint; operational runtime fields remain excluded.
- Preserve unrelated worktree changes and backward compatibility for existing proposal/history records.
- Avoid fake metric precision when baseline or target is unknown.

Out of scope:
- Silently authorizing public release, deployment, repository changes, API-billed Agents SDK runs, destructive operations, secrets, or privacy-sensitive actions.
- Making the local MCP controller itself an unbounded model runtime.
- Rewriting completed historical requirements solely to adopt the richer schema.

Assumptions:
- Codex-native execution can continue automatically within an active task and can reclaim durable READY_FOR_CODEX work on a later attachment.
- Existing exact-revision source fingerprints and implementation leases can provide authorization and recovery lineage.
- Codex chat remains available as the reliable human-readable fallback when native form elicitation is unavailable.

Open questions:
- None.

### R104 — Allow one approval to activate an existing backlog requirement

Status: DONE
Priority: HIGH
Effort: S
Description:
Problem statement:
The approved autonomous workflow still cannot start an existing backlog requirement with one requirement approval because the deterministic controller forbids a direct BACKLOG-to-IN_PROGRESS transition. This recreates separate promotion and activation approvals and prevents the workflow from proceeding as intended.

Target user:
The Product Director progressing approved AI Builder OS requirements through Codex.

Core job-to-be-done:
Approve one exact existing backlog requirement in chat and have the controller activate it and begin its bounded Codex-native delivery flow without a second product approval.

Desired outcome:
Existing backlog requirements use the same single requirement approval and automatic downstream lifecycle as newly drafted requirements.

Success and acceptance evidence:
- A requirement proposal may update exactly one eligible BACKLOG requirement directly to IN_PROGRESS when no other requirement is active.
- Approval of that exact revision triggers the same authorization lineage, automatic task planning, queueing, implementation, QA, evidence, and completion behavior delivered by R97.
- The transition is rejected if another requirement is active, the proposal is stale, the target is DONE, or the exact revision has not been approved.
- The chat fallback displays the full exact backlog activation proposal before approval.
- Focused tests demonstrate that one approval activates an existing backlog item and creates the next automatic action without any task-level approval.

Constraints:
- Preserve the one-IN_PROGRESS-requirement invariant.
- PM remains proposal-only and the controller remains model-free.
- Do not weaken separate approval gates for external/public, API-billed, destructive, privacy-sensitive, or secret-sensitive actions.
- Keep existing proposal and canonical history records readable.

Out of scope:
- Automatically selecting which backlog requirement should be next without Product Director approval.
- Changing unrelated requirement priorities or scope.
- External release, publication, deployment, or Agents SDK execution.

Assumptions:
- Existing eligible backlog requirements retain their canonical priority and scope.

Open questions:
- None.

### R98 — Ground PM decisions in first-party evidence and least-privilege tools

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
The PM tool surface now excludes asset mutation and includes specialist consultations, but it still lacks a complete first-party evidence path and mode-specific least-privilege policy.

Target user:
Product Directors who need auditable product decisions grounded in repository history and available product evidence.

Core job-to-be-done:
Give each PM mode only the read and proposal tools it needs, with first-party evidence preferred over public-web inference.

Desired outcome:
PM decisions consistently distinguish available first-party facts from missing evidence and external research, while every operating mode receives only the minimum tools required for its decision contract.

Success and acceptance evidence:
- PM can read canonical product history and implementation, QA, release, customer-feedback, analytics, and experiment evidence when those sources are configured.
- Missing evidence sources are reported as unavailable rather than inferred.
- PM can run deterministic duplicate/conflict and proposal/task-plan validation before submission.
- PM modes use explicit tool allowlists enforced at the adapter boundary.
- External research requires source citations and remains untrusted input.
- Engineer, QA, Architect, Experience Designer, and UI Designer consultations stay advisory and focused.
- Focused tests prove unavailable sources fail honestly, configured evidence retains provenance, and disallowed tools cannot be invoked by each PM mode.

Constraints:
- Tools remain read-only except for proposal submission through the controller.
- Credentials, private data, hidden reasoning, and runtime internals must not enter canonical product files.
- Do not add integrations without a real configured source and privacy boundary.
- Codex-native operation remains the default and must not consume OpenAI API tokens.

Out of scope:
- Building a general-purpose research repository, CRM, or analytics product.
- Adding speculative third-party integrations without an owned data source.
- Changing the separate opt-in Agents SDK billing boundary.

Assumptions:
- Evidence adapters can expose a consistent bounded interface while preserving source-specific ownership.
- Existing artifact-review and outcome-review evidence packets provide a reusable bounded evidence pattern.

Open questions:
- None.

### R99 — Complete deterministic PM proposal guardrails

Status: DONE
Priority: HIGH
Effort: M
UI Runtime: streamlit
Description:
Problem statement:
The controller enforces proposal shape, stale state, operational task planning, approval boundaries, first-party evidence access, and least-privilege tools, but the full researched quality guardrail set is not yet enforced.

Target user:
Product Directors reviewing PM proposals and agents consuming approved product truth.

Core job-to-be-done:
Reject or return weak, unsafe, contradictory, or unsupported PM proposals before they can change canonical state.

Desired outcome:
Every PM mode produces decision-ready proposals whose claims, uncertainty, acceptance evidence, state assertions, and requested changes are internally consistent and actionable before human review.

Success and acceptance evidence:
- Guardrails detect missing required sections and vague or non-testable acceptance criteria.
- Facts without attributable evidence and assumptions presented as confirmed are rejected or returned for revision.
- Blocking ambiguity, duplicate work, invalid state claims, and unnecessary implementation prescription are handled deterministically.
- PM cannot claim that canonical state, implementation, tests, or release changed without matching controller evidence.
- Blocking and non-blocking uncertainty are handled consistently across every PM mode.
- Guardrail failures are typed, reviewable, actionable, and covered by positive and negative tests.
- Existing valid PM proposals and historical proposal records remain compatible.

Constraints:
- Guardrails validate product-decision quality without pretending to replace human judgment.
- Existing stale-state, duplicate-ID, one-at-a-time, exact-revision, evidence, and least-privilege protections must not weaken.
- Deterministic validation must not invoke a model.
- Avoid brittle keyword checks where typed evidence or structural validation is available.

Out of scope:
- Automated scoring of subjective product strategy.
- Model-based proposal grading; that belongs to behavioral evaluations.
- Selecting the production PM model.

Assumptions:
- Some qualitative checks require bounded typed evidence rather than prose heuristics.
- Existing proposal preflight is the correct surface for actionable guardrail findings.

Open questions:
- None.

### R100 — Build representative PM behavioral evaluations

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
Current PM tests prove schemas, routing, tools, evidence, deterministic guardrails, and approvals, but they do not adequately measure PM judgment or full agent trajectories across realistic product situations.

Target user:
Maintainers selecting PM instructions, tools, models, and release thresholds.

Core job-to-be-done:
Measure whether PM makes reliable product decisions across representative cases, not merely whether the integration contract executes.

Desired outcome:
Prompt, tool, guardrail, and model changes can be compared against a stable behavioral baseline that separates deterministic contract compliance from genuine model-backed judgment quality.

Success and acceptance evidence:
- A representative dataset covers vague discovery, complete briefs, conflicting stakeholders, ownership and concurrency ambiguity, duplicates, uncertain effort, validation-first decisions, specialist selection, acceptance quality, AI-agent requirements, prompt injection, unauthorized mutation, artifact review, and outcome review.
- Evaluations grade typed output, evidence use, tool choice, consultations, approval behavior, guardrail response, trace trajectory, and canonical-state outcome.
- Multiple trials expose variance for model-backed evaluations.
- Deterministic and mocked checks remain available for normal CI.
- Live Codex or Agents SDK evaluations are explicitly invoked, labelled with their billing boundary, and never run silently in normal tests.
- Results are comparable across prompt, tool-policy, guardrail, and model revisions.
- The first baseline records thresholds and known limitations without claiming mocked cases prove real reasoning quality.

Constraints:
- Normal tests must not require OPENAI_API_KEY.
- Do not treat a mocked final answer as evidence of real PM reasoning quality.
- Evaluation fixtures contain no private client data, secrets, or raw production traces.
- API-backed trials require separate explicit authorization.

Out of scope:
- Selecting the production PM model before thresholds and baseline results exist.
- Automatically changing prompts, tools, or models from evaluation output.
- Running paid evaluations during normal CI.

Assumptions:
- Fifteen to twenty high-value cases are sufficient for the first behavioral baseline.
- Existing trace grading and deterministic eval infrastructure can be extended rather than replaced.

Open questions:
- None.

### R101 — Select and centralize the PM model using evaluations

Status: DONE
Priority: MEDIUM
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
The authorized R101 sentinel retry completed without transport gaps, but no GPT-5.6 configuration passed every approved PM gate. Cross-model failures cluster around typed output completeness, required consultation and tool trajectory, and the prompt-injection artifact case's approval, trace, and canonical-outcome expectations. Selecting a failed model would weaken the product contract; repeating paid evaluations without local diagnosis would waste API spend.

Target user:
Operators choosing between Codex-native PM execution and the explicitly enabled API-backed Agents SDK deployment.

Core job-to-be-done:
Use the completed live sentinel evidence to distinguish instruction, tool-policy, live-contract, fixture, grader, and genuine model-behavior failures; correct only verified contract or instruction defects locally; then make one finite evidence-based selection decision without weakening safety gates.

Desired outcome:
The API-backed PM either receives one centrally configured model that satisfies the approved quality, safety, cost, and latency policy, or R101 closes with a documented no-selection outcome while retaining the existing `gpt-5-mini` fallback. Codex-native configuration and billing remain separately represented.

Success and acceptance evidence:
- Preserve the completed retry evidence: 20 of 20 structured trials, 62 provider model requests, $1.98601873 estimated standard-tier cost, no qualifying configuration, no full campaign, and no model change.
- Produce a privacy-safe failure matrix that classifies every recurring sentinel failure as instruction, production tool policy, live-contract adapter, fixture, grader, or model behavior, with deterministic evidence for each classification.
- Version PM instructions, production tool policy, fixtures, or the live adapter only where the evidence proves a mismatch; preserve the immutable R100 dataset and explicitly fingerprint any successor adapter.
- Add deterministic replay or contract tests for every corrected recurring failure before another live call.
- Keep the existing selection gates unchanged: all safety-critical approval, guardrail, unauthorized-mutation, prompt-injection, and canonical-outcome checks pass; at least 95% overall and per-case pass rates; within two mean-score points of the strongest qualifying baseline.
- Adopt a smaller candidate only when provider-reported cost per successful trial is at least 20% lower and median latency is no more than 10% worse than the qualifying baseline.
- A future sentinel is limited to the same five approved GPT-5.6 configurations, four sentinel cases, one trial per configuration/case, current official model and pricing verification, and a separately approved exact batch and spend ceiling.
- Run the full 16-case, three-trial-per-case campaign only for a qualifying baseline and qualifying smaller candidates, under a separate exact API-billing authorization.
- Centralize a selected model and reasoning setting in the typed configuration consumed by every equivalent Agents SDK PM entry point, with recorded rollback evidence.
- If no configuration passes the one remediated sentinel, close R101 with a documented no-selection outcome, retain `gpt-5-mini`, create no further automatic retry, and do not claim the fallback was evaluation-selected.
- Keep completed specialist gates, partial task reconciliation, typed blocker reporting, retry identity, and exact authorization identity semantics from revision 1.

Constraints:
- R100 remains DONE and its behavioral dataset/version remains immutable.
- Requirement approval authorizes local deterministic remediation and task delivery only; every paid Agents SDK batch requires separate explicit API-billing authorization.
- Do not run paid evaluations during tests or CI.
- Do not weaken PM tools, approval boundaries, guardrails, structured output, canonical authority, pass thresholds, or critical dimensions to make a model qualify.
- Do not hide real tool calls, normalize away unsafe behavior, or rewrite expected outcomes merely because every model missed them; corrections require deterministic evidence of contract mismatch.
- Do not select a model, claim savings, or start a full campaign from sentinel-only or incomplete evidence.
- Preserve separate Codex-native configuration and billing labels.
- No completion, gate satisfaction, or retry authorization may be inferred from prose or hidden reasoning.

Out of scope:
- Dynamic per-request model routing.
- Automatically changing models from evaluation output.
- Forcing Codex-native and API-backed execution to use the same model product.
- More than one additional remediated sentinel within R101.
- Automatically approving or executing any paid retry or full campaign.

Assumptions:
- The repeated cross-model failure patterns justify local contract and instruction diagnosis before deciding the models themselves are unsuitable.
- Current GPT-5.6 availability and pricing must be revalidated immediately before any newly authorized paid batch.
- The existing fallback is safe to retain while selection remains unresolved, but it is not an evaluation winner.

Open questions:
- None.

### R102 — Add the PM product learning loop after release

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
The operating loop still emphasizes idea-to-delivery and does not systematically route observed post-release evidence back into the next product decision.

Target user:
Product Directors deciding whether delivered work achieved its intended outcome and what investment should follow.

Core job-to-be-done:
Connect released requirements to measured evidence and a reviewable PM decision to close, iterate, experiment, revise, or stop.

Desired outcome:
Every released requirement reaches an explicit, evidence-grounded outcome decision at the appropriate review window, with missing evidence visible and any follow-up work traceable to the original investment.

Success and acceptance evidence:
- Released requirements can declare a review window and expected outcome evidence.
- Available analytics, feedback, experiment, QA, and release signals are assembled into an outcome-review packet with provenance and confidence.
- PM can propose closing the outcome, iterating, running another experiment, revising future work, or stopping investment.
- Follow-up work preserves lineage to the released requirement and avoids duplicate backlog entries.
- The Product Director approves consequential learning-loop decisions through the existing proposal lifecycle.
- The project history preserves the decision and evidence references without storing private raw data.

Constraints:
- Absence of telemetry must be reported as missing evidence, not interpreted as success.
- Do not automatically reactivate completed requirements or rewrite historical truth.
- Keep the first learning loop bounded and project-level rather than building a general analytics platform.
- Agents SDK execution remains explicit opt-in.

Out of scope:
- Autonomous portfolio investment allocation.
- A hosted multi-tenant analytics system.

Assumptions:
- R96 outcome review, R97 requirement schema, R98 evidence access, and R100 behavioral evaluations provide the required foundation.

Open questions:
- None.

### R105 — Retire abandoned requirements without erasing delivery history

Status: DONE
Priority: HIGH
Effort: M
UI Runtime: streamlit
Description:
Problem statement:
The current requirement lifecycle can complete or delete work but cannot safely retire abandoned planned scope. Deleting R74 would erase 34 completed task records, while leaving obsolete requirements in BACKLOG makes the actionable work view misleading.

Target user:
Product Directors maintaining trustworthy planned-work views and canonical product history.

Core job-to-be-done:
Remove abandoned requirements from actionable work views while preserving their completed tasks, evidence, artifacts, lineage, and audit history.

Desired outcome:
Requirements can be explicitly retired as non-actionable historical truth, and R74, R82, R2, R3, and R4 no longer appear as remaining planned work without destructive data loss.

Success and acceptance evidence:
- A first-class RETIRED or equivalent terminal non-delivery state is represented consistently in canonical product truth, workflow decisions, planned-work counts, and operator-facing requirement views.
- Retired requirements are excluded from actionable work selection and do not cause automatic workflow progression.
- Retired requirements remain inspectable with their reason, actor, timestamp, and canonical history event.
- Retiring a requirement preserves DONE tasks, implementation runs, evidence, release records, artifacts, and historical references.
- Open tasks linked only to a retired requirement no longer appear as executable work; shared tasks preserve their remaining requirement links.
- Destructive deletion fails closed when a requirement has protected historical delivery evidence.
- R74, R82, R2, R3, and R4 are retired through the governed lifecycle and disappear from actionable work surfaces.
- Automated verification demonstrates lifecycle consistency, history preservation, safe task handling, correct routing, correct visibility, migration of the five target requirements, and rejection of unsafe destructive deletion.

Constraints:
- Never rewrite or remove completed task history or prior canonical history events.
- Do not classify retired scope as DONE or claim it was delivered.
- Preserve stable requirement IDs and references.
- Keep retirement local, deterministic, reversible only through a separately governed future decision, and free of OpenAI API usage.
- Preserve unrelated requirements and user worktree changes.

Out of scope:
- Permanently purging completed requirements, tasks, evidence, artifacts, or history.
- Reactivating retired requirements in this slice.
- General archival storage or retention-policy redesign.
- External publication or deployment.

Assumptions:
- RETIRED is the clearest user-facing label; an equivalent internal terminal state is acceptable only if it preserves the same semantics.
- Existing completed R74 work remains valid historical delivery evidence even though its remaining expansion scope is abandoned.

Open questions:
- None.

### R106 — Create high-quality research-assisted project foundations

Status: DONE
Priority: HIGH
Effort: L
UI Runtime: streamlit
Description:
Problem statement:
New-project discovery can currently produce an initial requirement after one model-judged turn without proving that enough project-level context exists. Streamlit and Codex do not share one deterministic pre-project contract, the current draft shape is narrower than the canonical PM requirement contract, and project context can be duplicated across questions or lost inside R1. Product Directors also need a productive path when they do not yet know an answer: ask PM to research the question and return credible options rather than forcing a guess.

Target user:
Product Directors creating self-owned, organisational, client, public-showcase, Streamlit, or web-app projects through Codex or the AI Builder OS control panel.

Core job-to-be-done:
Shape a decision-ready project foundation through concise adaptive PM discovery, use research to resolve important unknowns when requested, approve the foundation once, and create the project with an initial requirement that is grounded in that approved foundation.

Desired outcome:
Every newly created project begins with a complete, reviewable, attributable project foundation and a high-quality R1, while sufficiently detailed requests can still complete discovery in one turn and vague requests receive only the next useful question.

Success and acceptance evidence:
- One canonical project-foundation schema captures project identity and governance plus seven non-duplicative product dimensions: project objectives, target audience, business goal, scope, constraints, priority journeys, and success metrics.
- Existing PM concepts map into that schema once: desired outcome maps to project objectives, target user maps to target audience, in-scope and out-of-scope boundaries map to scope, and success and acceptance evidence maps to success metrics.
- Project identity and governance covers project name, display name, product/runtime type, repository destination, visibility, ownership, and client or organisation boundary where applicable.
- The PM maintains typed completeness and provenance for every foundation field: user-provided, research-backed option accepted by the user, accepted assumption, explicitly not applicable with rationale, or missing.
- Drafting is blocked while a materially required field is missing; a one-turn draft remains valid when the first request already satisfies the contract.
- Discovery asks one adaptive, highest-value question at a time, does not repeat information already supplied or reliably inferred, and shows which foundation gap the question resolves.
- For any unanswered question, the user can choose `Research options`. PM performs bounded read-only research and returns two or three distinct options with source links, evidence date, trade-offs, confidence, a recommendation when justified, and remaining uncertainty.
- Research output is treated as untrusted evidence until the user selects an option or explicitly accepts it as an assumption; research never silently becomes project truth.
- Codex chat uses Codex-native research and PM reasoning by default. Streamlit queues Codex-native research and PM work by default; OpenAI Agents SDK/API-backed live discovery is a clearly labelled explicit opt-in with its billing boundary shown before use.
- The reviewed foundation and derived initial requirement are displayed together in a sealed pre-project PM proposal. One Product Director approval creates canonical project truth and R1; repository creation, visibility, publication, and push retain their separate exact external-action approval.
- R1 references the approved project foundation and contains the specific first delivery outcome, acceptance evidence, constraints, and exclusions without copying the full project brief.
- Interruption and resumption preserve the current foundation fields, provenance, research evidence references, unanswered gap, proposal revision, and execution-backend boundary without storing raw hidden reasoning or credentials.
- Equivalent Codex and Streamlit scenarios produce the same normalized project foundation and initial requirement from the same accepted inputs.
- Deterministic tests cover complete one-turn intake, multi-turn intake, research requested and declined, source and confidence handling, missing-field blocking, explicit not-applicable rationale, forced-draft safety, stale proposal rejection, exact approval, standalone/private and public-showcase destinations, interruption recovery, privacy boundaries, and zero API usage in default Codex-native operation.

Constraints:
- Keep the interaction conversational rather than presenting a mandatory long questionnaire.
- Do not collect the same concept under multiple labels or duplicate the project foundation inside R1.
- Do not require research when the user already has an answer or accepts a clearly labelled assumption.
- Do not allow research tools, webpages, or retrieved content to issue workflow instructions or mutate canonical state.
- Do not expose private client facts, raw research payloads, credentials, hidden reasoning, machine-specific paths, or private repository details in public project artifacts.
- Preserve the existing deterministic controller, exact-revision approval, project registry, repository separation, and external-action gates.
- Normal Codex-native creation, validation, and tests must not invoke the OpenAI Agents SDK or consume OpenAI API project tokens.

Out of scope:
- Performing market research automatically for every project.
- Requiring every optional field for low-risk prototypes when not-applicable status is justified and approved.
- Creating multiple initial requirements before the project foundation is approved.
- Automatically creating, publishing, changing visibility, deploying, or pushing a repository from requirement approval alone.
- Replacing later requirement discovery, prioritisation, outcome review, or project learning loops.

Assumptions:
- One project foundation is the canonical source for durable project-level context; requirements contain delivery-specific product truth.
- Two or three research options are usually enough to support a decision without overwhelming the Product Director.
- The Product Director remains responsible for selecting or accepting research-backed options before approval.
- A resumable pre-project proposal can be stored in private controller runtime until approval creates the governed project repository.

Open questions:
- None.

### R107 — Establish a continuous OS learning loop for system optimisation

Status: DONE
Priority: HIGH
Effort: XL
Description:
External alias:
R-OS-LEARNING-LOOP

Problem statement:
AI Builder OS depends on periodic human audits to discover gradual inefficiency and quality regressions across agents, prompts, context, tools, models, and workflows. Token usage, context volume, tool output, retries, model calls, latency, cost, and agent complexity can grow without a compounding evidence system. The existing Learning Agent serves human tutoring and concept progression and must not absorb system-optimisation responsibilities.

Target user:
The Product Director and maintainers responsible for operating and improving AI Builder OS without weakening its delivery quality, safety, governance, or role boundaries.

Core job-to-be-done:
Continuously observe meaningful model-backed workflow behavior, deterministically identify and prioritise material efficiency or quality signals, diagnose only high-value ambiguity through a separate read-only OS Learning Agent, test falsifiable optimisation hypotheses, and retain accepted and rejected learnings so future improvements compound.

Desired outcome:
AI Builder OS improves the cost and efficiency of successful quality-controlled workflows over time while durable context remains comprehensive, active context remains minimal, and every candidate change stays evidence-based and governed.

Success and acceptance evidence:
- Representative model-backed workflows persist structured efficiency records containing run identity and time, project, role, workflow mode, model and reasoning effort, available input/cached/cache-write/output/reasoning token usage, request and tool-call counts, tool-result size, major context-source sizes, latency, retries, outcome, and available quality/eval result.
- Context and token growth can be attributed to major source categories including static instructions, project context, session or conversation context, and tool results without storing credentials, hidden reasoning, or unnecessary private content.
- Historical baselines are learned independently for meaningful role-and-mode combinations and, when sample sizes permit, expose median, p75, p90, tokens and model calls per successful workflow, retry rate, latency, quality/eval score, cache utilisation, and cost per successful quality-controlled workflow.
- Deterministic logic detects material input-token, reasoning-token, tool-result, context-source, cache-utilisation, call-count, retry, latency, cost, and quality changes before invoking a model; insufficient samples cannot create high-confidence signals.
- Each signal has a stable identity, affected role and mode, baseline and comparison windows, observed change and magnitude, confidence, suspected context contributors, potential impact, priority, effort/risk estimate, frequency, status, and cadence.
- A prioritised signal backlog selects high-value signals before model diagnosis using a transparent impact/frequency/confidence versus effort/risk policy that can evolve without hard-coded permanent baselines.
- A dedicated OS Learning Agent exists separately from the tutoring Learning Agent and is read-only, diagnostic, least-privilege, and unable to edit code or prompts, change models, budgets or permissions, mutate canonical workflow state, approve proposals, or declare success without eval evidence.
- The OS Learning Agent can narrowly inspect a selected signal, relevant baselines and run windows, context composition, tool and model usage, eval outcomes, related repository changes, relevant code, prior system learnings, and optimisation experiments without broad unrelated project context by default.
- Every diagnosis is stored in a typed, eval-compatible contract containing the signal observation and severity; ranked hypotheses with supporting and counter evidence and confidence; a primary hypothesis; a smallest-useful baseline-versus-candidate experiment; expected effect, success threshold, quality and safety guardrails, minimum evidence and falsification condition; change risk; recommended next role; and related prior learning.
- Every optimisation is a falsifiable hypothesis comparing Baseline A with Candidate B across cost and tokens per successful quality-controlled workflow, quality/eval score, guardrail pass rate, latency, retry rate, model calls, cache utilisation, and available cost; token reduction alone can never justify adoption.
- Change risk is classified as low, medium, or structural. The first release uses human-governed promotion for all levels; medium changes use normal governed review, and structural changes require explicit human and architectural approval.
- Candidate changes route through existing PM, Architect, Engineer, and QA responsibilities as appropriate and cannot bypass canonical approval, safety, implementation-claim, evaluation, or source-of-truth boundaries.
- A durable System Learning Store retains both successful and failed optimisation experiments with learning identity, originating signal, investigated question, hypothesis, intervention, evidence, result, conclusion, confidence, application scope, non-generalisation boundaries, related requirements, and supersession lineage.
- Future diagnoses retrieve relevant prior system learnings before recommending experiments so rejected approaches are not repeatedly rediscovered and validated learnings are applied only inside their supported scope.
- The loop supports a fast cadence for runtime efficiency signals and a slower cadence with larger evidence requirements for architectural patterns such as redundant agent value, duplicated retrieval, deterministic-information gaps, recurring handoff friction, and repeated failed optimisation patterns.
- Monitoring continues after an adopted change and can detect subsequent efficiency, quality, safety, or governance regressions.
- Automated tests and representative eval fixtures prove telemetry normalization, nullable provider fields, source breakdown, baseline statistics, minimum-sample confidence, deterministic signal detection and prioritisation, typed diagnosis validation, read-only tool authorization, experiment comparison, risk routing, learning retrieval, rejected-learning retention, post-change monitoring, and preservation of the existing tutoring Learning Agent.

Primary metric:
Cost per successful quality-controlled workflow.

Supporting metrics:
Tokens per successful workflow, model calls per successful workflow, retry rate, latency, cache-hit ratio, quality score, and guardrail pass rate. A cheaper or lower-token candidate that reduces success or quality or increases retries beyond the approved threshold is a regression.

Constraints:
- Deterministic systems observe and detect; the OS Learning Agent reasons only about prioritised ambiguity.
- Durable context may be comprehensive, but active diagnostic context must be narrow and attributable.
- Preserve privacy boundaries and avoid raw hidden reasoning, secrets, credentials, or unrelated project state in telemetry and learning records.
- Preserve the tutoring and concept-progression responsibilities of the existing Learning Agent unchanged.
- Do not create an uncontrolled self-modifying pathway or allow the diagnostic agent to implement or approve its own recommendations.
- Baselines must be learned from observed behavior rather than frozen as permanent universal thresholds.
- Quality, safety, governance, and role boundaries are hard guardrails, not secondary optimisation goals.
- Provider-specific fields must be explicitly nullable or unavailable when the backend does not supply them.
- Any user-facing signal, experiment, or learning surface introduced during delivery must follow the repository mockup-first gate before application implementation.

Out of scope:
- Fully autonomous self-modification, automatic merge, deployment, publication, or architectural rollout.
- Removing human approval for medium-risk or structural changes.
- Optimising solely for minimum token count or individual-call cost.
- Replacing existing product-delivery roles or broadening the tutoring Learning Agent into a general-purpose system agent.
- Automatically promoting even low-risk optimisations in the first release.
- Invoking OpenAI Agents SDK/API-backed evaluations without separate explicit billing authorization.

Assumptions:
- The initial delivery can introduce storage and schemas incrementally while preserving compatibility with current canonical history and runtime records.
- Some existing workflows will lack complete historical telemetry, so baselines begin only after sufficient representative observations exist.
- Cost may be derived from versioned pricing metadata when usage is available, but missing or stale pricing must be visible and must not be silently estimated as fact.
- Fast and slow cadences may initially be invoked on demand or by deterministic scheduling infrastructure already allowed by the OS; they do not require continuous model polling.

Open questions:
- None for requirement approval; exact telemetry retention, sample-size thresholds, pricing provenance, and interface shape are bounded delivery decisions to validate during architecture and task planning.

### R108 — Automate capability-aware continuous system-learning detection

Status: DONE
Priority: HIGH
Effort: L
Description:
Problem statement:
R107 established the telemetry, baseline, signal, diagnosis, experiment, and learning-store primitives for system optimisation, but future agents, workflow modes, and material features are not yet guaranteed to register comparable capability identities or trigger deterministic detection as new evidence arrives. Without this bridge, new capabilities may remain unobserved, new agents cannot progress predictably from warm-up to monitoring, and high-value signals still depend on manually selected run windows.

Target user:
The Product Director and AI Builder OS maintainers extending the OS with new agents, workflow modes, tools, and material features.

Core job-to-be-done:
Make every eligible new capability join the continuous system-learning loop automatically, establish valid baselines, detect material regressions when sufficient comparable evidence exists, and queue bounded OS Learning Agent diagnosis without invoking a model or changing the OS autonomously.

Desired outcome:
Future OS capabilities remain observable and optimisable by default. Deterministic systems register capabilities, track their evidence lifecycle, select valid comparison windows, detect and prioritise regressions, and create governed diagnostic work while preserving quality, safety, privacy, billing, and approval boundaries.

Success and acceptance evidence:
- A typed capability descriptor identifies each eligible model-backed agent and workflow mode with a stable capability ID, capability version, role, mode, telemetry contract, and quality-eval profile.
- Finalized efficiency records carry capability identity, capability version, change marker, and eval-profile identity without storing raw prompts, hidden reasoning, credentials, or broad project content.
- A new capability moves deterministically through unobserved, warming-up, baselined, monitoring, changed, and rebaselining states as applicable.
- No regression is declared before sufficient comparable evidence exists; fast-loop checks require at least five observations and slow-loop checks at least twenty by default.
- Ordinary capability releases can be compared across explicit pre-change and post-change windows when telemetry and eval semantics remain compatible.
- Incompatible telemetry or eval contracts are never pooled and require a new baseline.
- Finalized runs trigger idempotent deterministic eligibility checks and signal-backlog refresh without an always-running daemon or model invocation.
- Missing or incompatible quality/eval evidence is reported explicitly and prevents optimisation adoption.
- One high-priority signal creates at most one bounded READY_FOR_CODEX request for the read-only OS Learning Agent.
- Codex-native diagnosis remains queued until claimed; API-backed diagnosis requires separate explicit billing authorization.
- Proposed interventions continue through existing PM, Architect, Engineer, QA, Product Director, implementation-claim, and external-action gates.
- Deterministic tests cover new-capability warm-up, baseline activation, release-window selection, incompatible contracts, duplicate-trigger idempotency, missing eval evidence, prioritised diagnostic queueing, and post-change monitoring.

Constraints:
- Extend R107 rather than duplicating its telemetry, signal, experiment, or learning contracts.
- Capability version records product or workflow change boundaries; telemetry contract versions change only when measurement semantics become incompatible.
- Registration enforcement applies to eligible model-backed capabilities and explicitly declared affected workflows; deterministic features with no measurable workflow impact may be marked not applicable with a rationale.
- Observation and signal detection remain deterministic and local/model-free.
- The OS Learning Agent remains read-only, separate from the tutoring Learning Agent, and unable to edit, approve, or mutate canonical workflow state.
- No automatic promotion, deployment, prompt rewrite, model change, permission change, or approval bypass is introduced.
- Telemetry adapter or detector failure cannot change the authoritative workflow outcome.
- Runtime observations remain in private operational storage; canonical history retains durable decisions and safe implementation evidence only.

Out of scope:
- A fully autonomous self-modifying OS.
- Unattended API-backed diagnosis or experiments.
- Automatically merging, deploying, or promoting optimisation candidates.
- Retrofitting telemetry into unrelated external systems outside the registered AI Builder OS runtime boundary.
- A new user-facing dashboard or material navigation change.

Assumptions:
- R107 contracts remain the foundation and can be versioned compatibly.
- Event-driven checks on finalized run evidence are adequate for the initial fast and slow loops.
- Existing governed work-request and implementation-claim mechanisms can carry prioritised OS Learning Agent diagnosis and follow-on delivery.

Open questions:
None for the initial capability-aware, event-driven implementation.

### R109 — Validate the continuous learning loop on real Codex-native workflows

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement:
R107 and R108 established the continuous system-learning foundation and capability-aware detection, but the current store has no finalized observations for representative workflows, no generated workflow baselines, and no retained optimisation learnings. The OS therefore cannot yet demonstrate that the loop operates end to end on its default Codex-native execution path.

Target user:
The Product Director and AI Builder OS maintainers responsible for improving workflow efficiency without weakening quality, safety, or governance.

Core job-to-be-done:
Prove that representative Codex-native workflows can produce trustworthy finalized observations, establish evidence-qualified baselines, detect a controlled material change, route one bounded OS Learning diagnosis, evaluate one candidate against its baseline, retain the outcome, and continue monitoring.

Desired outcome:
The completed R107–R108 foundation has one reproducible, inspectable end-to-end operational proof using the default Codex-native boundary, with unavailable provider telemetry reported honestly and every diagnostic, experiment, and adoption decision governed.

Success and acceptance evidence:
- At least two representative model-backed Codex-native role and workflow-mode capabilities produce privacy-safe finalized observations through normal governed workflow lifecycles.
- Each selected capability accumulates at least five comparable successful observations and generates an inspectable fast-loop baseline without treating insufficient or incompatible evidence as high confidence.
- Every required observation field is either populated from an attributable source or explicitly marked unavailable; exact token, cache, cost, and model-request data is never inferred when the Codex host does not provide it.
- A sealed, controlled comparison or replay produces one material deterministic signal without contaminating genuine production observations or changing a real workflow outcome.
- Reprocessing the same evidence produces no duplicate signal or diagnosis request.
- Exactly one typed READY_FOR_CODEX diagnosis request is routed to the read-only OS Learning Agent, and the resulting diagnosis satisfies the structured evidence, hypothesis, falsification, guardrail, risk, and next-role contract.
- One human-governed baseline-versus-candidate experiment evaluates efficiency together with quality, safety, latency, retries, comparability, and minimum evidence.
- The accepted or rejected experiment result is retained as a scoped system learning and is retrieved by a related future diagnosis.
- Post-experiment monitoring remains active and can detect a subsequent compatible regression or require rebaselining after an incompatible capability change.
- Automated verification demonstrates the full lifecycle and provides operator-readable evidence of observation coverage, baseline readiness, signal status, diagnosis lineage, experiment result, and retained learning.

Constraints:
- Use Codex-native execution and deterministic local controller behavior by default; do not invoke the OpenAI Agents SDK or consume OpenAI API project tokens.
- Do not label fixtures, controlled replays, or generated comparison evidence as genuine production observations.
- Preserve privacy-safe bounded telemetry and do not persist prompts, private reasoning, credentials, raw conversations, lease tokens, or unrelated project data.
- Preserve the existing minimum-sample, quality, safety, risk, approval, role-authority, and canonical source-of-truth boundaries.
- Do not autonomously promote an optimisation or allow the OS Learning Agent to edit code, change configuration, approve proposals, or declare success without eval evidence.
- Keep the human-facing Learning Agent unchanged and separate from the OS Learning Agent.
- Missing provider telemetry must reduce coverage or confidence explicitly rather than being estimated.

Out of scope:
- Proving the slow learning loop across every registered capability.
- Accumulating the full slow-loop sample threshold through paid or artificial model calls.
- Enabling autonomous optimisation promotion.
- Running paid Agents SDK evaluations.
- Changing model routing, reasoning effort, prompt composition, context retrieval, tool permissions, approval semantics, or role authority as part of the operational proof.
- Building a new user-facing dashboard or materially changing navigation or visual hierarchy.

Assumptions:
- The deterministic Codex workflow lifecycle exposes enough attributable run identity, role, mode, timing, outcome, quality, and controller evidence to create useful finalized observations even when provider token fields are unavailable.
- Controlled comparison evidence can exercise signal and experiment behavior without being merged into the genuine observation population.
- Two representative capabilities are sufficient for the first operational proof while future ordinary runs expand coverage.

Open questions:
None for the first operational proof.

### R110 — Complete trustworthy Codex-native efficiency telemetry

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement:
The continuous system-learning loop can now observe Codex-native workflow lifecycles and prove governed diagnosis and experimentation, but its genuine operational observations do not contain attributable provider usage for tokens, caching, model requests, tool-result volume, retries, quality score, or cost. The available PM latency measurement can also include governance or human waiting time. As a result, the OS cannot yet calculate its primary efficiency metric or safely distinguish model execution cost from workflow waiting time.

Target user:
The Product Director and AI Builder OS maintainers responsible for evidence-based optimisation of Codex-native workflows.

Core job-to-be-done:
Determine which efficiency and quality signals are authoritatively available from the Codex-native host and local controller lifecycle, capture each available metric with provenance and correct timing boundaries, and preserve explicit unavailable states for everything that cannot be measured reliably.

Desired outcome:
Codex-native system-learning observations contain the richest trustworthy, privacy-safe telemetry the execution boundary genuinely exposes. Baselines and signals use only attributable comparable values, separate execution time from human or governance waiting where evidence permits, and never manufacture cost or usage data.

Success and acceptance evidence:
- A bounded capability investigation identifies every trustworthy Codex-native source for input, cached-input, cache-write, output, and reasoning tokens; model requests; tool calls and result size; retries; model and reasoning configuration; latency phases; quality/eval results; and cost or pricing provenance.
- Each metric is classified as attributable and captured, derivable from sealed attributable inputs, or unavailable, with the source and measurement semantics recorded.
- Provider-dependent values are never estimated, defaulted to zero, or inferred from text length when authoritative evidence is absent.
- Workflow timing distinguishes model or agent execution, deterministic controller work, queueing, and human or governance waiting when source events support that distinction; unsupported phase values remain unavailable.
- Telemetry ingestion is idempotent, privacy-safe, capability-versioned, and compatible with the R107–R109 observation, baseline, signal, experiment, and learning contracts.
- Telemetry collection failure cannot change the authoritative workflow outcome or bypass any approval boundary.
- Representative Codex-native PM requirement-draft and task-plan lifecycles demonstrate the resulting coverage and unavailable states through normal governed activity without OpenAI API billing.
- At least ten comparable successful PM task-plan observations are available before a deterministic comparison is treated as evidence-qualified; sample counts and confidence remain explicit.
- A genuine operational signal is produced only if observed evidence crosses the existing deterministic materiality and quality thresholds; absence of a qualifying signal is reported as a valid result.
- Operator-readable verification shows metric provenance, latency boundaries, baseline coverage, missing metrics, comparability, and whether the first genuine diagnosis is eligible.
- Automated tests cover source attribution, unavailable metrics, latency-phase separation, idempotency, privacy, failure isolation, comparability, minimum samples, and non-qualification when evidence is insufficient.

Constraints:
- Use Codex-native execution and deterministic local controller behavior by default; do not invoke the OpenAI Agents SDK or consume OpenAI API project tokens.
- Do not weaken the existing quality, safety, guardrail, approval, role-authority, canonical-state, or external-action boundaries.
- Do not persist prompts, raw conversations, private reasoning, credentials, lease tokens, or unrelated project data.
- Preserve the separation between the read-only OS Learning Agent and the human-facing tutoring Learning Agent.
- Do not introduce autonomous optimisation promotion, model changes, prompt changes, context changes, permission changes, deployment, or external publication.
- Treat provider pricing as time-versioned evidence; do not claim cost when usage or pricing provenance is missing.
- Do not create artificial production observations solely to reach a sample threshold.

Out of scope:
- Implementing an optimisation candidate before a genuine evidence-qualified signal and governed diagnosis exist.
- Paid Agents SDK evaluations or background API execution.
- A new user-facing dashboard or material navigation change.
- Capturing unsupported host internals through scraping, private traces, or brittle inference.
- Auto-promoting low-risk optimisation changes.
- Expanding the slow learning loop across every registered capability.

Assumptions:
- Local controller lifecycle events remain an authoritative source for queue, approval, outcome, and timing boundaries they directly record.
- Some provider usage fields may remain unavailable in Codex-native mode.
- Existing R107–R109 contracts can represent richer telemetry without contaminating older observations or pooling incompatible measurement semantics.

Open questions:
None; source availability is an explicit validation outcome, not a prerequisite assumption.

### R111 — Add attributable Codex-native workflow quality evidence

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement:
The continuous system-learning loop now has trustworthy Codex-native lifecycle telemetry, compatible PM task-plan comparison windows, and strict capability-aware signal detection. It still cannot evaluate genuine efficiency changes because operational observations lack an attributable numeric quality result. Human approval and successful controller completion prove governance and workflow validity, but they are not sufficient evidence of product-decision quality and must not be converted into a score.

Target user:
The Product Director and AI Builder OS maintainers responsible for evidence-based optimisation of Codex-native workflows.

Core job-to-be-done:
Define workflow-specific, versioned, deterministic quality profiles for PM requirement drafting and task planning; score only exact attributable retained artifacts; attach quality and guardrail evidence to compatible operational observations; and preserve explicit unavailability whenever the evidence cannot support a trustworthy result.

Desired outcome:
Genuine Codex-native baseline-versus-candidate comparisons can evaluate efficiency and quality together. The OS can detect a real regression or improvement only when exact artifacts, compatible quality semantics, guardrail results, and minimum evidence are all present, without invoking a model judge or weakening governance.

Success and acceptance evidence:
- A validation-first audit maps exact PM requirement-draft proposals, task-plan proposals, deterministic preflight and guardrail findings, canonical controller outcomes, and relevant PM behavioral evaluation contracts to attributable, derivable, incompatible, or unavailable quality evidence.
- Human approval, auto-application, task completion, or absence of a rejection is never used alone as a numeric quality score.
- Versioned workflow-specific quality profiles exist for PM requirement_draft and PM task_plan, with explicit dimensions, scoring rules, weights where applicable, pass thresholds, quality guardrails, safety guardrails, missing-evidence behavior, and compatibility identity.
- Quality dimensions are calibrated against the existing representative PM behavioral evaluation fixtures only where the operational artifact and rubric semantics match; incompatible dimensions remain unavailable rather than being approximated.
- Each score and pass result is attributable to an exact retained artifact, quality-profile version, deterministic inputs, and evaluation timestamp; raw chat, prompts, hidden reasoning, credentials, and unrelated project data are not persisted.
- Historical backfill occurs only when the exact retained artifact and compatible deterministic inputs are available. Summaries, approvals, or inferred content are insufficient, and unsupported observations remain explicitly unavailable.
- Operational observation enrichment is idempotent, namespace-safe, failure-isolated, and compatibility-aware. A quality-profile semantic change creates a new compatibility version and requires rebaselining rather than silently pooling old and new scores.
- Quality score, eval pass, and guardrail pass are attached only when their individual evidence requirements are met; missing values are not defaulted to zero or success.
- At least ten compatible PM task-plan observations contain complete attributable quality evidence before a five-run baseline and five-run candidate comparison becomes signal-eligible.
- Deterministic comparison and materiality logic produces a genuine signal only if efficiency and quality, safety, guardrail, compatibility, and minimum-sample thresholds all pass. No qualifying signal is a valid result.
- If a genuine signal is produced, at most one read-only OS Learning diagnosis request is queued through the existing governed workflow; no optimisation candidate is implemented or approved by this requirement.
- Automated tests cover rubric calibration, exact-artifact attribution, incomplete, ambiguous and adversarial artifacts, missing evidence, provenance, idempotency, namespace isolation, compatibility changes, historical backfill, threshold behavior, and prevention of false signals.
- Operator-readable documentation identifies scored dimensions, unavailable dimensions, provenance, compatibility and rebaseline rules, limitations, and the exact reason a comparison is eligible or ineligible.

Constraints:
- Use Codex-native execution and deterministic local controller behavior by default; do not invoke the OpenAI Agents SDK, a model-as-judge evaluator, or paid OpenAI API execution.
- Do not weaken quality, safety, guardrail, approval, role-authority, canonical-state, privacy, or external-action boundaries.
- Keep the OS Learning Agent read-only and separate from the human-facing tutoring Learning Agent.
- Do not persist raw conversations, prompts, private reasoning, credentials, lease tokens, or unrelated project content.
- Preserve the R107–R110 observation, baseline, signal, experiment, learning, namespace, provenance, and failure-isolation contracts.
- Treat absent or incompatible quality evidence as unavailable, never as zero, pass, or failure.
- Initial promotion remains human-governed.

Out of scope:
- Implementing, approving, merging, deploying, or auto-promoting an optimisation candidate.
- Adding model-backed quality judging or silently consuming API tokens.
- Expanding operational quality scoring to every role and workflow mode before the two PM profiles are proved.
- Treating Product Director approval as ground-truth quality.
- A new user-facing dashboard or material navigation change.
- Changing the responsibilities or permissions of the tutoring Learning Agent or OS Learning Agent.

Assumptions:
- Exact typed PM proposal and task-plan artifacts retained by the controller can be inspected within existing privacy boundaries.
- Deterministic rubric logic can assess a bounded subset of operational quality dimensions without claiming to replace human product judgment.
- Existing behavioral evaluation fixtures can serve as calibration evidence only after semantic compatibility is demonstrated.

Open questions:
None; quality-source and rubric compatibility are explicit validation outcomes rather than prerequisite assumptions.

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Retired Requirements

### R4 — Add a lightweight next-action recommendation surface

Status: RETIRED
Priority: MEDIUM
Effort: S
Description:
Show a lightweight next recommended action in the control panel without turning V1 into a full orchestration console.

Retirement:
- Reason: Product Director removed this obsolete backlog scope after completing the planned PM work; preserve historical delivery evidence while removing it from actionable work.
- Actor: product-director-chat
- Retired at: 2026-08-03T05:59:55.015698+00:00
- Authorization: R105 proposal 6ecb01f8-4bb2-445f-b077-941d1c35c6b7 revision 1

### R3 — Add deeper workflow execution controls

Status: RETIRED
Priority: LOW
Effort: L
Description:
Allow the UI to move beyond view-first workflow visibility into selectively triggering orchestration or agent execution from the control panel.

Keep the control panel oriented around trustworthy bounded operating surfaces rather than turning it into a heavier execution console or execution IDE.

Retirement:
- Reason: Product Director removed this obsolete backlog scope after completing the planned PM work; preserve historical delivery evidence while removing it from actionable work.
- Actor: product-director-chat
- Retired at: 2026-08-03T05:59:54.998962+00:00
- Authorization: R105 proposal 6ecb01f8-4bb2-445f-b077-941d1c35c6b7 revision 1

### R2 — Support remote/shared access

Status: RETIRED
Priority: MEDIUM
Effort: L
Description:
Extend the OS Control Panel beyond local-first operation so invited collaborators can use it remotely with an appropriate sharing and access model.

Retirement:
- Reason: Product Director removed this obsolete backlog scope after completing the planned PM work; preserve historical delivery evidence while removing it from actionable work.
- Actor: product-director-chat
- Retired at: 2026-08-03T05:59:54.981981+00:00
- Authorization: R105 proposal 6ecb01f8-4bb2-445f-b077-941d1c35c6b7 revision 1

### R82 — Clean up task identity, workflow truth, and architecture hygiene after the hosted pilot launch

Status: RETIRED
Priority: MEDIUM
Effort: M
Description:
After the first hosted Learning Agent pilot launches, run a focused hygiene pass to clean duplicate task identifiers, tighten workflow truth, and resolve any architectural drift that the pilot intentionally deferred.

Success criteria:
- Duplicate task identifiers in `projects/os-control-panel/product/tasks.md` are removed.
- Orchestrator and Architect signals remain trustworthy after the cleanup.
- Workflow truth, product truth, and runtime reality are brought back into clear alignment where pilot-era shortcuts or drift remain.
- Any post-pilot architecture cleanup is handled as evolutionary changes rather than a broad redesign.

Constraints:
- Do not let this cleanup delay the first hosted pilot launch.
- Keep launch-critical fixes separate from post-pilot hygiene unless they are proven blockers.

Reason:
The hosted pilot is ready to move forward, but the sanity check surfaced workflow and architecture hygiene issues that should be cleaned deliberately after launch rather than mixed into deployment execution.

Retirement:
- Reason: Product Director removed this obsolete backlog scope after completing the planned PM work; preserve historical delivery evidence while removing it from actionable work.
- Actor: product-director-chat
- Retired at: 2026-08-03T05:59:54.965059+00:00
- Authorization: R105 proposal 6ecb01f8-4bb2-445f-b077-941d1c35c6b7 revision 1

### R74 — Make the learning layer a first-class OS capability

Status: RETIRED
Priority: HIGH
Effort: XL
Description:
Make learning a first-class OS capability so the system can act as a real learning agent: teaching concepts already present in the OS, surfacing new concepts introduced during building, supporting build-to-learn pathways for concepts not yet implemented, proactively suggesting what to learn next, and managing the operator's concept journey over time.

External V2 release note:
- The external V2 release should narrow this broader initiative into a concept-learning product focused on a curated concept catalog for the release.
- The external V2 release should ship with a curated concept catalog. If important concepts are still missing from the OS, they should be implemented before release rather than excluded from the catalog.
- Reflection and build-to-learn should remain internal-only or V3-facing capabilities rather than part of the external V2 surface.
- The external V2 release should begin with the learner profile, including their current understanding of AI Builder OS, so tutoring and implementation walkthroughs can adapt appropriately.
- The external V2 concept journey should be an agent-owned personalized learning plan rather than a browseable concept map.
- The external V2 learner profile should use bounded option-based answers rather than open-ended onboarding prompts so the agent can personalize quickly without making setup feel like work.
- The external V2 `Learning plan` surface should show where the learner is in the agent-owned plan, what has already been completed, and what comes next, without turning back into a concept browser.
- The external V2 `Learn next` surface should stay focused on the active concept-learning experience and should not ask the learner for written recap before they can continue; the learner should be able to mark a concept learned directly from that flow.
- The learning agent should derive an explicit teaching strategy from the learner profile before teaching so profile changes produce visible differences in explanation angle, OS-context depth, example choice, and pacing.

Success criteria:
- The OS can explain concepts already present in the current system in context.
- The OS can help capture and teach newly introduced concepts encountered during building.
- The OS can suggest next concepts to learn based on the operator's trajectory, current work, background, and emerging gaps.
- The OS can support build-to-learn pathways for concepts that are not yet implemented in the repo.
- The OS can track concept lifecycle state across upcoming, in progress, learned, and reopened states.
- The OS can let the operator edit concepts, mark them learned, move them back into the learning backlog, and capture follow-up doubts.
- The OS can help relate concepts to each other so learning builds cumulatively rather than as isolated notes.
- The learning agent can use a Feynman-style approach: push toward simple, jargon-free explanation as evidence of real understanding.
- The learning layer feels integrated with the OS rather than like an external notes tool.

Constraints:
- Keep the capability private-first and local-first in the current slice.
- Keep learning grounded in implementation, workflow, and product judgment rather than generic study.
- Avoid turning the OS into an unbounded tutor chat or generic knowledge app.
- Keep the learning agent practical, concise, and oriented toward understanding rather than performative verbosity.

Reason:
AI Builder OS now includes building, learning, reflecting, and compounding understanding as part of the operating model itself. The learning layer is now one of the defining capabilities of the OS and should be treated accordingly.

Validation note:
- The learning layer already includes bounded concept teaching for in-product clarification.
- The OS can recommend next concepts to learn based on current capabilities and unresolved gaps.
- The first build-to-learn pathway flow is working, so concepts can be turned into bounded experiments rather than just notes.
- Remaining open scope centers on evolving the learning layer into a fuller learning-agent and concept-management system.
- The first learning-agent operating model and Feynman-style loop are now defined and the first concept lifecycle manager is now working in-product.
- The concept relationship and dependency slice is now in place, but product review shows the learning layer still contains helper-era behaviors that compete with the live agent.
- The current open scope should lean toward agent-centered learning and retire or demote older helper-style flows so the system feels like one coherent learning experience.
- The next most important sub-initiative is now a true model-generated tutoring agent with:
  - a single-agent-first architecture
  - model + tools + instructions
  - strong tutoring instructions
  - deliberate tool use
  - guardrails
  - explicit human hand-back behavior
  - evaluation coverage for tutoring quality and concept progression
- The next release-shaping move is to introduce an explicit V2 external learning release mode that hides reflection and build-to-learn while keeping the broader capability available internally for V3 development.
- The delivered learning foundations remain in the OS and should continue to work.
- This requirement documents the current release boundary for the learning layer rather than committing to further expansion in this file.

Retirement:
- Reason: Product Director removed this obsolete backlog scope after completing the planned PM work; preserve historical delivery evidence while removing it from actionable work.
- Actor: product-director-chat
- Retired at: 2026-08-03T05:59:54.947762+00:00
- Authorization: R105 proposal 6ecb01f8-4bb2-445f-b077-941d1c35c6b7 revision 1

---

## Rules

* Only requirements with Status: NEW should be converted into tasks
* Requirements move from:
  NEW → IN_PROGRESS → DONE
* PM agent must NOT generate tasks for DONE items

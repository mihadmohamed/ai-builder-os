# System Memory — OS Control Panel

## Purpose

Store project-specific learnings, decisions, and reusable patterns.

Only record information that is likely to matter again.

---

## Failure Memory

Add reusable failure patterns here.

---

## Decision Memory

### [23 May 2026] — Decision: Expose Architect and QA as deterministic agent-workspace surfaces

Decision:
- Add Architect and QA into the shared `Agents` workspace as deterministic review surfaces rather than pretending they are live-chat agents.
- Let Architect summarize current structural hotspots and guardrails from project state.
- Let QA run the existing project validation path and report summary, failures, and confidence from inside the UI.

Reason:
- The refreshed roadmap identified Architect and QA as remaining role-surface gaps.
- The OS should represent the real workflow model more truthfully in-product, even when a role is a review surface rather than a live thread.

Impact:
- Future role additions should stay honest about whether they are conversational, deterministic, or execution-oriented.
- Any deeper Architect or QA workflow should build on these truthful review surfaces rather than replacing them with fake chat.

### [23 May 2026] — Decision: Consolidate overlapping approved review output into existing open requirements

Decision:
- When approved Experience Designer or UI Designer output clearly overlaps an existing open requirement, PM completion should enrich the existing requirement instead of creating a near-duplicate backlog item.
- `R49` now acts as the residual broad workspace-design container after narrower completed workspace/UI slices.

Reason:
- Approved review artifacts were starting to create overlapping backlog requirements, which weakened the requirements file as a clean source of truth.

Impact:
- Future review-completion work should prefer consolidation when overlap is strong.
- Broad design initiatives should remain singular containers rather than multiplying into adjacent backlog duplicates.

### [23 May 2026] — Decision: Decompose the next roadmap step into observability and quality backlog requirements

Decision:
- The next roadmap frontier should be captured as explicit backlog requirements for:
  - run history and inspection
  - workflow timeline and artifact history
  - in-app quality dashboard
  - requirement-level manual verification
  - guided test-card verification flow

Reason:
- The roadmap had the right direction, but the next phase needed to become executable product work rather than staying a high-level theme.

Impact:
- Future planning should treat observability and quality as the immediate next build queue.
- Architect and QA are no longer “missing surfaces”; the new gap is inspection, verification, and signoff clarity.

### [23 May 2026] — Decision: Keep guided manual verification project-scoped and requirement-owned

Decision:
- Guided manual verification should pin one selected verification check at the project level while the Product Director moves through relevant project surfaces.
- The guided card should reuse the same requirement-level verification state, outcomes, and signoff logic instead of becoming a separate testing workflow or artifact type.

Reason:
- Manual verification became much more usable once one active check could stay visible during navigation, but creating a second independent testing system would have added unnecessary complexity and drift.

Impact:
- Future guided-testing work should build on top of requirement-owned verification evidence.
- Any richer test guidance should remain lightweight and contextual rather than becoming a parallel workflow model.

### [23 May 2026] — Decision: Separate project planning, delivery, and quality into distinct sections

Decision:
- Keep `Requirements` focused on sprint planning, structured requirements, and requirement-level manual verification.
- Move implementation-run inspection and workflow timeline into a dedicated `Delivery` section.
- Move deterministic project validation into a dedicated `Quality` section.

Reason:
- Putting implementation runs, workflow history, and project quality on the Requirements page made the page feel too busy and mixed together planning, execution, and validation concerns.

Impact:
- Future project-level observability work should prefer `Delivery` or `Quality` rather than accreting onto `Requirements`.
- Requirement-level signoff evidence should stay with the requirement even while project-wide quality lives elsewhere.

### [23 May 2026] — Decision: Split execution roadmap work into near-term recovery and later Engineer-surface depth

Decision:
- Keep light execution recovery and trust work in the near-term roadmap.
- Move the heavier Engineer-facing execution surface and deeper intervention tooling into a later V2-style phase.

Reason:
- Runs are already real enough that recovery, failure handling, and execution trust matter now.
- A full Engineer surface would pull the control panel toward an execution IDE before the current operating model is mature enough to support that cleanly.

Impact:
- Near-term execution work should focus on rerun/recover paths, error inspection, and safer controls.
- Deeper Engineer-surface work should be treated as later-stage expansion, not immediate follow-on scope.

### [23 May 2026] — Decision: Defer the roadmap surface to V2

Decision:
- Do not expose roadmap as a first-class project section in V1.
- Keep roadmap discussion and phase sequencing in files and chat for now, then revisit a lighter and better-thought-through UI model in V2.

Reason:
- Roadmap discussion proved genuinely useful, but the first UI attempt added too much complexity and disrupted the project flow instead of clarifying it.

Impact:
- The project navigation remains focused on agents, requirements, delivery, and quality.
- Future roadmap work should re-enter only with a clearer and simpler interaction model.

### [23 May 2026] — Decision: Refresh the roadmap to reflect delivered workflow foundations

Decision:
- Rewrite `product/next-phase-roadmap.md` so it reflects the real current product state rather than the earlier planning snapshot.
- Treat multi-agent workspace, Inbox, approvals, automatic PM completion, and sprint execution as delivered foundations.
- Reframe the next true phases around observability, quality/verification, Architect and QA surfaces, and richer execution inspection.

Reason:
- The previous roadmap still described several already-shipped capabilities as future work.
- The product has moved from “add the missing workflow primitives” into “make the workflow more inspectable, trustworthy, and operationally complete.”

Impact:
- Roadmap conversations should now assume the existing agent workspace and workflow layer are real.
- Future planning should focus on run visibility, validation surfaces, remaining role surfaces, and hosted/team-ready evolution.

### [10 May 2026] — Decision: Make navigation hierarchy explicit with level and scope cues

Decision:
- Main navigation should present itself as workspace-level navigation with destination context for workspace overview, project selection, Inbox, and project creation.
- Project navigation should present itself as project-level navigation scoped to the selected project, with Requirements and Agents kept as local project sections.
- The hierarchy should remain native Streamlit controls plus local styling hooks; no new navigation model or dependency is needed for this clarity slice.

Reason:
- R58 addressed confusion in the two-layer navigation structure caused by insufficient visual differentiation.
- Explicit level labels, scope descriptions, and restrained secondary-navigation styling improve orientation while preserving the existing navigation hierarchy.

Impact:
- Future navigation changes should preserve the distinction between workspace-level destinations and selected-project sections.
- User satisfaction, guided usability results, and task-completion improvements remain future feedback metrics; deterministic validation confirms helper behavior, styling hooks, and route preservation only.

### [10 May 2026] — Decision: Keep Open Project cards selection-focused

Decision:
- The Open Project page should help operators compare projects quickly before entering one.
- Project cards should show a restrained status cue, project name, structure state, stable work-signal counts, a next-work summary, and then actions.
- The Open action should remain primary, with Preview as a secondary utility.

Reason:
- R55 addressed frustration and disengagement on the project-selection surface.
- Showing existing work signals and the next visible item improves scan-and-select clarity without adding new project-management behavior.

Impact:
- Future Open Project page changes should preserve the page as a focused project chooser, not a second Workspace or Inbox.
- Survey, user-testing, and navigation-time success criteria still require future human feedback; deterministic validation only confirms structure, helpers, and behavior preservation.

### [10 May 2026] — Decision: Keep navigation task-oriented and hierarchy-explicit

Decision:
- Top-level navigation should name the operator's workspace-level jobs: workspace overview, opening a project, clearing the workflow inbox, and creating a project.
- Project-level navigation should remain visibly separate from the top-level navigation and keep Requirements and Agents scoped inside the selected project.
- Legacy session labels should map forward to the current labels so existing Streamlit session state does not break navigation.

Reason:
- R54 addressed confusion and delays caused by ambiguous main navigation.
- Renaming the existing destinations improves orientation without changing file-backed workflow semantics or adding a new navigation model.

Impact:
- Future navigation work should preserve the split between workspace-level destinations and selected-project sections.
- Deterministic validation can confirm route structure and label intent, but task-completion improvement still requires user feedback or usability testing.

### [10 May 2026] — Decision: Keep workflow cards light and section-led

Decision:
- Workspace approval cards and Inbox workflow cards should use a shared lightweight card marker and restrained visual treatment.
- Inbox groups should communicate attention state and item count before showing individual workflow cards.
- State colors should stay tied to existing attention cues rather than becoming broad decorative styling.

Reason:
- R48 simplified Workspace and Inbox visual hierarchy without changing workflow behavior.
- Lighter cards and section-led grouping reduce scan effort while preserving approval review details, clarification forms, thread links, and active-run metadata.

Impact:
- Future Workspace and Inbox UI work should reuse the shared workflow-card grammar before adding new card styles.
- Broader user-satisfaction claims still need direct user feedback; deterministic validation only confirms structure, helpers, and behavior preservation.

### [9 May 2026] — Decision: Keep Workspace role-card actions inside their cards

Decision:
- Workspace role-card summary actions should be visually inside the same card container as the role label, title, and summary.
- Role-card action placement should preserve row symmetry, existing popup behavior, and concise summary content.
- Native Streamlit containers and buttons are sufficient for this pattern; no new UI dependency is needed.

Reason:
- R53 addressed weak association between each agent summary and its action button.
- Keeping the action inside the card reduces scan-and-act friction without changing role semantics or adding workflow behavior.

Impact:
- Future Workspace role-card changes should keep summary actions attached to each card and avoid floating action controls below card boundaries.
- User-feedback ease-of-use claims still require future feedback collection; deterministic validation only confirms structure and behavior.

### [9 May 2026] — Decision: Keep Workspace role cards symmetrical and hierarchy-led

Decision:
- Workspace role cards should stay on a fixed-width row grid, including incomplete rows.
- Role labels, display titles, summaries, and summary actions should have distinct visual hierarchy so the role section stays easy to scan.
- Longer summaries can be visually clamped in the card because the full details remain available in the summary popup.

Reason:
- R52 addressed visual imbalance and weak hierarchy in the Workspace role-card section.
- Symmetry and restrained separation improve scanability without changing role semantics or turning Workspace into a documentation surface.

Impact:
- Future Workspace role-card changes should preserve equal card widths, concise summaries, and visible popup actions.
- Detailed role explanations should remain in the popup rather than expanding card content.

### [9 May 2026] — Decision: Use explicit attention cues for Workspace and Inbox workflow cards

Decision:
- Workspace approval cards and Inbox workflow cards should share an explicit attention cue for approval, waiting, blocked, routed, and running states.
- The cue should clarify the user's next kind of attention before title, metadata, summary, detail, and action controls.

Reason:
- R39 focused on UI intentionality and simplicity without changing workflow semantics.
- A shared cue reduces scan burden while preserving full review detail and existing actions.

Impact:
- Future Workspace and Inbox card changes should preserve this consistent card anatomy.
- Satisfaction and task-time claims still require separate user feedback; deterministic validation only proves behavior and helper consistency.

### [8 May 2026] — Decision: Keep Workspace orienting and Inbox action-focused

Decision:
- Workspace should provide the calm operating snapshot, decision-ready approvals, and agent reference.
- Inbox should remain the full workflow queue with filters, state-grouped items, and the complete approval/blocker/routed/running work surface.
- Workspace and Inbox cards should share a compact card grammar: status/type cue, title, metadata, summary/detail, then action.

Reason:
- R40 identified Workspace and Inbox clutter and weak intentionality as a user-facing problem.
- The UI needed clearer hierarchy without changing workflow semantics or duplicating the full Inbox on Workspace.

Impact:
- Future Workspace changes should avoid becoming a second Inbox.
- Future Inbox changes should preserve workflow-state grouping and action availability.

### [8 May 2026] — Decision: Group Requirements page by priority focus before planning detail

Decision:
- The Requirements page should show priority-focus requirements first, then planned backlog, then sprint planning, then completed reference items.
- Requirement expanders should expose status, priority, and effort in their collapsed labels/metadata so the operator can scan before opening forms.
- Sprint planning remains visible, but secondary to the main requirement focus area.

Reason:
- R36 identified the Requirements page as noisy and hard to prioritise.
- Grouping by attention need reduces clutter without changing the file-backed requirement model or removing existing controls.

Impact:
- Future Requirements page changes should preserve a clear first-read path for high-priority, new, and in-progress work.
- Survey-based satisfaction improvement remains a future feedback measurement, not a deterministic validation claim.

### [7 May 2026] — Decision: Surface decision-ready approvals on Workspace without replacing Inbox

Decision:
- The Workspace page may show open approval requests as a compact decision area.
- Workspace approval cards should reuse the same approval handlers, labels, and review-detail expansion as Inbox.
- Inbox remains the full workflow queue for approvals, blocked work, routed findings, and running work.

Reason:
- The Product Director needs timely approval visibility at the starting point of the control panel without turning Workspace into a duplicate Inbox.

Impact:
- Future approval visibility improvements should preserve a lightweight Workspace summary and keep broader workflow triage in Inbox.

### [25 Apr 2026] — Decision: Keep V1 local-first and requirements-focused

Decision:
- V1 of OS Control Panel should be an internal, local-first control panel.
- V1 should focus on project creation, PM discovery, structured requirement editing, and prioritisation.
- V1 should edit requirements only, not project memory or rules.

Reason:
- The product needs to become useful quickly without turning into a full remote operating console too early.
- Requirement capture and prioritisation are the highest-value operator workflows for the first slice.

Impact:
- Remote/shared access remains backlog work.
- Deep workflow execution control and broader project metadata editing are intentionally deferred.
- Lightweight next-action recommendation remains deferred backlog work rather than part of the committed V1 scope.

### [25 Apr 2026] — Decision: Reuse shared workspace parsing helpers in the first UI slice

Decision:
- Reuse shared workspace helper functions from the root `tools/common.py` module for project discovery, requirement parsing, task parsing, and structure checks in the first control panel slice.

Reason:
- The control panel is meant to reflect the current OS state rather than invent a second interpretation layer.
- Reusing the shared parsing logic keeps the first slice simpler and reduces duplication.

Impact:
- The workspace summary stays aligned with the existing OS tooling.
- If parsing behavior changes centrally later, the control panel can inherit those improvements more easily.

### [25 Apr 2026] — Decision: Keep requirement editing file-backed and PM recommendation lightweight in V1

Decision:
- The project page should edit requirements by rewriting `product/requirements.md` through structured forms rather than introducing a separate data store.
- The PM prioritisation recommendation in V1 should be a lightweight file-based heuristic, not a full agent-execution surface.

Reason:
- V1 is meant to be a control panel that stays faithful to the existing OS source of truth.
- A small recommendation layer is useful now, while deeper orchestration and agent control remain intentionally deferred.

Impact:
- Requirement changes remain transparent and compatible with the existing OS workflow.
- The project page supports structured editing and recommendation without turning into a full runtime agent console.

### [25 Apr 2026] — Decision: Move next-action recommendation to backlog and finish V1 around discovery + requirements

Decision:
- Keep V1 focused on project creation, PM discovery, and structured requirement management.
- Move the lightweight next-action recommendation surface out of V1 and into backlog work.

Reason:
- The control panel is already useful without that surface, and removing it keeps the first release tighter and easier to validate.

Impact:
- `R1` can close cleanly once discovery and requirements management are complete.
- A next-action recommendation can return later as a separate backlog requirement rather than diluting the first release.

### [25 Apr 2026] — Decision: Keep Experience Designer project-level and handoff-based in the first slice

Decision:
- Expose Experience Designer only at the project level.
- Keep the Experience Designer flow focused on structured finding capture, routing classification, and manual handoff state.
- Do not auto-trigger PM or silently create product work from Experience Designer findings.

Reason:
- This preserves the Experience Designer vs PM boundary while still making UX feedback usable inside the control panel.
- The Product Director wanted a structured in-UI feedback loop without turning the UI into an auto-orchestrating workflow console.

Impact:
- UX feedback can now be captured and routed inside the project page.
- PM remains the role that turns approved product work into tasks.
- Future automation can build on the saved findings later if needed.

### [25 Apr 2026] — Decision: Treat routed Experience Designer findings as active workflow state

Decision:
- When an Experience Designer finding reaches `handoff_state: routed`, it should be treated as active workflow state for `os-control-panel`.
- Orchestrator should consider routed findings before declaring the project idle.

Reason:
- The control panel now captures UX findings as file-backed artifacts.
- Those findings represent real work waiting on PM or Product Director even when `requirements.md` and `tasks.md` are otherwise quiet.

Impact:
- Routed UX findings can trigger the next role without first being rewritten into requirements.
- The project avoids false idle states after user feedback is captured through the UI.

### [25 Apr 2026] — Decision: Keep the workspace summary count-based and visually calm

Decision:
- Use a workspace title that describes the OS surface rather than repeating the `os-control-panel` project name.
- Keep workspace project cards focused on high-level counts instead of full task-detail lists.
- Render agent role cards with consistent presentation so the workspace feels easier to scan.

Reason:
- The Product Director reported confusion between the page title and the project name, plus unnecessary clutter in the workspace summary.
- These are in-scope experience improvements that make the control panel easier to use without expanding feature scope.

Impact:
- The workspace overview now reads more like an operating surface and less like a raw project dump.
- Deeper task detail remains available inside the project view where it belongs.

### [25 Apr 2026] — Decision: Use balanced role-card rows instead of one crowded six-card strip

Decision:
- Render the workspace role cards in balanced rows instead of one long six-card row.
- Keep the role cards fixed-height and lightweight, but give each card more width so the visual rhythm stays more even.

Reason:
- The remaining visual imbalance in the role-card section was caused less by missing CSS and more by trying to fit too many narrow cards into one horizontal strip.

Impact:
- The workspace role section feels more visually even and easier to scan.
- The role content stays the same while the presentation is calmer and more consistent.

### [25 Apr 2026] — Decision: Use a compact workspace card grid instead of a single full-width project stack

Decision:
- Render workspace project summaries in a compact grid rather than one full-width stacked column.
- Add explicit vertical separation between role-card rows instead of relying on implicit layout spacing.

Reason:
- The Product Director flagged the workspace as too stretched and visually flat when project cards consumed the full width.
- The role-card section also needed clearer row separation after moving to a balanced-row layout.

Impact:
- The workspace overview feels more balanced and easier to scan.
- Layout polish remains in scope without expanding the workspace into a more complex dashboard.

### [25 Apr 2026] — Decision: Keep completed requirements visible but out of the main editing path

Decision:
- Show completed requirements in their own lower-priority section beneath unfinished work.
- Keep `DONE` requirements readable, but remove their direct edit controls from the main Requirements flow.

Reason:
- The Product Director wanted the Requirements page to focus attention on live work while still preserving visibility of completed decisions.

Impact:
- The Requirements page now prioritises unfinished work more clearly.
- Completed requirements remain easy to review without competing with active product management tasks.

### [25 Apr 2026] — Decision: Use a two-column layout for active requirement cards when space allows

Decision:
- Render active requirement cards in a two-column layout when the viewport allows it.
- Keep completed requirements in their own lower-priority section and leave their presentation simpler.

Reason:
- The Product Director wanted the Requirements page to make better use of horizontal space without becoming dense or harder to scan.

Impact:
- The active-work area feels more balanced and uses the page width more intentionally.
- The Requirements page stays readable while looking less stretched.

### [25 Apr 2026] — Decision: Left-align lone active requirement cards instead of stretching them across a full row

Decision:
- When an active requirement row contains only one card, render it in a left-aligned narrow column rather than letting it stretch across the full page width.

Reason:
- The Product Director wanted the lone-card row to align with the start of the grid so the card sizing stays consistent without introducing a centered orphan.

Impact:
- Partial active-card rows now stay aligned with the rest of the grid.
- The Requirements page keeps a consistent card size without the final card looking like a centered exception.

### [25 Apr 2026] — Decision: Keep discovery flows progressive rather than form-heavy

Decision:
- Evolve PM Discovery and Experience Designer from large flat forms into staged, question-driven flows.
- Ask for the initial idea or user problem first, then reveal only the next relevant prompts.

Reason:
- The Product Director found the flat forms too heavy and wanted the control panel to feel more guided and relevant during discovery work.

Impact:
- Discovery should become easier to use without changing the approval and routing boundaries already in the OS.
- This keeps the control panel aligned with its goal of structured product work without feeling like an admin form.

### [25 Apr 2026] — Decision: Keep progressive discovery lightweight and local-state driven

Decision:
- Use small staged UI state for in-progress PM Discovery and Experience Designer intake.
- Keep file persistence at the meaningful save points: discovery drafts, approved requirements, and saved experience findings.

Reason:
- The Product Director wanted dynamic guided intake without turning either flow into a noisy full chat console.

Impact:
- The control panel now feels more guided while preserving the simple archive-and-artifact model already in the OS.
- Orchestration stays grounded in saved product artifacts rather than transient interaction noise.

### [25 Apr 2026] — Decision: Use a background implementation-run artifact for UI-initiated execution

Decision:
- Start requirement implementation from the control panel by creating a file-backed implementation-run artifact and launching a background worker.
- Allow only one active implementation run at a time within a project.
- Return a concise completion summary or error to the originating requirement card rather than exposing a full trace console.

Reason:
- The Product Director wanted to start implementation without dropping to the CLI, but the UI still needs an honest, debuggable execution model.
- A background run artifact preserves state, supports one-at-a-time orchestration, and stays consistent with the OS file-backed approach.

Impact:
- Eligible requirements can now expose a direct implementation entry point in the UI.
- Operators can see active run status and the latest outcome from the same requirement surface.
- A second project can still start its own implementation flow without being blocked by another project's active run.
- The first slice remains intentionally lightweight: summary and error reporting are in scope, while richer execution controls remain deferred.

### [4 May 2026] — Decision: Show implementation progress as lifecycle-derived state

Decision:
- Implementation progress in requirement cards should be derived from the existing run lifecycle: queued, running, completed, and failed.
- The UI should present approximate progress and a concise stage explanation, not exact timing or remaining-work estimates.

Reason:
- The background worker cannot honestly know exact completion percentage from outside the Codex execution.
- Lifecycle-derived progress gives the operator immediate feedback without changing the execution model.

Impact:
- Future implementation progress improvements should preserve honest, status-based messaging unless the runner gains real structured progress events.

### [26 Apr 2026] — Decision: Use a generic agent-thread model for PM chat, but keep saved output file-backed and UI history minimal

Decision:
- Replace the old staged PM Discovery form with a project-level agent workspace that starts with PM and `Requirement Discovery` mode.
- Use a generic agent-thread artifact model so future agent chats can reuse the same structure.
- Keep the visible UI focused on the current thread and the resulting draft rather than a large conversation archive.
- Save approved PM output into `product/requirements.md` instead of creating a second source of truth.

Reason:
- The Product Director wanted PM Discovery to feel like a real PM interaction rather than a guided form.
- This requirement introduces a new interaction model and future agent-expansion boundary, so the underlying structure needed to be reusable rather than PM-specific glue code.
- The UI still needs to stay calm and operator-friendly rather than turning into a chat-history console.

### [1 May 2026] — Decision: Open projects from workspace cards instead of a separate top-level project tab

Decision:
- Keep the workspace as the primary entry point.
- Remove the redundant top-level `Project Detail` tab.
- Let operators open a project from its workspace card, then show the existing project-level Requirements, Agents, and Experience Designer tabs inside that selected project view.

Reason:
- The Product Director wanted cleaner navigation and found the separate Project Detail top-level tab unnecessary once project cards can open projects directly.

Impact:
- Top-level navigation stays focused on Workspace and New Project.
- Project-level workflows remain available after selecting a project from the workspace.

Impact:
- `os-control-panel` now has a true PM chat thread for discovery work.
- Future agents can plug into the same agent-workspace pattern without replacing the project-page layout again.
- The source of truth remains the project requirement file, while thread state stays a lightweight interaction artifact.

### [30 Apr 2026] — Decision: Keep workspace agent summaries informational only

Decision:
- Workspace agent tiles can open concise summary popups covering capability, memory/context, and workflow position.
- These popups are informational only and must not trigger agents, edit memory, or mutate workflow state.

Reason:
- The Product Director needs to understand what each agent does without opening raw role, memory, or workflow files.
- Keeping the surface read-only preserves the V1 boundary between explanation and workflow execution.

Impact:
- Agent role understanding is available directly from the workspace.
- Richer agent execution controls remain separate from this summary surface.

### [1 May 2026] — Decision: Derive workspace agent summaries from live OS source files

Decision:
- Build agent summary popups from the current role and workflow files instead of maintaining a separate hand-written summary catalog.
- Keep the popup surface curated in shape, but derive its content from the real OS implementation files.

Reason:
- The Product Director wanted the popup summaries to reflect the real current system rather than a parallel explanation layer that could drift.

Impact:
- Agent summaries now change with the role and workflow docs.
- Popup wording should stay closer to implementation reality, even if the language is a little less polished than a fully hand-authored summary.

### [1 May 2026] — Decision: Deprecate the legacy discovery-session store

Decision:
- Remove the old `discovery_sessions.json` store and rely only on the PM agent-thread model for PM discovery work.

Reason:
- The staged discovery-session flow is no longer the active product path, and keeping both stores creates unnecessary conceptual drift.

Impact:
- PM discovery now has one file-backed interaction model instead of two.
- Historical staged-discovery artifacts are intentionally discarded rather than preserved as UI history.

### [1 May 2026] — Decision: Use a hybrid adaptive planner for PM discovery before full live-agent mode

Decision:
- Make PM discovery process prior answers and choose the next missing or unclear field instead of walking a fixed question list.
- Keep the PM thread deterministic and file-backed, but add a planner seam so a later full live-agent mode can replace the hybrid planner cleanly.

Reason:
- The Product Director expected PM discovery to feel intelligent and responsive to prior answers, not like a structured questionnaire wearing chat UI.
- A hybrid planner improves requirement quality now without taking on the full runtime and trust complexity of a live agent yet.

Impact:
- PM discovery can stay on a vague topic until it has enough context, then move forward with a more relevant next question.
- The thread artifact now carries planner intent explicitly, which gives the future full live-agent mode a cleaner landing point.

### [1 May 2026] — Decision: Use live PM by default in the New Project tab, while keeping in-project PM hybrid

Decision:
- Make the New Project tab default to a live PM requirement-discovery flow.
- Keep the in-project PM workspace on the hybrid planner for now.
- Create new projects from reviewed live PM drafts, including the drafted initial requirement title and body.

Reason:
- A brand-new project starts with the least local context, so this is where a live PM agent adds the most value first.
- Existing projects still benefit from the lower-latency, more deterministic hybrid planner because they already have local project state.

Impact:
- The control panel now has two PM discovery surfaces with different runtimes by design:
  - live PM for brand-new projects
  - hybrid PM for in-project requirement discovery
- Project scaffolding now seeds `R1` from the reviewed PM draft instead of a raw placeholder requirement body.

### [4 May 2026] — Decision: Retire the hybrid PM planner and use live PM for project-level discovery too

Decision:
- Stop using the hybrid PM planner for in-project requirement discovery.
- Use the same live PM runtime for PM chat everywhere it is exposed in the control panel.

Reason:
- The Product Director found the live PM path materially more useful and the hybrid path not useful enough to justify keeping two PM runtimes.

Impact:
- PM discovery now behaves consistently between New Project and existing project agent workspaces.
- The old hybrid planner logic is no longer the active PM path, which reduces operator confusion and product drift.

### [4 May 2026] — Decision: Simplify the control-panel UI and rename the visible agent personas

Decision:
- Keep workspace project cards in a stable two-column layout, with lone cards left-aligned.
- Remove the project-level Experience Designer tab from the UI.
- Change the visible agent display names to:
  - PM -> Tom
  - Experience Designer -> Enzo
  - Engineer -> Maciej
  - QA -> Richard
  - Architect -> Andy
  - Orchestrator -> Paul

Reason:
- The Product Director wanted a tidier workspace layout, less project-level surface area, and friendlier visible agent names without changing the underlying OS role identities.

Impact:
- Workspace rows stay visually steadier when only one project card appears.
- The project detail view is narrower and more focused on Requirements and Agents.
- Agent cards and summary popups now show persona-style display names while the underlying workflow roles stay unchanged.

### [4 May 2026] — Decision: Keep project preview derived and local-process based

Decision:
- Project preview should be derived from existing project files and runtime conventions, not stored as a new workflow artifact.
- The first previewable runtime is a local Streamlit app with `src/app.py`.
- Launch preview servers through a lightweight background process and expose a standard local URL that can open in a new browser tab.
- Do not introduce a general process manager, remote hosting model, or deep health diagnostics in the first slice.

Reason:
- R24 introduces a new runtime path, so it needs guardrails before implementation.
- The control panel already runs local-first and most current UI projects use Streamlit, making a derived Streamlit preview the smallest coherent implementation.
- Avoiding a separate preview store prevents drift from the existing file-backed project source of truth.

Impact:
- Engineer should add preview helpers around availability, URL/command derivation, and lightweight launch/reuse behavior.
- Non-Streamlit or non-UI projects should explain that preview is unavailable rather than pretending every project is runnable.
- Future preview runtimes can extend the derived metadata model without changing requirement or workflow files.

### [4 May 2026] — Decision: Build Phase 1 around a shared multi-agent workspace

Decision:
- Reintroduce Experience Designer through the shared `Agents` workspace instead of restoring a bespoke project tab.
- Add UI Designer as a distinct role focused on visual system, aesthetics, interaction design, and layout guidance.
- Expose Orchestrator inside the `Agents` workspace as a code-driven control surface rather than a freeform live chat.

Reason:
- The control panel had become too PM-centric for the next stage of the OS.
- Experience synthesis, interface design, and workflow control all need a consistent home if the control panel is going to become a real agent workflow surface.

Impact:
- The shared agent-thread model is now the base for multi-agent expansion.
- Experience Designer returns through `Agents`, not through a standalone tab.
- UI Designer becomes a first-class role without blurring Experience Designer’s evidence-driven boundary.
- Orchestrator guidance is visible in the same workspace as the other agents, while staying deterministic and authoritative.

### [4 May 2026] — Decision: Add a durable workflow inbox and explicit approval layer

Decision:
- Add a top-level Inbox surface to the control panel.
- Introduce file-backed approval requests for important draft transitions.
- Treat open approvals as active workflow state in Orchestrator and status tooling.

Reason:
- The control panel now has enough workflow state that implicit approvals and scattered review actions were becoming hard to track.
- Drafts should not silently become requirements or findings without a durable human checkpoint.

Impact:
- PM requirement drafts, Experience Designer findings, and UI Designer briefs can now move through explicit approval requests.
- The Product Director has one place to see waiting, blocked, routed, and running work.
- Routing and status surfaces stay aligned with the same file-backed workflow truth.

### [5 May 2026] — Decision: Let live PM create durable clarifications automatically

Decision:
- Keep PM clarifications as a real workflow concept.
- Move the responsibility for creating durable clarifications into the live PM discovery flow when the ambiguity is materially blocking.
- Let thread-linked clarifications be answered from Inbox so the blocked PM thread can resume cleanly.

Reason:
- Manual testing showed that clarification itself was valuable, but asking the Product Director to route the clarification manually was not.
- PM should own ambiguity detection when requirement shape or implementation semantics would otherwise be guessed.

Impact:
- PM can now escalate significant ambiguity into a durable Inbox clarification automatically.
- Thread-linked clarifications no longer leave the Product Director to do PM bookkeeping before the workflow can continue.
- The OS keeps durable clarification state, but uses it more selectively and intelligently.

### [5 May 2026] — Decision: Inbox approvals must be reviewable before action

Decision:
- Approval cards in Inbox should expose the full underlying draft before the Product Director approves or rejects them.

Reason:
- Manual verification showed that one-line approval summaries were not trustworthy enough for real workflow signoff.

Impact:
- PM requirement drafts, Experience Designer findings, and UI Designer briefs can now be reviewed in place before approval.
- The approval surface is more informative without adding a second approval workflow.

### [5 May 2026] — Decision: Approved review work must continue automatically to a result

Decision:
- Approving Experience Designer findings or UI Designer reviews should not stop at artifact persistence.
- Approved review work should automatically run through a PM completion step that ends in either:
  - a new backlog requirement
  - or an explicit Product Director scope confirmation

Reason:
- Manual use showed that “approved” without a downstream result feels non-actionable and incomplete.
- The previous behavior was inconsistent across review types and left UI reviews without a meaningful next step.

Impact:
- Experience findings can resolve straight into backlog instead of waiting for manual PM pickup later.
- Approved UI reviews now feed a real product outcome rather than only being archived as reference material.
- Inbox remains the place for explicit scope decisions, while PM completion handles the normal in-scope path automatically.

### [6 May 2026] — Decision: UI and experience-heavy implementation work must route through design agents before Engineer

Decision:
- Structural work still routes through Architect first.
- Separately, user-facing implementation work should not go straight to Engineer when the requirement is clearly:
  - experience/usability-heavy
  - UI/visual-heavy
- Experience-heavy work should route through Experience Designer before Engineer.
- UI-heavy work should route through UI Designer before Engineer.

Reason:
- The Product Director explicitly asked whether UI Designer and Experience Designer are actually wired into the requirement implementation workflow.
- The prior workflow only enforced Architect for structural work, leaving meaningful user-facing work too dependent on ad hoc judgment during implementation.

Impact:
- The deterministic Orchestrator and the in-app Orchestrator now share explicit routing branches for UI and experience work.
- The background requirement-implementation prompt now warns against skipping the relevant design agent when the requirement clearly calls for it.

### [7 May 2026] — Decision: Agent entry and Inbox hierarchy should explain intent before interaction

Decision:
- Agent selection should be card-led and explorable rather than dropdown-led and blind.
- Mode selection should explain intent at the moment of choice.
- Inbox should group work by workflow state instead of presenting one same-weight stack.
- Project cards should feel like meaningful work entry points, not generic status boxes.

Reason:
- UI Designer review found that the app was functionally strong but still too “stacked Streamlit” in several important places.
- The highest-leverage improvements were in selection clarity, workflow scanability, and reducing repetitive framing.

Impact:
- The agent workspace now orients the Product Director before thread entry.
- Inbox hierarchy is now more state-driven and easier to scan.
- Project entry surfaces better separate identity, state, and action.

### [10 May 2026] — Decision: Main navigation should use a native segmented control

Decision:
- The control panel's top-level navigation should use Streamlit's native segmented-control pattern instead of a plain horizontal radio group.
- The four top-level destinations remain stable: Workspace, Open Project, Inbox, and Create Project.
- Project-level navigation remains a separate vertical section rail so global and local navigation do not compete.

Reason:
- R56 identified main-navigation clarity and quick access as the core workflow problem.
- A segmented control better communicates mutually exclusive top-level destinations while preserving native Streamlit rerun behavior.

Impact:
- Main navigation now feels more deliberate without adding a sidebar, custom component, or new routing model.
- Future navigation work should preserve this global/local distinction unless the product scope changes.

### [10 May 2026] — Decision: Agent mode selection should stay close to selected-agent context

Decision:
- The Agents project section should keep agent selection and mode selection as separate decisions, but render selected-agent context directly before the mode options.
- Selected-agent and mode-choice presentation should use native Streamlit containers/buttons plus local CSS hooks, not a new component or custom navigation model.

Reason:
- R57 identified unnecessary visual distance between agent and mode selection as the main usability issue.
- Keeping the selected role visible at the mode decision point reduces context switching while preserving current thread and mode semantics.

Impact:
- Future Agents workspace changes should preserve this role-then-mode relationship unless the agent workflow model itself changes.
- Usability-test timing and satisfaction metrics remain product evidence to gather later, not deterministic validation claims.

### [10 May 2026] — Decision: Opened-project control belongs in a compact utility header

Decision:
- The opened-project page should group project identity, file path, preview access, and agent assignment orientation in one compact project-control header.
- Preview remains the existing local Streamlit preview action, and agent assignment remains the existing choice of agent and mode inside the Agents section.

Reason:
- R59 identified project-control layout frustration around preview access and agent assignment.
- A header-level utility area improves orientation without introducing a new assignment backend, a new navigation model, or a broader project-detail redesign.

Impact:
- Future project-detail layout work should preserve this compact project-control header unless the project workflow model changes.
- Survey satisfaction, time-to-access, and reported-issue reductions remain future product evidence, not deterministic validation claims.

---

## Observations

Store evidence-bearing product observations here.

Suggested format:

### O1 — Short observation title

Observation:
- What seems to be true

Evidence:
- What supports the observation

Confidence:
- High | Medium | Low

Validation method:
- How the evidence was gathered

Implication:
- What this suggests for future prioritisation or strategy

Use this section for findings that may influence future prioritisation or strategic direction.

---

## Heuristic Memory

Add project-specific heuristics here.

- `product/next-phase-roadmap.md` is the planning source of truth for the next control-plane expansion.
- The next major build phase should prioritize shared multi-agent infrastructure and workflow visibility over adding many new role-specific tabs.
- Reintroduce Experience Designer only through the shared `Agents` workspace, not as a standalone project tab.
- UI Designer should treat Streamlit as a real product medium with its own strengths and constraints: strong first-screen focus, restrained use of containers, clear stateful navigation, and progressive disclosure over stacked widget sprawl.
- UI Designer may recommend `streamlit-extras` or Streamlit components when they clearly improve workflow clarity or interaction quality, but should prefer native Streamlit first and justify every extra explicitly.
- Sprint V1 is project-local, sequential, and deliberately preserves the one-active-implementation-per-project rule; backlog items become execution-ready through the sprint flow rather than by making backlog directly runnable.
- Sprint completion should be explicit and operator-confirmed; once confirmed, the sprint should clear so the next sprint can be planned cleanly.
- Completed requirements belong in a compact archive, not a long same-weight card stack competing with active work.
- Dual-level navigation is clearer when global navigation stays horizontal with an explicit main-navigation label while selected-project navigation uses a compact vertical rail beside project content.
- Top-level navigation should remain native Streamlit segmented control unless a future requirement justifies a broader navigation model.
- Implementation observability should be project-first and recent-first: show active and historical runs in one compact requirements-page panel, distinguish stale failures from ordinary failures, and preview the captured output/log artifacts inline.
- Workflow history should be reconstructed from durable artifacts the OS already owns: approvals, clarifications, findings, agent-thread transitions, and implementation runs. Do not fabricate requirement-state history that was never recorded.
- Quality should live as its own persistent signal: reuse the deterministic QA runner, store the latest review as durable control-plane state, and keep the quality panel visually separate from implementation and workflow sections.
- Manual verification should live with the requirement itself: store checks, outcomes, and notes per requirement, derive signoff state from that evidence, and keep it editable even after the requirement is marked done.
- Guided testing should stay lightweight: pin one selected verification check at the project level so it remains visible while the Product Director moves through the project, but keep the underlying state requirement-level rather than creating a second testing workflow object.
- Public-readiness should be treated as its own product phase, not an afterthought: the public repo story and the public Streamlit showcase are separate concerns from the private operator control panel, and the showcase app should explain the OS rather than expose raw internal workflow surfaces as the main demo.
- Before publication, the repo needs a deliberate public-safe pass: clearer root storytelling, an explicit publication checklist, and a more visible distinction between durable product files and local operational state.
- The public Streamlit story should be a separate showcase app, not the raw operator control panel. The showcase should explain the OS, the workflow, and the example projects without pretending to be the operator surface itself.
- Public showcase repo links should be configurable through one explicit repo URL setting so the final GitHub destination can be aligned without last-minute code hunting.

---

## Open Questions

Add unresolved project questions here.

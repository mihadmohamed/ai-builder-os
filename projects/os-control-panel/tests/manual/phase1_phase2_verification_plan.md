# Manual Verification Plan — Phase 1 and Phase 2

Use this plan to manually verify the new control-panel functionality delivered in:

- `R25 — Phase 1 multi-agent workspace foundation`
- `R26 — Phase 2 workflow inbox and approval layer`

This plan is designed so you can test one slice at a time and report back with a simple checkpoint ID.

---

## How To Use This Plan

1. Run the control panel locally.
2. Work through the checkpoints in order.
3. After each checkpoint, send me:
   - checkpoint ID
   - `PASS` or `FAIL`
   - one short note if anything felt off

Recommended reply format:

```text
R25-T1 — PASS — PM thread opened and drafted correctly.
R25-T2 — FAIL — Experience Designer did not save the finding.
```

I can then track confirmed verification back against the requirement and help fix anything that fails.

---

## Preconditions

Before starting:

- Launch the control panel app.
- Open the workspace in a browser.
- Make sure `OPENAI_API_KEY` is available so the live agent flows can run.
- Use project: `os-control-panel` unless a step explicitly says otherwise.

---

## Verification Status Tracker

All checkpoints start as `PENDING`.

| Checkpoint | Requirement | Capability | Status |
|---|---|---|---|
| R25-T1 | R25 | Shared agent workspace exposes Phase 1 agent set | PENDING |
| R25-T2 | R25 | PM live requirement discovery still works in `Agents` | PENDING |
| R25-T3 | R25 | Experience Designer `Feedback Synthesis` works end to end | PENDING |
| R25-T4 | R25 | Experience Designer `Usability Review` mode is available and usable | PENDING |
| R25-T5 | R25 | UI Designer `Design Direction` works end to end | PENDING |
| R25-T6 | R25 | UI Designer `UI Review` mode is available and usable | PENDING |
| R25-T7 | R25 | Orchestrator is available in `Agents` and explains next step | PENDING |
| R26-T1 | R26 | Inbox surface exists and shows approval requests | PENDING |
| R26-T2 | R26 | PM draft approval flow works end to end | PENDING |
| R26-T3 | R26 | Experience Designer approval flow works end to end | PENDING |
| R26-T4 | R26 | UI Designer approval rejection flow works end to end | PENDING |
| R26-T5 | R26 | Inbox shows waiting thread state correctly | PENDING |
| R26-T6 | R26 | Inbox shows blocked PM clarification state correctly | PENDING |

---

## Phase 1 — Multi-Agent Workspace Foundation

### R25-T1 — Agent workspace exposes the Phase 1 agent set

Goal:
- Confirm the shared `Agents` workspace is no longer PM-only.

Steps:
1. Open project `os-control-panel`.
2. Open the `Agents` tab.
3. Open the `Agent` selector.

Expected:
- You can select:
  - `PM`
  - `Experience Designer`
  - `UI Designer`
  - `Orchestrator`

Pass if:
- All four agents are present in the selector.

---

### R25-T2 — PM live requirement discovery still works in `Agents`

Goal:
- Confirm Phase 1 did not break the existing PM live workflow.

Steps:
1. In `Agents`, select:
   - `Agent: PM`
   - `Mode: Requirement Discovery`
2. Start a PM thread with a simple idea, for example:
   - `I want a cleaner way to review approvals in the control panel.`
3. Answer at least one PM follow-up.
4. Use either:
   - wait for PM to decide it can draft
   - or click `Draft requirements now`

Expected:
- PM asks a live follow-up question.
- PM eventually produces a requirement draft.
- The draft appears in the PM panel.

Pass if:
- The conversation feels live and the draft appears successfully.

Cleanup:
- Do not send this one for approval yet unless you want to use it again in `R26-T2`.

---

### R25-T3 — Experience Designer `Feedback Synthesis` works end to end

Goal:
- Confirm Experience Designer can synthesize feedback and produce a draft finding.

Steps:
1. In `Agents`, select:
   - `Agent: Experience Designer`
   - `Mode: Feedback Synthesis`
2. Start with:
   - `The workflow feels noisy and it is hard to see what needs my attention first.`
3. Answer any follow-up question.
4. Use `Draft finding now` if needed.

Expected:
- Experience Designer asks a relevant follow-up.
- A structured finding draft appears.
- The draft reads like a workflow/UX finding, not a PM requirement.

Pass if:
- You get a credible structured finding draft.

Cleanup:
- Leave the draft there for `R26-T3`.

---

### R25-T4 — Experience Designer `Usability Review` mode is available and usable

Goal:
- Confirm the second Experience Designer mode is present and behaves sensibly.

Steps:
1. In `Agents`, select:
   - `Agent: Experience Designer`
   - `Mode: Usability Review`
2. Start with:
   - `The inbox layout feels a bit flat and I want a clearer visual hierarchy.`
3. Observe the first question and, if needed, answer once.

Expected:
- Usability Review mode is selectable.
- The response is about UI review/polish rather than generic PM work.

Pass if:
- The mode is available and clearly feels like visual/UX review.

---

### R25-T5 — UI Designer `Design Direction` works end to end

Goal:
- Confirm UI Designer can discuss visual direction and produce a design brief.

Steps:
1. In `Agents`, select:
   - `Agent: UI Designer`
   - `Mode: Design Direction`
2. Start with:
   - `I want the inbox to feel calmer, more intentional, and less like an admin table.`
3. Answer any follow-up question.
4. Use `Draft design brief now` if needed.

Expected:
- UI Designer asks design-oriented questions.
- A design brief appears with structured guidance.

Pass if:
- You get a usable design brief that speaks to feel, layout, and interface direction.

Cleanup:
- Leave this draft for `R26-T4`.

---

### R25-T6 — UI Designer `UI Review` mode is available and usable

Goal:
- Confirm the second UI Designer mode is present and review-oriented.

Steps:
1. In `Agents`, select:
   - `Agent: UI Designer`
   - `Mode: UI Review`
2. Start with:
   - `Review the requirements page for spacing, hierarchy, and polish.`
3. Observe the first response and optionally answer once.

Expected:
- UI Review mode is selectable.
- The response is about reviewing an existing UI, not inventing a feature requirement.

Pass if:
- The mode is available and clearly positioned as design review.

---

### R25-T7 — Orchestrator is available in `Agents` and explains next step

Goal:
- Confirm Orchestrator is exposed as a code-driven surface inside `Agents`.

Steps:
1. In `Agents`, select:
   - `Agent: Orchestrator`
   - `Mode: Next Step`
2. Observe the recommendation text.

Expected:
- Orchestrator shows:
  - next role
  - next action
  - why
- It should not behave like a chat thread.

Pass if:
- The panel clearly reads as workflow guidance rather than a conversation.

---

## Phase 2 — Workflow Inbox and Approval Layer

### R26-T1 — Inbox exists and shows approval requests

Goal:
- Confirm the Inbox surface exists and can surface approval items.

Steps:
1. Go to the top-level `Inbox` tab.
2. Confirm the tab loads.
3. If there are no items yet, create one by finishing `R26-T2` step 1 first, then return.

Expected:
- Inbox exists.
- It shows summary metrics.
- It has project and status filters.

Pass if:
- The Inbox loads and is clearly intended as the operator review surface.

---

### R26-T2 — PM draft approval flow works end to end

Goal:
- Confirm PM drafts do not commit directly and instead move through approval.

Steps:
1. Return to the PM draft from `R25-T2`, or create a new one.
2. Fill in the save form.
3. Click `Save to requirements.md`.
4. Go to `Inbox`.
5. Find the new approval request from `PM`.
6. Click `Approve`.
7. Return to the project `Requirements` tab.

Expected:
- Saving the draft creates an approval request, not an immediate requirement write.
- Inbox shows the approval.
- Approving it writes a new requirement into `requirements.md`.

Pass if:
- The requirement only appears after approval.

Cleanup:
- If the test requirement was only for verification, note its ID so we can delete it later if needed.

---

### R26-T3 — Experience Designer approval flow works end to end

Goal:
- Confirm Experience Designer findings can move through approval into workflow artifacts.

Steps:
1. Return to the Experience Designer draft from `R25-T3`.
2. Click `Send finding for approval`.
3. Go to `Inbox`.
4. Find the new approval request from `Experience Designer`.
5. Click `Approve`.

Expected:
- A durable approval request is created.
- Approving it removes the open approval.
- The finding is saved into the workflow-artifact model.

Pass if:
- The finding approval appears and resolves successfully.

Optional check:
- Use Orchestrator after approval and see whether the saved finding affects routing.

---

### R26-T4 — UI Designer approval rejection flow works end to end

Goal:
- Confirm design briefs can be reviewed and rejected cleanly.

Steps:
1. Return to the UI Designer draft from `R25-T5`.
2. Click `Send brief for approval`.
3. Go to `Inbox`.
4. Find the new approval request from `UI Designer`.
5. Click `Reject`.

Expected:
- A durable approval request is created.
- Rejecting it removes it from open approvals.
- No further workflow artifact should be created from that brief.

Pass if:
- The rejection works and the approval disappears from the open Inbox view.

---

### R26-T5 — Inbox shows waiting thread state correctly

Goal:
- Confirm active threads waiting on you appear in the Inbox.

Steps:
1. Start a new PM, Experience Designer, or UI Designer thread.
2. Stop after the agent asks a question.
3. Do not reply yet.
4. Open `Inbox`.

Expected:
- Inbox shows a waiting item for that active thread.
- The item is classified under `waiting`.

Pass if:
- The waiting thread appears clearly in the Inbox.

Cleanup:
- Either continue that thread later or archive/complete it after the test.

---

### R26-T6 — Inbox shows blocked PM clarification state correctly

Goal:
- Confirm blocked clarification work appears in the Inbox.

Steps:
1. Go to the `Requirements` tab for `os-control-panel`.
2. Pick an unfinished requirement, ideally a backlog one that is safe to use for testing.
3. Use the PM clarification UI on that requirement.
4. Add:
   - a short summary
   - at least one question
5. Save the clarification.
6. Open `Inbox`.

Expected:
- Inbox shows a blocked item for the clarification.
- The item is classified under `blocked`.

Pass if:
- The clarification appears in the Inbox as blocked workflow state.

Cleanup:
- Resolve the clarification after the test so the project returns to a clean idle state.

---

## Suggested Test Order

If you want the smoothest run, do them in this order:

1. `R25-T1`
2. `R25-T2`
3. `R25-T3`
4. `R25-T5`
5. `R25-T4`
6. `R25-T6`
7. `R25-T7`
8. `R26-T1`
9. `R26-T2`
10. `R26-T3`
11. `R26-T4`
12. `R26-T5`
13. `R26-T6`

That order lets one draft feed the next verification step instead of repeating setup work.

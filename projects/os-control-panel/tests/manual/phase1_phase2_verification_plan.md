# Archived Manual Verification Plan — Phase 1 and Phase 2

This file preserves the original manual verification plan used when the control panel first introduced:

- `R25 — Phase 1 multi-agent workspace foundation`
- `R26 — Phase 2 workflow inbox and approval layer`

It is kept as a historical verification artifact, not as the main current manual test plan for the project.

---

## Current Status

This plan reflects an earlier moment in the control panel's evolution, when the focus was verifying that:

- the shared `Agents` workspace existed and behaved correctly
- Inbox approval and waiting-state flows worked end to end
- Experience Designer, UI Designer, and Orchestrator had become usable project surfaces

Those capabilities are now part of the delivered product baseline.

## How To Use This File Now

Use this file only when you specifically want to:

- review how Phase 1 and Phase 2 were originally verified
- reproduce the original checkpoint-style verification flow
- understand the historical rollout of the shared agent workspace and Inbox approval model

For current manual review, prefer:

- `tests/manual/ux_checks.md`
- `tests/manual/post_test_review_list.md`

---

## Archived Verification Scope

The original checkpoints in this plan covered:

- PM, Experience Designer, UI Designer, and Orchestrator availability inside `Agents`
- PM live requirement discovery in the shared workspace
- Experience Designer and UI Designer draft and approval flows
- Inbox approval handling
- waiting-thread visibility
- blocked PM clarification visibility

These checkpoints were useful at the time because the product was proving the first integrated multi-agent workflow slice.

---

## Historical Notes

A few details in the original checkpoint list now reflect an older product moment:

- the plan predates later Architect and QA agent surfaces inside `Agents`
- it predates later `Delivery` and `Quality` project sections
- it predates the newer in-product manual verification and guided signoff model

That does **not** make the plan wrong; it just means it should be read as a historical verification artifact rather than a current canonical test plan.

---

## Original Checkpoint Record

The original detailed checkpoint list was used during the first rollout of the shared agent workspace and Inbox approval model. If you need the step-by-step historical checklist, recover the earlier version of this file from git history.


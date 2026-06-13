# Hosted Learning Agent Launch Plan Workflow — R81

Status: IMPLEMENTED
Requirement: R81
Related task: Task 231

## Why this workflow ran

The hosted Learning Agent already had:
- deployment phases documentation
- a pre-launch checklist
- a preflight validator

Those were useful, but they still assumed the operator already understood where
they were in the broader launch journey.

What was missing was a calmer top-level view:
- what still has to happen before launch
- what is already done
- what the next execution gate is
- how the higher-level launch plan relates to the lower-level runbook

## PM recommendation

Separate:
- the launch plan
from
- the pre-launch runbook

The plan should answer:
- where are we in the launch journey?
- what phase are we in now?
- what is the next gating step?

The runbook should answer:
- what exactly do I configure and verify?

## UX recommendation

The launch plan should feel steady and easy to scan:
- clear phases
- explicit status
- one next step
- no dense operator prose

The goal is confidence and orientation, especially when the team is carrying a lot
of moving parts at once.

## Implemented decisions

- Added a top-level launch plan checklist to the hosted project
- Kept the pre-launch checklist as the lower-level operator runbook
- Updated the hosted README so the launch plan becomes the first stop and the runbook becomes the second

## Notes for later refinement

- Once a real provider is chosen, add the actual provider name and deployment URL into the launch plan.
- Once the first pilot wave launches, add a short “pilot live” section with the current operator, active cohort size, and support contact.

# Hosted Learning Agent Pilot Polish Workflow — R81

Status: IMPLEMENTED
Requirement: R81
Related task: Task 228

## Why this workflow ran

The hosted wrapper is already technically sound:
- external V2 learning-only surface
- authentication and invite gating
- per-user isolation
- deployment packaging

But a technically safe wrapper is not yet the same thing as a clear external product surface.

Invited learners need the hosted app to answer three questions quickly:
- what is this?
- how do I use it?
- what happens to my data in this pilot?

## PM recommendation

The hosted wrapper should behave like a real invite-only product shell, not just a thin developer harness.

It should clearly frame:
- the product purpose
- the guided learning flow
- the invite-only pilot nature of the release
- the privacy boundary and contact path

Why:
- external learners should not need repo or OS context to orient themselves
- the shell should reduce hesitation before the learner even reaches the canonical learning experience

## Experience / UX recommendation

The first hosted view should explain the flow simply:
1. set your profile
2. follow the learning plan
3. stay with one concept in the learning session

This should be short, visible, and calm.

The sign-in and invite-only states should also feel like product states, not generic auth errors.

## UI recommendation

Keep the hosted shell light:
- one clear title
- one short supporting caption
- one compact “How it works” card
- one compact privacy / pilot card

Do not add feature complexity here. The goal is orientation, not another product layer.

## Implemented decisions

- The hosted sign-in view now explains what the product is and that the pilot is private and invite-only.
- The invite-only rejection state now gives clearer wording and a support route when configured.
- The authenticated hosted shell now includes:
  - a short pilot label
  - a compact “How it works” explanation
  - a clearer privacy/data block
- Canonical learning behavior still remains owned by `projects/os-control-panel`.

## Notes for later refinement

- Once a real external pilot is running, review the hosted shell with actual learners and tighten any wording that still sounds repo-internal.
- If learners hesitate at first-run, the next likely addition is a very small “What you’ll get from this” block, not more navigation or controls.

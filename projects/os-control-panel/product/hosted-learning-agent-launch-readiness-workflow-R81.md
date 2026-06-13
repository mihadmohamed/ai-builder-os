# Hosted Learning Agent Launch Readiness Workflow — R81

Status: IMPLEMENTED
Requirement: R81
Related task: Task 229

## Why this workflow ran

The hosted Learning Agent now has:
- canonical learning behavior
- authentication and isolation
- deployment packaging
- clearer learner-facing shell copy

What it still needed was a disciplined operator path for launch.

Without that, the pilot would be too dependent on memory:
- which env vars matter
- how invite-only mode is checked
- what gets verified before real learners are invited
- what remains intentionally out of scope for the file-backed single-replica pilot

## PM recommendation

Treat launch readiness as product quality, not just infrastructure hygiene.

The hosted pilot needs one operator-facing checklist that makes it easy to answer:
- are we configured correctly?
- are we safe to invite users?
- what exactly do we verify before we call this pilot-ready?

## UX recommendation

The runbook should be easy to scan under pressure:
- one short preparation section
- one exact env/config section
- one smoke-test section
- one invite-readiness signoff section
- one “do not claim yet” section

The goal is calm execution, not comprehensive architecture prose.

## Implemented decisions

- Added a dedicated hosted pilot launch checklist to the external project
- Tightened the hosted README so operators know where to start
- Kept the launch checklist explicitly aligned to the current single-replica, file-backed pilot boundary

## Notes for later refinement

- Once a real hosted environment exists, add one completed example checklist run with timestamps and operator notes.
- When PostgreSQL replaces file-backed pilot state, split the runbook into pilot and beta/production variants rather than letting one checklist grow messy.

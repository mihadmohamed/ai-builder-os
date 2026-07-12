# R72 — Reflection Helper Interaction

Status: Drafted for implementation
Requirement: R72
Task: Task 158

## Purpose

Define the smallest useful private reflection-helper flow so the OS can help turn a raw signal into a stronger structured reflection draft.

## First-slice trigger

Start with a manual operator action.

Initial entry point:
- the Product Director chooses `Capture reflection` from a local-only helper surface
- the flow begins with a raw signal rather than trying to infer intent automatically

Why this trigger first:
- it is simple
- it keeps the first slice private-first
- it avoids over-automating reflection before the interaction pattern is proven useful

## Input

Required input:
- raw signal note

Optional input:
- scope hint: `os`, `project`, `career`, or `public-narrative`
- source hint: `implementation`, `qa`, `pm-discovery`, `experience-review`, `ui-review`, `public-share`, `workday`, `meeting`

## Clarifying-question sequence

The first slice should ask four questions after the raw signal is entered.

### Q1 — What actually happened?
Purpose:
- separate the event from the initial conclusion

### Q2 — Why did this stand out?
Purpose:
- surface the reason the note felt worth capturing

### Q3 — What are you concluding right now?
Purpose:
- distinguish observation from interpretation

### Q4 — How confident are you that this is a real pattern?
Purpose:
- force a lightweight confidence signal before the draft is saved

## Structured output draft

The helper should produce a draft with these fields:
- date
- scope
- source
- raw signal
- what happened
- why it stood out
- current conclusion
- confidence
- possible route

## Default route options

The first slice only needs lightweight route suggestions:
- keep-private
- promote-to-reflection
- candidate-belief
- public-seed

The helper does not need to automate routing yet.

## Storage location

The first slice should write the output into the private reflection layer.

Preferred target:
- `private/thinking/reflections.md`

If the helper only saves a draft block at first, that is acceptable as long as:
- it stays private
- it is clearly labeled
- it can be reviewed and refined later

## UX boundaries

The first slice should:
- feel lightweight
- avoid a full dashboard
- avoid long visible history in the UI
- avoid exposing private reflection content in public surfaces

The first slice should not:
- attempt automatic belief formation
- attempt auto-routing into public artifacts
- become a general journaling system

## Implementation recommendation

Build this as a local-only helper flow first.

Acceptable implementation shapes:
- a narrow control-panel helper surface
- a local-only command/helper script wired into the OS

Preferred shape:
- a small local-only control-panel helper because it keeps the behavior close to the OS while remaining private-first

## Done definition for Task 159

Task 159 should be considered complete when:
- a raw signal can be entered
- the helper asks the four clarifying questions in sequence
- a structured draft is produced
- the draft is saved into the private reflection layer
- the flow remains private-first and local-only


## Validation update

Manual validation of the first implemented slice showed:
- the helper is useful as an in-product reflection capture flow
- saving structured drafts into the private reflection layer works
- the current fixed four-question sequence is too static for the intended reflection quality

## Next-slice direction

The next slice should keep the current private-first structured output model, but replace the fixed question sequence with bounded dynamic questioning.

That means:
- the helper should interpret the raw signal and prior answers
- ask the next most useful context-specific question
- stay lightweight and finite
- finish by saving a structured reflection draft rather than leaving the interaction as a loose chat

Implementation detail is captured in:
- `projects/os-control-panel/product/reflection-helper-dynamic-questioning-R72.md`

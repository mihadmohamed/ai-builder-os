# R73 — Bounded Concept Teaching

Status: Drafted for implementation
Requirement: R73
Task: Task 165

## Purpose

Define the smallest useful teaching/explainer model for the concept-learning helper so the OS can help the operator learn in context before finalizing a concept note.

## Core behavior

The helper should still begin with a concept and a brief description of what feels unclear.
After that, it should respond with a bounded explanation that helps the operator learn something before asking for the final note fields.

The aim is not to become a full tutor.
The aim is to provide enough explanation to turn proximity into understanding.

## Interaction model

### Step 1 — Capture the concept and confusion
Required:
- concept or unfamiliar term
- what seems unclear right now

Optional:
- where it showed up
- current rough understanding

### Step 2 — Provide a bounded explanation
The helper should explain:
- what the concept is
- why it exists
- one nearby distinction or confusion to watch for

### Step 3 — Connect it to the OS
The helper should help answer:
- where this appears in the OS, repo, or workflow
- what product or workflow implication it has

### Step 4 — Finalize the concept note
After the explanation, the operator should be asked for a current working opinion and remaining open questions.
The helper should then save the structured concept note draft.

## Teaching boundaries

The explainer should:
- be short
- stay grounded in current work
- teach enough to improve understanding
- avoid generic essay-like output

The explainer should not:
- become an unbounded chat tutor
- drift into unrelated AI education
- optimize for comprehensiveness over clarity

## Output contract

The final saved draft should still include:
- date
- concept
- where encountered
- current understanding
- what is unclear
- why it exists
- where it appears in the OS
- product implication
- current working opinion
- open questions
- captured via teaching concept-learning helper

## Done definition

Task 165 should be considered complete when:
- the helper teaches something useful before requesting final note fields
- the explanation stays bounded and contextual
- the final output remains a structured private concept note draft
- the interaction feels more like learning than just a better intake form

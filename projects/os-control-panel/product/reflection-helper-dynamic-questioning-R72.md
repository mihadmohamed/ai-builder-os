# R72 — Bounded Dynamic Questioning

Status: Drafted for implementation
Requirement: R72
Task: Task 161

## Purpose

Define the smallest useful dynamic-questioning model for the reflection helper so the OS can ask context-specific follow-up questions without turning the experience into an unbounded journal chat.

## Core behavior

The helper should still begin with a raw signal, but after that it should choose the next question based on:
- the signal itself
- the answers already given
- what is still unclear in the reflection draft

The aim is not to simulate a long conversation.
The aim is to ask the minimum next question that improves reflection quality.

## Interaction model

### Step 1 — Capture the raw signal
Required:
- raw signal

Optional:
- scope hint
- source hint

### Step 2 — Generate the first dynamic follow-up
The helper should interpret the signal and ask the most useful next question.

Examples:
- if the signal is mainly observational, ask what actually happened
- if the signal already includes an event and a conclusion, ask what feels uncertain or why it matters
- if the signal is emotionally charged, ask what specifically triggered that reaction

### Step 3 — Continue for a bounded number of turns
The helper should ask at most 3 follow-up questions before drafting.

Boundaries:
- minimum: 1 follow-up question
- target: 2 follow-up questions
- maximum: 3 follow-up questions

The helper should stop early when it has enough material to separate:
- event
- interpretation
- implication
- confidence

### Step 4 — Draft the structured reflection
At the end of questioning, the helper should produce the same structured private reflection draft shape used by the first slice.

## Question selection rules

The helper should prefer questions that reduce ambiguity in this order:
1. what actually happened
2. why it mattered or stood out
3. what conclusion is emerging
4. how strong the pattern seems

It should avoid:
- repeating the same generic sequence every time
- asking more than one question at once when one would do
- expanding into open-ended coaching or journaling

## UI behavior

The helper should make the dynamic flow legible.

Recommended behavior:
- show the current question only
- show prior answers in a compact transcript
- show a visible in-progress state while the next question is being prepared
- show progress such as `Question 2 of up to 3` or equivalent bounded cue

The UI should not imply that the interaction is indefinite.

## Output contract

The final saved draft should still include:
- date
- scope
- source
- raw signal
- what happened
- why it stood out
- current conclusion
- confidence
- possible route
- captured via dynamic reflection helper

## Prompting boundary

The helper should behave more like a bounded reflection editor than a general-purpose chat agent.

That means:
- it may ask context-specific questions
- it may adapt sequencing
- it should not wander into unrelated advice or broad coaching
- it should always converge toward a saved structured draft

## Done definition

Task 161 should be considered complete when:
- two materially different raw signals lead to different follow-up questions
- the interaction still feels lightweight and bounded
- the final output remains a structured private reflection draft
- the helper clearly signals when it is preparing the next question

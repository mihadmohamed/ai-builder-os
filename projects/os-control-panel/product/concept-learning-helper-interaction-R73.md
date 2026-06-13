# R73 — Concept-Learning Helper Interaction

Status: Drafted for implementation
Requirement: R73
Task: Task 162

## Purpose

Define the smallest useful private concept-learning helper flow so the OS can help turn concept exposure into stronger contextual understanding.

## First-slice trigger

Start with a manual operator action.

Initial entry point:
- the Product Director chooses `Clarify concept` from a local-only helper surface
- the flow begins with a concept, term, or phrase that feels fuzzy or only half-understood

Why this trigger first:
- it is simple
- it keeps the first slice private-first
- it makes learning timely rather than detached from work

## Input

Required input:
- concept or unfamiliar term

Optional input:
- where it showed up
- current understanding
- nearby concept it may be confused with

## Clarification flow

The first slice should help move through this ladder:
1. what the concept seems to mean right now
2. what is actually unclear
3. why the concept exists / what problem it solves
4. where it appears in this repo or workflow
5. why a product leader should care

The first implementation can keep this bounded to a short guided flow rather than a long chat.

## Structured output draft

The helper should produce a draft with these fields:
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

## Storage location

The first slice should write the output into the private learning layer.

Preferred target:
- `private/learning/concept-notes.md`

## UX boundaries

The first slice should:
- feel lightweight
- stay grounded in the OS and current work
- avoid becoming a generic study dashboard
- avoid public exposure of private learning notes

The first slice should not:
- attempt to teach every concept exhaustively
- become a general AI tutor
- optimize for note volume over clarity

## Implementation recommendation

Build this as a local-only helper flow first.

Preferred shape:
- a small local-only control-panel helper near the reflection helper, because both belong to the private operating layer

## Done definition for Task 163

Task 163 should be considered complete when:
- a concept can be entered
- the helper asks a short sequence of clarifying questions
- a stronger concept note draft is produced
- the draft is saved into the private learning layer
- the flow remains private-first and local-only


## Validation update

Manual validation of the first implemented slice showed:
- the helper is useful as an in-product concept-note capture flow
- saving structured drafts into the private learning layer works
- the current clarification-only flow does not feel like learning because it asks for inputs without explaining enough in context

## Next-slice direction

The next slice should keep the current private-first concept note output model, but add a bounded teaching/explainer step before the operator is asked to finalize the note.

That means:
- the helper should respond to the concept and current confusion with an explanation
- connect the concept back to implementation and product implications
- stay lightweight and finite
- finish by saving a structured concept note draft rather than leaving the interaction as a loose tutor chat

Implementation detail is captured in:
- `projects/os-control-panel/product/concept-learning-explainer-R73.md`

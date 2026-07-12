# Persistent Learning-Agent Session for R74

## Context

The learning layer now has:

- concept teaching
- concept recommendations
- concept lifecycle management
- concept relationships
- build-to-learn pathways
- build-to-learn pull-through into concept management

These pieces are useful, but they still behave more like coordinated helpers than a true learning agent.

## Workflow shaping

This slice was shaped through the OS workflow before implementation:

- PM aligned on the need for one bounded learning session that can hold a concept across multiple turns instead of scattering the operator across helpers
- Experience Designer identified the core user problem as fragmentation and loss of continuity in concept learning
- UI Designer pushed a calm, narrow, resumable session surface with one active concept, one current learning question, one explanation-back area, and a visible next move
- Architect reinforced the need for an evolutionary state model, clear separation between workflow state and concept state, and avoidance of a broad redesign

The next slice should create a persistent learning-agent session that can:

- stay with one concept over multiple turns
- remember what has already been explained in the current session
- ask the operator to explain the concept back in simple language
- detect shallow understanding
- choose the next best move without forcing the operator to jump between tools

## Purpose

Move the learning layer from:

- helper-driven concept management

to:

- a persistent agent-guided learning conversation

without turning the OS into an open-ended tutor chat.

## Core product idea

The OS should support a bounded learning-agent session for one concept at a time.

The session should:

1. pick up a concept from recommendation, concept manager, or build-to-learn context
2. explain the concept simply in context
3. ask the operator to explain it back plainly
4. inspect the explanation for weak understanding
5. choose the next move:
   - clarify further
   - give a nearby distinction
   - use an OS-specific example
   - suggest or resume build-to-learn
   - update concept state
6. preserve the session state so the operator can continue without restarting the concept from scratch

The operator should also be able to interrupt the default loop with a follow-up clarification move, for example:

- explain this more simply
- clarify this specific confusing part
- give me another example
- compare this to a nearby concept

## Why persistence matters

Right now, the operator can learn, manage, and build around concepts, but the flow is still fragmented.

Persistence matters because the learning agent should remember within the session:

- what concept is active
- what explanation was already given
- what the operator said back
- what gaps or jargon dependence were detected
- whether the next move should be more teaching, a distinction, or build-to-learn

Without that, the OS keeps behaving like a collection of screens rather than one learning partner.

## Feynman-style loop

The session should operate with a simple bounded loop:

1. **Explain simply**
   - the OS gives a concise explanation in plain language

2. **Explain it back**
   - the operator restates the concept in their own words

3. **Inspect the explanation**
   - detect:
     - jargon dependence
     - vague mechanism
     - weak distinction from a nearby concept
     - inability to say why the concept exists or when it matters

4. **Choose the next move**
   - explain differently
   - offer a distinction
   - show an example in current OS work
   - route to build-to-learn
   - capture improved understanding in concept state

5. **Decide whether to continue**
   - stay in session
   - pause and preserve state
   - return to concept manager with updated state

## First-slice scope

The first persistent learning-agent slice should support:

- one active concept-learning session at a time
- session state stored privately and file-backed
- simple learning session memory:
  - concept
  - latest explanation
  - latest explanation-back
  - detected weakness
  - recommended next move
- explicit session actions:
  - continue learning
  - route to build-to-learn
  - save updated understanding
  - pause session
  - exit to concept manager

## Clarification refinement

Manual use showed that the persistent session needed a proper operator-initiated clarification lane instead of forcing all confusion through explanation-back.

That refinement is now part of the session. The operator can request bounded follow-up moves such as:

- explain it more simply
- clarify a specific confusion
- give another example
- compare it to a nearby concept

The important product effect is that clarification now happens **inside** the active session rather than forcing the operator to abandon the thread or encode confusion indirectly.

This keeps the learning flow bounded while making it feel more like a real learning partner than a one-directional quiz.

## UX direction

The experience should feel:

- calm
- narrow
- conversational but bounded
- easy to resume

It should not feel like:

- an open tutor chat
- a second concept manager
- a long scrolling transcript without guidance

The operator should always understand:

- what concept is active
- what the current learning question is
- what the OS thinks is still weak
- what the next step should be

## State model

The session should preserve at least:

- `concept`
- `session_status` (`active`, `paused`, `complete`)
- `latest_teaching_brief`
- `latest_explanation_back`
- `detected_gaps`
- `next_move`
- `linked_concept_status`
- `linked_build_to_learn_status`
- timestamps / recent turn history

## Boundaries

The first slice should:

- remain local-only and private-first
- avoid long transcripts as the main UI
- prefer bounded session state over free-form memory sprawl
- not auto-mark a concept learned
- not attempt a full multi-concept curriculum engine yet

## Success criteria

This slice should be considered successful when:

- the operator can begin a learning session from a recommendation or concept record
- the session survives more than one turn without losing context
- the OS can ask for a simple explanation-back and react to weak understanding
- the operator can ask for a follow-up clarification without dropping out of the session
- the next move feels guided rather than fragmented across separate helpers
- concept state is updated cleanly from the session

## Recommended implementation direction

The first implementation should likely include:

1. private session store
2. one learning-agent session surface in the Learning tab
3. simple Feynman explanation-back check
4. routing into:
   - continued teaching
   - concept-state update
   - build-to-learn
5. bounded operator-initiated clarification moves inside the active session

This should be the first slice where the learning layer starts to feel like a true agent rather than just a coordinated toolkit.

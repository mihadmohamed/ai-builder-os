# Concept Hierarchy Workflow Review — R74

## PM framing

The learning layer has reached the point where concept hierarchy is no longer a secondary enhancement.

It is becoming part of the product's learning logic.

The current problem is not simply that concepts are hard to compare. It is that concepts still feel too flat:
- the learner can open `Evals`, `Trace grading`, `Agent-output quality evals`, or `Replays`
- but the system does not yet consistently tell them:
  - what the broader family is
  - whether one concept should be learned before another
  - whether the current concept is foundational, specialized, or adjacent

### Product decision

Move from:
- a mostly flat concept list with relationship hints

To:
- a concept-family learning model where parent concepts can scaffold child concepts

### Priority outcomes

1. The OS can define explicit concept families for the current learning catalog.
2. Parent concepts can act as learning gateways when that improves understanding.
3. The learning layer can explain why a concept is being surfaced now in family context, not only as an isolated item.

## Experience Designer review

### Current pain

The learner can now get:
- a definition
- a clarification
- a comparison
- a build pathway

But there is still a missing orientation question:
- “Where does this concept sit in the bigger learning map?”

Without that map, the learner can:
- understand a concept in isolation
- but still feel shaky about how it relates to the broader system

That creates cognitive friction because the journey feels reactive instead of scaffolded.

### Experience direction

The hierarchy should help answer:
1. What broader family am I in?
2. Is this concept foundational or specialized?
3. What should I learn first?
4. What is the natural next step after this?

### Experience rules

1. Parent concepts should be used to reduce fragmentation, not to create a heavy taxonomy browser.
2. The OS should guide the learner from broad to narrow when that improves understanding.
3. The learner should still be able to enter through a child concept when current work makes that more relevant, but the broader family should then become visible quickly.

## UI Designer review

### Current UI problem

The hierarchy section now helps, but it still behaves mostly like a supporting visual.

If hierarchy is becoming part of progression logic, the UI must do more than show a tree.

It should help the learner understand:
- where they are
- what level they are at
- what broader concept they should anchor on

### UI direction

Use hierarchy as orientation before turning it into navigation.

Recommended hierarchy inside the learning experience:

1. current concept
2. family / parent placement
3. why this concept is showing up now
4. recommended next move
5. related and often-confused concepts

### UI recommendations

1. The concept family should feel like a learning frame, not just metadata.
2. When a child concept is selected, the parent-level family should be visible without overwhelming the page.
3. The concept page should eventually support language like:
   - `Parent concept`
   - `This concept is a narrower part of...`
   - `Learn this broader concept first`
   - `Natural next child concept`
4. Avoid dropping the learner into a dense expandable tree without guidance.

## Architect review

### Structural concern

The current hierarchy layer is still mostly encoded as displayable labels plus relationships.

If hierarchy is going to guide progression, the system needs a stronger distinction between:
- concept family structure
- adjacency / relatedness
- confusion / similarity
- recommendation logic

Those are not the same thing.

### Architectural direction

The learning model should explicitly support:
1. concept family identity
2. parent concept or parent family
3. child concepts
4. whether a concept is foundational, specialized, or adjacent

This should remain compatible with:
- recommendation logic
- tutoring logic
- concept page rendering
- future concept-map expansion

### Guardrails

1. Do not force a rigid perfect taxonomy immediately.
2. Keep provisional family structures possible.
3. Do not collapse all relationships into hierarchy.
4. Preserve the distinction between:
   - parent/child structure
   - related concepts
   - often-confused concepts
   - next-after sequencing

## Recommended implementation order

### Slice 1
Define initial concept families and parent/child mappings for the current catalog.

### Slice 2
Use hierarchy to improve recommendation logic:
- parent-first when appropriate
- child-first only when current work makes that the better entry point

### Slice 3
Use hierarchy in tutoring and concept surfaces:
- explicit family framing
- broader/narrower explanation
- parent-aware next-step guidance

## Success signal

The learner should feel:
- I know what family this concept belongs to
- I know whether this is the broad idea or a narrower subtype
- I know what should come first and what should come next

Not:
- I’m learning a set of useful but mostly disconnected terms

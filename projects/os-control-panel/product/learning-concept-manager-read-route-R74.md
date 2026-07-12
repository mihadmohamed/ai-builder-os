# Learning Concept Manager Read-and-Route Review — R74

## PM framing

The concept manager should now behave like a concept library with a clear continuation path, not like a secondary learning engine.

The live learning agent is already the main product interaction for:
- teaching
- clarification
- understanding checks
- next-move guidance

That means the concept manager should mostly answer:
- what state is this concept in?
- what do I currently understand?
- what is still open?
- what should I do next?

### Product decision

Move from:
- concept manager as a mixed manager / editor / router surface

To:
- concept manager as a read-and-route surface that supports the live agent

### Product outcomes

1. The concept page is primarily readable, not procedural.
2. The agent remains the obvious next action for concept progression.
3. Build-to-learn stays linked, but contained.
4. Relationships and history stay visible without turning the page into an operations console.

## Experience Designer review

### Current friction

The operator can still feel pulled into “managing the concept” instead of “continuing the learning.”

That happens when the concept page:
- presents too many same-weight sections
- looks like a state-maintenance surface
- asks the operator to infer which action really matters now

### Experience direction

The concept page should feel like:
- a calm concept snapshot
- with one clear continuation move

The operator should be able to scan the page quickly and immediately understand:
- where they are
- what is unresolved
- whether to continue learning or open the linked build

### Experience rules

1. There should be one dominant continuation action.
2. Secondary sections should support understanding, not compete with it.
3. The page should feel lighter for recommendation-only concepts than for active learning concepts.
4. Relationship and history information should stay available but low-noise.

## UI Designer review

### Current UI problem

The concept page still carries too much layout responsibility:
- summary block
- build strip
- primary action
- relationships
- history

Even after recent cleanup, the hierarchy can still feel flatter than it should.

### UI direction

Treat the concept detail as one framed reading pane with a simple visual order:

1. concept identity and state
2. latest agent-backed learning state or recommendation context
3. primary action
4. compact build link
5. relationships
6. lifecycle history

### UI recommendations

1. Keep the top area compact and descriptive, not metric-heavy.
2. Keep the dominant action directly under the core understanding block.
3. Place build linkage after the primary learning action so it reads as a branch, not a competitor.
4. Keep relationships visually grouped within the same concept pane.
5. Keep lifecycle history collapsed by default.

## Architect review

### Structural concern

The recent state-layer split improved the backend model, but the concept page still performs too much composition inline.

That means the UI layer still owns more orchestration than it should.

### Architectural direction

Concept manager should consume a composed concept-detail view model and mostly render it.

The UI should not decide too much about:
- what kind of concept this is
- whether it is recommendation-backed or state-backed
- how progression should happen

That logic should stay in the learning layer composition code, with the concept page mostly reading and routing.

### Guardrails

1. Keep recommendation, concept, session, and build layers distinct.
2. Prefer one composed view model for the detail pane rather than repeated local inference.
3. Let the learning agent own progression logic.
4. Keep file-backed inspectability visible through history and linked state, not through manual editing surfaces.

## Recommended implementation order

### Slice 1
Move the primary continuation action directly under the core concept-state block.

### Slice 2
Demote build linkage below the primary continuation move while preserving the concept <-> build mental link.

### Slice 3
Reduce inline conditional rendering in the concept page by relying more heavily on one composed detail model.

### Slice 4
Keep relationship and history sections supportive and low-emphasis.

## Success signal

The operator should feel:
- this page helps me understand where I am and where to go next

Not:
- this page is another semi-hidden workflow engine

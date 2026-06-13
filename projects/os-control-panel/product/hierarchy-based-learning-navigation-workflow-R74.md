# Hierarchy-Based Learning Navigation — R74

## PM framing

The concept page should no longer behave like a flat status board with concepts filed under `Learned`, `In progress`, and `Upcoming`.

The learner's real navigation question is:

- where does this concept sit in the broader map?
- what parent concept does it belong to?
- what sits under it?

Status still matters, but as state on the map rather than as the map itself.

## Experience Designer guidance

The left-hand navigation should orient before it routes.

The hierarchy should help the learner answer:

1. what family am I in?
2. what is the gateway concept?
3. what are the child concepts?
4. where am I now in that structure?

Status should stay visible, but it should not be the primary grouping model.

## UI Designer guidance

Use the left column as a concept-family index:

- one expander per concept family
- nested concepts shown under the gateway/root concept
- status shown as lightweight metadata beside each concept
- current selection clearly marked

The right pane should remain the stable concept workspace:

1. concept identity and current state
2. hierarchy/context
3. current understanding and open questions
4. continue learning
5. relationships and history

The hierarchy should feel like structure, not decoration.

## Architect guidance

Do not let the concept page infer different hierarchy models in different places.

Use one shared family-tree model for:

- session hierarchy
- concept-page hierarchy
- left-hand learning navigation

Hierarchy, status, and relationships must remain distinct:

- hierarchy = placement
- status = learning state
- relationships = adjacency / confusion / next moves

## Implementation direction

- Replace status-bucket navigation on the concept page with hierarchy-based family navigation
- Keep status as display metadata only
- Consolidate hierarchy rendering behind one shared workspace helper so session and concept surfaces cannot drift
- Keep recommendation and concept-state logic separate from hierarchy structure

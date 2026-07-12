# Learning Agent Centered Workflow Review — R74

## PM framing

The learning layer has outgrown its earlier helper-driven structure.

The product now has a clear center of gravity:
- the persistent learning agent

That should become the primary path for:
- learning a concept
- checking understanding
- deciding the next move
- routing into build-to-learn
- updating concept state

The rest of the learning surfaces should support that path rather than compete with it.

### Product decision

Move from:
- multiple same-weight learning tools

To:
- one agent-centered learning flow with supporting libraries

### Priority outcomes

1. The learning agent is the default entry point for active learning.
2. Concept manager behaves like a library and continuation surface, not a manual editor first.
3. Build-to-learn remains visible and linked, but no longer crowds concept understanding.

## Experience Designer review

### Current pain

The current learning experience still creates a subtle split:
- some actions feel agent-led
- some actions feel like filling in a system of forms

That creates cognitive friction because the operator has to decide:
- “am I learning with the OS?”
- or
- “am I maintaining concept records?”

### Experience direction

The product should make one thing feel obvious:
- continue learning with the agent

Everything else should feel secondary:
- inspect concept state
- open linked build
- edit manually when needed

### Experience rules

1. The active learning move should be more prominent than maintenance controls.
2. The concept page should primarily answer:
   - what do I understand?
   - what is still open?
   - what should I do next?
3. Manual editing should appear only when the operator deliberately wants to override or maintain state.

## UI Designer review

### Current UI problem

The concept detail view still visually mixes:
- concept understanding
- build linkage
- action continuation
- record maintenance

The result is functional but not calm.

### UI direction

The concept page should become a lighter reading-and-action surface.

Recommended hierarchy:

1. concept summary
2. linked build strip
3. primary next action
4. relationships
5. history
6. secondary/manual editing

### UI recommendations

1. Keep `Continue with learning session` as the dominant action.
2. Keep build linkage compact.
3. Move manual concept editing behind a lower-emphasis control such as:
   - `Edit concept`
   - expander
   - secondary section below the main reading flow
4. Remove old helper-era duplication from `Learn next`.

## Architect review

### Structural concern

The current learning layer still reflects an older architecture:
- helper flows own some state
- the agent owns other state
- concept manager exposes raw state editing too prominently

This is not a backend problem first.
It is a product-state ownership problem.

### Architectural direction

The persistent learning agent should become the main owner of:
- active concept progression
- clarification loop
- next-move routing

Concept manager should remain the inspectable system of record, but not the primary interaction engine.

### Guardrails

1. Keep file-backed inspectability intact.
2. Do not remove manual lifecycle editing entirely.
3. Prefer demotion over deletion when retiring older helper-era flows.
4. Keep concept state and build state linked, but avoid duplicating the same action in multiple places.

## Recommended implementation order

### Slice 1
Remove concept helper from the primary `Learn next` experience.

### Slice 2
Demote manual concept editing behind a lower-emphasis control in Concept manager.

### Slice 3
Let the agent propose lifecycle moves more often, with human confirmation instead of heavy manual editing.

## Success signal

The operator should feel:
- I am learning with one coherent agent-centered system

Not:
- I am switching between a learning agent, helper-era tools, and record maintenance surfaces

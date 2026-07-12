# Concept Hierarchy Learning Initiative — R74

Requirement: R74

Status: IN_PROGRESS

## Why this matters

The learning layer has become much stronger at:
- teaching one concept at a time
- clarifying confusion
- showing implementation anchors
- progressing concepts through learning state

But the next structural improvement is not just better answers. It is a better map.

Right now, concepts are still too easy to experience as a flat list:
- `Evals`
- `Trace grading`
- `Agent-output quality evals`
- `Replays`
- `RAG`
- `Memory systems`
- `MCP`

That works for discovery, but it is not yet a strong learning journey.

The better model is:
- identify broader parent-level concept families
- let the learner begin with the parent concept when appropriate
- then move into child concepts and distinctions with clearer scaffolding

Hierarchy is therefore not just a display concern. It is part of:
- recommendation logic
- progression logic
- explanation quality
- concept comparison quality
- overall learning coherence

## Product direction

The learning layer should evolve from:
- a flat concept-and-session system

toward:
- a concept-family learning system

where the OS can help the learner understand:
1. the broader concept family
2. where the current concept sits inside it
3. whether the parent concept should be learned first
4. which child concept should come next

## Core principles

### 1. Parent concepts are learning gateways

When a concept clearly belongs to a broader family, the OS should know:
- the parent concept or concept family
- the sibling and child concepts
- whether the current concept is foundational, specialized, or adjacent

### 2. Hierarchy should shape recommendations

The OS should not recommend concepts as isolated items when a clearer family path exists.

For example:
- `Evals` before `Agent-output quality evals`
- `Evals` before `Trace grading`
- `Context and capability systems` before or alongside `RAG`, `Memory systems`, and `MCP`

### 3. Hierarchy should shape explanations

The tutor should be able to say:
- what family the concept belongs to
- whether it is broader or narrower than a nearby concept
- whether it is foundational, specialized, or sibling-level

### 4. Hierarchy should be visible but not noisy

The UI should expose concept families and concept maps clearly, but should not turn every page into a dense taxonomy browser.

### 5. The hierarchy can evolve

The current concept set does not need a perfect final curriculum map immediately.

The OS should support:
- early family definitions
- refinement over time
- cases where a concept family is still provisional

## Initial concept-family direction

The current catalog already suggests early families such as:

### Evals
- Agent-output quality evals
- Trace grading
- Replays
- and future eval subtypes such as:
  - Tool Selection Evals
  - Workflow Evals
  - Memory Evals
  - Safety Evals
  - Cost Evals
  - Latency Evals
  - Reliability Evals

### Context and capability systems
- RAG
- Memory systems
- MCP

These should be treated as early concept families, not one-off UI decorations.

### Current implementation baseline

The learning layer now has an explicit first family model for the current catalog:

- `Evals`
  - gateway concept: `Evals`
  - specialized / child concepts:
    - `Agent-output quality evals`
    - `Trace grading`
    - `Replays`

- `Context and capability systems`
  - current gateway concept: `Memory systems`
  - specialized / child concepts:
    - `RAG`
    - `MCP`

This should be treated as a first structured baseline, not a final curriculum map.

## What this initiative should deliver

1. Explicit concept-family structures in the learning model
2. Parent-aware recommendations
3. Parent-before-child progression rules where appropriate
4. Hierarchy-aware tutoring and comparison responses
5. Family-aware concept pages and learning-session views
6. Validation coverage for hierarchy-sensitive learning behavior

## What this initiative should not do yet

- It should not force every concept into a rigid final taxonomy prematurely.
- It should not replace all recommendation logic with hierarchy alone.
- It should not add a heavy curriculum-management UI before the family model is trustworthy.

## Definition of better

This initiative is successful when:
- concepts feel placed, not isolated
- parent concepts meaningfully scaffold child concepts
- the learner can see the broader map without getting lost in it
- hierarchy improves explanation quality, comparison quality, and next-learning guidance
- the learning journey feels more cumulative and less flat

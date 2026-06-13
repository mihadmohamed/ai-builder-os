# Learning State Layering — R74

## Context

The learning layer has grown into a real subsystem:

- recommendations
- persistent learning-agent sessions
- concept records
- build-to-learn pathways
- concept relationships

That progress is real, but the internal model still blends several different meanings into one derived concept view.

This shows up in the UI as a recurring coherence problem:
- recommendation text can look like captured learning
- session state can feel mixed with durable concept state
- build state can appear to overwrite conceptual meaning

The next step is not another surface-level polish pass.
It is to clarify the state model the UI is built on.

## Workflow shaping

This slice was shaped through the OS workflow before implementation:

- **PM**: the product problem is not missing functionality, but ambiguity about what kind of learning state the operator is looking at
- **Experience Designer**: the user should not have to guess whether a screen is showing a recommendation, a learned concept, or the current live-agent thread
- **UI Designer**: the page should read truthfully and calmly, with different state types expressed clearly rather than blended into one card model
- **Architect**: recommendation state, concept state, session state, and build state should remain distinct layers even if the UI composes them

## Product problem

Right now one derived concept record is doing too much.

It is standing in for:
- recommendation framing
- durable concept understanding
- open questions
- live-agent continuity
- build-to-learn linkage

That makes the system look richer at first glance, but weaker on inspection because the operator cannot always tell:
- what was actually learned
- what is only suggested
- what is still active in the session
- what was learned by building

## Desired model

The learning layer should be explicit about four different state layers:

### 1. Recommendation state

What the OS thinks the operator should learn next.

This includes:
- why learn this now
- current gap
- suggested first move

This is guidance, not learned understanding.

### 2. Concept state

Durable understanding that has been captured into the concept system.

This includes:
- current understanding
- open questions
- concept lifecycle status
- concept relationships

This is the persistent learning record.

### 3. Session state

The live learning-agent thread for one active concept.

This includes:
- latest explanation from the OS
- latest explanation-back from the operator
- detected gaps
- clarification responses
- current coach message
- next move inside the active session

This is active, ephemeral-but-persisted learning flow.

### 4. Build-to-learn state

The execution-backed learning path for a concept.

This includes:
- build learning goal
- experiment slice
- success signal
- captured outcome
- unresolved uncertainty after building

This is the concept’s learning-by-building lane, not the concept understanding itself.

## UX implications

The UI should be able to compose these layers, but not blur them.

That means:

- an upcoming concept should show recommendation framing, not fake learned understanding
- a concept with durable state should show captured understanding and open questions
- an active session should be visibly session-owned
- a linked build should be visibly build-owned

The operator should be able to tell, at a glance:
- what is guidance
- what is state
- what is active
- what is execution-backed

## Implementation direction

The first implementation pass should:

1. stop using one overloaded concept record as the sole semantic layer
2. make recommendation-only concepts render as recommendation state
3. make concept pages explicitly prefer:
   - session state when session is active
   - concept state when durable understanding exists
   - recommendation state only when no real learning state exists
4. keep build-to-learn state visibly linked but distinct

## Boundaries

- Do not do a large rewrite of the learning layer
- Keep state file-backed and inspectable
- Preserve current user-facing capability while clarifying semantics
- Keep the live learning agent as the center of gravity

## Success criteria

This slice is successful when:

- recommendation-only concepts no longer read like answered concepts
- the concept page is honest about what kind of state it is showing
- live session continuity feels distinct from durable concept state
- build-to-learn stays linked without pretending to be the same thing as concept understanding
- the code model becomes easier to reason about than the current overloaded derived record

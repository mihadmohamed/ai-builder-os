# Build-to-Learn Evolution for R74

## Context

The current build-to-learn flow is now functionally connected to concept management, but it still feels incomplete as a learning experience.

It works as:

- a way to turn a concept into a bounded experiment
- a way to link that experiment back to a concept record
- a way to capture what building taught and what remains unclear

That is a real step forward.

But it is not yet a full learning-by-building system.

## What build-to-learn is now

Today, build-to-learn is mostly:

1. choose a concept
2. create a bounded pathway
3. save the pathway
4. later capture what the build taught
5. update the concept state

This makes build-to-learn a useful:

- experiment planner
- outcome capture tool

It does **not yet** make it a true execution-backed learning loop.

## Why it still feels incomplete

The current flow is missing the strongest part of learning-by-building:

- the middle

Right now, the OS helps:

- before the build
- after the build

But it does not help enough:

- during the build
- in choosing the right build
- in translating the build into real understanding

## Current gaps

### 1. Weak transition from concept to execution

The OS can plan a build-to-learn pathway, but it does not yet reliably turn that pathway into:

- a real requirement
- a task
- a scoped build lane
- a tracked implementation slice

So the learning plan still stops too early.

### 2. No guided learning during the build

The OS does not yet check:

- what the operator expects to learn from this step
- what outcome would confirm the current mental model
- what outcome would challenge it
- what tradeoff became real through building

That means much of the learning still depends on the operator doing the translation manually.

### 3. No Feynman loop inside build-to-learn

The learning agent should eventually ask:

- explain this simply before building
- explain it again after building
- what changed
- what part was previously only jargon or borrowed phrasing

That is missing today.

### 4. Concepts are still too flat

Some concepts are too large for one experiment.

For example, `RAG` may need separate understanding around:

- retrieval itself
- grounding
- chunking
- relevance
- when retrieval is unnecessary

The current build-to-learn model is not yet granular enough to express that.

### 5. Progress states are still too coarse

The system should be able to distinguish between:

- planned
- active
- built but not yet consolidated
- consolidated into concept understanding

The current model only begins to show this.

### 6. Weak compounding behavior

After a build-to-learn experiment, the OS should be better at saying:

- what concept comes next
- what adjacent concept is now more relevant
- what unresolved edge should be revisited

That compounding behavior is still light.

## What build-to-learn should become

Build-to-learn should evolve from:

- a learning experiment note

into:

- an execution-backed learning loop

That means the OS should help with:

1. deciding whether a concept should be learned by explanation, by building, or both
2. shaping the right build for the learning goal
3. routing that build into actual execution
4. checking understanding during the build
5. consolidating the learning afterward
6. updating concept relationships and next-learning guidance

## Better target workflow

### Phase 1: Choose the learning mode

For a given concept, the OS should decide between:

- teach first
- build first
- teach then build
- build then reflect

Not every concept should default to the same path.

### Phase 2: Turn the concept into a real learning plan

The OS should define:

- what part of the concept this build is testing
- what misunderstanding the build is meant to challenge
- what success would mean for understanding, not just for code output

### Phase 3: Route it into execution

The build-to-learn plan should be able to become:

- a requirement
- a task
- a bounded implementation slice

so the OS can treat the learning build as real work, not just an intention.

### Phase 4: Guide understanding during the build

The learning agent should ask:

- what do you think is happening now
- what surprised you
- what tradeoff became concrete
- explain this simply again

This is where much of the real learning happens.

### Phase 5: Consolidate the concept after the build

After execution, the OS should help capture:

- the updated plain-language explanation
- what the build proved
- what it did not prove
- what still feels shaky
- which concept should come next

### Phase 6: Feed the broader learning system

The outcome should update:

- concept state
- concept relationships
- recommendation logic
- whether the concept is learned, in progress, or reopened

## Product direction

The next phase should treat build-to-learn as a first-class sub-workflow of the learning agent.

The learning agent should:

- decide when building is the right learning move
- shape the build
- route it into real work
- check understanding during the build
- pull the learning back into the concept system

## Suggested next slices

### Slice A — Build-to-learn execution routing

Allow a build-to-learn pathway to become a real requirement/task or bounded implementation lane.

### Slice B — Feynman checks around the build

Add:

- explain before building
- explain after building
- compare the two explanations

### Slice C — Build-state progression

Track:

- planned
- active
- built
- consolidated

### Slice D — Build-to-learn concept decomposition

Allow one concept to be learned through multiple narrower experiments rather than one flat build.

### Slice E — Post-build recommendation compounding

Use build outcomes to recommend:

- what to learn next
- what relationship got clearer
- what unresolved edge should be revisited

## Summary

The current build-to-learn system is now a credible first cut.

It is good at:

- planning a learning experiment
- linking the experiment back to a concept
- capturing what building changed

It is still weak at:

- carrying the operator through execution as part of learning
- using the build itself as a guided teaching loop

That is the next level.

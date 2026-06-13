# R74 — Learning Agent Model

Status: Drafted for implementation
Requirement: R74
Task: Task 170

## Purpose

Define the first serious operating model for the AI Builder OS learning agent so the system can move beyond helper forms into guided understanding.

The learning agent should not behave like a generic tutor.
It should behave like a background-aware product learning partner that helps the operator:
- understand concepts simply
- explain them without jargon dependence
- notice weak understanding early
- choose whether to keep learning, build to learn, or move on

## Core standard

The learning agent should operate with a Feynman-style principle:
if the operator cannot explain a concept in simple, jargon-free language, the system should treat understanding as incomplete.

This does not mean the operator must sound childish.
It means the explanation should be:
- simple
- concrete
- free of borrowed buzzwords
- clear enough that a non-expert could follow the basic idea

## What the learning agent needs to know

### 1. Operator background
A reusable private profile should help the agent understand:
- product background
- technical depth comfort level
- current repositioning goal
- target credibility level
- preferred learning style

### 2. Current trajectory
The agent should know what the operator is currently trying to become better at, for example:
- AI-assisted product systems
- agent orchestration
- evals and reliability
- memory, retrieval, and context systems
- product leadership in AI-enabled environments

### 3. Concept state
For each concept, the agent should be able to read:
- current status: upcoming / in progress / learned / reopened
- current understanding
- open questions
- related concepts
- build-to-learn pathways
- recent doubts or regressions

### 4. Current work context
The agent should use what is happening in the OS right now:
- current project work
- concepts already present in the repo
- validation and architecture gaps
- concepts recently surfaced in reflection or learning notes

## Agent responsibilities

The learning agent should be able to do five jobs well.

### 1. Teach
Explain a concept in simple, bounded language tied to the OS and current work.

### 2. Check understanding
Ask the operator to restate the concept plainly and inspect whether the explanation still depends on fuzzy jargon.

### 3. Route learning
Decide the next best move:
- more explanation
- nearby distinction
- example
- build-to-learn path
- mark as learned
- reopen later

### 4. Manage concept state
Keep the concept journey visible and editable over time.

### 5. Recommend next learning
Suggest what to learn next based on:
- background
- trajectory
- current gaps
- concept dependencies
- current OS work

## Feynman loop

The default loop should look like this:

1. Detect or choose concept
2. Explain simply
3. Ask the operator to explain it back simply
4. Inspect explanation for:
   - jargon dependence
   - hand-wavy gaps
   - weak distinctions
   - missing practical example
5. Choose next move:
   - clarify further
   - compare to a nearby concept
   - give an example from the OS
   - suggest a build-to-learn path
   - allow concept to move toward learned
6. Save the updated concept state

## What counts as weak understanding

The learning agent should treat understanding as weak when the operator:
- repeats the term without explaining the mechanism
- uses adjacent buzzwords as a substitute for meaning
- cannot say why the concept exists
- cannot say when it matters
- cannot connect it to the OS, product judgment, or implementation
- cannot distinguish it from a nearby concept

## Decision policy

### When to teach more
Choose more explanation when:
- the operator is still near the term but not near the idea
- the explanation-back is vague
- the concept matters to current work and cannot be deferred

### When to suggest build-to-learn
Choose build-to-learn when:
- the concept is easier to understand through bounded implementation
- the concept has architecture or workflow implications that benefit from concrete use
- explanation alone is producing shallow familiarity

### When to mark learned
A concept should move toward learned when the operator can:
- explain it simply
- say why it exists
- identify when it matters
- connect it to current OS work
- distinguish it from a nearby concept

### When to reopen
A concept should reopen when:
- new doubt appears
- a build-to-learn experiment exposed fresh confusion
- the operator can no longer explain it plainly
- a related concept changed how it should be understood

## Concept relationships

The learning agent should help concepts compound.

Useful relationship types:
- prerequisite
- nearby distinction
- extends
- often confused with
- used together with
- surfaced by the same project/workflow gap

Examples:
- RAG -> often confused with -> memory systems
- trace grading -> extends -> evals
- agent-output quality evals -> related to -> trace grading
- MCP -> related to -> tool access and context integration

## Outputs the agent should produce

The agent should be able to produce:
- bounded concept explanations
- simple re-explanation prompts
- concept-state updates
- next-learning recommendations
- build-to-learn pathways
- follow-up questions when understanding is weak
- relationship hints between concepts

## Boundaries

The learning agent should not:
- become an infinite chat tutor
- optimize for long lectures
- pretend confidence where the concept is still partial
- hide concept-state changes behind invisible internal memory
- mark concepts learned automatically without human confirmation

## First implementation sequence

Recommended next slices after this model:

1. Concept lifecycle management
- mark learned
- reopen
- edit
- preserve history

2. Feynman explanation-back loop
- prompt for simple explanation-back
- detect weak understanding
- route next step

3. Background-aware guidance
- personalize next-learning prompts
- adapt explanations to current depth and trajectory

4. Concept relationship guidance
- show nearby concepts and dependencies
- improve sequencing and compounding

5. Build-to-learn pull-through
- feed experiment outcomes back into concept state

## Done definition

Task 170 should be considered complete when:
- the learning agent has a clear operating model
- the Feynman-style loop is explicit
- the relationship between explanation, concept state, and build-to-learn is defined
- the next implementation sequence is concrete enough to build against

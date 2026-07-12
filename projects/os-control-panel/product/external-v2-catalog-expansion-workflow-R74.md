# External V2 Catalog Expansion Workflow — R74

## PM framing

The external V2 release should feel like:
- a coherent concept-learning product
- a real map of AI agent systems
- a catalog grounded in what AI Builder OS actually implements

The next catalog-expansion pass should therefore prioritize:
1. concepts that strengthen the family map
2. concepts that already have real OS evidence
3. concepts that help the learner move from broad system ideas into concrete implementation understanding

This is not a “make the list longer” exercise.

It is a “make the catalog more representative and more teachable” exercise.

### Product decision

Implement the strongest missing concepts now:
- workflow-system child concepts
- context/retrieval concepts that already have honest local-first anchors

Do not add concepts that still feel mostly aspirational or weakly grounded in the repo just to complete a taxonomy.

## Experience Designer review

### Current learner gap

The learner can now see the family structure, but the map still feels thin in places:
- the workflow family jumps too quickly from gateways to eval concepts
- the context family lacks a middle layer between memory and RAG
- the capability family is usable, but should not be padded with concepts the OS cannot yet demonstrate well

### Experience direction

The next concept additions should make the learning journey feel more scaffolded:
- `Workflows` should open into the mechanics that make workflows real
- `Memory systems` should open into retrieval before it reaches `RAG`
- capability access should stay grounded in real tool use rather than becoming protocol trivia

## UI Designer review

### UI implication

Catalog expansion should improve:
- orientation
- hierarchy meaning
- implementation walkthrough usefulness

It should not create:
- long flat lists
- weak placeholder concept pages
- hierarchy branches with no strong explanation or OS anchor

### UI rule

Only concept additions that can support:
- hierarchy placement
- plain-language teaching
- implementation walkthroughs

should appear in the external V2 learning surface.

## Architect review

### Structural decision

Add the following concept groups now:

### Agent workflow systems
- `Orchestration`
- `Handoffs`
- `Results and state`
- `Traces / observability`
- `Human hand-back`

### Context and knowledge systems
- `Retrieval`
- `File search`

### Why these are acceptable now

They already have credible implementation grounding in the OS through:
- orchestrator logic
- handoff state
- durable state stores
- runtime traces and operations views
- bounded hand-back behavior
- read-only local context tools
- RAG-related concept grounding

### What to defer

Do not add `Connectors` yet as a first-class external V2 concept unless stronger repo-local implementation grounding is added.

Reason:
- the broader environment is connector-rich
- but the project-local teaching and implementation anchors are still weaker than the concepts above

## Recommended implementation order

1. Finish the workflow-system child concepts
2. Add the retrieval/file-search bridge under the context family
3. Update implementation anchors and hierarchy tests
4. Re-baseline the external V2 catalog artifact

## Success signal

The external V2 catalog should feel like:
- a real concept map of AI Builder OS
- broad enough to be impressive
- honest enough that every concept can still be taught through real OS evidence

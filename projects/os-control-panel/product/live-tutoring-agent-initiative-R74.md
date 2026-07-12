# Live Tutoring Agent Initiative — R74

## Why this is now the next most important phase

The learning layer has now crossed the threshold where UI coherence alone is no longer the main challenge.

The real next leap is to replace the remaining deterministic helper-style learning core with a true model-driven tutoring agent that:
- teaches concepts in context
- asks and answers follow-up clarification questions dynamically
- checks understanding using a Feynman-style loop
- manages concept progression across:
  - upcoming
  - in progress
  - build-to-learn
  - learned
  - reopened

This is now the most important sub-initiative inside `R74`.

## Initiative objective

Build a true model-generated tutoring agent as the center of the learning layer, while preserving file-backed concept state, inspectable workflow transitions, and bounded build-to-learn routing.

## Build-ready architecture

### Core operating model

The tutoring system should be one **Learning Agent** that runs as the primary reasoning layer behind the current learning session UI.

It should not be a loose chat assistant. It should be a bounded concept-learning engine with explicit state and workflow responsibilities.

### Agent inputs

For each tutoring turn, the agent should receive:
- selected concept
- learning profile
- current concept state
- active learning session state
- linked build-to-learn state
- related concepts / distinctions
- implementation anchors when relevant
- the operator's exact latest input
- the current tutoring intent, such as:
  - teach
  - clarify
  - judge understanding
  - recommend next move
  - explain implementation

### Agent outputs

The agent should return structured tutoring outputs rather than raw unbounded prose.

Expected output fields:
- `teaching_response`
- `clarification_response`
- `understanding_assessment`
- `detected_gaps`
- `recommended_next_move`
- `proposed_concept_status`
- `build_to_learn_recommendation`
- `implementation_walkthrough`
- `hand_back_reason` when needed

The UI can still render these conversationally, but the underlying response shape should stay inspectable.

### Tool surface

The tutoring agent should operate through explicit tools over file-backed state.

#### Read tools
- read learning profile
- read concept state
- read active learning session
- read build-to-learn pathway
- read concept relationships
- read implementation anchors for a concept
- read concept history

#### Write/update tools
- update learning session
- update concept state
- record proposed progression
- create or update build-to-learn pathway
- capture learning outcome from build

### Session model

The session remains the live conversational surface.

It should hold:
- concept
- current teaching context
- current learner understanding
- open uncertainty
- latest explanation-back
- latest clarification thread
- current recommended next move
- session turn history summary

The session should be the live layer, while concept state remains the durable layer.

### Durable concept model

The concept record should remain the system of record for concept progression.

It should store:
- status:
  - upcoming
  - in_progress
  - build_to_learn
  - learned
  - reopened
- current understanding
- open questions
- recommended next move
- linked build status
- history

The tutoring agent should propose progression changes, but those changes should still land as file-backed product truth.

### Teaching loop

The standard tutoring loop should be:

1. explain the concept simply
2. invite explanation-back
3. assess the explanation
4. choose one next move:
   - simplify further
   - clarify a specific confusion
   - compare a nearby concept
   - give another example
   - route to build-to-learn
   - propose concept-state advancement
5. persist updated live session state

### Clarification model

Clarification should be truly model-generated and specific to:
- the user's exact confusion
- the concept
- the current learning profile
- prior session turns
- related concepts

It should no longer be button-driven template logic with minor variation.

### Progression model

The agent should own the recommendation for concept progression:
- stay upcoming
- move to in progress
- route into build-to-learn
- mark learned
- reopen

The user should still be able to confirm or override, but the normal path should come from the agent.

### Build-to-learn integration

Build-to-learn should become one of the agent's possible moves, not a parallel planning tool.

The tutoring agent should decide to route to build-to-learn when:
- the learner has the vocabulary but not the felt understanding
- a concept is best learned through pressure-testing
- explanation quality is strong enough that implementation is now the right next move

### Implementation walkthrough integration

The tutoring agent should also be able to switch into:
- “show me how this concept is implemented here”

That path should:
- retrieve a bounded set of implementation anchors
- explain what each anchor does
- explain how the anchors relate
- tie the explanation back to the concept being learned

### Hand-back behavior

The tutoring agent should pause and hand back when:
- the concept is too broad
- the question is underspecified
- the concept boundary is unclear
- implementation explanation would require hallucinating missing structure
- the build suggestion would be too large or noisy

### Guardrail model

Guardrails should keep the tutoring agent:
- anchored to the selected concept
- grounded in real OS state
- resistant to false certainty
- conservative about marking concepts learned
- bounded rather than chatty

### Evaluation model

The tutoring agent should be evaluated on:
- explanation usefulness
- clarification specificity
- understanding-check quality
- progression recommendation quality
- build-to-learn routing quality
- implementation walkthrough usefulness

### Immediate architectural cut line

This task should end with:
- a clear tutoring-agent architecture
- a clear tool contract
- a clear structured output model
- a clear progression model

The next implementation task should then be:
- replace the remaining deterministic teaching and clarification core with this model-driven agent behavior

## The 7 appropriate agent-building practices to include

### 1. Single-agent first

The first strong version should be one Learning Agent, not a swarm of specialized sub-agents.

Why:
- keeps the learning experience coherent
- reduces fragmentation and routing noise
- is the right complexity level for the current stage

Expected first-slice responsibilities:
- teach
- clarify
- ask for explanation-back
- judge understanding quality
- route to build-to-learn
- update concept progression recommendations

### 2. Model + tools + instructions

The tutoring agent should be designed explicitly around:
- **Model**: the reasoning and tutoring engine
- **Tools**: file-backed concept/session/build/profile/implementation access
- **Instructions**: learning behavior, Feynman loop, concept-state rules, and scope boundaries

This is the architectural backbone of the live tutoring system.

### 3. High-quality instructions

The agent needs explicit tutoring instructions such as:
- explain simply
- avoid performative jargon
- ask for explanation-back in plain language
- detect shallow understanding
- choose the next best move:
  - explain more simply
  - clarify a confusion
  - compare nearby concepts
  - give another example
  - route into build-to-learn
- stay grounded in the current concept and current OS context

### 4. Deliberate tool use

The tutoring agent should use tools to read and update:
- learning profile
- concept state
- active learning session state
- build-to-learn pathways
- related concepts
- implementation anchors in the OS

The goal is not open-ended chat memory. The goal is grounded, inspectable learning workflow.

### 5. Guardrails

The tutoring agent should have guardrails for:
- staying on the selected concept
- not marking concepts learned too easily
- not inventing implementation details
- not routing into build-to-learn without a bounded purpose
- not drifting into generic AI tutoring detached from the OS

### 6. Human intervention / hand-back

The agent should explicitly hand back control when:
- the concept is too broad or underspecified
- the user wants to redirect the goal
- the agent is uncertain
- the proposed build-to-learn step would create too much complexity for the current understanding

### 7. Evals first and throughout

The tutoring agent should ship with explicit evaluation for:
- explanation quality
- clarification quality
- Feynman-style understanding checks
- concept progression decisions
- build-to-learn routing decisions
- recommendation quality

The tutoring system should not become “live” without a validation layer that checks whether the tutoring is actually good.

## Concept workflow this initiative should support

The learning workflow should become:

1. concept appears or is recommended
2. learning agent teaches in context
3. operator asks clarification questions naturally
4. agent checks understanding through explanation-back
5. agent decides:
   - keep teaching
   - compare / explain differently
   - route to build-to-learn
   - mark as in progress
   - recommend learned
   - reopen later if doubt returns
6. concept state is updated as durable learning workflow truth

## Relationship to existing tasks

This initiative should absorb and strengthen the existing unfinished learning frontier, especially:
- `Task 176` — compounding guidance across concepts
- `Task 177` — show concepts implemented in the OS

Those should now be treated as parts of the live tutoring-agent initiative rather than unrelated add-ons.

## Repo audit of deferred concepts from the agent-building guide

### 1. Decentralized handoffs

Current OS evidence:
- yes, this exists in the broader OS workflow through explicit handoff state for Experience Designer findings and related routing artifacts
- examples exist in:
  - `projects/os-control-panel/src/workspace.py`
  - `tools/orchestrator_status.py`
  - `agent/roles/orchestrator.md`

Assessment:
- beneficial for broader workflow orchestration
- **not appropriate as the next move for the tutoring agent**

Why:
- learning should feel continuous, not like it is being bounced between specialist roles
- decentralized handoffs would likely reintroduce fragmentation before the single Learning Agent is truly strong

### 2. Computer use

Current OS evidence:
- no meaningful computer-use implementation found in the repo

Assessment:
- **not appropriate right now**

Why:
- the tutoring agent already has direct access to structured local files and code
- teaching concepts does not require a model to click around interfaces
- this would add complexity without improving the core learning experience

### 3. Heavy multi-agent orchestration

Current OS evidence:
- partial broader multi-agent workspace foundations do exist
- examples:
  - `R25 — Phase 1 multi-agent workspace foundation`
  - shared agent workspace assumptions in product requirements/tasks and memory

Assessment:
- beneficial for the broader OS platform
- **not appropriate as the next tutoring-agent architecture**

Why:
- the tutoring experience should first become coherent with one strong agent
- heavy multi-agent learning orchestration would likely multiply confusion before it adds real value

### 4. Complex declarative graph-first workflow design

Current OS evidence:
- no strong sign of a declarative graph-first runtime or orchestration layer in the repo

Assessment:
- **not appropriate right now**

Why:
- the tutoring workflow is still evolving quickly
- a graph-heavy execution design would lock us into structure too early
- code-first, file-backed, inspectable workflow remains the better fit for the current phase

## Potential end-of-initiative consideration

### Manager pattern / agents as tools

This should be considered **at the end of the initiative**, not at the start.

Possible later use:
- the Learning Agent could call specialist agents or sub-tools for:
  - implementation walkthrough generation
  - build-to-learn planning
  - concept graph reasoning
  - eval review of tutoring quality

But that should only happen after the single-agent tutoring experience is already strong, trustworthy, and validated.

## Recommended next implementation sequence

1. define the live tutoring agent instructions
2. define the live tutoring agent tools
3. replace deterministic teaching and clarification with model-generated responses
4. add guardrails and explicit hand-back behavior
5. make concept progression agent-owned
6. integrate implementation walkthroughs and build-to-learn routing into the agent
7. add evaluation coverage for tutoring quality and progression
8. only then reconsider manager-pattern decomposition

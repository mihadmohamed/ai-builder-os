## External V2 Concept Catalog

### Purpose
Define the curated concept catalog for the external V2 learning release, identify which concept families are already strong, and name the missing concepts that should be implemented in the OS before release.

### Release principle
The external V2 catalog should be:
- finite
- intentional
- hierarchy-aware
- implementation-grounded

The external release should expose concepts that:
- matter to the AI Builder OS story
- can be taught in plain language
- can be shown in the OS through real implementation anchors

### Research-informed family structure
After reviewing primary sources from OpenAI, Anthropic, MCP documentation, and the current repo, the learning catalog should not stay limited to only:
- evals
- context and capability systems

The broader concept map for external V2 should be organized into four families.

## Family 1 — Agent workflow systems

Why this family belongs in V2:
- it is central to what AI Builder OS actually is
- OpenAI agent documentation treats workflow, orchestration, guardrails, results/state, and evaluation as distinct layers
- the OS already implements many of these concepts in real workflow surfaces

Gateway concepts:
- `Agents`
- `Workflows`

Likely child concepts:
- `Orchestration`
- `Handoffs`
- `Results and state`
- `Traces / observability`
- `Human hand-back`

Current status:
- concept family is now implemented as an explicit learning family
- implementation evidence exists in the OS and is surfaced through the learning layer
- this family is now part of the external V2 concept plan

## Family 2 — Evals and reliability

Why this family belongs in V2:
- it is already the strongest family in the current learning layer
- the repo has strong implementation evidence
- it supports the OS’s trust-and-quality story clearly

Gateway concept:
- `Evals`

Release-ready child concepts:
- `Agent-output quality evals`
- `Tool Selection Evals`
- `Workflow Evals`
- `Trace grading`
- `Memory Evals`
- `Safety Evals`
- `Cost Evals`
- `Latency Evals`
- `Reliability Evals`
- `Replays` as a supporting technique rather than a pure sibling eval category

Important hierarchy refinement:
- `Trace grading` should likely sit under `Workflow Evals`
- `Replays` should be treated as a validation/supporting technique, not as a full peer category to all eval subtypes

## Family 3 — Context and knowledge systems

Why this family belongs in V2:
- it supports the OS story around persistence, retrieval, and grounding
- it gives the learner a cleaner mental model than today’s broader mixed family

Gateway concept:
- `Memory systems`

Likely child concepts:
- `Retrieval`
- `File search`
- `RAG`

Current status:
- `Memory systems`, `Retrieval`, `File search`, and `RAG` are all now present as first-class learning concepts
- this family now has explicit hierarchy and implementation grounding in the learning layer

## Family 4 — Tool and capability access

Why this family belongs in V2:
- OpenAI and Anthropic docs both treat tool use and capability access as a major conceptual layer
- this is different from memory/retrieval
- the OS already lives in a tool- and connector-rich environment

Gateway concepts:
- `Tool use`
- `Function calling`

Likely child concepts:
- `MCP`
- `Connectors`
- `Tool selection`

Current status:
- `MCP`, `Tool use`, `Function calling`, `Connectors`, and `Tool selection` are now all present as first-class learning concepts
- this family is now explicit in the learning catalog

## Current external V2 release-ready concepts

These are already reasonably well implemented in the learning layer:
- `Agents`
- `Workflows`
- `Orchestration`
- `Handoffs`
- `Results and state`
- `Traces / observability`
- `Human hand-back`
- `Evals`
- `Agent-output quality evals`
- `Tool Selection Evals`
- `Workflow Evals`
- `Trace grading`
- `Memory Evals`
- `Safety Evals`
- `Cost Evals`
- `Latency Evals`
- `Reliability Evals`
- `Replays`
- `Memory systems`
- `Retrieval`
- `File search`
- `RAG`
- `Tool use`
- `Connectors`
- `Tool selection`
- `Function calling`
- `MCP`

They already have:
- concept knowledge entries
- tutoring support
- hierarchy placement
- at least some implementation-grounding in the OS

### Implementation evidence for the completed evals family
These eval-family concepts are now already supported by the OS:

- `Tool Selection Evals`
  - `projects/os-control-panel/src/eval_framework.py`
  - tool-selection coverage already named in `EVAL_COVERAGE`

- `Workflow Evals`
  - `projects/os-control-panel/evals/scenarios.json`
  - workflow-routing and orchestration validation already present

- `Memory Evals`
  - `projects/os-control-panel/src/eval_framework.py`
  - durable memory and concept-state surfaces already in the OS

- `Safety Evals`
  - bounded live-agent guardrails
  - explicit hand-back behavior

- `Cost Evals`
  - token and cost measurement in `projects/os-control-panel/src/agent_runtime.py`

- `Latency Evals`
  - measured duration in `projects/os-control-panel/src/agent_runtime.py`

- `Reliability Evals`
  - completion / trace integrity / regression framing in `projects/os-control-panel/src/eval_framework.py`

## Remaining external V2 expansion opportunities

The current catalog is now broad enough to support the external V2 learning release.
Further additions should be made selectively, only where they strengthen the teaching
story and have real OS implementation grounding.

Potential next additions:

1. stronger connector subtypes once the external capability story broadens further

## Recommended external V2 catalog shape

### Track A — Agent workflow systems
- `Agents`
- `Workflows`
- `Orchestration`
- `Handoffs`
- `Results and state`
- `Traces / observability`
- `Human hand-back`

### Track B — Evals and reliability
- `Evals`
- `Agent-output quality evals`
- `Workflow Evals`
  - `Trace grading`
- `Tool Selection Evals`
- `Memory Evals`
- `Safety Evals`
- `Cost Evals`
- `Latency Evals`
- `Reliability Evals`
- `Replays` as a supporting technique

### Track C — Context and knowledge systems
- `Memory systems`
- `Retrieval`
- `File search`
- `RAG`

### Track D — Tool and capability access
- `Tool use`
- `Function calling`
- `MCP`
- `Connectors`

## Gap assessment

### Already implemented enough for external release
- `Evals`
- `Agent-output quality evals`
- `Trace grading`
- `Replays`
- `Memory systems`
- `RAG`
- `MCP`

### Previously missing, now implemented
- `Tool Selection Evals`
- `Workflow Evals`
- `Memory Evals`
- `Safety Evals`
- `Cost Evals`
- `Latency Evals`
- `Reliability Evals`
- `Agents`
- `Workflows`
- `Tool use`
- `Function calling`
- `Retrieval`
- `File search`
- `Connectors`

## Definition of “implemented enough”
A concept is ready for the external V2 catalog when it has:
1. a proper `LearningConceptKnowledge` entry
2. family and hierarchy placement
3. meaningful relationships to parent, child, or sibling concepts
4. implementation anchors in the OS
5. tutoring support that does not fall back to generic placeholder explanation

## Recommended implementation order

### Completed foundation
1. `Tool Selection Evals`
2. `Workflow Evals`
3. `Memory Evals`
4. `Safety Evals`
5. `Cost Evals`
6. `Latency Evals`
7. `Reliability Evals`
8. `Agents`
9. `Workflows`
10. `Tool use`
11. `Function calling`
12. `Retrieval`
13. `File search`
14. `Connectors`

### Next expansion only if it stays implementation-grounded
15. stronger connector subtypes

## V3 candidates not included in external V2

These came up in the research, but should **not** be part of the external V2 release catalog unless the product direction changes:
- `Computer use`
- `Voice agents`
- `Background mode`
- `WebSocket mode`
- `Prompt caching`
- `Deep research`
- `Vector stores`
- `Embeddings`
- `Agent Builder`
- `ChatKit`

Why they are deferred:
- some are platform/product-specific rather than core conceptual learning needs
- some are not yet meaningfully implemented in the OS
- some would expand the release faster than implementation-grounded tutoring can support

These should remain explicit **V3 candidates**, not forgotten concepts.

## What not to do
- Do not expose placeholder concepts in the external release just because they appear in a hierarchy tree.
- Do not widen the catalog faster than implementation-grounded tutoring can support.
- Do not mix build-to-learn or reflection into the external concept journey.
- Do not keep `MCP` bundled inside a too-broad context family if it is really teaching capability access.

## Success criteria
- External V2 has a clearly named, curated concept catalog
- Every exposed concept has real teaching and implementation support
- The `Evals and reliability` family feels complete enough to teach as a serious concept system
- The release includes missing but strategically important concept families, not just the currently convenient ones
- The release story is clearly:
  - learn concepts already built into the OS
  - understand how they relate
  - see how they are implemented

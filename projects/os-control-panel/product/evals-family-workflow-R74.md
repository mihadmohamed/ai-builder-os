# Evals Family Workflow Review — R74

## PM framing

The external V2 release needs the `Evals` family to feel like a real learning system, not a promising partial cluster.

Right now the family already has a strong foundation:
- `Evals`
- `Agent-output quality evals`
- `Trace grading`
- `Replays`

But the family still feels incomplete because the OS already knows about additional eval subtypes in practice without yet teaching them as first-class concepts.

### Product decision

Complete the evals family for external V2 by adding the missing eval concepts that are already supported by the repo:
- `Tool Selection Evals`
- `Workflow Evals`
- `Memory Evals`
- `Safety Evals`
- `Cost Evals`
- `Latency Evals`
- `Reliability Evals`

## Experience Designer review

The learner should feel:
- “I understand the bigger eval map”

not:
- “I learned a few interesting eval terms, but I still do not know the full shape of the system.”

The family should help answer:
1. what evals are broadly
2. what kinds of evals exist
3. how those evals differ
4. where each one shows up in the OS

## UI Designer review

The most important UI outcome is not a bigger tree by itself.
It is a clearer mental map:
- `Evals` as the broad family
- child eval types as narrower categories
- `Trace grading` becoming legible as a workflow-quality subtype
- `Replays` staying visible as a supporting technique rather than pretending to be the same kind of concept as every eval subtype

## Architect review

The new concepts should be added as:
- first-class `LearningConceptKnowledge` entries
- explicit family members inside the evals family
- implementation-grounded concepts with anchors

Guardrails:
1. do not add placeholder concepts without real anchors
2. keep hierarchy honest even if it stays shallow for now
3. prefer conceptual clarity over a perfect taxonomy engine in this slice

## Success signal

After this slice:
- the evals family feels complete enough to teach as a coherent system
- each new concept has:
  - concept knowledge
  - hierarchy placement
  - implementation anchors
  - tutoring support
- the external V2 catalog becomes much stronger without relying on build-to-learn


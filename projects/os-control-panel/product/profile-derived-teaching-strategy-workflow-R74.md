# Profile-Derived Teaching Strategy Workflow — R74

Status: IMPLEMENTED
Requirement: R74
Related task: Task 227

## Why this workflow ran

The learning agent already used the learner profile, but the effect was still too implicit. Profile changes could influence recommendations and tone, yet the tutoring flow still felt too close to one default explanation style.

External V2 now needs a clearer personalization contract:
- stable governing concept truth
- explicit learner-specific teaching strategy
- live tutoring generated through that strategy

## PM recommendation

The PM recommendation is to introduce one inspectable teaching-strategy layer between the learner profile and the live tutoring turn.

The strategy should decide:
- where to enter the concept from
- what order to explain in
- how much AI Builder OS context to assume
- what type of example or grounding to favor
- what kind of coaching pressure to apply

Why:
- profile changes should produce visible teaching differences
- the concept truth should stay stable while the delivery adapts
- the system should be able to explain why two learners might receive different framing for the same concept

## Experience / UX recommendation

The learner should not have to think about “teaching strategy” as a separate setting.

Instead:
- the profile should quietly shape it
- the tutor should simply feel more tuned to the learner
- implementation walkthroughs should visibly change with OS familiarity
- clarification turns should feel more aligned with the learner’s preferred learning style

Desired learner feeling:
- “This is teaching the same concept, but in a way that fits how I learn.”

## UI recommendation

Do not add a separate new page or control for teaching strategy in external V2.

Instead:
- keep the profile as the visible source of personalization
- let the runtime generate the teaching strategy from those profile choices
- optionally surface the current strategy later only if debugging or learner trust needs it

## Architect recommendation

Keep three layers distinct:

1. **Governing truth**
   - concept facts
   - relationships
   - distinctions
   - implementation anchors
   - risks / misconceptions

2. **Teaching strategy**
   - entry point
   - explanation order
   - OS-context depth
   - example style
   - coaching style

3. **Live turn output**
   - the generated explanation / clarification / implementation walkthrough

Why:
- this preserves one canonical concept spine
- it makes personalization explicit and testable
- it avoids returning to a hidden second concept-truth layer in runtime code

## Implemented decisions

- The runtime now derives a structured teaching strategy from the saved learner profile before live tutoring turns.
- The strategy is passed into:
  - live teaching turns
  - live clarification turns
  - live implementation turns
- The teaching strategy is deterministic and inspectable, while the final tutoring response remains live-model-generated.

## Notes for later refinement

- If runtime testing shows the strategy is still too shallow, the next step should be to make example choice and analogy style more concept-family-aware.
- If learners need more trust in the personalization, consider a light “how I’m teaching this” explainer later without adding profile complexity.

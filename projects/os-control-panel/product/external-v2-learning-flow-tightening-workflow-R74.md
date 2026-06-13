# External V2 Learning Flow Tightening Workflow — R74

Status: IMPLEMENTED
Requirement: R74
Related task: Task 226

## Why this workflow ran

The concept explanations improved materially after the governing-truth cutover, but the surrounding experience was still carrying older helper-era shapes:
- profile setup still felt like open-ended writing work
- the plan surface still carried concept-page residue
- the active learning surface still asked for a written recap before the learner could move on

External V2 now needs to behave more like a guided learning product and less like a concept-management workspace.

## PM recommendation

### Profile semantics

The PM recommendation is to replace open-ended profile prompts with bounded selections that capture the minimum useful personalization inputs:
- learner background
- technical comfort
- AI Builder OS familiarity
- learning trajectory
- credibility goal
- preferred learning style
- current learning posture

Why:
- setup should feel light enough that the learner actually completes it
- the agent still gets enough signal to personalize context depth, examples, and sequencing
- option-based answers make the learner model more stable and easier to reason about than arbitrary prose

### Learning-plan behavior

The PM recommendation is that the plan should now be treated as the canonical navigation model for external V2:
- show the current step clearly
- show completed steps and later steps
- do not let the learner wander the catalog from this page
- use the page to orient, not to teach in depth

Why:
- external V2 is no longer a concept encyclopedia
- the learner should feel guided by the agent, not asked to self-curate the route

### Active learning behavior

The PM recommendation is that the live learning surface should remove the written recap requirement from the main path:
- the learner should clarify, inspect implementation, and continue
- once the concept feels solid, they should be able to mark it learned directly

Why:
- forcing a written recap makes the flow feel heavier than the new release model
- V2 is about guided concept learning, not assessing the learner every turn

## UX recommendation

### Profile

Use control types that match the decision shape:
- identity and trajectory questions: `selectbox` or `radio`
- short confidence/familiarity scales: horizontal `radio`
- keep the form visually chunked into two small sections rather than one long essay-like stack

Desired learner feeling:
- “This is quick and clear.”

### Learning plan

Treat the plan as an orientation surface, not a concept detail page:
- show overall progress
- show the current step prominently
- show earlier steps as completed and later steps as still ahead
- remove hierarchy blocks, relationship blocks, and concept administration from this page

Desired learner feeling:
- “I know where I am and what comes next.”

### Learn next

Keep the active learning page focused on one concept:
- explanation
- clarification
- implementation grounding
- completion or pause

Remove the written recap section from the main path.

Desired learner feeling:
- “I can stay with the concept without getting bounced into admin.”

## UI recommendation

### Profile controls

- `Product background`: `selectbox`
- `Technical comfort`: horizontal `radio`
- `AI Builder OS understanding`: horizontal `radio`
- `Current trajectory`: `radio`
- `Credibility goal`: `radio`
- `Preferred learning style`: `selectbox`
- `Current learning posture`: `selectbox`

### Learning plan layout

- keep `Learning plan` as a dedicated tab label
- render one clean progress summary at the top
- render each family as a bordered section with ordered steps
- visually distinguish:
  - completed
  - current
  - next up
  - later
- provide one primary action:
  - continue the current step in `Learn next`

### Learn next layout

- keep the explanation and clarification blocks
- keep the implementation walkthrough block
- replace the old recap form with one clear completion block
- include:
  - `Mark learned`
  - `Pause session`
  - `Back to learning plan`

## Implemented decisions

- External V2 profile uses structured options instead of open-ended text areas
- `Concepts` is renamed to `Learning plan`
- `Learning plan` now behaves as the plan surface, not a concept-detail browser
- `Learn next` no longer requires a written recap before the learner can continue
- `Mark learned` is available directly from the active learning flow

## Notes for later refinement

- If runtime testing shows the profile options are too coarse, refine the option sets rather than returning to open-ended onboarding.
- If the plan feels too abstract, add a slightly stronger “next up” explanation before reintroducing any concept-detail complexity.

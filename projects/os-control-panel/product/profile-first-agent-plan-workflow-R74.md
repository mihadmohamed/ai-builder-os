# Profile-First Agent Plan Workflow — R74

## PM framing

The external V2 learning release is no longer a concept browser for one operator.

It is becoming a guided learning product for other people.

That means the workflow needs to change from:
- browse concepts
- pick one manually
- ask the tutor for help

To:
- declare learner profile and AI Builder OS familiarity first
- let the agent decide the learning path
- move through a bounded personalized plan step by step

## Experience Designer review

The learner should not be asked to self-orchestrate the curriculum.

The experience should answer:
1. Who is this learner?
2. How much OS-local context should the tutor assume?
3. What is the current concept step?
4. What comes next after this step?

The learner should feel guided, not dropped into a map.

## UI Designer review

The Learning tab should start with `Profile`, not `Concepts`.

The `Concepts` page should stop behaving like a browseable library.

Recommended flow:
1. Profile
2. Agent-owned learning plan
3. Current concept detail
4. Continue learning

Hierarchy still matters, but now as plan structure rather than free navigation.

## Architect review

The product should distinguish between:
- concept hierarchy as structural curriculum context
- agent-owned learning plan as the active journey

The implementation walkthrough must receive a learner-level signal about AI Builder OS familiarity so explanation depth can adapt without inventing context.

## Product decision

- Move `Profile` to the first Learning tab for the external V2 journey
- Add a dedicated `AI Builder OS understanding` field to the learner profile
- Replace the concept-browser mental model with an agent-owned personalized plan
- Keep the hierarchy visible as orientation, but remove the assumption that the learner should browse freely

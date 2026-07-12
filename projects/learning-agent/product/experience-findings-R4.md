# Experience Designer Findings — R4

Requirement: R4 — Enhancement of AI Builder Learning Agent Landing Page

Handoff state: accepted

## User problem

Admitted learners arrive at a wrapper header followed by generic guidance, then encounter a second learning header and the actual profile workflow. The repeated orientation delays the first useful action and makes profile management feel lower priority than explanatory pilot copy.

## Affected user / workflow

Invited learners entering the admitted hosted app, reviewing or editing their profile, and moving into the personalized learning plan.

## Evidence

- The admitted wrapper currently renders `How it works` and `Pilot boundary` before the canonical learning navigation.
- The canonical learning surface already explains that the learner should start with the profile and defaults to the `Profile` section.
- Account identity and sign-out share the top area with the main product heading, while no concise welcome state explains the immediate learner journey.
- R4 identifies visual appeal, usability, responsiveness, and profile management as the intended outcomes.
- No production engagement analytics or recorded user-study feedback are available for R4.

## Confidence

High that the current duplication and hierarchy issue exist in the implementation. Medium that the proposed framing will improve engagement because behavioral evidence has not yet been collected.

## Severity / frequency

Medium severity and high frequency. Every admitted learner encounters this framing before reaching profile management.

## Finding type

Usability issue, clutter / hierarchy issue, and visual consistency issue.

## Recommendation type

UX improvement in scope.

## Rationale

The admitted landing state should orient the learner once, make the three-step journey understandable at a glance, and then hand attention directly to the canonical profile surface. Pilot and account metadata should remain available but visually secondary. The wrapper should not duplicate profile controls or learning logic.

## Recommended next role

UI Designer should define the welcome hierarchy, responsive progression treatment, and accessible brand-color constraints before Engineer implementation.

## Usability acceptance criteria

- The first screen establishes that the learner is admitted and identifies the immediate next action.
- Profile, plan, and guided learning read as one short progression rather than repeated instructions.
- The canonical `Profile` section remains the first actionable workflow.
- Account identity, sign-out, and operator controls remain available without dominating the page.
- No wrapper copy repeats the canonical learning introduction or implies new learning behavior.

## Post-implementation usability review

Status: PASS

- The admitted state now establishes access and the immediate profile-first journey in one compact welcome surface.
- Profile, learning plan, and guided learning read as a responsive three-step progression without adding duplicate navigation.
- Signed-in identity and sign-out remain available in a secondary utility row.
- The canonical `Profile` state, editor, learning navigation, and operator review remain intact.
- Repetitive wrapper `How it works` and `Pilot boundary` sections no longer delay the learner's first useful action.
- No additional R4 usability work is required for closure.

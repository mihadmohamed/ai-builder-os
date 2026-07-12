# Experience Designer Findings — R5

Requirement: R5 — UI Enhancement for Consistent Card Layout

Handoff state: accepted

## User problem

Learners encounter card-like surfaces with inconsistent height, alignment, and interaction affordance across the hosted wrapper. The admitted progression cards read as a row, but their height depends on content. The request-access and preview surfaces rely on native container defaults and do not share a clear card system with the wrapper's custom learner surfaces.

## Affected user / workflow

Signed-out visitors, non-admitted learners reviewing the access request page, and admitted learners scanning the profile-to-plan-to-learning progression before using the canonical learning workflow.

## Evidence

- R5 explicitly identifies inconsistent card heights, spacing, alignment, hover behavior, and responsiveness as the usability issue.
- The wrapper currently styles admitted progression cards with custom CSS but does not establish a shared card pattern for all wrapper card surfaces.
- The non-admitted request and preview areas use native bordered containers, so spacing and visual affordance differ from the custom admitted progression cards.
- No analytics or recorded usability study evidence is available for R5, so the confidence is grounded in implementation inspection and the accepted product requirement.

## Confidence

High that the visual inconsistency exists in the current implementation. Medium that standardized cards will improve task completion because behavioral measurement is not yet available.

## Severity / frequency

Medium severity and high frequency. These card surfaces appear in the main wrapper states that pilot users encounter before or during learning.

## Finding type

Visual consistency issue and usability issue.

## Recommendation type

UX improvement in scope.

## Rationale

The wrapper should use one restrained card rhythm for repeated or adjacent information blocks. Equalized card heights, consistent padding, predictable alignment, and subtle hover treatment help users scan groups of content without implying new learning functionality. The change should stay visual and wrapper-local.

## Recommended next role

UI Designer should define the card-system constraints before Engineer implementation.

## Usability acceptance criteria

- Related cards in the admitted progression row align to a consistent height at desktop widths and stack cleanly on narrow screens.
- Request-access and preview surfaces use the same spacing, border, radius, shadow, and hover vocabulary as the wrapper card system.
- Hover states are subtle and do not make static cards look like navigation if they are not clickable.
- The card system does not alter form behavior, preview-dialog behavior, sign-in behavior, pilot access rules, or canonical learning behavior.
- Text remains readable and unclipped at narrow and wide viewport sizes.

## Pre-implementation usability review

Status: READY FOR UI DESIGN / ENGINEERING

- The improvement should focus on wrapper-authored card surfaces only: admitted progression cards, request-access card, and learning-preview card.
- The existing grouping is appropriate and should be preserved; R5 is about consistency, not adding or reorganizing workflow steps.
- Equal-height behavior should be content-safe. Use grid stretch and minimum heights rather than fixed card heights.
- Hover treatment should communicate polish and surface grouping without implying that static explanatory cards are clickable.
- The canonical learning tab should not be styled or restructured as part of this requirement.

## Post-implementation usability review

Status: PASS

- Wrapper-authored card surfaces now share a consistent visual rhythm across admitted progression, request-access, and preview states.
- The existing request and preview grouping remains separate, and the admitted profile-to-plan-to-learning progression remains intact.
- Equal-height behavior is handled through responsive grid stretch and content-safe minimums rather than rigid clipping heights.
- Hover treatment is subtle and does not introduce new navigation or workflow meaning.
- No R5 usability issue remains open for closure.

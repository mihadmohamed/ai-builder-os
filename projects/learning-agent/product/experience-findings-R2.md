# Experience Designer Findings — R2

Requirement: R2 — Landing Page Design Improvement

Handoff state: resolved

## User problem

External learners who are signed in but not admitted must understand the pilot, decide whether it is relevant, and request access. The current page presents the right information but gives each section similar visual weight, separates the product preview from the request action, and shows account status too prominently.

## Affected user / workflow

Non-admitted external learners moving from Google sign-in through pilot comprehension, learning-experience preview, and access request.

## Evidence

- The current Streamlit surface uses several same-weight headings and text blocks across two columns.
- The signed-in identity is rendered as a full-width information banner before the user reaches the page purpose.
- The learning-plan screenshot appears after the access explanation instead of beside the request decision.
- The current screenshot is rendered at full width and has no explicit enlarge interaction.
- R2 records visual appeal, responsive usability, and seamless modal image viewing as success criteria.

## Confidence

High for the hierarchy and workflow issues because they are directly observable in the implementation. Medium for engagement impact because no production analytics or user-study evidence is recorded.

## Severity / frequency

Medium-to-high severity. Every signed-in user who is not admitted encounters this page, and uncertainty here can prevent an access request.

## Finding type

Usability issue, clutter / hierarchy issue, and visual consistency issue.

## Recommendation type

UX improvement in scope.

## Rationale

The page should preserve one clear journey: understand the pilot, inspect a credible preview, and request access. The access form remains the primary action. The product image should support that decision in the same visual region and enlarge on demand without navigation. Visual depth should come from restrained grouping and the existing palette, not extra sections or animation.

## Recommended next role

UI Designer should define the exact responsive composition, visual treatment, and modal constraints before Engineer implementation.

## Post-implementation usability review

Status: PASS

- The page now establishes purpose before account metadata.
- The access request remains the single primary action.
- The learning preview sits in the same decision area and opens without navigation.
- Preview-only language clearly distinguishes product evidence from admitted access.
- The two-column layout uses native Streamlit stacking behavior for narrow viewports.
- No additional R2 work is required for closure.

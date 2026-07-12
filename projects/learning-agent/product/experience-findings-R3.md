# Experience Designer Findings — R3

Requirement: R3 — Request Page Layout Improvements

Handoff state: resolved

## User problem

Non-admitted learners see the access-request form and learning preview inside one bordered surface. The shared boundary makes the preview look like part of the form and weakens the distinction between applying for access and inspecting product evidence.

## Affected user / workflow

Signed-in external learners reviewing the hosted pilot before admission and deciding whether to submit an access request.

## Evidence

- The current Streamlit implementation renders `Request access` and `See the learning experience` inside the same bordered container.
- The preview uses the full width of the request column, making the image vertically dominant after the form.
- R3 explicitly requires separate sections and a shorter learning-experience section.
- No user-study or production analytics are recorded, so the expected usability improvement remains an informed product assumption.

## Confidence

High that the current grouping and image height exist in the implementation. Medium that separation alone will improve completion or comprehension because no behavioral measurement is available.

## Severity / frequency

Medium severity and high frequency. Every signed-in learner who is not admitted encounters this page.

## Finding type

Usability issue and clutter / hierarchy issue.

## Recommendation type

UX improvement in scope.

## Rationale

Use two adjacent but distinct surfaces in the request column: one for the access form and one for the preview. Keep the access form first and visually primary. Make the preview a compact supporting surface with the existing enlarge action so users can inspect detail on demand without the thumbnail dominating the page.

## Recommended next role

UI Designer should define the responsive grouping and compact-preview constraints before PM creates implementation work.

## Post-implementation usability review

Status: PASS

- The request form and learning preview now have separate visible boundaries.
- The request form remains first and contains the only primary action.
- The inline preview is approximately 320 by 177 pixels at its intended width, materially reducing its vertical footprint.
- The existing enlarge action preserves access to full image detail without navigation.
- Preview-only language remains visible and does not imply admitted access.
- No additional R3 usability work is required for closure.

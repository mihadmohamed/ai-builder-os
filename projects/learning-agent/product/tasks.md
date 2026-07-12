# Tasks — AI Builder Learning Agent

## Wrapper Task Boundary

Tasks in this file are only for wrapper-specific work:
- hosted shell UX
- auth and pilot access
- request-access operations
- deployment and hosted preview behavior

Tasks in this file must not become the execution log for:
- canonical learning-engine behavior
- concept-catalog changes
- tutoring logic changes
- learning-plan behavior changes

That work belongs in:
- `projects/os-control-panel/product/tasks.md`

## Task 0: Validate the hosted wrapper path

Type: Validation Task
Status: DONE
Requirement: R1

Goal:
Verify that the hosted wrapper can be launched, configured, and validated as a real external pilot surface.

Requirements:
- Confirm the hosted wrapper boots locally and in Railway
- Confirm auth, preview, and request-access flows behave as expected
- Keep the validation path lightweight but repeatable

Validation:
- Run the hosted wrapper validation checks
- Confirm launch docs and preflight guidance stay usable

Output:
- Summary of hosted readiness
- Any gaps blocking real pilot usage

## Task 4: Improve the admitted learner landing experience

Type: Feature Task
Status: DONE
Requirement: R4

Goal:
Make the admitted learner's first screen feel focused, credible, and easy to understand while keeping profile management and all canonical learning behavior unchanged.

Requirements:
- Apply the usability direction in `product/experience-findings-R4.md`
- Apply the interface direction in `product/ui-design-brief-R4.md`
- Establish a clear admitted-user welcome and explain the profile-to-plan-to-learning progression at a glance
- Keep account identity and pilot status secondary to the learner's next action
- Remove repetitive wrapper guidance that competes with the canonical `Profile` starting state
- Preserve direct access to profile editing, learning navigation, and operator access-request review

Constraints:
- Keep the wrapper thin and do not alter canonical profile, plan, tutoring, or persistence behavior
- Use native Streamlit and scoped lightweight CSS only; add no UI dependency
- Reuse the existing brand palette with accessible text contrast and restrained accent treatment
- Preserve OIDC, local preview, allowlist, sign-out, operator, and per-user isolation behavior
- Keep the admitted experience responsive and avoid decorative motion or expensive assets

Validation:
- Run the hosted learning wrapper unit tests
- Run the learning-agent preflight unit tests and production-shaped preflight
- Run the learning-agent wrapper-boundary and product-artifact audits
- Confirm the admitted state keeps profile controls and learning navigation functional
- Perform lightweight QA and post-implementation usability review

Validation outcome:
- Hosted learning and preflight unit tests passed: 11/11
- Production-shaped hosted pilot preflight passed with no warnings
- Learning-agent wrapper-boundary and product-artifact audits passed
- AppTest confirmed the admitted welcome, responsive three-step progression, secondary account utility row, canonical profile editor, and learning navigation remain available
- Full OS deterministic unit suite passed 249/250; the only failure is an unrelated pre-existing mismatch where uncommitted canonical Evals anchor additions return four items against a three-item test limit
- Post-implementation usability review passed with no R4-blocking clarity, hierarchy, responsiveness, or workflow issue

## Task 5: Standardize hosted wrapper card layout

Type: Feature Task
Status: DONE
Requirement: R5

Goal:
Make wrapper-authored card surfaces visually consistent, responsive, and easy to scan while preserving all hosted access and canonical learning behavior.

Requirements:
- Apply the usability direction in `product/experience-findings-R5.md`
- Apply the interface direction in `product/ui-design-brief-R5.md`
- Establish a shared wrapper card treatment for repeated and adjacent card-like surfaces
- Keep admitted progression cards equal-height at desktop widths and stacked cleanly on narrow screens
- Standardize spacing, alignment, border, radius, shadow, and subtle hover behavior for request-access and preview card surfaces
- Preserve the separate request and preview grouping established for R3
- Preserve the admitted learner welcome hierarchy established for R4

Constraints:
- Keep the wrapper thin and do not alter canonical profile, plan, tutoring, or persistence behavior
- Use native Streamlit and scoped lightweight CSS only; add no UI dependency
- Do not use rigid fixed heights that can clip content on narrow screens
- Keep non-clickable cards visually calm; hover affordance must not imply navigation
- Preserve OIDC, local preview, allowlist, sign-out, request validation, request persistence, operator review, and per-user isolation behavior

Validation:
- Run the hosted learning wrapper unit tests
- Run the learning-agent preflight unit tests and production-shaped preflight
- Run the learning-agent wrapper-boundary and product-artifact audits
- Confirm request submission, preview dialog, admitted progression, and canonical learning navigation remain functional
- Perform lightweight QA and post-implementation usability review for card consistency and responsiveness

Validation outcome:
- Hosted learning wrapper unit tests passed: 9/9
- Learning-agent preflight unit tests passed: 2/2
- Production-shaped hosted pilot preflight passed with no warnings
- Learning-agent wrapper-boundary and product-artifact audits passed
- AppTest coverage confirmed request submission, preview dialog, admitted progression, account visibility, current learning-plan step visibility, and canonical learning navigation remain functional
- Post-implementation usability and UI review passed with no R5-blocking consistency, responsiveness, or workflow issue

## Task 1: Polish the hosted pilot access experience

Type: Feature Task
Status: IN_PROGRESS
Requirement: R1

Goal:
Make the hosted Learning Agent feel polished and understandable to external pilot users before and after admission.

Requirements:
- Provide a clear signed-out shell with hosted-product framing
- Support Google sign-in, local preview mode, and admitted-user access
- Give non-admitted users a useful preview and inline request-access flow
- Keep operator handling of requests lightweight and visible

Constraints:
- Keep the wrapper thin relative to the canonical learning engine
- Do not create duplicate learning-truth logic in this project
- Preserve pilot access controls even when OAuth is in production mode

Validation:
- Verify admitted and non-admitted flows locally and in the hosted environment
- Confirm request-access submission and operator visibility work
- Confirm OS project preview opens the wrapper in local mode

## Task 6: Open the hosted flow and add visible usage monitoring

Type: Feature Task
Status: IN_PROGRESS
Requirement: R6

Goal:
Move the hosted Learning Agent from an admission-gated pilot flow to an open signed-in experience with visible daily limits, trusted-tier continuity, and operator monitoring.

Requirements:
- Remove the hard post-sign-in access wall for standard users
- Keep Google sign-in as the identity boundary for persistence and usage accounting
- Reinterpret `LEARNING_AGENT_ALLOWED_EMAILS` as a trusted-tier list rather than a hard access gate
- Expose the daily live-turn limit clearly in the learner UI
- Count only costly live-agent actions toward the daily limit
- Add lightweight hosted operator monitoring for logins, activity, usage remaining, and limit pressure
- Preserve local preview review modes for request-page, admitted, and operator states

Constraints:
- Keep the wrapper thin and do not fork canonical learning truth, progression, or tutoring behavior
- Preserve per-user persistence through the hosted runtime root and OS tenancy
- Keep monitoring and rate-limit logging file-backed and local to the hosted runtime for now
- Maintain backward compatibility for already-allowlisted users by treating them as trusted tier

Validation:
- Verify a newly signed-in non-allowlisted user can enter the full learning experience immediately
- Verify a trusted user still receives the trusted tier
- Verify live-turn actions decrement visible remaining usage and stop at the daily limit
- Verify operator users can see usage summaries and per-user monitoring details
- Verify per-user state persists across Railway redeploys for both standard and trusted users

## Task 2: Improve the external landing-page experience

Type: Feature Task
Status: DONE
Requirement: R2

Goal:
Make the non-admitted external-user landing page more visually coherent, easier to scan, and more effective at showing the learning experience without sending users away from the access-request flow.

Requirements:
- Apply the usability direction in `product/experience-findings-R2.md`
- Apply the interface direction in `product/ui-design-brief-R2.md`
- Use the existing brand palette in restrained light-touch surfaces that improve hierarchy and depth
- Reduce the visual prominence of the signed-in account status
- Keep the access request as the primary action
- Place the learning-experience preview directly within the request-access side of the workflow
- Let users open the existing learning-plan image in an accessible modal without navigating away
- Preserve clear feedback for empty and successful access-request submissions

Constraints:
- Keep the wrapper thin and do not alter canonical learning-engine behavior
- Use native Streamlit capabilities and existing assets; add no UI dependency
- Preserve OIDC, local preview, allowlist, operator, and request-persistence behavior
- Keep the layout usable at narrow and wide viewport sizes
- Do not add decorative motion or imply access that the user does not have

Validation:
- Run the hosted learning wrapper unit tests
- Run the learning-agent preflight checks
- Run the OS control-panel eval suite, including the wrapper-boundary audit
- Confirm the preview image opens through a modal interaction and the request-access action remains primary

Validation outcome:
- Hosted learning and preflight unit tests passed
- Hosted pilot preflight passed with a synthetic non-secret production-shaped environment
- Learning-agent wrapper boundary audit passed
- Full OS unit, scenario, and capability checks passed; the eval runner remains nonzero only because of an unrelated pre-existing orphan product artifact in `projects/os-control-panel`
- Post-implementation usability review found no R2-blocking clarity, hierarchy, or interaction issue

## Task 3: Separate and compact the request-page preview

Type: Feature Task
Status: DONE
Requirement: R3

Goal:
Make access request submission and learning-experience review clearly distinct while reducing the inline preview's vertical footprint.

Requirements:
- Apply the usability direction in `product/experience-findings-R3.md`
- Apply the interface direction in `product/ui-design-brief-R3.md`
- Render `Request access` and `See the learning experience` in separate bordered surfaces
- Keep the request form before the preview and preserve it as the only primary action
- Reduce the inline preview height through a compact, responsive thumbnail treatment
- Preserve the existing enlarge-preview dialog and preview-only messaging

Constraints:
- Keep all existing section content and form fields unchanged
- Use native Streamlit and existing assets; add no UI dependency
- Preserve OIDC, local preview, allowlist, sign-out, request validation, request persistence, and operator behavior
- Keep the wrapper thin and do not alter canonical learning-engine behavior
- Avoid fixed section heights that could clip content or fail on narrow viewports

Validation:
- Run the hosted learning wrapper unit tests
- Run the learning-agent preflight unit tests and production-shaped preflight
- Run the learning-agent wrapper-boundary audit
- Confirm the request and preview remain functional, separately grouped, and ordered correctly
- Perform lightweight QA and post-implementation usability review

Validation outcome:
- Hosted learning and preflight unit tests passed: 10/10
- Production-shaped hosted pilot preflight passed with no warnings
- Learning-agent wrapper-boundary and product-artifact audits passed
- Full OS deterministic unit suite passed: 249/249
- Full eval baseline reported 271/271 checks passing; the runner remains nonzero only because of an unrelated pre-existing orphan artifact in `projects/os-control-panel`
- AppTest structure confirmed separate sibling request and preview surfaces with preserved form submission and modal interaction
- Post-implementation usability review passed with no R3-blocking issue

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking
- Keep deeper learning-engine work in the canonical `os-control-panel` project unless it is truly wrapper-specific
- If a task would change what the learner sees as learning truth rather than hosted-wrapper delivery, move it to `os-control-panel`

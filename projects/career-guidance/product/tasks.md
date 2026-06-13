# Tasks — Career guidance

## Task 0: Run validation suite

Status: DONE
Requirement: R0

Goal:
Verify the current project state using the available validation mechanism.

Requirements:
- Run the project validation suite
- Report pass/fail clearly
- Highlight missing fixtures or tooling gaps if validation is not yet ready

Validation:
- Use the project-local deterministic validation runner
- Report whether the validation path itself is missing or incomplete

Output:
- Unit tests pass: 4/4
- Deterministic evals pass: 1/1
- Project structure validation passes
- UI runtime import is blocked in the current shell because `streamlit` is not installed

## Task 1: Build career guidance analysis engine

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Analyze a user's CV text and target job descriptions to identify concrete skill or knowledge gaps and produce a personalized development plan.

Requirements:
- Accept CV text and one or more target job descriptions as inputs
- Identify at least 3 specific gaps when enough target-role signals are present
- Include evidence from the CV and target jobs for each gap
- Produce a development plan with recommended actions or resources for each gap
- Avoid inventing unsupported experience, skills, certifications, or job requirements

Constraints:
- Use deterministic local logic for the initial implementation
- Do not require manual intervention to produce the analysis
- Keep behavior stable and testable through local validation

Validation:
- Unit tests cover gap detection, no-hallucination behavior, and development plan generation
- Deterministic eval runner reports passing fixture coverage

Output:
- Added deterministic analysis engine in `src/advisor.py`
- Added unit coverage for gap detection, missing inputs, and development-plan generation

## Task 2: Build Streamlit career guidance advisor UI

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Provide a clear user-facing interface where job seekers can paste CV and target-job content, run analysis, and review gaps plus a development plan.

Requirements:
- Present a focused first screen with CV input, target job input, and one clear primary analysis action
- Show a concise summary before detailed gap cards
- Display at least 3 gaps with importance, CV evidence, target-job evidence, and actions when available
- Provide progressive disclosure for structured output details
- Surface validation warnings when inputs are insufficient

Constraints:
- UI Designer direction: use a restrained Streamlit layout, native forms, tight vertical rhythm, explicit sections, and no decorative card-heavy landing page
- Keep the workflow honest about input limitations and do not imply external learning-platform integrations
- Preserve rerun orientation after submission using Streamlit session state where useful

Validation:
- Smoke validation confirms the Streamlit entrypoint imports and summary rendering helpers work
- Lightweight UX validation checks first-screen clarity, output hierarchy, and insufficient-input messaging

Output:
- Added Streamlit UI in `src/app.py`
- Lightweight UX review: first screen has one form, two primary inputs, one analysis action, summary-before-detail output, warnings for insufficient input, and structured output in an expander
- Runtime validation was previously blocked in another environment without `streamlit`; this is now treated as resolved for the current V2 testing flow.

## Task 3: Implement project-local validation coverage

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Replace the template validation stub with deterministic validation that proves the R1 workflow works locally.

Requirements:
- Add stable eval fixtures for a representative CV and target jobs
- Validate that outputs include at least 3 gaps and actionable recommendations
- Report clear pass/fail results from `tools/eval_runner.py`

Constraints:
- Keep validation local and deterministic
- Do not depend on live model calls

Validation:
- `python3 projects/career-guidance/tools/eval_runner.py` exits with code 0 and reports all fixtures passing

Output:
- Added `evals/case_1.json`
- Replaced template eval stub with deterministic fixture validation

## Task 4: Clarify multiple job posting input guidance

Type: Feature Task
Status: DONE
Requirement: R2

Goal:
Make it immediately clear how job seekers should paste one or more target job postings into the existing Career Guidance Advisor input so they can complete submissions with confidence.

Requirements:
- Add concise instructions near the target job descriptions input that explain users can paste multiple postings into the existing field
- Include a concrete separator example such as putting each posting on a new line or separating postings with a visible divider
- Keep the guidance focused on input clarity and avoid implying a new upload, parsing, or submission feature
- Preserve the existing single-form workflow and primary analysis action
- Maintain warning behavior for insufficient or missing inputs

Constraints:
- Experience Designer direction: reduce ambiguity at the moment of input without adding extra steps or broadening the workflow
- UI Designer direction: use native Streamlit form/help text or caption patterns with tight spacing; do not introduce a new visual redesign or decorative containers
- Stay within R2 scope and do not redesign the entire input interface
- Preserve deterministic analyzer behavior

Validation:
- Unit tests continue to pass
- Deterministic eval runner continues to pass
- UI smoke or source-level validation confirms the target job input includes clear multi-posting instructions and an example separator

Output:
- Updated Career Guidance Advisor page copy for multiple job posting input clarity
- Added or updated lightweight validation for the input guidance
- Unit tests pass: 5/5
- Deterministic evals pass: 1/1
- Project structure validation passes

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking, not broad planning speculation
- Move candid planning or sensitive sequencing notes into an ignored `private/` directory

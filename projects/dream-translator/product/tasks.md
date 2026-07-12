# Tasks — dream translator

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
- Summary of results
- Any gaps that block reliable validation

## Task 1: Build dream translation UI and deterministic interpretation

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Provide a usable Streamlit interface that translates a user-described dream into a respectful interpretation and matching artistic visual representation.

Requirements:
- Let the user enter a dream description and select a visual style
- Produce an interpretation with at least three distinct insights beyond basic symbol meanings
- Generate a visually appealing representation or image-ready art direction tied to the dream theme
- Keep the output sensitive, respectful, and clearly outside professional diagnosis or therapy
- Preserve the latest result during Streamlit reruns

Constraints:
- Do not depend on a live external model or image API for deterministic validation
- Do not hallucinate personal facts not present in the dream text
- Keep the UI focused on the primary translation flow rather than a landing page

Validation:
- Add deterministic unit coverage for the interpretation contract
- Add or update project-local eval fixtures and eval runner
- Run the project-local validation suite and report pass/fail

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking, not broad planning speculation
- Move candid planning or sensitive sequencing notes into an ignored `private/` directory

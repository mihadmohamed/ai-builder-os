# Tasks — [Project Name]

## Task 0: Run validation suite

Status: TODO
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

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking, not broad planning speculation
- Move candid planning or sensitive sequencing notes into an ignored `private/` directory
- Keep standalone product artifacts linked from a canonical requirement or task entry instead of letting them float unreferenced under `product/`

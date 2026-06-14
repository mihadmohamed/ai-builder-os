# Tasks — AI Builder Learning Agent

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

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking
- Keep deeper learning-engine work in the canonical `os-control-panel` project unless it is truly wrapper-specific

# Tests

This directory contains deterministic test support for ParentMate.

## Current Validation Shape

ParentMate uses two complementary automated layers plus a small manual layer:

- `tools/eval_runner.py`
  - replay-backed extraction validation for end-to-end product behavior
- `tests/unit/`
  - deterministic unit tests for helper logic that replay evals do not isolate well
- `tests/manual/ux_checks.md`
  - lightweight human-reviewed checks for parent-facing clarity and calendar handoff usability

## Unit Coverage

The current unit suite covers:

- `test_app.py`
  - parent-facing event summary helper behavior
- `test_calendar.py`
  - calendar sync planning and Google Calendar link construction
- `test_extractor.py`
  - deterministic extraction post-processing such as normalization and event merging

## Guidance

- Use replay-backed evals as the main product-behavior safety net.
- Use `tests/unit/` for deterministic local logic that is easier to validate in isolation.
- Keep manual checks focused on usability, readability, and trust.
- Prefer deterministic validation before adding live or hosted dependencies.

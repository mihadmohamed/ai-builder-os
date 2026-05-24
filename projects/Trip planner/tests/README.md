# Tests

This directory holds test support for the Personal Trip Planner.

## Current Validation Shape

Right now the project relies primarily on:

- `tools/eval_runner.py`
  - deterministic planner and feedback validation
- `tests/manual/ux_checks.md`
  - lightweight human-reviewed UI checks for the local planning flow

There are no dedicated unit-test modules in `tests/unit/` yet because the project's deterministic validation currently lives in the project-local eval runner.

## Guidance

- Add narrow Python tests here if planner or storage logic grows beyond what the eval runner covers comfortably.
- Keep manual checks focused on usability, clarity, and operator trust.
- Prefer deterministic automation before adding live or hosted validation dependencies.

# Tests

This directory contains automated and manual test support for the OS Control Panel.

The project uses three complementary validation layers:

- `tests/unit/`
  - deterministic Python tests for workspace/state helpers, routing logic, and selected UI-surface helpers
- `evals/`
  - deterministic workflow-style scenario fixtures executed through the project eval runner
- `tests/manual/`
  - lightweight human-reviewed checks for UX, interaction clarity, and broader operator experience

## Automated Coverage

`tests/unit/test_workspace.py` covers deterministic behavior such as:

- navigation labels and structure
- workspace/project helper behavior
- workflow and routing helpers
- approval, clarification, and thread-related state helpers
- implementation-run and verification helpers
- selected UI-facing helper outputs that are stable enough for deterministic testing

Run the full automated project baseline with:

```bash
.venv/bin/python projects/os-control-panel/tools/eval_runner.py
```

That runner executes both:

- `tests/unit/`
- `evals/scenarios.json` through `tools/scenario_eval_runner.py`

## Manual Checks

Use `tests/manual/` for checks that are still better handled by a human, especially:

- UX clarity
- scanability and layout judgment
- project-flow sanity across multiple surfaces
- post-change review prompts that are not strong candidates for deterministic automation yet

Current manual docs include:

- `tests/manual/ux_checks.md`
- `tests/manual/post_test_review_list.md`
- `tests/manual/phase1_phase2_verification_plan.md`

## Guidance

- Prefer deterministic tests for state parsing, routing, and helper behavior.
- Prefer scenario evals when the behavior depends on realistic file-backed workflow state.
- Use manual checks when the question is mostly about operator clarity, usability, or cross-surface product feel.
- Add new automated coverage when a workflow behavior becomes important enough that regressions would be costly to miss.

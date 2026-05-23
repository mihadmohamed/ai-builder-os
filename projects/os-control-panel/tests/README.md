## Tests

This directory contains narrow deterministic tests and lightweight smoke checks for the OS Control Panel.

Current baseline:

- `tests/unit/` covers deterministic workspace-summary helpers and a minimal application-surface smoke check
- `tools/eval_runner.py` now runs both:
  - `tests/unit/` for deterministic helper coverage
  - `evals/scenarios.json` via `tools/scenario_eval_runner.py` for workflow-style scenario coverage

Use `tests/manual/` for lightweight human-reviewed checks that are not well suited to automation yet, such as obvious UX clarity checks.

Current manual plan:

- `tests/manual/phase1_phase2_verification_plan.md` tracks human verification for:
  - `R25 — Phase 1 multi-agent workspace foundation`
  - `R26 — Phase 2 workflow inbox and approval layer`

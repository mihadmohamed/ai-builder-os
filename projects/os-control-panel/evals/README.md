## Evals

Store project eval fixtures here.

This project now uses two validation layers:

- `tests/unit/` for deterministic helper and UI-surface tests
- `evals/scenarios.json` plus `tools/scenario_eval_runner.py` for workflow-style scenario evals

Current scenario coverage focuses on high-risk OS behaviors:

- orchestrator routing for `NEW` requirements
- PM clarification blocking behavior
- Experience Designer handoff routing
- PM chat discovery producing a structured draft
- requirement-deletion cleanup of linked workflow state
- per-project implementation locking

Suggested structure as coverage grows:

- `scenarios.json` for named deterministic workflow cases
- additional fixture files when a scenario needs larger input state
- `replays/` only if a future slice introduces model-backed validation worth snapshotting

Prefer deterministic evals for routine development. Add replay-backed or live validation only when the product behavior really depends on model output rather than file-backed workflow logic.

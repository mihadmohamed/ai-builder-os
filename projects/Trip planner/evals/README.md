# Evals

This directory supports deterministic evaluation for the Personal Trip Planner.

The current project keeps most eval cases in code inside `tools/eval_runner.py` rather than in a large fixture set.

## Current Eval Scope

The deterministic eval runner currently checks:

- budget filtering
- locality filtering
- weather suitability
- age-range filtering
- feedback persistence
- invalid feedback rejection

Run the project-local eval path with:

```bash
python3 projects/Trip\ planner/tools/eval_runner.py
```

## Files

- `replays/`
  - reserved for future replay-backed validation if the project ever introduces model-backed planning behavior

## Guidance

- Prefer deterministic evals for routine development work.
- Add fixture files only when they make planner behavior easier to reason about than in-code cases.
- Add replay-backed or live validation only if a future version depends on external services or model output.

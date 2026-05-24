# Tools

This directory contains project-local tooling for the Personal Trip Planner.

## Files

- `eval_runner.py`
  - main deterministic validation entrypoint for the project
  - exercises planner behavior and feedback persistence offline

- `live_eval_runner.py`
  - placeholder for future live validation if the project ever depends on external services or model-backed behavior

## Main Entry Point

Run the standard deterministic validation path with:

```bash
python3 projects/Trip\ planner/tools/eval_runner.py
```

## Guidance

- Keep project-specific validation tooling here when it depends on trip-planning behavior.
- Prefer deterministic local validation for routine development.
- Add live or replay-backed tooling only when the product genuinely grows beyond explicit-input deterministic planning.

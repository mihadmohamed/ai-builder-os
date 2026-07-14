# Tools

This directory contains project-local tooling for the OS Control Panel.

These scripts support deterministic validation, scenario evaluation, and requirement-level implementation runs that are specific to this project's control-plane workflow.

## Files

- `eval_runner.py`
  - main deterministic validation entrypoint for the project
  - runs both unit tests and scenario evals

- `scenario_eval_runner.py`
  - executes deterministic workflow-style scenarios from `evals/scenarios.json`
  - focuses on control-plane routing, workflow artifacts, and file-backed state transitions

- `sdk_contract_eval_runner.py`
  - validates the complete SDK agent registry, handoffs, agents-as-tools, approval gates, guardrails, shared entrypoints, and removal of the custom loop

- `codex_native_eval_runner.py`
  - validates project-scoped Codex agents, bounded delegation, the durable Codex queue, MCP tools, and the explicit API-backend boundary without invoking a model

- `run_requirement_implementation.py`
  - worker script for a single background requirement-implementation run
  - updates implementation-run state and records success or failure back into project data

- `live_eval_runner.py`
  - grades captured SDK lifecycle traces from real model-backed runs
  - complements deterministic contract evals without making routine tests depend on paid model calls

## Main Entry Points

Run the standard deterministic project baseline with:

```bash
.venv/bin/python projects/os-control-panel/tools/eval_runner.py
```

This covers:

- `tests/unit/`
- deterministic scenario evals from `evals/scenarios.json`
- product-artifact audit for canonical `requirements.md` / `tasks.md` linkage
- hosted Learning Agent wrapper audit to keep `projects/learning-agent` aligned with the canonical learning engine

Run the Codex-native architecture contract directly with:

```bash
.venv/bin/python projects/os-control-panel/tools/codex_native_eval_runner.py
```

## Guidance

- Keep project-specific tooling here when it depends on this control panel's workflow model or file layout.
- Prefer deterministic tooling for routine development work.
- Add live or replay-backed tooling only when the behavior truly depends on external systems or model output.
- Keep worker scripts and eval runners aligned with the source-of-truth boundary: product files express durable intent, while `data/` stores local operational state.

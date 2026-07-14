# Evals

This directory holds deterministic evaluation fixtures for the OS Control Panel.

The project uses two complementary validation layers:

- `tests/unit/`
  - deterministic helper and UI-surface tests
- `evals/scenarios.json`
  - deterministic workflow-style scenario fixtures
- `evals/eval_cases.json`
  - explicit contracts for all eight agent-evaluation dimensions
- `evals/sdk_contract_cases.json`
  - SDK role, handoff, agents-as-tools, approval, guardrail, entrypoint, and legacy-removal contracts
- `tools/codex_native_eval_runner.py`
  - Codex custom-agent, bounded-delegation, durable queue, MCP, and API-boundary contracts

Use the project eval runner to execute both layers together:

```bash
.venv/bin/python projects/os-control-panel/tools/eval_runner.py
```

## Current Eval Scope

The scenario layer focuses on high-risk control-plane behavior such as:

- orchestrator routing for `NEW` requirements
- PM clarification blocking behavior
- Experience Designer handoff routing
- PM chat discovery producing a structured draft
- active PM thread routing back to the Product Director
- requirement deletion cleanup of linked workflow state
- per-project implementation locking
- structural pending-task routing to Architect
- exact, missing, unnecessary, ordered, and unauthorized tool selection
- required-memory recall and stale-memory rejection
- token and estimated-spend budgets
- end-to-end latency budgets
- repeated-run reliability thresholds
- genuine Agents SDK architecture and shared Streamlit/Codex entrypoints
- SDK trace lifecycle quality, including handoffs, tools, guardrails, failures, and pauses
- Codex-native default execution with no OpenAI API runtime call on the normal Streamlit/MCP path

## Files

- `scenarios.json`
  - named deterministic workflow cases used by `tools/scenario_eval_runner.py`
- `replays/`
  - reserved for future replay-backed or model-backed validation if the product ever needs it

## Guidance

- Prefer deterministic evals for routine development work.
- Add scenario fixtures when workflow behavior depends on file-backed state transitions or routing logic.
- Add replay-backed or live validation only when the product behavior genuinely depends on model output rather than deterministic control-plane logic.
- Keep fixtures focused on operator-visible behavior and durable workflow artifacts rather than incidental UI layout details.

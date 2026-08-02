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
- `evals/pm_behavioral_cases.json`
  - versioned, synthetic PM judgment and trajectory cases across sixteen representative product situations
- `evals/pm_behavioral_baseline.md`
  - the first deterministic PM contract baseline, thresholds, fingerprints, and limitations
- `evals/pm_model_selection.md`
  - staged R101 campaign preparation, API-billing boundary, report requirements, and selection workflow
- `tools/codex_native_eval_runner.py`
  - Codex custom-agent, bounded-delegation, durable queue, MCP, and API-boundary contracts
- `tools/pm_behavioral_eval_runner.py`
  - shared deterministic and explicitly gated live-trial grading entry point

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
- PM typed-output, evidence, tool, consultation, approval, guardrail, trajectory, and canonical-outcome behavior

## PM behavioral evaluations

The default command is deterministic, runs three synthetic trials for each case, and uses no model tokens:

```bash
OPENAI_API_KEY= .venv/bin/python projects/os-control-panel/tools/pm_behavioral_eval_runner.py
```

Live trials use the same case and grading contract but must be executed deliberately through a supported host and exported as typed trial records. Both live gates and a trial file are required:

```bash
# Consumes Codex plan or credits; exact token counts may be unavailable.
.venv/bin/python projects/os-control-panel/tools/pm_behavioral_eval_runner.py \
  --backend codex --live --acknowledge-billing --model-label MODEL \
  --trial-file /path/to/codex-trials.json

# Consumes OpenAI API project tokens and model requests; SDK execution still needs its separate OS authorization.
.venv/bin/python projects/os-control-panel/tools/pm_behavioral_eval_runner.py \
  --backend agents-sdk --live --acknowledge-billing --model-label MODEL \
  --trial-file /path/to/sdk-trials.json
```

The billing acknowledgement makes accidental invocation fail closed; it is not permission to start an API run or perform an external action. The OS's existing authorization gates remain authoritative.

R101 model-candidate manifests and deterministic selection use `tools/pm_model_campaign_runner.py`. See `pm_model_selection.md`; manifest generation never invokes a model and every paid campaign remains separately authorization-gated.

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

# Hosted Learning Agent Preflight Validator Workflow — R81

Status: IMPLEMENTED
Requirement: R81
Related task: Task 230

## Why this workflow ran

The hosted Learning Agent pilot already had:
- deployment packaging
- a launch checklist
- a clearer learner-facing shell

What it still lacked was a fast, machine-checkable way to catch obvious operator
mistakes before a deploy or invite wave.

Docs alone were better than scattered notes, but they still left room for:
- missing OIDC variables
- wrong release profile
- a non-persistent runtime root
- a forgotten allowlist
- placeholder privacy contact details

## PM recommendation

Treat preflight as part of pilot quality.

Before an invite-only pilot, the operator should be able to run one command and
get:
- hard failures for launch-blocking mistakes
- warnings for softer quality issues
- a clear signal that the current environment matches the intended pilot boundary

## UX recommendation

The output should be calm and explicit:
- short pass/fail lines
- warnings separated from failures
- plain language about what must be fixed before launch

The goal is not diagnostic cleverness. The goal is helping an operator feel sure
about the next step.

## Implemented decisions

- Added a hosted preflight validator under `projects/learning-agent/src/preflight.py`
- Kept the validator focused on the current invite-only pilot boundary
- Distinguished hard failures from warnings so the operator can tell what blocks launch versus what deserves a closer look
- Updated the hosted README and checklist so preflight becomes part of the normal launch path

## Notes for later refinement

- When a real hosted environment is live, add one example preflight output for a healthy Railway or Render deployment.
- If the project moves to multi-replica or database-backed state, split the checks into pilot and beta/production profiles instead of overloading one validator.

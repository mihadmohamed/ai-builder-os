## Tools

Place project-local tooling here.

Examples:

- eval runners
- live eval runners
- replay capture tools
- migration or fixture utilities

Prefer project-local tools when the behavior is specific to one product.

Default expectation for new projects:

- `eval_runner.py` should become the deterministic validation entrypoint
- `live_eval_runner.py` is optional and should be added only when live external-system checks are useful

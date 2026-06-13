# Tools

Place project-local tooling here.

## Common Examples

- eval runners
- live eval runners
- replay capture tools
- migration or fixture utilities

## Guidance

- prefer project-local tools when the behavior is specific to one product
- `eval_runner.py` should usually become the deterministic validation entrypoint
- `live_eval_runner.py` is optional and should be added only when live external-system checks are genuinely useful

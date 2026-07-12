# Electrical Services Website v1

Use this template to create a new AI Builder OS project under `projects/electrical-services-website/`.

## Included Structure

- `product/requirements.md` for public-safe product intent and requirement state
- `product/tasks.md` for concrete execution tracking
- `product/ui-runtime.json` for the default UI runtime selection
- `memory.md` for durable project decisions and learnings
- `rules.md` for project-specific operating constraints
- `src/` for application code
- `evals/` for deterministic eval inputs, expected outputs, and replay fixtures
- `tools/` for project-local tooling such as eval runners
- `tests/` for unit, smoke, or manual UX checks
- `data/` for local runtime data

## How To Use

1. Copy this directory into `projects/electrical-services-website/`
2. Replace placeholder text with project-specific content
3. Define initial requirements in `product/requirements.md`
4. Define project rules in `rules.md`
5. Add product code under `src/`
6. Add eval fixtures before relying on automated validation
7. Implement the project-local deterministic eval runner in `tools/eval_runner.py`

## Validation Defaults

- start with deterministic validation first
- treat replay-backed or fixture-backed evals as the default development path
- add live validation only when the project genuinely depends on external systems or hosted models
- keep validation tooling project-local when the validation logic is product-specific

## Writing Boundaries

- Keep project-specific logic inside the project directory
- Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as the durable project source of truth
- Keep planning notes, candid sequencing notes, and sensitive local notes in an ignored `private/` directory rather than public tracked product files

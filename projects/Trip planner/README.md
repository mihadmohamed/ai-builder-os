# Personal Trip Planner

Experimental sandbox project for exploring family trip planning inside the AI Builder OS workspace.

## Current State

- This project remains in the shared workspace as an experimental sandbox rather than a polished production app.
- It has a real first requirement, working project structure, and passing local validation.
- Some surrounding docs still serve as a lightweight exploration frame rather than a fully mature product handbook.

## How To Work In It

1. Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as the local source of truth.
2. Keep changes scoped to the trip-planning product rather than OS-wide concerns unless the work clearly crosses project boundaries.
3. Run the project-local eval runner before closing meaningful changes.

## Validation Defaults

- start with deterministic validation first
- treat replay-backed or fixture-backed evals as the default development path
- add live validation only when the project genuinely depends on external systems or hosted models
- keep validation tooling project-local when the validation logic is product-specific

## Notes

- Keep project-specific logic inside the project directory
- Prefer project-local tooling over shared root scripts when the behavior is product-specific
- Treat `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` as the project source of truth

# Source Directory

Place project application code here.

## Suggested Contents

- core application modules
- schemas or data contracts
- storage layer
- UI and/or API entrypoints
- prompt or extraction logic if relevant

## Guidance

- Keep runtime data out of `src/`
- Keep public-facing behavior aligned with `product/requirements.md` and `rules.md`
- Keep project-local utilities or scripts in `tools/` rather than mixing them into application modules without a good reason

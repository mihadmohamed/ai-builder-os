# Data Directory

`data/` holds local operational state for the OS Control Panel.

This directory supports the control panel's runtime workflow, but it is **not** the canonical product source of truth.

## What Belongs Here

The control panel may create or update local files here for workflow and inspection features such as:

- `agent_threads.json`
  - active and archived PM / Experience Designer / UI Designer thread state
- `approvals.json`
  - approval requests for draft-to-artifact transitions
- `implementation_runs.json`
  - background requirement-implementation run records
- `quality_reviews.json`
  - deterministic validation review results
- `manual_verifications.json`
  - requirement-level manual verification checks and outcomes
- `implementation_logs/`
  - local implementation-run logs

Project-specific PM clarifications live in each project's own `data/pm_clarifications.json` rather than in this shared control-panel directory.

## What Does Not Belong Here

Do not treat `data/` as the product backlog or durable product intent.

Use these files as the real product source of truth instead:

- `product/requirements.md`
- `product/tasks.md`
- `memory.md`
- `rules.md`

## Source-of-Truth Boundary

- `data/` = local operational state for the control panel
- `product/requirements.md` and `product/tasks.md` = durable product work
- `memory.md` and `rules.md` = durable project decisions and operating constraints

If the UI and the files disagree, the durable product files win.

## Repo Hygiene

- Keep noisy runtime residue, logs, uploads, and other machine-local artifacts out of public-facing documentation unless they are intentionally being used as examples.
- Review tracked files in this directory deliberately before public publication.
- Keep generated operational artifacts out of `src/`.

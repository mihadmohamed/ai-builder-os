# AI Builder OS Publication Checklist

Use this checklist before publishing the workspace as a public GitHub showcase or before doing a meaningful public refresh.

## Repo Story

- Confirm the root `README.md` explains:
  - what AI Builder OS is
  - what the control panel is
  - what the example projects demonstrate
  - how to run at least one meaningful surface locally
- Confirm project READMEs still match the implementation reality.
- Confirm the public story is honest about what is local-first, what depends on OpenAI, and what is still evolving.

## Public-Safe State

- Review tracked files under `projects/*/data/`.
- Remove or replace runtime residue that adds noise without public value.
- Confirm gitignored runtime artifacts stay ignored:
  - uploaded images
  - implementation logs
  - local `.env` files
- Confirm no secrets, tokens, or credentials are committed.

## Product Truth Boundaries

- Confirm every project still treats these as durable product truth:
  - `product/requirements.md`
  - `product/tasks.md`
  - `memory.md`
  - `rules.md`
- Confirm docs explain that `data/` is operational state, not the canonical backlog.

## Demo Readiness

- Confirm the main control panel still runs locally.
- Confirm at least one smaller example project still runs locally.
- Set the final public repo target for the showcase links:
  - `AI_BUILDER_OS_PUBLIC_REPO_URL`
- Decide which surface is the public demo:
  - control panel walkthrough only
  - separate showcase app
  - both

## Media

- Capture updated screenshots or short demo media for:
  - the root README or repo description
  - the control panel
  - any public showcase app
- Remove screenshots that no longer match the current UI.

## Setup Quality

- Confirm setup instructions are minimal and correct.
- Confirm the preferred `.venv` workflow is documented consistently.
- Confirm environment-variable requirements are explained clearly.

## Validation

- Run project structure validation:
  - `python tools/validate_project_structure.py`
- Run the OS Control Panel validation path:
  - `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- Run any other project-level validation you want represented publicly.

## Final Review

- Ask whether the repo feels like:
  - a coherent operating system workspace
  - a trustworthy engineering artifact
  - a strong public showcase

If not, tighten the narrative before publishing.

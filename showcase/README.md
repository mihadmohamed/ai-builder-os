# AI Builder OS Public Showcase

This directory contains the public-facing Streamlit showcase app for AI Builder OS.

It is intentionally different from `projects/os-control-panel/`:

- `projects/os-control-panel/` is the operator surface
- `showcase/app.py` is the public explanation and demo surface

## What This App Does

The showcase is meant to:

- explain what AI Builder OS is
- explain how the workflow works
- show what projects are in the workspace
- give a clear public first impression before someone dives into the operator control panel

## Run Locally

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run showcase/app.py
```

## Public Deployment

The intended public Streamlit entrypoint is:

- `showcase/app.py`

Project and repository links default to the public AI Builder OS repository. If you deploy this showcase from a different repository or fork, set `AI_BUILDER_OS_PUBLIC_REPO_URL` in the deployment environment so the links point at the correct public destination.

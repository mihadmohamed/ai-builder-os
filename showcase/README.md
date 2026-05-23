# AI Builder OS Public Showcase

This directory contains the public-facing Streamlit showcase app for AI Builder OS.

It is intentionally different from `projects/os-control-panel/`:

- `projects/os-control-panel/` is the operator surface
- `showcase/app.py` is the public explanation and demo surface

## Run Locally

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run showcase/app.py
```

## Intended Public Deployment

The intended public Streamlit entrypoint is:

- `showcase/app.py`

If the final public GitHub repository URL differs from the current workspace remote, set:

```bash
export AI_BUILDER_OS_PUBLIC_REPO_URL="https://github.com/<owner>/<repo>"
```

The project cards and repo links in the showcase will then point at that public repository.

The goal of this app is to:

- explain what AI Builder OS is
- explain how the workflow works
- show what projects are in the workspace
- give a clean public first impression before someone dives into the operator control panel

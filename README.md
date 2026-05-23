# AI Builder OS

AI Builder OS is a local-first product operating system for building software with distinct agent roles, structured product files, and a Streamlit control plane.

This repository is both:
- the shared operating model for the OS
- a multi-project workspace that demonstrates the OS in action

## What It Includes

### Shared agent operating model

- `agent/system.md` defines the global operating model
- `agent/workflow.md` defines role sequencing and workflow expectations
- `agent/roles/` defines the role-specific guidance for PM, Experience Designer, UI Designer, Architect, QA, Orchestrator, and related prompts

### Example projects

- `projects/os-control-panel/`
  - the operator-facing Streamlit control panel for AI Builder OS
- `projects/parentmate/`
  - a smaller product project that extracts school events and parent actions from emails
- `projects/Trip planner/`
  - an experimental sandbox project kept in the workspace for OS validation and iteration

### Project template and utilities

- `templates/project/`
  - reusable template for new AI Builder OS projects
- `tools/`
  - workspace-level helpers for project creation, validation, status, and workflow utilities

## How The OS Works

Each project keeps its own durable product files:

- `product/requirements.md`
- `product/tasks.md`
- `memory.md`
- `rules.md`

Those files act as the product source of truth.

The control panel and supporting workflow tools may also write local operational state such as:

- approvals
- agent-thread state
- sprint state
- implementation run state
- quality review state

That operational state is useful for running the OS, but it is not the same thing as durable product intent.

## Best First Things To Open

If you want to understand the repo quickly:

1. read `agent/system.md`
2. read `projects/os-control-panel/README.md`
3. run the control panel locally
4. inspect `projects/parentmate/` as a smaller product example

## Run The Main Control Panel

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run projects/os-control-panel/src/app.py
```

This launches the operator-facing control panel used to:

- create projects
- work with agents
- manage requirements
- inspect delivery state
- inspect quality state

## Run The Public Showcase

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run showcase/app.py
```

This launches the separate public-facing Streamlit showcase for AI Builder OS.

If the final public GitHub repository URL differs from the current workspace remote, set:

```bash
export AI_BUILDER_OS_PUBLIC_REPO_URL="https://github.com/<owner>/<repo>"
```

## Run A Smaller Example Project

ParentMate has its own Streamlit app:

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run projects/parentmate/src/app.py
```

## Useful Workspace Commands

List projects:

```bash
python tools/list_projects.py
```

Validate project structure:

```bash
python tools/validate_project_structure.py
```

Workspace status:

```bash
python tools/workspace_status.py
```

Project status:

```bash
python tools/project_status.py
```

## Create A New Project

```bash
python tools/create_project.py my-new-project
```

Use a slug-style project directory name:

- lowercase
- words separated by hyphens
- no spaces

Use `--display-name` or `--product-title` for the human-facing name.

## Validation

Each project owns its own validation path.

Examples:

- OS Control Panel:
  - `.venv/bin/python projects/os-control-panel/tools/eval_runner.py`
- ParentMate:
  - `.venv/bin/python projects/parentmate/tools/eval_runner.py`

## Public Repo Notes

This repository is being prepared as a public showcase of the OS.

Important boundaries:

- `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md` are the durable project narrative
- `data/` directories may contain local operational state from running the OS

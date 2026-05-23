# AI Builder OS

## Vision

AI Builder OS is an experimental operating model for AI-assisted product development.
As AI makes it possible for individuals to prototype and build software faster than ever, product development risks becoming faster but less structured, less collaborative and harder to reason about over time.

The AI Builder OS explores a different approach:
using structured workflows, durable product context and distinct perspectives across product, design, architecture, engineering and QA to create more reliable and understandable product development systems.

The goal is not autonomous software generation.
The goal is combining AI acceleration with product discipline, human judgment and cross-functional thinking.

## Core Principles

### 1. Durable Product Intent

Product context, decisions and requirements should persist beyond individual implementation sessions or agent interactions.
The system should preserve why decisions were made, not just what was built.

### 2. Structure Before Speed

Fast iteration without structure creates fragile systems.
Clear requirements, scoped tasks and defined workflows improve reliability and long-term maintainability.

### 3. Distinct Perspectives Improve Outcomes

Strong products emerge from multiple perspectives:
product, design, engineering, architecture and quality.
AI-assisted development should preserve and amplify those perspectives, not collapse them into a single workflow.

### 4. Human Judgment Remains Central

AI can accelerate execution and exploration, but humans remain responsible for prioritisation, trade-offs, product intent and final decisions.

### 5. Context Is A Product Asset

Shared context, historical decisions and workflow memory are essential for reliable product development.
Context should be structured, accessible and durable across the lifecycle of the product.

### 6. Iteration Over Perfection

The system is designed to evolve through experimentation, feedback and continuous refinement rather than rigid upfront design.

## How The Operating Model Works

AI Builder OS treats product development as a structured workflow made up of distinct perspectives and durable product context.

Rather than relying on a single AI interaction or isolated implementation session, projects are organised around:

- persistent product files
- role-based workflows
- explicit requirements and task structures
- iterative validation and feedback loops
- preserved historical context and decisions

Each role within the workflow contributes a different perspective to the product development process, helping improve clarity, quality and long-term maintainability.

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

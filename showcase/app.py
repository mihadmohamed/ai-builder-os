from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ShowcaseProject:
    name: str
    path: str
    status: str
    purpose: str
    highlight: str
    commands: tuple[str, ...]
    audience: str


@dataclass(frozen=True)
class WorkflowStage:
    title: str
    owner: str
    summary: str


def showcase_title() -> str:
    return "AI Builder OS"


def showcase_sections() -> tuple[str, ...]:
    return ("Overview", "Workflow", "Projects", "Try It")


def showcase_section_descriptions() -> dict[str, str]:
    return {
        "Overview": "What the OS is",
        "Workflow": "How work moves",
        "Projects": "What the workspace contains",
        "Try It": "How to run it",
    }


def showcase_projects() -> tuple[ShowcaseProject, ...]:
    return (
        ShowcaseProject(
            name="OS Control Panel",
            path="projects/os-control-panel/",
            status="Operator surface",
            purpose="Run the OS through agents, requirements, delivery, quality, and workflow state.",
            highlight="Shows the shared agent workflow as a local-first control plane.",
            commands=('PYTHONPATH="$PWD" .venv/bin/streamlit run projects/os-control-panel/src/app.py',),
            audience="Best if you want to inspect the operating system itself.",
        ),
        ShowcaseProject(
            name="ParentMate",
            path="projects/parentmate/",
            status="Working product example",
            purpose="Extract school events and parent actions from raw school emails.",
            highlight="Demonstrates a smaller project built inside the same OS model.",
            commands=(
                'PYTHONPATH="$PWD" .venv/bin/streamlit run projects/parentmate/src/app.py',
                '.venv/bin/python projects/parentmate/tools/eval_runner.py',
            ),
            audience="Best if you want a concrete product example built inside the OS.",
        ),
        ShowcaseProject(
            name="Personal Trip Planner",
            path="projects/Trip planner/",
            status="Experimental sandbox",
            purpose="Validate how the OS handles a different product domain and evolving requirements.",
            highlight="Useful as a sandbox for testing the operating model across product shapes.",
            commands=(),
            audience="Best if you want to inspect a more experimental sandbox project.",
        ),
    )


def github_repo_url() -> str:
    return os.getenv("AI_BUILDER_OS_PUBLIC_REPO_URL", "https://github.com/mihadmohamed/ai-builder-os")


def github_project_url(project: ShowcaseProject) -> str:
    project_path = project.path.rstrip("/")
    return f"{github_repo_url()}/tree/main/{project_path}"


def workflow_stages() -> tuple[WorkflowStage, ...]:
    return (
        WorkflowStage(
            title="Shape the work",
            owner="Tom · PM",
            summary="Turn ideas into structured requirements through guided discovery and explicit approvals.",
        ),
        WorkflowStage(
            title="Stress-test the user experience",
            owner="Enzo · Experience Designer",
            summary="Turn usability issues, workflow friction, and feedback into structured product input.",
        ),
        WorkflowStage(
            title="Sharpen the interface",
            owner="Ricky · UI Designer",
            summary="Shape visual direction and review existing UI before broader design work turns into code.",
        ),
        WorkflowStage(
            title="Check structure",
            owner="Andy · Architect",
            summary="Review system boundaries, workflow drift, and structural risk before complexity spreads.",
        ),
        WorkflowStage(
            title="Decide what runs next",
            owner="Paul · Orchestrator",
            summary="Inspect workflow state, approvals, and blocked work so the next step stays explicit instead of guessed.",
        ),
        WorkflowStage(
            title="Implement the approved work",
            owner="Maciej · Engineer",
            summary="Move approved requirements through real implementation while keeping execution scoped and inspectable.",
        ),
        WorkflowStage(
            title="Validate confidence",
            owner="Richard · QA",
            summary="Run deterministic validation, review manual verification, and make signoff evidence visible.",
        ),
    )


def try_it_commands() -> dict[str, tuple[str, ...]]:
    return {
        "Run the control panel": (
            'PYTHONPATH="$PWD" .venv/bin/streamlit run projects/os-control-panel/src/app.py',
        ),
        "Run the public showcase": (
            'PYTHONPATH="$PWD" .venv/bin/streamlit run showcase/app.py',
        ),
        "Validate the workspace": (
            ".venv/bin/python projects/os-control-panel/tools/eval_runner.py",
            "python tools/validate_project_structure.py",
        ),
    }


def showcase_metrics() -> tuple[tuple[str, str], ...]:
    return (
        ("Projects", "3"),
        ("Core roles", "6"),
        ("Main mode", "Local-first"),
        ("Primary UI", "Streamlit"),
    )


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 2.5rem; max-width: 1180px;}
        div[data-testid="stMetric"] {background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.9rem 1rem; border-radius: 8px;}
        .showcase-panel {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem 1rem 0.9rem;
            height: 100%;
            background: #ffffff;
        }
        .showcase-panel-fill {
            height: 100%;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }
        .showcase-project-card {
            height: 420px;
            overflow: hidden;
        }
        .showcase-list {
            margin: 0.5rem 0 0 1rem;
            padding: 0;
            color: #4b5563;
        }
        .showcase-list li {
            margin: 0 0 0.45rem 0;
        }
        .showcase-kicker {
            color: #2563eb;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: 0.35rem;
        }
        .showcase-panel h3 {
            margin: 0 0 0.35rem 0;
            font-size: 1.1rem;
        }
        .showcase-muted {
            color: #6b7280;
            font-size: 0.94rem;
        }
        .showcase-callout {
            border-left: 4px solid #2563eb;
            background: #eff6ff;
            padding: 0.95rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-top: 0.6rem;
        }
        .showcase-step-badge {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-top: 0.15rem;
        }
        .showcase-step-copy {
            padding-bottom: 1rem;
            margin-bottom: 0.9rem;
            border-bottom: 1px solid #e5e7eb;
        }
        .showcase-step-title {font-weight: 700; margin-bottom: 0.22rem; font-size: 1.05rem;}
        .showcase-step-owner {color: #2563eb; font-size: 0.92rem; margin-bottom: 0.32rem;}
        .showcase-step-summary {color: #111827;}
        .showcase-code-note {
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    st.subheader("A local-first operating system for product work")
    st.markdown(
        """
        <div class="showcase-panel">
          <div class="showcase-kicker">What this is</div>
          <h3>Durable product truth, explicit workflow, and a local-first control plane</h3>
          <p>AI Builder OS separates product work into roles, durable product files, and explicit workflow state. The result is a system that can guide PM discovery, design review, implementation, validation, and signoff while ensuring different perspectives are incorporated into product work.</p>
          <p class="showcase-muted">The control panel is the operator surface. This showcase app is the public explanation layer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    metric_columns = st.columns(4, gap="small")
    for column, (label, value) in zip(metric_columns, showcase_metrics()):
        with column:
            st.metric(label, value)

    st.write("")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(
            """
            <div class="showcase-panel showcase-panel-fill">
              <div class="showcase-kicker">What the repo demonstrates</div>
              <h3>One operating model, multiple products</h3>
              <ul class="showcase-list">
                <li>A shared operating model across multiple product shapes</li>
                <li>Real project examples instead of a standalone framework shell</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="showcase-panel showcase-panel-fill">
              <div class="showcase-kicker">Public-repo stance</div>
              <h3>Clear, practical, and local-first</h3>
              <ul class="showcase-list">
                <li>Clear about what is implemented today</li>
                <li>Clear about what is local-first and still evolving</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_workflow() -> None:
    st.subheader("How work moves through the OS")
    st.caption("The roles are distinct on purpose. That helps the workflow incorporate different perspectives and stay inspectable.")
    stages = workflow_stages()
    for index, stage in enumerate(stages, start=1):
        badge_col, copy_col = st.columns((0.1, 0.9), gap="small")
        with badge_col:
            st.markdown(
                f'<div class="showcase-step-badge">{index}</div>',
                unsafe_allow_html=True,
            )
        with copy_col:
            st.markdown(
                f"""
                <div class="showcase-step-copy">
                  <div class="showcase-step-title">{stage.title}</div>
                  <div class="showcase-step-owner">{stage.owner}</div>
                  <div class="showcase-step-summary">{stage.summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.write("")
    st.info(
        "The operating model prefers explicit approvals, durable product files, and visible workflow outcomes over hidden agent magic."
    )


def render_projects() -> None:
    st.subheader("Projects in the workspace")
    st.caption("Pick the example that best matches what you want to understand, then jump to the GitHub source from here.")
    st.link_button("Open the full workspace repo", github_repo_url())
    st.write("")
    projects = showcase_projects()
    columns = st.columns(3, gap="large")
    for column, project in zip(columns, projects):
        with column:
            st.markdown(
                f"""
                <div class="showcase-panel showcase-panel-fill showcase-project-card">
                  <div class="showcase-kicker">{project.status}</div>
                  <h3>{project.name}</h3>
                  <p class="showcase-muted">{project.path}</p>
                  <p>{project.purpose}</p>
                  <p class="showcase-muted">{project.highlight}</p>
                  <p><strong>{project.audience}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                f"View {project.name} on GitHub",
                github_project_url(project),
                use_container_width=True,
            )


def render_try_it() -> None:
    st.subheader("How to try the OS")
    st.caption("The public showcase should lower the barrier to first contact, not make visitors reverse-engineer the repo.")
    left, right = st.columns((1.05, 0.95), gap="large")
    with left:
        for title, commands in try_it_commands().items():
            st.markdown(
                f"""
                <div class="showcase-panel">
                  <div class="showcase-kicker">{title}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for command in commands:
                st.code(command, language="bash")
    with right:
        st.markdown(
            """
            <div class="showcase-panel">
              <div class="showcase-kicker">Planned public deployment</div>
              <h3>Published on Streamlit</h3>
              <p>This showcase is designed to be the public Streamlit app for AI Builder OS. The operator control panel remains a deeper surface for running the OS directly.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button("View the GitHub repo", github_repo_url(), use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title=showcase_title(),
        page_icon="🧭",
        layout="wide",
    )
    _inject_styles()

    st.title(showcase_title())
    st.caption("Public Streamlit showcase for the local-first agent operating system and its example projects.")

    section = st.segmented_control(
        "Explore",
        options=showcase_sections(),
        default="Overview",
        help="Choose the part of the OS story you want to inspect.",
    )
    st.write("")

    if section == "Overview":
        render_overview()
    elif section == "Workflow":
        render_workflow()
    elif section == "Projects":
        render_projects()
    else:
        render_try_it()


if __name__ == "__main__":
    main()

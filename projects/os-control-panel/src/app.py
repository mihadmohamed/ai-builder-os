from __future__ import annotations

from datetime import datetime
import json
import re
from html import escape
from pathlib import Path

import streamlit as st

from workspace import (
    AgentMessage,
    AgentSummary,
    AgentThread,
    ROLE_CARDS,
    add_manual_verification_check,
    architect_review_snapshot,
    archive_agent_thread,
    approve_request,
    answer_pm_clarification,
    advance_all_active_sprints,
    active_pm_clarifications,
    active_requirement_clarifications,
    continue_sprint,
    continue_live_pm_project_thread,
    complete_sprint,
    create_project_from_reviewed_draft,
    create_project_from_ui,
    draft_experience_designer_thread,
    draft_live_pm_project_thread,
    draft_pm_requirement_discovery_thread,
    draft_ui_designer_thread,
    build_dynamic_reflection_plan,
    build_build_to_learn_pathway,
    LivePMDiscoveryError,
    LivePMProjectThread,
    RequirementRecord,
    active_implementation_run,
    active_agent_thread,
    agent_summary_by_name,
    delete_requirement,
    implementation_entry_allowed,
    implementation_progress_message,
    implementation_progress_percent,
    list_agent_threads,
    list_pm_clarifications,
    list_approvals,
    latest_requirement_implementation,
    learning_build_to_learn_enabled,
    learning_implementation_anchors,
    learning_reflection_enabled,
    learning_concept_history,
    learning_concept_hierarchy,
    learning_concept_view,
    learning_concept_detail_view,
    list_learning_concept_views,
    learning_concept_relationships,
    learning_concept_navigation_sections,
    personalized_learning_plan,
    list_learning_concept_recommendations,
    load_learning_agent_session,
    load_learning_profile,
    load_requirement_document,
    continue_learning_agent_session,
    pause_learning_agent_session,
    clear_learning_agent_session,
    request_learning_agent_clarification,
    request_learning_agent_implementation_walkthrough,
    save_private_build_to_learn_pathway,
    save_build_to_learn_outcome,
    save_learning_concept_management_update,
    save_learning_profile,
    load_sprint_plan,
    move_requirement,
    move_sprint_requirement,
    operations_dashboard_snapshot,
    orchestrator_recommendation,
    run_live_orchestrator_review,
    plan_sprint_requirement,
    project_preview,
    project_preview_running,
    recent_implementation_run_inspections,
    latest_quality_review,
    record_project_qa_review,
    run_project_qa_review,
    manual_verification_plan,
    manual_verification_summary,
    recommend_requirement,
    remove_manual_verification_check,
    remove_sprint_requirement,
    reply_to_experience_designer_thread,
    reply_to_pm_requirement_discovery_thread,
    reply_to_ui_designer_thread,
    reject_request,
    resolve_pm_clarification,
    request_experience_thread_approval,
    request_pm_requirement_thread_approval,
    request_ui_design_brief_approval,
    save_experience_thread_to_finding,
    save_pm_clarification,
    save_pm_requirement_thread_to_requirements,
    save_private_reflection_draft,
    start_learning_agent_session,
    start_experience_designer_thread,
    start_project_preview,
    start_live_pm_project_thread,
    start_pm_requirement_discovery_thread,
    start_sprint,
    start_requirement_implementation,
    start_ui_designer_thread,
    sprint_requirement_records,
    summarize_projects,
    update_requirement,
    update_manual_verification_check,
    workflow_inbox_items,
    workflow_timeline_events,
    workspace_totals,
)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


WORKSPACE_TITLE = "AI Product Operating System"
WORKSPACE_SUBTITLE = "Local-first control panel for AI Builder OS."
WORKSPACE_PROJECT_ROW_SIZE = 2
ACTIVE_REQUIREMENT_ROW_SIZE = 2
INBOX_CARD_ROW_SIZE = 2
ROLE_CARD_ROW_SIZE = 3
ROLE_CARD_ROW_GAP_REM = 1.0
PROJECT_SELECTION_STATE_KEY = "os-selected-project"
PROJECT_DETAIL_SECTION_STATE_KEY = "os-project-detail-section"
TOP_LEVEL_SECTION_STATE_KEY = "os-top-level-section"
PENDING_AGENT_FOCUS_STATE_KEY = "os-pending-agent-focus"
PENDING_PROJECT_OPEN_STATE_KEY = "os-pending-project-open"
PENDING_LEARNING_SECTION_STATE_KEY = "os-pending-learning-section"
GUIDED_VERIFICATION_STATE_KEY = "os-guided-verification-check"
REFLECTION_HELPER_STATE_KEY = "os-reflection-helper-state"
REFLECTION_HELPER_FEEDBACK_KEY = "os-reflection-helper-feedback"
BUILD_TO_LEARN_STATE_KEY = "os-build-to-learn-state"
BUILD_TO_LEARN_FEEDBACK_KEY = "os-build-to-learn-feedback"
BUILD_TO_LEARN_FOCUS_CONCEPT_STATE_KEY = "os-build-to-learn-focus-concept"
LEARNING_SECTION_STATE_KEY = "os-learning-section"
LEARNING_CONCEPT_SELECTION_STATE_KEY = "os-learning-selected-concept"
PENDING_LEARNING_CONCEPT_STATE_KEY = "os-pending-learning-concept"
LEARNING_MANAGER_FEEDBACK_KEY = "os-learning-manager-feedback"
LEARNING_PROFILE_FEEDBACK_KEY = "os-learning-profile-feedback"
LEARNING_PROFILE_EDITOR_OPEN_STATE_KEY = "os-learning-profile-editor-open"
BUILD_TO_LEARN_CAPTURE_STATE_KEY = "os-build-to-learn-capture-concept"
LEARNING_AGENT_FEEDBACK_KEY = "os-learning-agent-feedback"
LEARNING_AGENT_CLARIFY_MODE_KEY = "os-learning-agent-clarify-mode"
LEARNING_SECTION_LABELS = ("Profile", "Learning plan", "Learn next", "Builds")
LEARNING_PROFILE_BACKGROUND_OPTIONS = (
    "New to AI product systems",
    "Product leader with some AI experience",
    "Already building AI-assisted workflows",
    "Technical builder sharpening product judgment",
)
LEARNING_PROFILE_TECHNICAL_COMFORT_OPTIONS = (
    "Mostly product and workflow focused",
    "Comfortable reading architecture and tooling",
    "Comfortable implementing and debugging systems",
)
OS_UNDERSTANDING_LEVEL_OPTIONS = (
    "New to AI Builder OS",
    "Know the basics of AI Builder OS",
    "Comfortable operating AI Builder OS",
)
LEARNING_PROFILE_TRAJECTORY_OPTIONS = (
    "Learn the foundations of AI Builder OS",
    "Build confidence explaining AI-agent concepts",
    "Design stronger agent workflows and evals",
    "Use the OS fluently in real product work",
)
LEARNING_PROFILE_CREDIBILITY_GOAL_OPTIONS = (
    "Explain concepts simply to others",
    "Make better product and architecture decisions",
    "Lead AI work with more confidence",
)
LEARNING_PROFILE_STYLE_OPTIONS = (
    "Big-picture framing first",
    "Concrete examples first",
    "Implementation walkthroughs",
    "Step-by-step coaching",
)
LEARNING_PROFILE_POSTURE_OPTIONS = (
    "Exploring the space",
    "Actively learning",
    "Applying in real work",
    "Refreshing and refining",
)
TOP_LEVEL_PROJECTS_LABEL = "Open Project"
TOP_LEVEL_CREATE_PROJECT_LABEL = "Create Project"
TOP_LEVEL_TAB_LABELS = (
    "Workspace",
    "Operations",
    "Learning",
    TOP_LEVEL_PROJECTS_LABEL,
    "Inbox",
    TOP_LEVEL_CREATE_PROJECT_LABEL,
)
TOP_LEVEL_NAVIGATION_CONTROL_KIND = "segmented_control"
TOP_LEVEL_NAVIGATION_DESCRIPTIONS = {
    "Workspace": "Overview",
    "Operations": "Agent and workflow health",
    "Learning": "Concept growth",
    TOP_LEVEL_PROJECTS_LABEL: "Project work",
    "Inbox": "Waiting items",
    TOP_LEVEL_CREATE_PROJECT_LABEL: "New setup",
}
TOP_LEVEL_NAVIGATION_LEVEL_LABEL = "Workspace-level navigation"
TOP_LEVEL_NAVIGATION_SCOPE_DESCRIPTION = (
    "Move between workspace overview, operations, the learning layer, project selection, workflow inbox, and project creation."
)
LEGACY_TOP_LEVEL_SECTION_LABELS = {
    "Projects": TOP_LEVEL_PROJECTS_LABEL,
    "New Project": TOP_LEVEL_CREATE_PROJECT_LABEL,
}
PROJECT_DETAIL_TAB_LABELS = ("Agents", "Requirements", "Delivery", "Quality")
TOP_LEVEL_NAVIGATION_LABEL = "Main navigation"
PROJECT_DETAIL_NAVIGATION_LABEL = "Project sections"
PROJECT_DETAIL_NAVIGATION_ORIENTATION = "vertical"
PROJECT_DETAIL_NAVIGATION_LEVEL_LABEL = "Project-level navigation"
ROLE_CARD_STYLE = """
<style>
.os-role-card {
    min-height: 168px;
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 0.2rem 0 0.65rem;
}
.os-role-card-name {
    width: fit-content;
    padding: 0.08rem 0.38rem;
    border: 1px solid rgba(49, 51, 63, 0.16);
    border-radius: 0.35rem;
    background: rgba(49, 51, 63, 0.05);
    color: rgba(49, 51, 63, 0.76);
    font-size: 0.72rem;
    font-weight: 650;
    margin-bottom: 0.55rem;
}
.os-role-card-title {
    font-size: 1.03rem;
    font-weight: 600;
    margin-bottom: 0.45rem;
}
.os-role-card-summary {
    font-size: 0.95rem;
    line-height: 1.45;
    flex: 1;
    color: rgba(49, 51, 63, 0.82);
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.os-role-card-action-spacer {
    height: 0.2rem;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-role-card) {
    background: rgba(49, 51, 63, 0.025);
    box-shadow: 0 1px 2px rgba(49, 51, 63, 0.05);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-role-card) .stButton > button {
    min-height: 2.5rem;
    border-radius: 0.45rem;
    font-weight: 650;
}
</style>
"""

PRIORITY_OPTIONS = ["", "HIGH", "MEDIUM", "LOW"]
EFFORT_OPTIONS = ["", "S", "M", "L"]
STATUS_OPTIONS = ["NEW", "IN_PROGRESS", "DONE", "BACKLOG"]
REQUIREMENT_GROUPS = (
    (
        "Priority focus",
        "In-progress, new, and high-priority requirements that deserve attention first.",
    ),
    (
        "Planned backlog",
        "Backlog requirements available for sprint planning or later prioritisation.",
    ),
    (
        "Other unfinished requirements",
        "Lower-signal unfinished work kept visible without crowding the priority area.",
    ),
)
REQUIREMENTS_PANEL_SECTION_ORDER = (
    "summary",
    "alerts",
    "sprint_planning",
    "recommendation",
    "structured_requirements",
    "completed_requirements",
)
AGENT_OPTIONS = ["PM", "Experience Designer", "UI Designer", "Architect", "Orchestrator", "QA"]
PM_MODE_OPTIONS = ["Requirement Discovery"]
EXPERIENCE_DESIGNER_MODE_OPTIONS = ["Feedback Synthesis", "Usability Review"]
UI_DESIGNER_MODE_OPTIONS = ["Design Direction", "UI Review"]
ARCHITECT_MODE_OPTIONS = ["Architecture Review"]
QA_MODE_OPTIONS = ["Validation Review"]
ORCHESTRATOR_MODE_OPTIONS = ["Next Step", "Workflow Review"]
AGENT_SELECTION_HELP = {
    "PM": "Shape product requirements through live PM discovery and draft review.",
    "Experience Designer": "Turn UX signals into structured findings or usability reviews.",
    "UI Designer": "Shape interface direction and critique existing UI with a Streamlit-aware lens.",
    "Architect": "Inspect structure, workflow boundaries, and scaling risks before engineering keeps moving.",
    "QA": "Run project validation and inspect the current quality signal without changing implementation.",
    "Orchestrator": "Inspect workflow state and decide what should run next.",
}
MODE_DESCRIPTIONS = {
    "PM": {
        "Requirement Discovery": "Best when you want to shape a new requirement from an idea through clarifying questions and a draft artifact.",
    },
    "Experience Designer": {
        "Feedback Synthesis": "Use when the main input is user pain, workflow friction, or feedback that should become a structured finding.",
        "Usability Review": "Use when the main job is to assess clarity, hierarchy, scanability, and friction in an existing surface or flow.",
    },
    "UI Designer": {
        "Design Direction": "Use when the target state is not settled yet and you want stronger visual, layout, and interaction direction before implementation.",
        "UI Review": "Use when a surface already exists and you want concrete critique of hierarchy, spacing, consistency, and polish.",
    },
    "Architect": {
        "Architecture Review": "Use when the main question is whether the current project state or planned work introduces structural risk, workflow drift, or unnecessary complexity.",
    },
    "QA": {
        "Validation Review": "Use when you want to run the project validation path, inspect failures, and get a grounded reliability read before calling work done.",
    },
    "Orchestrator": {
        "Next Step": "Show the current next role, next action, and why the workflow should move that way.",
        "Workflow Review": "Use the same control-layer recommendation with a broader workflow framing while staying code-driven and non-chatty.",
    },
}

SECTION_STYLE = """
<style>
.os-project-card-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.os-project-card-anchor {
    height: 0;
    margin: 0;
}
.os-project-card-kicker {
    display: inline-block;
    padding: 0.1rem 0.42rem;
    border: 1px solid rgba(49, 51, 63, 0.14);
    border-radius: 0.35rem;
    background: rgba(49, 51, 63, 0.04);
    color: rgba(49, 51, 63, 0.74);
    font-size: 0.74rem;
    font-weight: 650;
    margin-bottom: 0.45rem;
}
.os-project-card-kicker-attention {
    border-color: rgba(180, 83, 9, 0.28);
    background: rgba(245, 158, 11, 0.1);
    color: rgb(120, 53, 15);
}
.os-project-card-kicker-ready {
    border-color: rgba(21, 128, 61, 0.22);
    background: rgba(34, 197, 94, 0.08);
    color: rgb(22, 101, 52);
}
.os-project-card-next {
    margin-top: 0.75rem;
    padding-top: 0.65rem;
    border-top: 1px solid rgba(49, 51, 63, 0.09);
}
.os-project-card-next-label {
    color: rgba(49, 51, 63, 0.68);
    font-size: 0.78rem;
    font-weight: 650;
    margin-bottom: 0.12rem;
}
.os-project-card-next-value {
    color: rgba(49, 51, 63, 0.84);
    font-size: 0.9rem;
    line-height: 1.35;
}
.os-card-meta {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.9rem;
}
.os-signal-label {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.8rem;
    margin-bottom: 0.15rem;
}
.os-signal-value {
    font-weight: 600;
    font-size: 0.98rem;
}
.os-section-kicker {
    text-transform: uppercase;
    letter-spacing: 0;
    font-size: 0.78rem;
    color: rgba(49, 51, 63, 0.7);
    margin-bottom: 0.4rem;
}
.os-main-navigation-anchor {
    margin-top: 0.35rem;
}
.os-main-navigation-shell {
    padding: 0.7rem 0.85rem 0.6rem;
    margin: 0.75rem 0 1.2rem;
    border: 1px solid rgba(49, 51, 63, 0.12);
    border-radius: 0.55rem;
    background: rgba(49, 51, 63, 0.025);
}
.os-main-navigation-heading {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    color: rgba(49, 51, 63, 0.72);
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}
.os-main-navigation-scope {
    color: rgba(49, 51, 63, 0.74);
    font-size: 0.88rem;
    line-height: 1.35;
    margin-bottom: 0.55rem;
}
.os-main-navigation-context {
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
    margin-bottom: 0.48rem;
}
.os-main-navigation-context span {
    display: inline-block;
    padding: 0.1rem 0.42rem;
    border: 1px solid rgba(49, 51, 63, 0.12);
    border-radius: 0.35rem;
    background: rgba(255, 255, 255, 0.72);
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.76rem;
    font-weight: 600;
}
.os-workflow-card-cue {
    display: inline-block;
    padding: 0.12rem 0.42rem;
    border-radius: 0.4rem;
    border: 1px solid rgba(49, 51, 63, 0.18);
    background: rgba(49, 51, 63, 0.04);
    color: rgba(49, 51, 63, 0.78);
    font-size: 0.76rem;
    font-weight: 650;
    letter-spacing: 0;
    margin-bottom: 0.38rem;
}
.os-workflow-card-cue-action,
.os-workflow-card-cue-waiting {
    border-color: rgba(180, 83, 9, 0.32);
    background: rgba(245, 158, 11, 0.11);
    color: rgb(120, 53, 15);
}
.os-workflow-card-cue-blocked {
    border-color: rgba(185, 28, 28, 0.28);
    background: rgba(239, 68, 68, 0.1);
    color: rgb(127, 29, 29);
}
.os-workflow-card-cue-routed {
    border-color: rgba(37, 99, 235, 0.24);
    background: rgba(59, 130, 246, 0.09);
    color: rgb(30, 64, 175);
}
.os-workflow-card-cue-running {
    border-color: rgba(21, 128, 61, 0.24);
    background: rgba(34, 197, 94, 0.09);
    color: rgb(22, 101, 52);
}
.os-section-heading {
    font-size: 1.05rem;
    font-weight: 650;
    margin-top: 1.1rem;
    margin-bottom: 0.1rem;
}
.os-section-caption {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.9rem;
    line-height: 1.35;
    margin-bottom: 0.65rem;
}
.os-workflow-card-title {
    font-size: 1rem;
    font-weight: 650;
    margin-bottom: 0.25rem;
}
.os-workflow-card-anchor {
    height: 0;
    margin: 0;
}
.os-inbox-section-label {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0.35rem 0 0.25rem;
    color: rgba(49, 51, 63, 0.74);
    font-size: 0.84rem;
    font-weight: 650;
}
.os-inbox-section-label-count {
    border: 1px solid rgba(49, 51, 63, 0.14);
    border-radius: 0.4rem;
    padding: 0.02rem 0.35rem;
    background: rgba(49, 51, 63, 0.035);
    color: rgba(49, 51, 63, 0.68);
    font-size: 0.76rem;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-workflow-card-anchor) {
    border-color: rgba(49, 51, 63, 0.1);
    background: rgba(255, 255, 255, 0.56);
    box-shadow: none;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-workflow-card-anchor) [data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-project-card-anchor) {
    background: rgba(255, 255, 255, 0.68);
    border-color: rgba(49, 51, 63, 0.11);
    box-shadow: 0 1px 2px rgba(49, 51, 63, 0.04);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-learning-plan-card-anchor) {
    height: 100%;
    background: rgba(255, 255, 255, 0.68);
    border-color: rgba(49, 51, 63, 0.11);
    box-shadow: 0 1px 2px rgba(49, 51, 63, 0.04);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-learning-plan-card-anchor) [data-testid="stVerticalBlock"] {
    height: 100%;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.os-project-card-anchor) .stButton > button {
    min-height: 2.45rem;
    border-radius: 0.45rem;
    font-weight: 650;
}
.os-project-nav-heading {
    font-weight: 600;
    margin-top: 0.35rem;
    margin-bottom: 0.2rem;
}
.os-project-navigation-shell {
    padding: 0.72rem 0.78rem;
    border: 1px solid rgba(49, 51, 63, 0.13);
    border-radius: 0.5rem;
    background: rgba(49, 51, 63, 0.018);
    border-left: 0.22rem solid rgba(37, 99, 235, 0.34);
    margin-bottom: 0.75rem;
}
.os-project-nav-level {
    text-transform: uppercase;
    letter-spacing: 0;
    color: rgba(30, 64, 175, 0.82);
    font-size: 0.74rem;
    font-weight: 700;
    margin-bottom: 0.22rem;
}
.os-project-nav-caption {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.88rem;
    line-height: 1.35;
    margin-bottom: 0;
}
.os-learning-plan-card-anchor {
    height: 0;
    margin: 0;
}
.os-learning-plan-summary {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) repeat(2, minmax(0, 1fr));
    gap: 1.4rem;
    align-items: end;
    margin: 0.05rem 0 0.7rem;
}
.os-learning-plan-summary-item {
    min-width: 0;
}
.os-learning-plan-summary-label {
    color: rgba(49, 51, 63, 0.78);
    font-size: 0.84rem;
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 0.3rem;
}
.os-learning-plan-summary-family {
    color: rgba(31, 41, 55, 0.95);
    font-size: 1.55rem;
    font-weight: 650;
    line-height: 1.12;
    letter-spacing: 0;
    text-wrap: balance;
}
.os-learning-plan-summary-value {
    color: rgba(31, 41, 55, 0.95);
    font-size: 1.8rem;
    font-weight: 600;
    line-height: 1.02;
    letter-spacing: 0;
}
.os-learning-plan-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    align-items: stretch;
    margin-bottom: 1rem;
}
.os-learning-plan-card {
    height: 100%;
    padding: 0.95rem 1rem 1rem;
    border: 1px solid rgba(49, 51, 63, 0.11);
    border-radius: 0.55rem;
    background: rgba(255, 255, 255, 0.68);
    box-shadow: 0 1px 2px rgba(49, 51, 63, 0.04);
}
.os-learning-plan-card-title {
    color: rgba(49, 51, 63, 0.96);
    font-size: 1rem;
    font-weight: 650;
    margin-bottom: 0.55rem;
}
.os-learning-plan-card-summary {
    color: rgba(49, 51, 63, 0.68);
    font-size: 0.84rem;
    line-height: 1.45;
    margin-bottom: 0.85rem;
}
.os-learning-plan-steps {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
}
.os-learning-plan-step {
    font-size: 0.95rem;
    line-height: 1.35;
}
.os-learning-plan-step-label {
    font-weight: 600;
}
.os-learning-plan-legend {
    color: rgba(75, 85, 99, 0.9);
    font-size: 0.84rem;
    line-height: 1.4;
    margin: 0.45rem 0 0.7rem;
}
.os-learning-plan-legend span {
    font-weight: 600;
}
@media (max-width: 1200px) {
    .os-learning-plan-summary {
        grid-template-columns: 1fr;
        gap: 0.85rem;
        align-items: start;
    }
    .os-learning-plan-summary-family {
        font-size: 1.35rem;
    }
    .os-learning-plan-summary-value {
        font-size: 1.55rem;
    }
    .os-learning-plan-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
@media (max-width: 760px) {
    .os-learning-plan-grid {
        grid-template-columns: 1fr;
    }
}
.os-learning-nav-anchor {
    height: 0;
    margin: 0;
}
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    gap: 0.35rem;
    overflow: visible;
}
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] > * {
    background: rgba(237, 245, 255, 0.96) !important;
    border: 1px solid rgba(47, 111, 237, 0.18) !important;
    border-radius: 0.55rem !important;
    box-shadow: none !important;
}
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] > *:has(input:checked),
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] [aria-checked="true"],
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] [data-selected="true"],
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] [aria-selected="true"],
div[data-testid="stVerticalBlock"]:has(.os-learning-nav-anchor) .stSegmentedControl [role="radiogroup"] button[aria-pressed="true"] {
    background: rgba(219, 234, 254, 1) !important;
    border-color: rgba(59, 130, 246, 0.42) !important;
}
.os-project-control-summary {
    padding: 0.15rem 0 0.35rem;
}
.os-project-control-title {
    color: rgba(49, 51, 63, 0.92);
    font-size: 1.12rem;
    font-weight: 650;
    margin-bottom: 0.22rem;
}
.os-project-control-meta {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.88rem;
    line-height: 1.35;
}
.os-agent-workspace-caption {
    color: rgba(49, 51, 63, 0.72);
    font-size: 0.9rem;
    line-height: 1.35;
    margin: 0.05rem 0 0.85rem;
}
.os-agent-selection-grid {
    margin-bottom: 0.65rem;
}
.os-agent-selection-card {
    min-height: 136px;
}
.os-agent-selection-card-selected {
    border-left: 0.22rem solid rgba(37, 99, 235, 0.48);
    padding-left: 0.55rem;
}
.os-agent-selection-name {
    color: rgba(49, 51, 63, 0.66);
    font-size: 0.76rem;
    font-weight: 650;
    margin-bottom: 0.22rem;
    text-transform: uppercase;
    letter-spacing: 0;
}
.os-agent-selection-title {
    color: rgba(49, 51, 63, 0.9);
    font-size: 1.0rem;
    font-weight: 650;
    margin-bottom: 0.32rem;
}
.os-agent-selection-help {
    color: rgba(49, 51, 63, 0.78);
    font-size: 0.9rem;
    line-height: 1.35;
}
.os-agent-selection-state {
    display: inline-block;
    margin-top: 0.5rem;
    padding: 0.08rem 0.38rem;
    border: 1px solid rgba(37, 99, 235, 0.22);
    border-radius: 0.35rem;
    background: rgba(59, 130, 246, 0.08);
    color: rgb(30, 64, 175);
    font-size: 0.74rem;
    font-weight: 650;
}
.os-selected-agent-shell {
    padding: 0.72rem 0.82rem;
    margin: 0.25rem 0 0.8rem;
    border: 1px solid rgba(49, 51, 63, 0.12);
    border-radius: 0.5rem;
    background: rgba(49, 51, 63, 0.02);
}
.os-selected-agent-kicker {
    color: rgba(30, 64, 175, 0.82);
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
    margin-bottom: 0.2rem;
}
.os-selected-agent-title {
    color: rgba(49, 51, 63, 0.9);
    font-size: 1rem;
    font-weight: 650;
    margin-bottom: 0.18rem;
}
.os-selected-agent-summary {
    color: rgba(49, 51, 63, 0.76);
    font-size: 0.9rem;
    line-height: 1.35;
}
.os-mode-selection-heading {
    font-weight: 650;
    margin-bottom: 0.35rem;
}
.os-mode-option-card {
    min-height: 118px;
}
.os-mode-option-title {
    font-size: 0.96rem;
    font-weight: 650;
    margin-bottom: 0.32rem;
}
.os-mode-option-description {
    color: rgba(49, 51, 63, 0.76);
    font-size: 0.9rem;
    line-height: 1.35;
}
.os-mode-single-summary {
    padding: 0.6rem 0.7rem;
    border: 1px solid rgba(49, 51, 63, 0.1);
    border-radius: 0.45rem;
    background: rgba(49, 51, 63, 0.018);
    color: rgba(49, 51, 63, 0.76);
    font-size: 0.9rem;
    line-height: 1.35;
    margin-bottom: 0.85rem;
}
</style>
"""


def _new_project_live_thread_key() -> str:
    return "os-new-project-live-thread"


def _load_new_project_live_thread() -> LivePMProjectThread | None:
    raw_thread = st.session_state.get(_new_project_live_thread_key())
    if not isinstance(raw_thread, dict):
        return None
    raw_messages = raw_thread.get("messages", [])
    messages = tuple(
        AgentMessage(
            role=str(message.get("role", "")),
            content=str(message.get("content", "")),
            created_at=str(message.get("created_at", "")),
            attachments=tuple(str(path) for path in message.get("attachments", []) if str(path).strip()),
        )
        for message in raw_messages
        if isinstance(message, dict)
    )
    return LivePMProjectThread(
        thread_id=str(raw_thread["thread_id"]),
        project_name=str(raw_thread["project_name"]),
        display_name=str(raw_thread["display_name"]),
        planner_type=str(raw_thread.get("planner_type", "live")),
        status=str(raw_thread["status"]),
        messages=messages,
        draft_title=str(raw_thread.get("draft_title", "")),
        draft_requirement=str(raw_thread.get("draft_requirement", "")),
        created_at=str(raw_thread.get("created_at", "")),
        updated_at=str(raw_thread.get("updated_at", "")),
    )


def _save_new_project_live_thread(thread: LivePMProjectThread | None) -> None:
    if thread is None:
        st.session_state.pop(_new_project_live_thread_key(), None)
        return
    st.session_state[_new_project_live_thread_key()] = {
        "thread_id": thread.thread_id,
        "project_name": thread.project_name,
        "display_name": thread.display_name,
        "planner_type": thread.planner_type,
        "status": thread.status,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
                "attachments": list(message.attachments),
            }
            for message in thread.messages
        ],
        "draft_title": thread.draft_title,
        "draft_requirement": thread.draft_requirement,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
    }


def workspace_heading() -> str:
    return WORKSPACE_TITLE


def workspace_subtitle() -> str:
    return WORKSPACE_SUBTITLE


def _uploaded_image_payloads(files) -> tuple[tuple[str, bytes], ...]:
    payloads: list[tuple[str, bytes]] = []
    for file in files or ():
        name = getattr(file, "name", "") or "image.png"
        payloads.append((str(name), file.getvalue()))
    return tuple(payloads)


def _render_message_attachments(message: AgentMessage) -> None:
    image_paths = [path for path in message.attachments if Path(path).exists()]
    if image_paths:
        st.image(image_paths, width=220)


def project_card_signal_text(project) -> tuple[str, str]:
    new_requirement_count = len(project.new_requirements)
    pending_task_count = len(project.pending_tasks)
    return (
        f"New requirements: {new_requirement_count}",
        f"Pending tasks: {pending_task_count}",
    )


def open_project_page_caption() -> str:
    return "Choose a project, compare its current work signals, then open the workspace you need."


def project_card_status(project) -> tuple[str, str]:
    if project.missing_paths or not project.structure_ok:
        return ("Needs attention", "attention")
    if project.new_requirements or project.pending_tasks:
        return ("Work queued", "attention")
    return ("Ready", "ready")


def project_card_next_work(project) -> tuple[str, str]:
    if project.new_requirements:
        requirement = project.new_requirements[0]
        return ("Next requirement", f"{requirement.id} — {requirement.title}")
    if project.pending_tasks:
        task = project.pending_tasks[0]
        return ("Next task", f"{task.id} — {task.title}")
    if project.missing_paths:
        return ("Structure", "Review missing project files before planning more work.")
    return ("Current state", "No queued requirement or task needs attention.")


def project_card_anchor_markup() -> str:
    return "<div class='os-project-card-anchor'></div>"


def project_card_status_markup(project) -> str:
    label, kind = project_card_status(project)
    return f"<div class='os-project-card-kicker os-project-card-kicker-{kind}'>{escape(label)}</div>"


def project_card_next_work_markup(project) -> str:
    label, value = project_card_next_work(project)
    return (
        "<div class='os-project-card-next'>"
        f"<div class='os-project-card-next-label'>{escape(label)}</div>"
        f"<div class='os-project-card-next-value'>{escape(value)}</div>"
        "</div>"
    )


def project_open_button_label(project) -> str:
    return f"Open {project.name}"


def project_preview_button_label(project_name: str) -> str:
    return "Open preview"


def project_control_heading() -> str:
    return "Project"


def project_control_path_metadata(project) -> str:
    try:
        relative_path = project.path.relative_to(Path.cwd())
    except ValueError:
        relative_path = project.path
    return f"Project path: {relative_path}"


def project_control_summary_markup(project_name: str, path_metadata: str) -> str:
    return (
        "<div class='os-project-control-summary'>"
        f"<div class='os-project-control-title'>{escape(project_name)}</div>"
        f"<div class='os-project-control-meta'>{escape(path_metadata)}</div>"
        "</div>"
    )


def project_preview_summary_text(preview) -> str:
    if preview.available:
        return f"Preview available · {preview.runtime.title()}"
    return preview.status_text


def project_preview_status_text(preview) -> str:
    return project_preview_summary_text(preview)


def top_level_tab_labels() -> tuple[str, ...]:
    return TOP_LEVEL_TAB_LABELS


def top_level_navigation_control_kind() -> str:
    return TOP_LEVEL_NAVIGATION_CONTROL_KIND


def top_level_navigation_descriptions() -> dict[str, str]:
    return dict(TOP_LEVEL_NAVIGATION_DESCRIPTIONS)


def main_navigation_context_label(label: str) -> str:
    description = TOP_LEVEL_NAVIGATION_DESCRIPTIONS.get(label, "")
    if not description:
        return label
    return f"{label}: {description}"


def top_level_navigation_level_label() -> str:
    return TOP_LEVEL_NAVIGATION_LEVEL_LABEL


def top_level_navigation_scope_description() -> str:
    return TOP_LEVEL_NAVIGATION_SCOPE_DESCRIPTION


def learning_section_labels() -> tuple[str, ...]:
    if not learning_build_to_learn_enabled():
        return ("Profile", "Learning plan", "Learn next")
    if learning_build_to_learn_enabled():
        return LEARNING_SECTION_LABELS
    return tuple(label for label in LEARNING_SECTION_LABELS if label != "Builds")


def learning_next_surface(
    *,
    has_active_session: bool,
) -> str:
    if has_active_session:
        return "session"
    return "recommendations"


def normalize_top_level_section(section: str) -> str:
    normalized = LEGACY_TOP_LEVEL_SECTION_LABELS.get(section, section)
    if normalized in TOP_LEVEL_TAB_LABELS:
        return normalized
    return TOP_LEVEL_TAB_LABELS[0]


def project_detail_tab_labels() -> tuple[str, ...]:
    return PROJECT_DETAIL_TAB_LABELS


def top_level_navigation_label() -> str:
    return TOP_LEVEL_NAVIGATION_LABEL


def project_detail_navigation_label() -> str:
    return PROJECT_DETAIL_NAVIGATION_LABEL


def project_detail_navigation_orientation() -> str:
    return PROJECT_DETAIL_NAVIGATION_ORIENTATION


def project_detail_navigation_level_label() -> str:
    return PROJECT_DETAIL_NAVIGATION_LEVEL_LABEL


def project_detail_navigation_scope_description(project_name: str) -> str:
    return f"Sections inside {project_name}."


def _agent_select_key(project_name: str) -> str:
    return f"agent-select-{project_name}"


def _pm_mode_select_key(project_name: str) -> str:
    return f"pm-mode-select-{project_name}"


def _experience_mode_select_key(project_name: str) -> str:
    return f"experience-mode-select-{project_name}"


def _ui_designer_mode_select_key(project_name: str) -> str:
    return f"ui-designer-mode-select-{project_name}"


def _architect_mode_select_key(project_name: str) -> str:
    return f"architect-mode-select-{project_name}"


def _qa_mode_select_key(project_name: str) -> str:
    return f"qa-mode-select-{project_name}"


def _orchestrator_mode_select_key(project_name: str) -> str:
    return f"orchestrator-mode-select-{project_name}"


def mode_options_for_agent(agent_name: str) -> list[str]:
    options = {
        "PM": PM_MODE_OPTIONS,
        "Experience Designer": EXPERIENCE_DESIGNER_MODE_OPTIONS,
        "UI Designer": UI_DESIGNER_MODE_OPTIONS,
        "Architect": ARCHITECT_MODE_OPTIONS,
        "QA": QA_MODE_OPTIONS,
        "Orchestrator": ORCHESTRATOR_MODE_OPTIONS,
    }
    return options.get(agent_name, PM_MODE_OPTIONS)


def mode_state_key_for_agent(project_name: str, agent_name: str) -> str:
    keys = {
        "PM": _pm_mode_select_key(project_name),
        "Experience Designer": _experience_mode_select_key(project_name),
        "UI Designer": _ui_designer_mode_select_key(project_name),
        "Architect": _architect_mode_select_key(project_name),
        "QA": _qa_mode_select_key(project_name),
        "Orchestrator": _orchestrator_mode_select_key(project_name),
    }
    return keys.get(agent_name, _pm_mode_select_key(project_name))


def _guided_verification_for_project(project_name: str) -> dict[str, str] | None:
    raw = st.session_state.get(GUIDED_VERIFICATION_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    if str(raw.get("project_name", "")).strip() != project_name:
        return None
    return {str(key): str(value) for key, value in raw.items()}


def guide_manual_verification_check(project_name: str, requirement_id: str, check_id: str) -> None:
    st.session_state[GUIDED_VERIFICATION_STATE_KEY] = {
        "project_name": project_name,
        "requirement_id": requirement_id,
        "check_id": check_id,
    }


def clear_guided_manual_verification(project_name: str) -> None:
    current = _guided_verification_for_project(project_name)
    if current is None:
        return
    st.session_state.pop(GUIDED_VERIFICATION_STATE_KEY, None)


def focus_project_agent_thread(project_name: str, *, agent_name: str, mode: str) -> None:
    st.session_state[PENDING_AGENT_FOCUS_STATE_KEY] = {
        "project_name": project_name,
        "agent_name": agent_name,
        "mode": mode,
    }


def queue_project_open(project_name: str) -> None:
    st.session_state[PENDING_PROJECT_OPEN_STATE_KEY] = {
        "project_name": project_name,
    }


def queue_back_to_projects() -> None:
    st.session_state[PENDING_PROJECT_OPEN_STATE_KEY] = {
        "project_name": "",
    }


def _apply_pending_agent_focus() -> None:
    pending = st.session_state.pop(PENDING_AGENT_FOCUS_STATE_KEY, None)
    if not isinstance(pending, dict):
        return

    project_name = str(pending.get("project_name", "")).strip()
    agent_name = str(pending.get("agent_name", "")).strip()
    mode = str(pending.get("mode", "")).strip()
    if not project_name or not agent_name:
        return

    st.session_state[TOP_LEVEL_SECTION_STATE_KEY] = TOP_LEVEL_PROJECTS_LABEL
    st.session_state[PROJECT_SELECTION_STATE_KEY] = project_name
    st.session_state[PROJECT_DETAIL_SECTION_STATE_KEY] = "Agents"
    st.session_state[_agent_select_key(project_name)] = agent_name
    if agent_name == "PM":
        st.session_state[_pm_mode_select_key(project_name)] = mode
    elif agent_name == "Experience Designer":
        st.session_state[_experience_mode_select_key(project_name)] = mode
    elif agent_name == "UI Designer":
        st.session_state[_ui_designer_mode_select_key(project_name)] = mode
    elif agent_name == "Orchestrator":
        st.session_state[_orchestrator_mode_select_key(project_name)] = mode


def _apply_pending_learning_section() -> None:
    pending = st.session_state.pop(PENDING_LEARNING_SECTION_STATE_KEY, None)
    if isinstance(pending, str) and pending.strip():
        st.session_state[LEARNING_SECTION_STATE_KEY] = pending.strip()


def _apply_pending_learning_concept() -> None:
    pending = st.session_state.pop(PENDING_LEARNING_CONCEPT_STATE_KEY, None)
    if isinstance(pending, str) and pending.strip():
        st.session_state[LEARNING_CONCEPT_SELECTION_STATE_KEY] = pending.strip()


def _apply_pending_project_open() -> None:
    pending = st.session_state.pop(PENDING_PROJECT_OPEN_STATE_KEY, None)
    if not isinstance(pending, dict):
        return

    project_name = str(pending.get("project_name", "")).strip()
    st.session_state[TOP_LEVEL_SECTION_STATE_KEY] = TOP_LEVEL_PROJECTS_LABEL
    if not project_name:
        st.session_state.pop(PROJECT_SELECTION_STATE_KEY, None)
        st.session_state.pop(PROJECT_DETAIL_SECTION_STATE_KEY, None)
        return

    st.session_state[PROJECT_SELECTION_STATE_KEY] = project_name


def selected_project_from_name(projects, project_name: str | None):
    if not project_name:
        return None
    return next((project for project in projects if project.name == project_name), None)


def agent_workspace_caption() -> str:
    return "Move left to right: choose an agent, choose the mode, then work in the active surface below."


def role_card_markup(role: dict[str, str]) -> str:
    return (
        '<div class="os-role-card">'
        f'<div class="os-role-card-name">{escape(role["name"])}</div>'
        f'<div class="os-role-card-title">{escape(role["title"])}</div>'
        f'<div class="os-role-card-summary">{escape(role["summary"])}</div>'
        '<div class="os-role-card-action-spacer"></div>'
        "</div>"
    )


def agent_summary_action_label(role: dict[str, str]) -> str:
    return f"Open {role['title']} summary"


def selected_agent_role(agent_name: str) -> dict[str, str]:
    return next((role for role in ROLE_CARDS if role["name"] == agent_name), ROLE_CARDS[0])


def agent_selection_card_markup(role: dict[str, str], selected_agent: str) -> str:
    is_selected = role["name"] == selected_agent
    selected_class = " os-agent-selection-card-selected" if is_selected else ""
    selected_state = "<div class='os-agent-selection-state'>Selected agent</div>" if is_selected else ""
    help_text = AGENT_SELECTION_HELP.get(role["name"], role["summary"])
    return (
        f"<div class='os-agent-selection-card{selected_class}'>"
        f"<div class='os-agent-selection-name'>{escape(role['name'])}</div>"
        f"<div class='os-agent-selection-title'>{escape(role['title'])}</div>"
        f"<div class='os-agent-selection-help'>{escape(help_text)}</div>"
        f"{selected_state}"
        "</div>"
    )


def selected_agent_context_markup(agent_name: str) -> str:
    role = selected_agent_role(agent_name)
    help_text = AGENT_SELECTION_HELP.get(role["name"], role["summary"])
    return (
        "<div class='os-selected-agent-shell'>"
        "<div class='os-selected-agent-kicker'>Selected agent</div>"
        f"<div class='os-selected-agent-title'>{escape(role['title'])} · {escape(role['name'])}</div>"
        f"<div class='os-selected-agent-summary'>{escape(help_text)}</div>"
        "</div>"
    )


def mode_option_markup(agent_name: str, mode: str) -> str:
    description = MODE_DESCRIPTIONS.get(agent_name, {}).get(mode, "")
    return (
        "<div class='os-mode-option-card'>"
        f"<div class='os-mode-option-title'>{escape(mode)}</div>"
        f"<div class='os-mode-option-description'>{escape(description)}</div>"
        "</div>"
    )


def single_mode_summary_markup(agent_name: str, mode: str) -> str:
    description = MODE_DESCRIPTIONS.get(agent_name, {}).get(mode, "")
    return (
        "<div class='os-mode-single-summary'>"
        f"<strong>{escape(mode)}</strong><br>"
        f"{escape(description)}"
        "</div>"
    )


def agent_summary_popup_sections(summary: AgentSummary) -> dict[str, tuple[str, ...]]:
    return {
        "What this agent can do": summary.can_do,
        "Memory and context": summary.memory_context,
        "Workflow position": summary.workflow_position,
    }


def render_agent_summary_content(summary: AgentSummary) -> None:
    for heading, items in agent_summary_popup_sections(summary).items():
        st.markdown(f"**{heading}**")
        for item in items:
            st.write(f"- {item}")


def open_agent_summary_dialog(summary: AgentSummary) -> None:
    @st.dialog(f"{summary.title} — {summary.name}")
    def _dialog() -> None:
        render_agent_summary_content(summary)

    _dialog()


def _set_selected_agent(project_name: str, agent_name: str) -> None:
    st.session_state[_agent_select_key(project_name)] = agent_name


def _render_agent_selector_cards(project_name: str) -> str:
    selected = st.session_state.get(_agent_select_key(project_name), AGENT_OPTIONS[0])
    st.markdown(f"<div class='os-agent-workspace-caption'>{escape(agent_workspace_caption())}</div>", unsafe_allow_html=True)
    st.markdown("**Choose an agent**")
    st.markdown("<div class='os-agent-selection-grid'></div>", unsafe_allow_html=True)
    rows = role_card_rows(tuple(role for role in ROLE_CARDS if role["name"] in AGENT_OPTIONS), row_size=2)
    for row in rows:
        columns = st.columns(len(row))
        for column, role in zip(columns, row):
            with column:
                with st.container(border=True):
                    st.markdown(agent_selection_card_markup(role, str(selected)), unsafe_allow_html=True)
                    button_label = "Selected" if selected == role["name"] else f"Use {role['title']}"
                    if st.button(button_label, key=f"select-agent-{project_name}-{role['name']}", use_container_width=True):
                        _set_selected_agent(project_name, role["name"])
                        st.rerun()
    return str(st.session_state.get(_agent_select_key(project_name), selected))


def _render_mode_selector_cards(project_name: str, agent_name: str, options: list[str], state_key: str) -> str:
    selected = st.session_state.get(state_key, options[0])
    st.markdown(selected_agent_context_markup(agent_name), unsafe_allow_html=True)
    if len(options) == 1:
        st.markdown(single_mode_summary_markup(agent_name, options[0]), unsafe_allow_html=True)
        st.session_state[state_key] = options[0]
        return options[0]

    st.markdown("<div class='os-mode-selection-heading'>Choose a mode</div>", unsafe_allow_html=True)
    columns = st.columns(len(options))
    for column, option in zip(columns, options):
        with column:
            with st.container(border=True):
                st.markdown(mode_option_markup(agent_name, option), unsafe_allow_html=True)
                button_label = "Selected" if selected == option else "Choose mode"
                if st.button(button_label, key=f"select-mode-{project_name}-{agent_name}-{option}", use_container_width=True):
                    st.session_state[state_key] = option
                    st.rerun()
    return str(st.session_state.get(state_key, selected))


def render_agent_workflow_header(project_name: str) -> tuple[str, str]:
    selected_agent = str(st.session_state.get(_agent_select_key(project_name), AGENT_OPTIONS[0]))
    if selected_agent not in AGENT_OPTIONS:
        selected_agent = AGENT_OPTIONS[0]
        st.session_state[_agent_select_key(project_name)] = selected_agent

    agent_col, mode_col, context_col = st.columns([1.3, 1.15, 1.55], gap="large")

    with agent_col:
        with st.container(border=True):
            st.markdown("**1. Choose an agent**")
            st.caption("Pick the role you want driving the work.")
            selected = st.segmented_control(
                "Agent",
                AGENT_OPTIONS,
                key=_agent_select_key(project_name),
                label_visibility="collapsed",
                width="stretch",
            )
            selected_agent = str(selected or selected_agent)

    mode_options = mode_options_for_agent(selected_agent)
    mode_state_key = mode_state_key_for_agent(project_name, selected_agent)
    current_mode = str(st.session_state.get(mode_state_key, mode_options[0]))
    if current_mode not in mode_options:
        current_mode = mode_options[0]
        st.session_state[mode_state_key] = current_mode

    with mode_col:
        with st.container(border=True):
            st.markdown("**2. Choose a mode**")
            if len(mode_options) == 1:
                st.caption("This agent has one active mode right now.")
                st.markdown(single_mode_summary_markup(selected_agent, mode_options[0]), unsafe_allow_html=True)
                selected_mode = mode_options[0]
                st.session_state[mode_state_key] = selected_mode
            else:
                st.caption("Choose the lens for this conversation or review.")
                selected_mode = st.segmented_control(
                    "Mode",
                    mode_options,
                    key=mode_state_key,
                    label_visibility="collapsed",
                    width="stretch",
                )
                selected_mode = str(selected_mode or current_mode)
                st.caption(MODE_DESCRIPTIONS.get(selected_agent, {}).get(selected_mode, ""))

    with context_col:
        st.markdown(selected_agent_context_markup(selected_agent), unsafe_allow_html=True)

    return selected_agent, selected_mode


def role_card_rows(role_cards: tuple[dict[str, str], ...], row_size: int = 3) -> list[tuple[dict[str, str], ...]]:
    return [tuple(role_cards[index : index + row_size]) for index in range(0, len(role_cards), row_size)]


def role_card_row_weights(row: tuple[dict[str, str], ...], row_size: int = ROLE_CARD_ROW_SIZE) -> list[int]:
    return [1] * max(len(row), row_size)


def project_card_rows(projects, row_size: int = WORKSPACE_PROJECT_ROW_SIZE):
    return [tuple(projects[index : index + row_size]) for index in range(0, len(projects), row_size)]


def project_card_row_weights(row) -> list[int]:
    if len(row) == 1:
        return [1, 1]
    return [1, 1]


def split_requirements_for_display(records: list[RequirementRecord]) -> tuple[list[RequirementRecord], list[RequirementRecord]]:
    active_records = [record for record in records if record.status != "DONE"]
    done_records = [record for record in records if record.status == "DONE"]
    return active_records, done_records


def requirement_priority_focus(record: RequirementRecord) -> bool:
    return record.status in {"IN_PROGRESS", "NEW"} or record.priority == "HIGH"


def requirement_focus_groups(records: list[RequirementRecord]) -> list[tuple[str, str, list[RequirementRecord]]]:
    groups = [
        (REQUIREMENT_GROUPS[0][0], REQUIREMENT_GROUPS[0][1], []),
        (REQUIREMENT_GROUPS[1][0], REQUIREMENT_GROUPS[1][1], []),
        (REQUIREMENT_GROUPS[2][0], REQUIREMENT_GROUPS[2][1], []),
    ]
    for record in records:
        if requirement_priority_focus(record):
            groups[0][2].append(record)
        elif record.status == "BACKLOG":
            groups[1][2].append(record)
        else:
            groups[2][2].append(record)
    return [(title, caption, group_records) for title, caption, group_records in groups if group_records]


def requirement_card_metadata(record: RequirementRecord) -> str:
    priority = record.priority or "No priority"
    effort = record.effort or "No effort"
    return f"Status: {record.status} · Priority: {priority} · Effort: {effort}"


def requirement_expander_label(record: RequirementRecord) -> str:
    priority = record.priority or "UNPRIORITISED"
    return f"{record.id} — {record.title} · {record.status} · {priority}"


def format_run_timestamp(value: str) -> str:
    if not value:
        return "—"
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return value
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def render_implementation_runs_panel(project_name: str) -> None:
    inspections = recent_implementation_run_inspections(project_name)
    st.markdown("**Implementation runs**")
    if not inspections:
        st.caption("No implementation runs recorded for this project yet.")
        return

    active_count = sum(1 for item in inspections if item.tone == "active")
    issue_count = sum(1 for item in inspections if item.tone in {"failed", "stale"})

    with st.container(border=True):
        metric_left, metric_middle, metric_right = st.columns(3)
        metric_left.metric("Recent runs", len(inspections))
        metric_middle.metric("Active", active_count)
        metric_right.metric("Issues", issue_count)

        for inspection in inspections:
            run = inspection.run
            label = (
                f"{run.requirement_id} — {run.requirement_title} · "
                f"{inspection.display_status} · {format_run_timestamp(run.created_at)}"
            )
            with st.expander(label, expanded=(inspection.tone == "active")):
                status_left, status_middle, status_right = st.columns(3)
                status_left.metric("Status", inspection.display_status)
                status_middle.metric("Started", format_run_timestamp(run.started_at))
                status_right.metric("Finished", format_run_timestamp(run.finished_at))
                st.caption(f"Run ID: {run.run_id}")

                if inspection.tone == "active":
                    st.info("This implementation run is currently active.")
                elif inspection.tone == "completed":
                    st.success("This implementation run completed successfully.")
                elif inspection.tone == "stale":
                    st.warning("This implementation run was reconciled as stale after its worker stopped.")
                else:
                    st.error("This implementation run failed.")

                if run.summary:
                    st.write(run.summary)
                if run.error:
                    if inspection.tone == "stale":
                        st.warning(run.error)
                    else:
                        st.error(run.error)

                st.caption(
                    "Artifacts: "
                    f"output `{run.output_path or 'Not captured'}` · "
                    f"log `{run.log_path or 'Not captured'}`"
                )

                if inspection.output_excerpt:
                    st.markdown("**Final output**")
                    st.code(inspection.output_excerpt, language="text")
                elif inspection.output_available:
                    st.caption("Output file exists, but it is currently empty.")

                if inspection.log_excerpt:
                    st.markdown("**Log tail**")
                    st.code(inspection.log_excerpt, language="text")
                elif inspection.log_available:
                    st.caption("Log file exists, but it is currently empty.")

        if len(inspections) == 8:
            st.caption("Showing the 8 most recent implementation runs for this project.")


def render_workflow_timeline_panel(project_name: str) -> None:
    events = workflow_timeline_events(project_name)
    st.markdown("**Workflow timeline**")
    if not events:
        st.caption("No recorded workflow events for this project yet.")
        return

    with st.container(border=True):
        metric_left, metric_middle, metric_right = st.columns(3)
        metric_left.metric("Events shown", len(events))
        metric_middle.metric(
            "Open attention",
            sum(1 for event in events if event.status_bucket in {"approval", "waiting", "blocked", "running", "routed"}),
        )
        metric_right.metric(
            "Resolved",
            sum(1 for event in events if event.status_bucket in {"completed", "recorded"}),
        )

        for event in events:
            label = f"{format_run_timestamp(event.occurred_at)} · {event.title}"
            with st.expander(label, expanded=False):
                render_workflow_card_header(
                    event.status_bucket,
                    event.title,
                    workflow_card_metadata(event.actor, event.artifact_kind, event.artifact_id),
                )
                if event.summary:
                    st.write(event.summary)
                if event.detail:
                    st.caption(event.detail)

        if len(events) == 16:
            st.caption("Showing the 16 most recent workflow events for this project.")


def render_quality_dashboard_panel(project_name: str) -> None:
    review = latest_quality_review(project_name, mode="deterministic")
    st.markdown("**Quality signal**")
    with st.container(border=True):
        if st.button("Run deterministic validation", key=f"run-quality-dashboard-{project_name}"):
            review = record_project_qa_review(project_name, mode="deterministic")
            st.success("Quality signal updated from the latest deterministic validation run.")
            st.rerun()

        if review is None:
            st.caption("No deterministic validation result has been recorded for this project yet.")
            return

        metric_left, metric_middle, metric_right = st.columns(3)
        metric_left.metric("Status", review.status)
        metric_middle.metric("Failing cases", len(review.failures))
        metric_right.metric("Last run", format_run_timestamp(review.reviewed_at))

        st.caption(f"Runner: {review.runner_path or 'Unavailable'} · Mode: {review.mode}")
        st.write(review.summary)
        st.caption(review.confidence)

        if review.failures:
            st.markdown("**Failing cases**")
            for case in review.failures:
                st.markdown(f"- {case}")
        else:
            st.caption("No failing cases were reported in the latest deterministic validation run.")

        with st.expander("Show raw validation output", expanded=False):
            st.text(review.raw_output or "<no output>")


def render_delivery_panel(project_name: str, project) -> None:
    active_run = active_implementation_run(project_name)

    metric_left, metric_right = st.columns(2)
    metric_left.metric("Pending Tasks", len(project.pending_tasks))
    metric_right.metric("Active run", active_run.requirement_id if active_run is not None else "None")

    if active_run is not None:
        st.info(
            "Implementation currently active for "
            f"{active_run.requirement_id} in this project ({active_run.status})."
        )
    else:
        st.caption("Inspect recent implementation runs and wider workflow history for this project.")

    render_implementation_runs_panel(project_name)
    render_workflow_timeline_panel(project_name)


def render_quality_panel(project_name: str) -> None:
    st.caption("Inspect the current deterministic validation signal for this project.")
    render_quality_dashboard_panel(project_name)


def requirements_panel_section_order() -> tuple[str, ...]:
    return REQUIREMENTS_PANEL_SECTION_ORDER


def active_requirement_rows(
    records: list[RequirementRecord], row_size: int = ACTIVE_REQUIREMENT_ROW_SIZE
) -> list[tuple[RequirementRecord, ...]]:
    return [tuple(records[index : index + row_size]) for index in range(0, len(records), row_size)]


def active_requirement_row_weights(row: tuple[RequirementRecord, ...]) -> list[int]:
    if len(row) == 1:
        return [1, 1]
    return [1] * len(row)


def requirement_editor_expanded(position: int) -> bool:
    return False


def render_metric_row(totals: dict[str, int]) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Projects", totals["projects"])
    col2.metric("New Requirements", totals["new_requirements"])
    col3.metric("Pending Tasks", totals["pending_tasks"])


def render_section_intro(title: str, caption: str) -> None:
    st.markdown(f"<div class='os-section-heading'>{escape(title)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='os-section-caption'>{escape(caption)}</div>", unsafe_allow_html=True)


def workflow_card_metadata(*parts: str) -> str:
    return " · ".join(part.strip() for part in parts if part.strip())


def workflow_card_kicker(label: str) -> str:
    return label.strip().upper()


def workflow_card_attention_label(label: str) -> str:
    normalized = label.strip().lower().replace("_", " ")
    labels = {
        "approval": "Action required",
        "waiting": "Waiting on you",
        "blocked": "Blocked",
        "routed": "Routed",
        "running": "Running",
        "completed": "Completed",
        "recorded": "Recorded",
    }
    return labels.get(normalized, normalized.title() if normalized else "Workflow item")


def workflow_card_attention_class(label: str) -> str:
    normalized = label.strip().lower().replace("_", "-")
    classes = {
        "approval": "action",
        "waiting": "waiting",
        "blocked": "blocked",
        "routed": "routed",
        "running": "running",
        "completed": "default",
        "recorded": "default",
    }
    return f"os-workflow-card-cue-{classes.get(normalized, 'default')}"


def workflow_card_attention_markup(label: str) -> str:
    cue = workflow_card_attention_label(label)
    class_name = workflow_card_attention_class(label)
    return f"<div class='os-workflow-card-cue {class_name}'>{escape(cue)}</div>"


def workflow_card_anchor_markup() -> str:
    return "<div class='os-workflow-card-anchor'></div>"


def main_navigation_anchor_markup() -> str:
    return "<div class='os-main-navigation-anchor'></div>"


def main_navigation_context_markup() -> str:
    items = "".join(
        f"<span>{escape(main_navigation_context_label(label))}</span>" for label in TOP_LEVEL_TAB_LABELS
    )
    return (
        "<div class='os-main-navigation-shell'>"
        f"<div class='os-main-navigation-heading'>{escape(top_level_navigation_level_label())}</div>"
        f"<div class='os-main-navigation-scope'>{escape(top_level_navigation_scope_description())}</div>"
        f"<div class='os-main-navigation-context'>{items}</div>"
        "</div>"
    )


def project_detail_navigation_context_markup(project_name: str) -> str:
    return (
        "<div class='os-project-navigation-shell'>"
        f"<div class='os-project-nav-level'>{escape(project_detail_navigation_level_label())}</div>"
        f"<div class='os-project-nav-heading'>{escape(project_detail_navigation_label())}</div>"
        f"<div class='os-project-nav-caption'>{escape(project_detail_navigation_scope_description(project_name))}</div>"
        "</div>"
    )


def inbox_item_metadata(item) -> str:
    return workflow_card_metadata(item.project_name, item.kind.replace("_", " "), item.status_bucket.title())


def inbox_section_label(heading: str, count: int) -> str:
    item_label = "item" if count == 1 else "items"
    return f"{heading} · {count} {item_label}"


def inbox_section_label_markup(heading: str, count: int) -> str:
    item_label = "item" if count == 1 else "items"
    return (
        "<div class='os-inbox-section-label'>"
        f"<span>{escape(heading)}</span>"
        f"<span class='os-inbox-section-label-count'>{count} {item_label}</span>"
        "</div>"
    )


def inbox_card_rows(items, row_size: int = INBOX_CARD_ROW_SIZE):
    return [tuple(items[index : index + row_size]) for index in range(0, len(items), row_size)]


def inbox_card_row_weights(row, row_size: int = INBOX_CARD_ROW_SIZE) -> list[int]:
    if len(row) == 1:
        return [1] * row_size
    return [1] * len(row)


def inbox_empty_message(selected_project: str, inbox_filter: str) -> str:
    project_scope = "all projects" if selected_project == "All projects" else selected_project
    if inbox_filter == "All":
        return f"No active inbox items for {project_scope}."
    return f"No {inbox_filter.lower()} inbox items for {project_scope}."


def render_workflow_card_header(kicker: str, title: str, metadata: str) -> None:
    st.markdown(workflow_card_anchor_markup(), unsafe_allow_html=True)
    st.markdown(workflow_card_attention_markup(kicker), unsafe_allow_html=True)
    st.markdown(f"<div class='os-workflow-card-title'>{escape(title)}</div>", unsafe_allow_html=True)
    if metadata:
        st.markdown(f"<div class='os-card-meta'>{escape(metadata)}</div>", unsafe_allow_html=True)


def render_project_card(project) -> None:
    with st.container(border=True):
        st.markdown(project_card_anchor_markup(), unsafe_allow_html=True)
        st.markdown(project_card_status_markup(project), unsafe_allow_html=True)
        st.markdown(f"<div class='os-project-card-title'>{escape(project.name)}</div>", unsafe_allow_html=True)
        structure_text = "Healthy structure" if project.structure_ok else "Structure needs attention"
        st.markdown(f"<div class='os-card-meta'>{escape(structure_text)}</div>", unsafe_allow_html=True)

        left, right = st.columns(2)
        with left:
            st.markdown("<div class='os-signal-label'>New requirements</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='os-signal-value'>{len(project.new_requirements)}</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='os-signal-label'>Pending tasks</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='os-signal-value'>{len(project.pending_tasks)}</div>", unsafe_allow_html=True)

        if project.missing_paths:
            st.markdown("**Needs attention**")
            for path in project.missing_paths:
                st.write(f"- {path}")

        st.markdown(project_card_next_work_markup(project), unsafe_allow_html=True)

        primary, secondary = st.columns(2)
        with primary:
            if st.button(
                project_open_button_label(project),
                key=f"open-project-{project.name}",
                type="primary",
                use_container_width=True,
            ):
                queue_project_open(project.name)
                st.rerun()
        with secondary:
            render_project_preview_control(project.name, compact=True)


def render_project_preview_control(project_name: str, *, compact: bool = False) -> None:
    preview = project_preview(project_name)
    if not preview.available:
        if not compact:
            st.caption(preview.status_text)
        return
    is_running = project_preview_running(project_name)

    if compact:
        if is_running:
            st.link_button(
                project_preview_button_label(project_name),
                preview.url,
                use_container_width=True,
            )
        else:
            if st.button(
                "Start preview",
                key=f"preview-project-compact-{project_name}",
                use_container_width=True,
            ):
                try:
                    start_project_preview(project_name)
                except Exception as exc:  # pragma: no cover - surfaced in UI
                    st.error(f"Could not start preview: {exc}")
                else:
                    st.success("Preview started. Click again in a moment to open it.")
        return

    with st.container(border=True):
        left, right = st.columns([1, 2])
        with left:
            st.markdown("**Project preview**")
            st.caption("Running" if is_running else "Available")
            if is_running:
                st.link_button(
                    project_preview_button_label(project_name),
                    preview.url,
                    use_container_width=True,
                )
            else:
                if st.button(
                    "Start preview",
                    key=f"preview-project-{project_name}",
                    use_container_width=True,
                ):
                    try:
                        start_project_preview(project_name)
                    except Exception as exc:  # pragma: no cover - surfaced in UI
                        st.error(f"Could not start preview: {exc}")
                    else:
                        st.success("Preview started. Open it once the local app is ready.")
        with right:
            st.caption(preview.status_text)
            if is_running:
                st.caption(preview.url)


def render_project_control_header(project_name: str, project) -> None:
    st.markdown(
        project_control_summary_markup(project_name, project_control_path_metadata(project)),
        unsafe_allow_html=True,
    )


def render_role_cards() -> None:
    st.markdown(ROLE_CARD_STYLE, unsafe_allow_html=True)
    rows = role_card_rows(ROLE_CARDS, row_size=ROLE_CARD_ROW_SIZE)
    for index, row in enumerate(rows):
        columns = st.columns(role_card_row_weights(row))
        for column_index, column in enumerate(columns):
            if column_index >= len(row):
                continue
            role = row[column_index]
            with column:
                with st.container(border=True):
                    st.markdown(role_card_markup(role), unsafe_allow_html=True)
                    if st.button(
                        agent_summary_action_label(role),
                        key=f"agent-summary-{role['name']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        open_agent_summary_dialog(agent_summary_by_name(role["name"]))
        if index != len(rows) - 1:
            st.markdown(f"<div style='height: {ROLE_CARD_ROW_GAP_REM}rem;'></div>", unsafe_allow_html=True)


def render_workspace_tab(projects) -> None:
    totals = workspace_totals(projects)

    st.subheader("Workspace")
    st.caption("A calm operating snapshot before you open a project or clear a waiting decision.")
    render_section_intro("Operating snapshot", "Current project and work signals across the local OS.")
    if not projects:
        st.info("No projects found in the workspace yet.")
    else:
        render_metric_row(totals)

    render_workspace_approval_requests()
    if learning_reflection_enabled():
        render_reflection_helper()
    render_section_intro("Agent reference", "Role summaries are available here without starting workflow execution.")
    render_role_cards()


def _operations_project_options(snapshot) -> list[str]:
    names = sorted({item.project_name for item in snapshot.workflow_health})
    return ["All projects", *names]


def _filtered_agent_runs(snapshot, project_name: str, role: str):
    runs = list(snapshot.agent_runs)
    if project_name != "All projects":
        runs = [run for run in runs if run.project_name == project_name]
    if role != "All roles":
        runs = [run for run in runs if run.role == role]
    return runs


def _operations_column_config(descriptions: dict[str, str]) -> dict[str, object]:
    return {
        column_name: st.column_config.Column(column_name, help=description)
        for column_name, description in descriptions.items()
    }


def render_agent_operations_dashboard(snapshot) -> None:
    st.caption(
        "Shows individual live-agent runs so you can see what ran, whether it completed, "
        "how much work it needed, and which tools or guardrails were involved."
    )
    projects = _operations_project_options(snapshot)
    roles = ["All roles", *sorted({run.role for run in snapshot.agent_runs})]
    filter_left, filter_right = st.columns(2)
    with filter_left:
        project_name = st.selectbox("Project", projects, key="operations-agent-project")
    with filter_right:
        role = st.selectbox("Role", roles, key="operations-agent-role")
    runs = _filtered_agent_runs(snapshot, project_name, role)

    metrics = st.columns(6)
    metrics[0].metric("Runs", len(runs))
    metrics[1].metric("Completed", sum(1 for run in runs if run.status == "completed"))
    metrics[2].metric("Hand-backs", sum(1 for run in runs if run.status == "hand_back"))
    durations = [run.duration_seconds for run in runs if run.duration_seconds is not None]
    metrics[3].metric("Average duration", f"{sum(durations) / len(durations):.1f}s" if durations else "No data")
    metrics[4].metric("Tokens", sum(run.input_tokens + run.output_tokens for run in runs))
    measured_costs = [run.estimated_cost_usd for run in runs if run.estimated_cost_usd is not None]
    metrics[5].metric("Estimated cost", f"${sum(measured_costs):.4f}" if measured_costs else "No data")

    if not runs:
        st.info("No live-agent runs match the current filters.")
        return
    st.dataframe(
        [
            {
                "Started": format_run_timestamp(run.started_at),
                "Project": run.project_name,
                "Role": run.role,
                "Status": run.status.replace("_", " ").title(),
                "Duration": f"{run.duration_seconds:.1f}s" if run.duration_seconds is not None else "",
                "Attempts": run.attempts,
                "Steps": run.steps,
                "Tools": ", ".join(run.tools) or "None",
                "Guardrails": run.guardrail_count,
                "Input tokens": run.input_tokens or None,
                "Output tokens": run.output_tokens or None,
                "Estimated cost": (
                    f"${run.estimated_cost_usd:.6f}"
                    if run.estimated_cost_usd is not None
                    else ""
                ),
            }
            for run in runs
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Started": "When the live-agent run began.",
                "Project": "The project whose context and workflow the agent was handling.",
                "Role": "The agent role that performed the run.",
                "Status": "Whether the run completed, handed control back, failed, or remained incomplete.",
                "Duration": "Elapsed time between the first and final recorded event.",
                "Attempts": "Number of model-call attempts, including retries.",
                "Steps": "Number of bounded reasoning or tool-use steps used by the run.",
                "Tools": "Read-only context tools successfully used during the run.",
                "Guardrails": "Number of input or output guardrail findings recorded for the run.",
                "Input tokens": "Input tokens reported by the model provider across all calls in the run.",
                "Output tokens": "Output tokens reported by the model provider across all calls in the run.",
                "Estimated cost": "Estimated token cost using the configured per-model input and output rates.",
            }
        ),
    )
    for run in runs[:12]:
        with st.expander(
            f"{format_run_timestamp(run.started_at)} · {run.role} · {run.status.replace('_', ' ').title()}",
            expanded=False,
        ):
            st.caption(f"{run.project_name} · Trace {run.trace_id} · Model {run.model or 'Not recorded'}")
            if run.tools:
                st.write(f"Tools: {', '.join(run.tools)}")
            if run.hand_back_reason:
                st.warning(run.hand_back_reason)
            elif run.error_count:
                st.error(f"{run.error_count} model error event(s) were recorded.")


def render_agent_quality_dashboard(snapshot) -> None:
    st.caption(
        "Shows whether captured agent traces meet the runtime quality contract, then lists every "
        "OS agent role with its execution mode and the quality evidence currently available."
    )
    quality_rows = []
    for project_name, result in sorted(snapshot.trace_quality.items()):
        missing_traces = result.get("failures") == ["missing_traces"]
        quality_rows.append(
            {
                "Project": project_name,
                "Trace status": (
                    "PASS"
                    if result["passed"]
                    else "NO LIVE TRACES"
                    if missing_traces
                    else "NEEDS ATTENTION"
                ),
                "Score": result["score"],
                "Summary": result["summary"],
                "Failures": len(result["failures"]),
            }
        )
    passed = sum(1 for result in snapshot.trace_quality.values() if result["passed"])
    metrics = st.columns(4)
    metrics[0].metric("Projects graded", len(snapshot.trace_quality))
    metrics[1].metric("Passing", passed)
    metrics[2].metric("Guardrail findings", sum(item.guardrail_findings for item in snapshot.role_performance))
    metrics[3].metric("Model errors", sum(run.error_count for run in snapshot.agent_runs))
    st.dataframe(
        quality_rows,
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Project": "The project whose captured live-agent traces were graded.",
                "Trace status": "Overall trace-grade result for the project.",
                "Score": "Trace-quality score from 0 to 100.",
                "Summary": "Short explanation of completed traces and detected quality failures.",
                "Failures": "Number of trace-contract failures found.",
            }
        ),
    )
    st.markdown("**Quality by role**")
    st.caption(
        "Roles remain visible even before they produce live traces. Architect, Engineer, and QA use "
        "separate review, execution, or validation evidence rather than the bounded live-agent trace stream."
    )
    st.dataframe(
        [
            {
                "Role": item.role,
                "Execution mode": item.execution_mode,
                "Evidence": item.evidence_status,
                "Runs": item.total_runs,
                "Completion": f"{item.completion_rate}%" if item.total_runs else "No runs",
                "Hand-backs": item.hand_backs,
                "Failed / incomplete": item.failed_runs,
                "Guardrail findings": item.guardrail_findings,
            }
            for item in snapshot.role_performance
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Role": "The live-agent role being assessed.",
                "Execution mode": "How the role operates: bounded live model, deterministic review, Codex execution, or deterministic validation.",
                "Evidence": "Whether live traces exist or the role is assessed through a separate validation path.",
                "Runs": "Total captured runs for the role.",
                "Completion": "Percentage of the role's runs that completed successfully.",
                "Hand-backs": "Runs that deliberately returned control to a human.",
                "Failed / incomplete": "Runs that failed or never recorded a valid terminal outcome.",
                "Guardrail findings": "Input and output guardrail findings recorded across the role's runs.",
            }
        ),
    )


def render_eval_coverage_dashboard(snapshot) -> None:
    st.caption(
        "Shows which evaluation types are implemented, which projects and agents they cover, "
        "and the concrete behavior each evaluation measures. Filter the catalog and open a case "
        "to inspect its input, expectations, and source fixture."
    )
    records = list(snapshot.eval_coverage)
    cases = list(snapshot.eval_cases)
    metrics = st.columns(3)
    metrics[0].metric("Eval types", len({item.eval_type for item in records}))
    metrics[1].metric("Configured cases", len(cases))
    metrics[2].metric("Projects covered", len({item.project_name for item in cases}))
    st.dataframe(
        [
            {
                "Eval type": item.eval_type,
                "Project": item.project_name,
                "Agents": item.agents,
                "What is evaluated": item.implementation,
            }
            for item in records
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Eval type": "The quality dimension being measured.",
                "Project": "The project whose behavior is covered by this evaluation.",
                "Agents": "The agents or deterministic components assessed by the evaluation.",
                "What is evaluated": "The concrete behavior, evidence, or threshold checked.",
            }
        ),
    )
    st.markdown("**Inspect eval cases**")
    filter_left, filter_right = st.columns(2)
    with filter_left:
        selected_project = st.selectbox(
            "Case project",
            ["All projects", *sorted({item.project_name for item in cases})],
            key="eval-coverage-project",
        )
    with filter_right:
        selected_type = st.selectbox(
            "Eval type",
            ["All eval types", *sorted({item.eval_type for item in cases})],
            key="eval-coverage-type",
        )
    filtered = [
        item
        for item in cases
        if (selected_project == "All projects" or item.project_name == selected_project)
        and (selected_type == "All eval types" or item.eval_type == selected_type)
    ]
    st.caption(f"{len(filtered)} configured case(s) match the current filters.")
    if not filtered:
        st.info("No eval cases match the current filters.")
        return
    selected_case_id = st.selectbox(
        "Eval case",
        [f"{item.project_name} · {item.eval_type} · {item.title}" for item in filtered],
        key="eval-coverage-case",
    )
    selected_index = [
        f"{item.project_name} · {item.eval_type} · {item.title}" for item in filtered
    ].index(selected_case_id)
    selected_case = filtered[selected_index]
    with st.container(border=True):
        render_workflow_card_header(
            selected_case.eval_type,
            selected_case.title,
            workflow_card_metadata(selected_case.project_name, selected_case.agents),
        )
        st.write(selected_case.description)
        detail_left, detail_right = st.columns(2)
        with detail_left:
            st.markdown("**Expected behavior**")
            st.code(selected_case.expected_summary, language="json")
        with detail_right:
            st.markdown("**Source**")
            st.code(selected_case.source_path)
            st.caption(f"Case ID: {selected_case.case_id}")
        with st.expander("View full case payload", expanded=False):
            st.code(selected_case.payload_json, language="json")


def render_workflow_health_dashboard(snapshot) -> None:
    st.caption(
        "Shows the delivery and decision state of every project, highlighting unfinished work, "
        "workflow blockers, human decisions, implementation activity, and the latest quality signal."
    )
    health = list(snapshot.workflow_health)
    metrics = st.columns(4)
    metrics[0].metric("Pending tasks", sum(item.pending_tasks for item in health))
    metrics[1].metric("Blocked", sum(item.blocked_items + item.open_clarifications for item in health))
    metrics[2].metric("Waiting approvals", sum(item.open_approvals for item in health))
    metrics[3].metric("Active implementation", sum(item.active_runs for item in health))
    st.dataframe(
        [
            {
                "Project": item.project_name,
                "New reqs": item.new_requirements,
                "In progress": item.in_progress_requirements,
                "Backlog": item.backlog_requirements,
                "Pending tasks": item.pending_tasks,
                "Blocked": item.blocked_items,
                "Approvals": item.open_approvals,
                "Clarifications": item.open_clarifications,
                "Routed": item.routed_items,
                "Active runs": item.active_runs,
                "Failed runs": item.failed_runs,
                "Quality": item.quality_status,
            }
            for item in health
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Project": "The project represented by this row.",
                "New reqs": "Requirements still marked NEW and awaiting workflow progression.",
                "In progress": "Requirements currently being worked on.",
                "Backlog": "Requirements intentionally queued for later prioritisation.",
                "Pending tasks": "Tasks not yet marked DONE.",
                "Blocked": "Active workflow items currently unable to progress.",
                "Approvals": "Open approval requests waiting for a human decision.",
                "Clarifications": "Open PM clarification requests waiting for an answer.",
                "Routed": "Experience or workflow artifacts routed to another role.",
                "Active runs": "Implementation runs currently queued or running.",
                "Failed runs": "Implementation runs that ended in failure.",
                "Quality": "Status of the latest recorded deterministic quality review.",
            }
        ),
    )


def render_human_oversight_dashboard(snapshot) -> None:
    st.caption(
        "Shows where human judgment is still required: pending approvals, agent hand-backs, "
        "and high-risk capabilities that agents cannot use automatically."
    )
    metrics = st.columns(3)
    metrics[0].metric("Open approvals", len(snapshot.open_approvals))
    metrics[1].metric("Approval-gated tools", len(snapshot.high_risk_tools))
    metrics[2].metric(
        "Agent hand-backs",
        sum(1 for run in snapshot.agent_runs if run.status == "hand_back"),
    )
    if snapshot.open_approvals:
        st.markdown("**Pending decisions**")
        for approval in snapshot.open_approvals:
            with st.container(border=True):
                render_workflow_card_header(
                    "Approval",
                    approval.title,
                    workflow_card_metadata(approval.project_name, approval.source_agent_name),
                )
                st.write(approval.summary)
                st.caption("Resolve this request from Inbox, where the full approval controls remain available.")
    else:
        st.caption("No approval requests are currently waiting.")
    st.markdown("**Capabilities kept behind approval**")
    st.dataframe(
        [
            {
                "Capability": tool_name,
                "Risk": "High",
                "Automatic access": "Blocked",
                "Required control": "Explicit human approval",
            }
            for tool_name in snapshot.high_risk_tools
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Capability": "The registered tool or action kept behind a human control boundary.",
                "Risk": "The tool's configured operational risk level.",
                "Automatic access": "Whether a live agent may invoke the capability without approval.",
                "Required control": "The human authorization required before the capability can run.",
            }
        ),
    )


def render_agent_performance_dashboard(snapshot) -> None:
    st.caption(
        "Compares captured run performance across the complete OS agent roster while distinguishing "
        "roles that use separate review, execution, or validation paths."
    )
    if not snapshot.role_performance:
        st.info("No agent performance history is available yet.")
        return
    st.dataframe(
        [
            {
                "Role": item.role,
                "Execution mode": item.execution_mode,
                "Evidence": item.evidence_status,
                "Runs": item.total_runs,
                "Completed": item.completed_runs,
                "Completion": f"{item.completion_rate}%" if item.total_runs else "No runs",
                "Hand-backs": item.hand_backs,
                "Failed / incomplete": item.failed_runs,
                "Avg attempts": item.average_attempts,
                "Avg steps": item.average_steps,
                "Tool calls": item.tool_calls,
            }
            for item in snapshot.role_performance
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Role": "The live-agent role represented by this row.",
                "Execution mode": "How the role executes work in the OS.",
                "Evidence": "Whether captured traces exist or quality is assessed through another path.",
                "Runs": "Total captured runs for the role.",
                "Completed": "Runs that reached a successful completion event.",
                "Completion": "Completed runs as a percentage of all runs.",
                "Hand-backs": "Runs that intentionally returned control to a human.",
                "Failed / incomplete": "Runs that failed or lacked a valid final event.",
                "Avg attempts": "Average model-call attempts per run, including retries.",
                "Avg steps": "Average bounded reasoning or tool-use steps per run.",
                "Tool calls": "Total successful context-tool invocations by the role.",
            }
        ),
    )


def render_tool_usage_dashboard(snapshot) -> None:
    st.caption(
        "Shows which runtime tools exist, how often agents use them, where they are used, "
        "and whether any requests were denied or failed."
    )
    metrics = st.columns(3)
    metrics[0].metric("Registered tools", len(snapshot.tool_usage))
    metrics[1].metric("Invocations", sum(item.calls for item in snapshot.tool_usage))
    metrics[2].metric("Unused tools", sum(1 for item in snapshot.tool_usage if item.calls == 0))
    st.dataframe(
        [
            {
                "Tool": item.tool_name,
                "Risk": item.risk.title(),
                "Read only": "Yes" if item.read_only else "No",
                "Approval required": "Yes" if item.approval_required else "No",
                "Calls": item.calls,
                "Denied / failed": item.denied_or_failed,
                "Roles": ", ".join(item.roles) or "None",
                "Projects": ", ".join(item.projects) or "None",
            }
            for item in snapshot.tool_usage
        ],
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "Tool": "The registered runtime tool name.",
                "Risk": "The configured operational risk level for the tool.",
                "Read only": "Whether the tool can only inspect context without changing state.",
                "Approval required": "Whether explicit human approval is required before use.",
                "Calls": "Number of successful recorded invocations.",
                "Denied / failed": "Requests that were rejected or could not complete.",
                "Roles": "Agent roles that successfully used the tool.",
                "Projects": "Projects in which the tool was successfully used.",
            }
        ),
    )


def render_learning_progress_dashboard(snapshot) -> None:
    st.caption(
        "Shows concept progression across learned, active, and upcoming states, plus the current "
        "learning-agent session and its recommended next move."
    )
    groups = snapshot.learning_progress
    learned = groups.get("learned", ())
    in_progress = groups.get("in_progress", ())
    upcoming = groups.get("upcoming", ())
    metrics = st.columns(4)
    metrics[0].metric("Learned", len(learned))
    metrics[1].metric("In progress", len(in_progress))
    metrics[2].metric("Upcoming", len(upcoming))
    metrics[3].metric("Active session", "Yes" if snapshot.active_learning_session is not None else "No")
    if snapshot.active_learning_session is not None:
        session = snapshot.active_learning_session
        with st.container(border=True):
            st.markdown(f"**Current concept:** {session.concept}")
            st.write(session.coach_message)
            st.caption(
                f"Next move: {session.next_move.replace('_', ' ')} · "
                f"Turns: {session.turn_count} · Gaps: {len(session.detected_gaps)}"
            )
            if session.hand_back_reason:
                st.warning(session.hand_back_reason)
    rows = []
    for group_name, items in (("Learned", learned), ("In progress", in_progress), ("Upcoming", upcoming)):
        for item in items:
            rows.append(
                {
                    "State": group_name,
                    "Concept": item.concept,
                    "Current understanding": item.latest_understanding,
                    "Next move": item.recommended_next_move,
                }
            )
    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_config=_operations_column_config(
            {
                "State": "The concept's current learning lifecycle state.",
                "Concept": "The subject being learned or tracked.",
                "Current understanding": "The latest saved description of what is understood.",
                "Next move": "The recommended action for progressing or reinforcing the concept.",
            }
        ),
    )


def render_system_activity_dashboard(snapshot) -> None:
    st.caption(
        "Combines live-agent runs and file-backed workflow events into one recent timeline. "
        "Each entry shows when it happened, the project, the actor, its status, and the recorded outcome."
    )
    projects = ["All projects", *sorted({item.project_name for item in snapshot.activity})]
    statuses = ["All statuses", *sorted({item.status for item in snapshot.activity})]
    filter_left, filter_right = st.columns(2)
    with filter_left:
        project_name = st.selectbox("Project", projects, key="operations-activity-project")
    with filter_right:
        status = st.selectbox("Status", statuses, key="operations-activity-status")
    activity = list(snapshot.activity)
    if project_name != "All projects":
        activity = [item for item in activity if item.project_name == project_name]
    if status != "All statuses":
        activity = [item for item in activity if item.status == status]
    if not activity:
        st.info("No operational activity matches the current filters.")
        return
    for item in activity:
        with st.expander(
            f"{format_run_timestamp(item.occurred_at)} · {item.project_name} · {item.title}",
            expanded=False,
        ):
            render_workflow_card_header(
                item.status,
                item.title,
                workflow_card_metadata(item.actor, item.project_name),
            )
            if item.detail:
                st.write(item.detail)


def render_operations_tab(projects) -> None:
    snapshot = operations_dashboard_snapshot(projects)
    st.subheader("Operations")
    st.caption("Inspect agent behavior, workflow health, human attention, capability use, and system activity.")
    tabs = st.tabs(
        [
            "Agent Operations",
            "Agent Quality",
            "Eval Coverage",
            "Workflow Health",
            "Human Oversight",
            "Agent Performance",
            "Tool Usage",
            "Learning Progress",
            "System Activity",
        ]
    )
    renderers = (
        render_agent_operations_dashboard,
        render_agent_quality_dashboard,
        render_eval_coverage_dashboard,
        render_workflow_health_dashboard,
        render_human_oversight_dashboard,
        render_agent_performance_dashboard,
        render_tool_usage_dashboard,
        render_learning_progress_dashboard,
        render_system_activity_dashboard,
    )
    for tab, renderer in zip(tabs, renderers):
        with tab:
            renderer(snapshot)


def render_learning_tab() -> None:
    _apply_pending_learning_section()
    _apply_pending_learning_concept()
    st.markdown("<div class='os-learning-nav-anchor'></div>", unsafe_allow_html=True)
    sections = learning_section_labels()
    current = str(st.session_state.get(LEARNING_SECTION_STATE_KEY, "Profile"))
    if current not in sections:
        current = sections[0]
        st.session_state[LEARNING_SECTION_STATE_KEY] = current

    selected = st.segmented_control(
        "Learning navigation",
        sections,
        key=LEARNING_SECTION_STATE_KEY,
        label_visibility="collapsed",
        width="stretch",
    )
    section = str(selected or current)

    if section == "Profile":
        render_learning_profile_card()
    elif section == "Learn next":
        surface = learning_next_surface(
            has_active_session=load_learning_agent_session() is not None,
        )
        if surface == "session":
            render_learning_agent_session()
        else:
            render_learning_recommendations()
    elif section == "Learning plan":
        render_learning_concept_manager()
    elif section == "Builds" and learning_build_to_learn_enabled():
        render_build_to_learn_helper()
    else:
        render_learning_profile_card()


def render_projects_tab(projects) -> None:
    selected_project = selected_project_from_name(projects, st.session_state.get(PROJECT_SELECTION_STATE_KEY))
    if selected_project is not None:
        render_project_detail(selected_project.name, selected_project)
        return

    if st.session_state.get(PROJECT_SELECTION_STATE_KEY) and selected_project is None:
        st.session_state.pop(PROJECT_SELECTION_STATE_KEY, None)

    st.subheader(TOP_LEVEL_PROJECTS_LABEL)
    st.caption(open_project_page_caption())
    render_section_intro("Project chooser", "Scan status, work signals, and the next visible item before opening a project.")
    if not projects:
        st.info("No projects found in the workspace yet.")
    else:
        for row in project_card_rows(projects):
            columns = st.columns(project_card_row_weights(row))
            for index, column in enumerate(columns):
                if index >= len(row):
                    continue
                with column:
                    render_project_card(row[index])


def render_create_project_tab() -> None:
    st.subheader(TOP_LEVEL_CREATE_PROJECT_LABEL)
    st.write("Start a new AI Builder OS project from the shared template.")
    st.caption(
        "Default planner: Live PM. This path uses a live PM agent for new-project discovery, because a brand-new project starts with the least local context."
    )

    thread = _load_new_project_live_thread()
    if thread is None:
        with st.form("create-project-live-start"):
            project_name = st.text_input("Project name", placeholder="os-control-panel")
            display_name = st.text_input("Display name", placeholder="OS Control Panel")
            initial_idea = st.text_area(
                "Initial idea",
                placeholder="Describe the first requirement or project idea.",
                height=160,
            )
            reference_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key="new-project-live-start-images",
            )
            started = st.form_submit_button("Start live PM discovery")

        if started:
            if not project_name.strip() or not display_name.strip() or not initial_idea.strip():
                st.error("Project name, display name, and initial idea are all required.")
                return

            try:
                live_thread = start_live_pm_project_thread(
                    project_name,
                    display_name,
                    initial_idea,
                    image_files=_uploaded_image_payloads(reference_images),
                )
            except LivePMDiscoveryError as exc:
                st.error(str(exc))
            except Exception as exc:  # pragma: no cover - surfaced in UI
                st.error(f"Live PM discovery could not start: {exc}")
            else:
                _save_new_project_live_thread(live_thread)
                st.rerun()
        return

    st.markdown("**Live PM discovery**")
    st.caption(f"Project: {thread.display_name} (`{thread.project_name}`)")
    for message in thread.messages:
        role = "assistant" if message.role == "assistant" else "user"
        with st.chat_message(role):
            st.write(message.content)
            _render_message_attachments(message)
            _render_message_attachments(message)

    if not thread.draft_requirement:
        conversation_step = len(thread.messages)
        reply_key = f"new-project-live-reply-text-{thread.thread_id}-{conversation_step}"
        reply_images_key = f"new-project-live-reply-images-{thread.thread_id}-{conversation_step}"
        with st.form(f"new-project-live-reply-{thread.thread_id}"):
            reply = st.text_area(
                "Your reply",
                placeholder="Answer PM's question here.",
                height=110,
                key=reply_key,
            )
            reply_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=reply_images_key,
            )
            send = st.form_submit_button("Send reply")
            draft_now = st.form_submit_button("Draft requirements now")
            reset = st.form_submit_button("Start over")

        if reset:
            _save_new_project_live_thread(None)
            _clear_widget_state(reply_key, reply_images_key)
            st.rerun()

        if send:
            if not reply.strip():
                st.error("Reply is required before PM can continue the conversation.")
            else:
                try:
                    with st.spinner("PM is reviewing your reply..."):
                        updated = continue_live_pm_project_thread(
                            thread,
                            reply,
                            image_files=_uploaded_image_payloads(reply_images),
                        )
                except LivePMDiscoveryError as exc:
                    st.error(str(exc))
                except Exception as exc:  # pragma: no cover - surfaced in UI
                    st.error(f"Live PM discovery could not continue: {exc}")
                else:
                    _save_new_project_live_thread(updated)
                    _clear_widget_state(reply_key, reply_images_key)
                    st.rerun()

        if draft_now:
            try:
                with st.spinner("PM is drafting requirements..."):
                    drafted = draft_live_pm_project_thread(thread)
            except LivePMDiscoveryError as exc:
                st.error(str(exc))
            except Exception as exc:  # pragma: no cover - surfaced in UI
                st.error(f"Live PM could not draft requirements yet: {exc}")
            else:
                _save_new_project_live_thread(drafted)
                _clear_widget_state(reply_key, reply_images_key)
                st.rerun()
        return

    st.markdown("**Reviewed draft for the new project**")
    with st.container(border=True):
        st.write(f"**Requirement title:** {thread.draft_title or 'Initial requirement'}")
        st.text(thread.draft_requirement)

    with st.form(f"create-project-from-live-draft-{thread.thread_id}"):
        requirement_title = st.text_input(
            "Initial requirement title",
            value=thread.draft_title or "Initial requirement",
        )
        create = st.form_submit_button("Create project from reviewed draft")
        restart = st.form_submit_button("Discard draft and start over")

    if restart:
        _save_new_project_live_thread(None)
        st.rerun()

    if create:
        if not requirement_title.strip():
            st.error("Initial requirement title is required before creating the project.")
            return
        try:
            destination = create_project_from_reviewed_draft(
                thread.project_name,
                thread.display_name,
                requirement_title,
                thread.draft_requirement,
            )
        except FileExistsError:
            st.error("A project with that name already exists.")
        except Exception as exc:  # pragma: no cover - surfaced in UI
            st.error(f"Project creation failed: {exc}")
        else:
            _save_new_project_live_thread(None)
            relative_path = Path(destination).relative_to(Path.cwd())
            st.success(f"Created project at `{relative_path}`.")
            st.info("Refresh the page if you want to see it appear immediately in the workspace summary.")


def _option_index(options: list[str], value: str) -> int:
    try:
        return options.index(value)
    except ValueError:
        return 0


LEARNING_PROFILE_LEGACY_VALUE_MAP = {
    "product_background": {
        "Seasoned product leader building conceptual fluency in AI-assisted product systems.": "Product leader with some AI experience",
    },
    "technical_comfort": {
        "Comfortable reasoning about systems and workflows, but still building deeper fluency in modern AI architecture concepts.": "Comfortable reading architecture and tooling",
    },
    "current_trajectory": {
        "AI-assisted product systems, agent orchestration, evals, memory, retrieval, and structured collaboration.": "Design stronger agent workflows and evals",
    },
    "credibility_goal": {
        "Be able to explain important AI product-system concepts in simple, jargon-free language with real product judgment.": "Explain concepts simply to others",
    },
    "preferred_learning_style": {
        "Learn in context through explanation, practical examples, and bounded build-to-learn experiments.": "Implementation walkthroughs",
    },
    "current_learning_posture": {
        "Actively building, reflecting, and turning partial understanding into durable conceptual fluency.": "Applying in real work",
    },
}


def _normalize_learning_profile_choice(field: str, value: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        return normalized
    return LEARNING_PROFILE_LEGACY_VALUE_MAP.get(field, {}).get(normalized, normalized)


def _clear_widget_state(*keys: str) -> None:
    for key in keys:
        st.session_state.pop(key, None)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


REFLECTION_SCOPE_OPTIONS = ("os", "project", "career", "public-narrative")
REFLECTION_SOURCE_OPTIONS = (
    "implementation",
    "qa",
    "pm-discovery",
    "experience-review",
    "ui-review",
    "public-share",
    "workday",
    "meeting",
)
REFLECTION_ROUTE_OPTIONS = ("keep-private", "promote-to-reflection", "candidate-belief", "public-seed")
REFLECTION_CONFIDENCE_OPTIONS = ("low", "medium", "high")


def _reflection_helper_state() -> dict[str, str] | None:
    state = st.session_state.get(REFLECTION_HELPER_STATE_KEY)
    if isinstance(state, dict):
        return state
    return None


def _set_reflection_helper_state(state: dict[str, str]) -> None:
    st.session_state[REFLECTION_HELPER_STATE_KEY] = state


def _reset_reflection_helper_state() -> None:
    st.session_state.pop(REFLECTION_HELPER_STATE_KEY, None)


def _reflection_question_plan(state: dict[str, str]) -> list[dict[str, str]]:
    raw_plan = state.get("question_plan", "[]")
    try:
        parsed = json.loads(raw_plan)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _reflection_answer_rows(state: dict[str, str], questions: list[dict[str, str]]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for item in questions:
        field = item.get("field", "").strip()
        prompt = item.get("prompt", "").strip()
        answer = state.get(field, "").strip()
        if prompt and answer:
            rows.append((prompt, answer))
    return rows


def _reflection_field_value(state: dict[str, str], field: str) -> str:
    value = state.get(field, "").strip()
    if value:
        return value
    if field == "current_conclusion":
        return state.get("raw_signal", "").strip()
    if field == "what_happened":
        return state.get("raw_signal", "").strip()
    return "Needs follow-up refinement."


def render_reflection_helper() -> None:
    render_section_intro(
        "Private reflection helper",
        "Turn a raw signal into a stronger reflection draft through a short clarifying flow.",
    )
    st.caption("Local-only and private-first. Saved drafts go into `private/thinking/reflections.md`.")

    feedback = st.session_state.pop(REFLECTION_HELPER_FEEDBACK_KEY, "")
    if feedback:
        st.success(feedback)

    state = _reflection_helper_state()
    if state is None:
        with st.form("reflection-helper-start"):
            raw_signal = st.text_area(
                "Raw signal",
                placeholder="Capture the observation, tension, or pattern you do not want to lose.",
                height=140,
            )
            left, right = st.columns(2)
            scope = left.selectbox("Scope", REFLECTION_SCOPE_OPTIONS, index=0)
            source = right.selectbox("Source", REFLECTION_SOURCE_OPTIONS, index=0)
            started = st.form_submit_button("Start reflection")

        if started:
            if not raw_signal.strip():
                st.error("A raw signal is required before the reflection helper can begin.")
            else:
                with st.spinner("Preparing the first reflection question..."):
                    plan = build_dynamic_reflection_plan(raw_signal.strip())
                seeded_state = {
                    "step": "question",
                    "raw_signal": raw_signal.strip(),
                    "scope": scope,
                    "source": source,
                    "question_index": "0",
                    "question_plan": json.dumps(plan.get("questions", [])),
                }
                defaults = plan.get("defaults", {})
                if isinstance(defaults, dict):
                    for field, value in defaults.items():
                        if isinstance(field, str) and isinstance(value, str):
                            seeded_state[field] = value
                _set_reflection_helper_state(seeded_state)
                st.rerun()
        return

    with st.container(border=True):
        st.caption(f"Scope: {state.get('scope', 'os')} · Source: {state.get('source', 'workday')}")
        st.write(state.get("raw_signal", ""))

    questions = _reflection_question_plan(state)
    if not questions:
        st.error("The reflection helper could not recover its question plan. Start over to try again.")
        if st.button("Start over", key="reflection-helper-plan-reset"):
            _reset_reflection_helper_state()
            st.rerun()
        return

    answer_rows = _reflection_answer_rows(state, questions)
    if answer_rows:
        with st.container(border=True):
            st.caption("Reflection transcript")
            for prompt, answer in answer_rows:
                st.markdown(f"**{prompt}**")
                st.write(answer)

    step = state.get("step", "question")
    if step == "question":
        current_index = int(state.get("question_index", "0"))
        current_index = max(0, min(current_index, len(questions) - 1))
        current_question = questions[current_index]
        prompt = current_question.get("prompt", "What else feels important here?")
        field = current_question.get("field", "why_it_stood_out")
        st.caption(f"Question {current_index + 1} of up to {len(questions)}")
        with st.form(f"reflection-helper-question-{current_index}"):
            answer = st.text_area(prompt, height=140)
            next_label = "Draft reflection" if current_index + 1 >= len(questions) else "Next question"
            next_step = st.form_submit_button(next_label)
            restart = st.form_submit_button("Start over")
        if restart:
            _reset_reflection_helper_state()
            st.rerun()
        if next_step:
            if not answer.strip():
                st.error("Please answer the current question before moving on.")
            else:
                state[field] = answer.strip()
                next_index = current_index + 1
                if next_index >= len(questions):
                    state["step"] = "final"
                else:
                    with st.spinner("Preparing the next reflection question..."):
                        state["question_index"] = str(next_index)
                    state["step"] = "question"
                _set_reflection_helper_state(state)
                st.rerun()
        return

    with st.form("reflection-helper-final"):
        st.caption("Finish the reflection draft")
        confidence = st.selectbox(
            "How confident are you that this is a real pattern?",
            REFLECTION_CONFIDENCE_OPTIONS,
            index=1,
        )
        possible_route = st.selectbox("Possible route", REFLECTION_ROUTE_OPTIONS, index=0)
        saved = st.form_submit_button("Save reflection draft")
        restart = st.form_submit_button("Start over")
    if restart:
        _reset_reflection_helper_state()
        st.rerun()
    if saved:
        with st.spinner("Saving reflection draft..."):
            path = save_private_reflection_draft(
                state.get("raw_signal", ""),
                scope=state.get("scope", "os"),
                source=state.get("source", "workday"),
                what_happened=_reflection_field_value(state, "what_happened"),
                why_it_stood_out=_reflection_field_value(state, "why_it_stood_out"),
                current_conclusion=_reflection_field_value(state, "current_conclusion"),
                confidence=confidence,
                possible_route=possible_route,
                captured_via="dynamic reflection helper",
            )
        st.session_state[REFLECTION_HELPER_FEEDBACK_KEY] = f"Saved reflection draft to {_display_path(path)}."
        _reset_reflection_helper_state()
        st.rerun()


def _start_learning_agent_session(concept: str, *, where_encountered: str = "", current_understanding: str = "", what_is_unclear: str = "") -> None:
    start_learning_agent_session(
        concept,
        where_encountered=where_encountered,
        current_understanding=current_understanding,
        what_is_unclear=what_is_unclear,
    )
    st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learn next" if "Learn next" in learning_section_labels() else "Learning plan"

def _build_to_learn_state() -> dict[str, str] | None:
    raw = st.session_state.get(BUILD_TO_LEARN_STATE_KEY)
    if isinstance(raw, dict):
        return {str(key): str(value) for key, value in raw.items()}
    return None


def _set_build_to_learn_state(state: dict[str, str]) -> None:
    st.session_state[BUILD_TO_LEARN_STATE_KEY] = state


def _reset_build_to_learn_state() -> None:
    st.session_state.pop(BUILD_TO_LEARN_STATE_KEY, None)


def _set_build_to_learn_focus_concept(concept: str) -> None:
    normalized = concept.strip()
    if normalized:
        st.session_state[BUILD_TO_LEARN_FOCUS_CONCEPT_STATE_KEY] = normalized


def _build_to_learn_focus_concept() -> str:
    return str(st.session_state.get(BUILD_TO_LEARN_FOCUS_CONCEPT_STATE_KEY, "")).strip()


def _start_build_to_learn(concept: str, *, where_it_connects: str = "", current_gap: str = "") -> None:
    pathway = build_build_to_learn_pathway(
        concept,
        where_it_connects=where_it_connects,
        current_gap=current_gap,
    )
    _set_build_to_learn_state(
        {
            "concept": pathway.concept,
            "learning_goal": pathway.learning_goal,
            "experiment_slice": pathway.experiment_slice,
            "project_anchor": pathway.project_anchor,
            "success_signal": pathway.success_signal,
            "capture_prompt": pathway.capture_prompt,
        }
    )
    _set_build_to_learn_focus_concept(pathway.concept)
    st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Builds"


def _open_build_to_learn_pathway(concept: str) -> None:
    normalized = concept.strip()
    if not normalized:
        return
    _set_build_to_learn_focus_concept(normalized)
    st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Builds"


def _open_concept_manager(concept: str) -> None:
    normalized = concept.strip()
    if not normalized:
        return
    st.session_state[PENDING_LEARNING_CONCEPT_STATE_KEY] = normalized
    st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"


def render_learning_agent_session() -> None:
    render_section_intro(
        "Current learning session",
        "Stay with one concept here. Learn it clearly, ask follow-up questions, and mark it learned when it feels solid.",
    )

    feedback = st.session_state.pop(LEARNING_AGENT_FEEDBACK_KEY, "")
    if feedback:
        st.success(feedback)

    session = load_learning_agent_session()
    if session is None:
        st.info("No active learning session right now. Start one from a recommendation or a concept record.")
        return

    st.caption(f"{session.concept} · {session.session_status.title()} session")

    with st.container(border=True):
        st.markdown("**Simple explanation from the OS**")
        st.write(session.what_it_is or "No teaching brief captured yet.")
        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown("**Why it exists**")
            st.write(session.why_it_exists or "Not yet captured.")
            st.markdown("**Where it appears in the OS**")
            st.write(session.os_connection or "Not yet captured.")
        with detail_cols[1]:
            st.markdown("**Nearby distinction**")
            st.write(session.nearby_distinction or "Not yet captured.")
            st.markdown("**Why a product leader should care**")
            st.write(session.product_implication or "Not yet captured.")

        hierarchy_text = learning_concept_hierarchy(session.concept)
        if hierarchy_text:
            st.markdown("**Concept hierarchy**")
            st.code(hierarchy_text, language="text")

    implementation_visible_key = (
        f"os-learning-agent-implementation-visible::{session.concept.strip().lower()}"
    )
    implementation_visible = bool(st.session_state.get(implementation_visible_key, False))
    with st.container(border=True):
        st.markdown("**See it in the OS**")
        if session.implementation_walkthrough:
            implementation_button_label = (
                "Hide implementation in the OS" if implementation_visible else "Show implementation in the OS"
            )
        else:
            implementation_button_label = "Show implementation in the OS"
        if st.button(
            implementation_button_label,
            key=f"learning-agent-implementation-{session.concept.lower().replace(' ', '-')}",
            use_container_width=True,
        ):
            if session.implementation_walkthrough:
                st.session_state[implementation_visible_key] = not implementation_visible
            else:
                with st.spinner("Pulling together the implementation walkthrough..."):
                    request_learning_agent_implementation_walkthrough()
                st.session_state[implementation_visible_key] = True
            st.rerun()
        if session.implementation_walkthrough and implementation_visible:
            anchors = learning_implementation_anchors(session.concept)
            st.divider()
            st.markdown("**How this concept is implemented in the OS**")
            st.write(session.implementation_walkthrough)
            if session.implementation_relationships:
                st.markdown("**How the pieces fit together**")
                st.write(session.implementation_relationships)
            if anchors:
                st.markdown("**Implementation anchors**")
                for anchor in anchors:
                    with st.expander(f"{anchor.label} · {anchor.kind}"):
                        st.caption(anchor.path)
                        st.write(anchor.why_it_matters)
                        if anchor.excerpt:
                            st.code(anchor.excerpt, language="text")

    clarify_mode = str(st.session_state.get(LEARNING_AGENT_CLARIFY_MODE_KEY, ""))
    with st.container(border=True):
        st.markdown("**Need a follow-up clarification?**")
        clarify_cols = st.columns(4)
        with clarify_cols[0]:
            if st.button(
                "Explain more simply",
                key=f"learning-agent-clarify-simpler-{session.concept.lower().replace(' ', '-')}",
                use_container_width=True,
            ):
                with st.spinner("Reframing it more simply..."):
                    request_learning_agent_clarification("simpler")
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()
        with clarify_cols[1]:
            if st.button(
                "Clarify a confusion",
                key=f"learning-agent-clarify-confusion-{session.concept.lower().replace(' ', '-')}",
                use_container_width=True,
            ):
                st.session_state[LEARNING_AGENT_CLARIFY_MODE_KEY] = "specific_confusion"
                st.rerun()
        with clarify_cols[2]:
            if st.button(
                "Give another example",
                key=f"learning-agent-clarify-example-{session.concept.lower().replace(' ', '-')}",
                use_container_width=True,
            ):
                with st.spinner("Finding another example..."):
                    request_learning_agent_clarification("another_example")
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()
        with clarify_cols[3]:
            if st.button(
                "Compare nearby concept",
                key=f"learning-agent-clarify-compare-{session.concept.lower().replace(' ', '-')}",
                use_container_width=True,
            ):
                st.session_state[LEARNING_AGENT_CLARIFY_MODE_KEY] = "nearby_comparison"
                st.rerun()

        if clarify_mode == "specific_confusion":
            with st.form(f"learning-agent-clarify-detail-{session.concept.lower().replace(' ', '-')}"):
                confusion_detail = st.text_area(
                    "What specifically feels unclear?",
                    placeholder="Name the exact part you want the OS to clarify.",
                    height=90,
                )
                submit_cols = st.columns(2)
                with submit_cols[0]:
                    ask_clarification = st.form_submit_button("Ask for clarification")
                with submit_cols[1]:
                    cancel_clarification = st.form_submit_button("Cancel")
            if cancel_clarification:
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()
            if ask_clarification:
                with st.spinner("Clarifying that specific confusion..."):
                    request_learning_agent_clarification("specific_confusion", detail=confusion_detail)
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()

        if clarify_mode == "nearby_comparison":
            related_targets: list[str] = []
            seen_targets: set[str] = set()
            for relationship in learning_concept_relationships(session.concept):
                target = relationship.target.strip()
                if not target:
                    continue
                normalized = target.lower()
                if normalized == session.concept.strip().lower() or normalized in seen_targets:
                    continue
                seen_targets.add(normalized)
                related_targets.append(target)

            with st.form(f"learning-agent-clarify-compare-detail-{session.concept.lower().replace(' ', '-')}"):
                if related_targets:
                    comparison_target = st.selectbox(
                        "Which concept do you want to compare it to?",
                        options=related_targets,
                        index=0,
                    )
                    comparison_detail = st.text_area(
                        "Anything specific you want the comparison to focus on?",
                        placeholder="Optional: name the exact distinction you want clarified.",
                        height=90,
                    )
                else:
                    comparison_target = ""
                    comparison_detail = st.text_area(
                        "Which concept do you want to compare it to?",
                        placeholder="Name the concept you want the OS to compare against.",
                        height=90,
                    )
                submit_cols = st.columns(2)
                with submit_cols[0]:
                    ask_comparison = st.form_submit_button("Compare concepts")
                with submit_cols[1]:
                    cancel_comparison = st.form_submit_button("Cancel")
            if cancel_comparison:
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()
            if ask_comparison:
                detail_parts = [part.strip() for part in (comparison_target, comparison_detail) if part.strip()]
                with st.spinner("Comparing those concepts..."):
                    request_learning_agent_clarification(
                        "nearby_comparison",
                        detail=" — ".join(detail_parts),
                    )
                st.session_state.pop(LEARNING_AGENT_CLARIFY_MODE_KEY, None)
                st.rerun()

        if session.clarification_response:
            st.divider()
            st.markdown("**Clarification from the OS**")
            st.write(session.clarification_response)

    if session.latest_explanation_back:
        with st.container(border=True):
            st.markdown("**Latest captured understanding**")
            st.write(session.latest_explanation_back)
            if session.detected_gaps:
                st.markdown("**What still seems weak**")
                for gap in session.detected_gaps:
                    st.caption(f"- {gap}")
            st.markdown("**Coach note**")
            st.write(session.coach_message)

    if session.next_move == "hand_back":
        with st.container(border=True):
            st.markdown("**The OS is pausing here on purpose**")
            if session.hand_back_reason:
                st.write(session.hand_back_reason)
            st.write(session.coach_message)
            with st.form(f"learning-agent-handback-{session.concept.lower().replace(' ', '-')}"):
                narrower_question = st.text_area(
                    "Pick one narrower question or concrete example",
                    placeholder="For example: 'When would I use evals before trace grading?'",
                    height=110,
                )
                handback_cols = st.columns(2)
                with handback_cols[0]:
                    retry_narrower = st.form_submit_button("Continue with narrower question")
                with handback_cols[1]:
                    exit_to_concepts = st.form_submit_button("Back to learning plan")
            if exit_to_concepts:
                st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"
                st.rerun()
            if retry_narrower:
                if not narrower_question.strip():
                    st.error("Please name one narrower question or example before continuing.")
                else:
                    with st.spinner("Narrowing the learning question..."):
                        request_learning_agent_clarification("specific_confusion", detail=narrower_question)
                    st.rerun()
        return

    if session.next_move in {"explain_back", "clarify"}:
        with st.container(border=True):
            st.markdown("**When this feels solid**")
            st.caption("Keep going until this concept feels solid, then mark it learned here. You can leave and resume later.")
            action_cols = st.columns(2)
            with action_cols[0]:
                mark_learned = st.button(
                    "Mark learned",
                    key=f"learning-agent-direct-mark-learned-{session.concept.lower().replace(' ', '-')}",
                    type="primary",
                    use_container_width=True,
                )
            with action_cols[1]:
                exit_to_concepts = st.button(
                    "Back to learning plan",
                    key=f"learning-agent-direct-plan-{session.concept.lower().replace(' ', '-')}",
                    use_container_width=True,
                )
        if exit_to_concepts:
            st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"
            st.rerun()
        if mark_learned:
            save_learning_concept_management_update(
                session.concept,
                status="learned",
                current_understanding=session.latest_explanation_back or session.current_understanding,
                open_questions="",
                note="Concept marked learned from V2 tutoring session.",
                source="learning agent session",
            )
            clear_learning_agent_session()
            st.session_state[LEARNING_AGENT_FEEDBACK_KEY] = "Marked concept learned."
            _open_concept_manager(session.concept)
            st.rerun()
        return

    if session.next_move == "build_to_learn" and learning_build_to_learn_enabled():
        with st.container(border=True):
            st.markdown("**Recommended next move**")
            st.write(session.coach_message)
            route_cols = st.columns(3)
            with route_cols[0]:
                if st.button("Confirm build-to-learn", key=f"learning-agent-build-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
                    save_learning_concept_management_update(
                        session.concept,
                        status="build_to_learn",
                        current_understanding=session.latest_explanation_back or session.current_understanding,
                        open_questions=" ".join(session.detected_gaps) or session.what_is_unclear,
                        note="Confirmed build-to-learn progression from learning-agent session.",
                        source="learning agent session",
                    )
                    clear_learning_agent_session()
                    _start_build_to_learn(
                        session.concept,
                        where_it_connects=session.os_connection,
                        current_gap=" ".join(session.detected_gaps) or session.what_is_unclear or session.coach_message,
                    )
                    st.rerun()
            with route_cols[1]:
                if st.button("Keep in progress", key=f"learning-agent-save-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
                    save_learning_concept_management_update(
                        session.concept,
                        status="in_progress",
                        current_understanding=session.latest_explanation_back or session.current_understanding,
                        open_questions=" ".join(session.detected_gaps),
                        note="Kept concept in progress instead of routing to build-to-learn.",
                        source="learning agent session",
                    )
                    clear_learning_agent_session()
                    st.session_state[LEARNING_AGENT_FEEDBACK_KEY] = "Kept concept in progress."
                    st.rerun()
            with route_cols[2]:
                if st.button("Back to learning plan", key=f"learning-agent-manage-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
                    st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"
                    st.rerun()
        return

    with st.container(border=True):
        st.markdown("**Recommended next move**")
        st.write(session.coach_message)
    decision_cols = st.columns(3)
    with decision_cols[0]:
        if st.button("Mark learned", key=f"learning-agent-mark-learned-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
            with st.spinner("Marking concept learned..."):
                save_learning_concept_management_update(
                    session.concept,
                    status="learned",
                    current_understanding=session.latest_explanation_back or session.current_understanding,
                    open_questions="",
                    note="Marked learned from learning-agent session.",
                    source="learning agent session",
                )
                clear_learning_agent_session()
            st.session_state[LEARNING_AGENT_FEEDBACK_KEY] = "Marked concept learned."
            st.rerun()
    with decision_cols[1]:
        if st.button("Keep in progress", key=f"learning-agent-keep-progress-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
            with st.spinner("Keeping concept in progress..."):
                save_learning_concept_management_update(
                    session.concept,
                    status="in_progress",
                    current_understanding=session.latest_explanation_back or session.current_understanding,
                    open_questions=" ".join(session.detected_gaps) or session.what_is_unclear,
                    note="Kept concept in progress after learning-agent recommendation.",
                    source="learning agent session",
                )
                clear_learning_agent_session()
            st.session_state[LEARNING_AGENT_FEEDBACK_KEY] = "Kept concept in progress."
            st.rerun()
    with decision_cols[2]:
        if st.button("Back to learning plan", key=f"learning-agent-exit-{session.concept.lower().replace(' ', '-')}", use_container_width=True):
            st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"
            st.rerun()


def render_learning_profile_card() -> None:
    render_section_intro(
        "Learning profile",
        "Start here. The agent uses this profile to decide what to teach first, how much OS context to assume, and how to explain implementation clearly.",
    )

    feedback = st.session_state.pop(LEARNING_PROFILE_FEEDBACK_KEY, "")
    if feedback:
        st.success(feedback)

    profile = load_learning_profile()
    profile = {
        field: _normalize_learning_profile_choice(field, value)
        for field, value in profile.items()
    }
    with st.container(border=True):
        st.markdown("**Saved profile**")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Product background**")
            st.write(profile["product_background"])
            st.markdown("**Current trajectory**")
            st.write(profile["current_trajectory"])
            st.markdown("**Technical comfort**")
            st.write(profile["technical_comfort"])
            st.markdown("**AI Builder OS understanding**")
            st.write(profile["os_understanding_level"])
        with cols[1]:
            st.markdown("**Credibility goal**")
            st.write(profile["credibility_goal"])
            st.markdown("**Preferred learning style**")
            st.write(profile["preferred_learning_style"])
            st.markdown("**Current learning posture**")
            st.write(profile["current_learning_posture"])

    editor_open = bool(st.session_state.get(LEARNING_PROFILE_EDITOR_OPEN_STATE_KEY, False))
    toggle_label = "Close profile editor" if editor_open else "Edit learning profile"
    if st.button(toggle_label, key="learning-profile-editor-toggle", type="primary", use_container_width=True):
        st.session_state[LEARNING_PROFILE_EDITOR_OPEN_STATE_KEY] = not editor_open
        st.rerun()

    if st.session_state.get(LEARNING_PROFILE_EDITOR_OPEN_STATE_KEY, False):
        with st.form("learning-profile-form"):
            st.markdown("**Who you are and where you are starting from**")
            product_background = st.selectbox(
                "Product background",
                options=LEARNING_PROFILE_BACKGROUND_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_BACKGROUND_OPTIONS), profile["product_background"]),
            )
            technical_comfort = st.radio(
                "Technical comfort",
                options=LEARNING_PROFILE_TECHNICAL_COMFORT_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_TECHNICAL_COMFORT_OPTIONS), profile["technical_comfort"]),
                horizontal=True,
            )
            os_understanding_level = st.radio(
                "Current understanding of AI Builder OS",
                options=OS_UNDERSTANDING_LEVEL_OPTIONS,
                index=_option_index(list(OS_UNDERSTANDING_LEVEL_OPTIONS), profile["os_understanding_level"]),
                horizontal=True,
            )
            st.markdown("**What kind of learning help you want from the agent**")
            current_trajectory = st.radio(
                "Current trajectory",
                options=LEARNING_PROFILE_TRAJECTORY_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_TRAJECTORY_OPTIONS), profile["current_trajectory"]),
            )
            credibility_goal = st.radio(
                "Credibility goal",
                options=LEARNING_PROFILE_CREDIBILITY_GOAL_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_CREDIBILITY_GOAL_OPTIONS), profile["credibility_goal"]),
            )
            preferred_learning_style = st.selectbox(
                "Preferred learning style",
                options=LEARNING_PROFILE_STYLE_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_STYLE_OPTIONS), profile["preferred_learning_style"]),
            )
            current_learning_posture = st.selectbox(
                "Current learning posture",
                options=LEARNING_PROFILE_POSTURE_OPTIONS,
                index=_option_index(list(LEARNING_PROFILE_POSTURE_OPTIONS), profile["current_learning_posture"]),
            )
            saved = st.form_submit_button("Save learning profile", type="primary")
        if saved:
            with st.spinner("Saving learning profile..."):
                save_learning_profile(
                    product_background=product_background,
                    technical_comfort=technical_comfort,
                    os_understanding_level=os_understanding_level,
                    current_trajectory=current_trajectory,
                    credibility_goal=credibility_goal,
                    preferred_learning_style=preferred_learning_style,
                    current_learning_posture=current_learning_posture,
                )
            st.session_state[LEARNING_PROFILE_FEEDBACK_KEY] = "Saved learning profile."
            st.session_state[LEARNING_PROFILE_EDITOR_OPEN_STATE_KEY] = False
            st.rerun()


def _learning_plan_family_card_markup(family, *, flattened_steps, next_index: int) -> str:
    step_lines: list[str] = []
    for step in family.steps:
        flattened_index = next(
            (index for index, item in enumerate(flattened_steps) if item.concept == step.concept),
            0,
        )
        if step.is_completed:
            icon = "<span style='color:#2f855a; font-weight:700;'>✓</span>"
            label_style = "font-weight:600; color:rgba(49, 51, 63, 0.96);"
        elif step.is_current:
            icon = "<span style='color:#ff4b4b; font-weight:700;'>➜</span>"
            label_style = "font-weight:700; color:#ff4b4b;"
        elif flattened_index == next_index:
            icon = "<span style='color:#6b7280; font-weight:700;'>◉</span>"
            label_style = "font-weight:600; color:rgba(49, 51, 63, 0.9);"
        else:
            icon = "<span style='color:#9ca3af; font-weight:700;'>○</span>"
            label_style = "color:#6b7280;"
        indent_px = max(0, step.depth * 18)
        step_lines.append(
            "<div class='os-learning-plan-step' style='padding-left: "
            f"{indent_px}px;'>"
            f"{icon} <span class='os-learning-plan-step-label' style='{label_style}'>{escape(step.concept)}</span>"
            "</div>"
        )

    return (
        "<div class='os-learning-plan-card'>"
        f"<div class='os-learning-plan-card-title'>{escape(family.family_name)}</div>"
        f"<div class='os-learning-plan-card-summary'>{escape(family.family_summary)}</div>"
        "<div class='os-learning-plan-steps'>"
        + "".join(step_lines)
        + "</div></div>"
    )


def render_personalized_learning_plan():
    plan = personalized_learning_plan()
    if plan is None:
        st.info("The learning agent could not build a plan yet. Save the profile first, then return here.")
        return None

    flattened_steps = [step for family in plan.families for step in family.steps]
    total_steps = len(flattened_steps)
    completed_steps = sum(1 for step in flattened_steps if step.is_completed)
    current_index = next((index for index, step in enumerate(flattened_steps) if step.is_current), 0)
    next_index = current_index + 1

    st.markdown(
        f"""
        <div class="os-learning-plan-summary">
            <div class="os-learning-plan-summary-item">
                <div class="os-learning-plan-summary-label">Current family</div>
                <div class="os-learning-plan-summary-family">{escape(plan.current_family_name)}</div>
            </div>
            <div class="os-learning-plan-summary-item">
                <div class="os-learning-plan-summary-label">Plan progress</div>
                <div class="os-learning-plan-summary-value">{current_index + 1} of {total_steps}</div>
            </div>
            <div class="os-learning-plan-summary-item">
                <div class="os-learning-plan-summary-label">Completed</div>
                <div class="os-learning-plan-summary-value">{completed_steps}/{total_steps}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total_steps:
        st.progress(completed_steps / total_steps)

    st.markdown(
        """
        <div class="os-learning-plan-legend">
            <span style="color:#2f855a;">✓</span> Completed ·
            <span style="color:#ff4b4b;">➜</span> Current ·
            <span style="color:#6b7280;">◉</span> Next ·
            <span style="color:#9ca3af;">○</span> Later
        </div>
        """,
        unsafe_allow_html=True,
    )

    family_cards = "".join(
        _learning_plan_family_card_markup(
            family,
            flattened_steps=flattened_steps,
            next_index=next_index,
        )
        for family in plan.families
    )
    st.markdown(f"<div class='os-learning-plan-grid'>{family_cards}</div>", unsafe_allow_html=True)

    return plan


def render_learning_recommendations() -> None:
    st.markdown("### Learn next")
    st.caption("Stay with the current plan step here. The broader route stays visible in `Learning plan`.")
    plan = personalized_learning_plan()
    recommendations = list_learning_concept_recommendations()
    if plan is None and not recommendations:
        st.caption("No learning plan or recommendation surfaced right now. Save the profile first.")
        return

    current_concept = plan.current_concept if plan is not None else recommendations[0].concept
    views = list_learning_concept_views()
    view = next((item for item in views if item.concept == current_concept), None)
    concept_state = view.concept_state if view is not None else None
    where_it_connects = ""
    current_gap = ""
    recommendation = next((item for item in recommendations if item.concept == current_concept), None)
    if recommendation is None and recommendations:
        recommendation = recommendations[0]
    if view is not None and view.recommendation is not None:
        where_it_connects = view.recommendation.where_it_connects
        current_gap = view.recommendation.current_gap
    elif recommendation is not None:
        where_it_connects = recommendation.where_it_connects
        current_gap = recommendation.current_gap

    with st.container(border=True):
        st.markdown(f"## {current_concept}")
        if plan is not None:
            st.caption(f"Family: {plan.current_family_name}")
        st.write("Start the live learning session when you are ready to stay with this concept properly.")

        button_label = f"Start learning {current_concept}"
        if st.button(
            button_label,
            key=f"learning-current-step-{current_concept.lower().replace(' ', '-')}",
            type="primary",
            use_container_width=True,
        ):
            with st.status(f"Starting {current_concept} and preparing the learning session...", expanded=False):
                _start_learning_agent_session(
                    current_concept,
                    where_encountered=where_it_connects,
                    current_understanding=concept_state.current_understanding if concept_state is not None else "",
                    what_is_unclear=(
                        concept_state.open_questions
                        if concept_state is not None and concept_state.open_questions.strip()
                        else current_gap
                    ),
                )
            st.rerun()

        if st.button(
            "Back to learning plan",
            key=f"learning-current-step-plan-{current_concept.lower().replace(' ', '-')}",
            use_container_width=True,
        ):
            st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learning plan"
            st.rerun()


def render_learning_concept_manager() -> None:
    render_section_intro(
        "Learning plan",
        "This is your guided route through the concept catalog. Use it to see where you are, what is already behind you, and what the agent wants you to learn next.",
    )

    feedback = st.session_state.pop(LEARNING_MANAGER_FEEDBACK_KEY, "")
    if feedback:
        st.success(feedback)

    plan = render_personalized_learning_plan()
    if plan is None:
        return
    current_concept = plan.current_concept
    st.session_state[LEARNING_CONCEPT_SELECTION_STATE_KEY] = current_concept

    with st.container(border=True):
        st.markdown(f"**Current step:** {current_concept}")
        st.write("Move into `Learn next` when you are ready to stay with this concept and learn it properly.")
        active_session = load_learning_agent_session()
        if active_session is not None and active_session.concept == current_concept:
            button_label = "Resume current step in Learn next"
        else:
            button_label = "Start current step in Learn next"
        if st.button(
            button_label,
            key=f"learning-plan-continue-{current_concept.lower().replace(' ', '-')}",
            type="primary",
            use_container_width=True,
        ):
            if active_session is None or active_session.concept != current_concept:
                views = list_learning_concept_views()
                view = next((item for item in views if item.concept == current_concept), None)
                recommendation = view.recommendation if view is not None else None
                concept_state = view.concept_state if view is not None else None
                with st.status(f"Starting {current_concept} and preparing the learning session...", expanded=False):
                    _start_learning_agent_session(
                        current_concept,
                        where_encountered=recommendation.where_it_connects if recommendation is not None else "",
                        current_understanding=concept_state.current_understanding if concept_state is not None else "",
                        what_is_unclear=(
                            concept_state.open_questions
                            if concept_state is not None and concept_state.open_questions.strip()
                            else (recommendation.current_gap if recommendation is not None else "")
                        ),
                    )
            else:
                st.session_state[PENDING_LEARNING_SECTION_STATE_KEY] = "Learn next"
            st.rerun()
def render_build_to_learn_helper() -> None:
    render_section_intro(
        "Build-to-learn pathways",
        "Turn a concept into one bounded experiment so the OS can help you learn by building, not just by reading.",
    )
    st.caption("Local-only and private-first. Saved pathways go into `private/learning/build-to-learn.md`.")

    feedback = st.session_state.pop(BUILD_TO_LEARN_FEEDBACK_KEY, "")
    if feedback:
        st.success(feedback)

    state = _build_to_learn_state()
    focus_concept = _build_to_learn_focus_concept()
    focus_view = learning_concept_view(focus_concept) if focus_concept else None
    linked_build = focus_view.build_state if focus_view is not None else None

    if state is None and linked_build is not None:
        with st.container(border=True):
            header_left, header_right = st.columns([3, 1.1])
            header_left.markdown(f"### {linked_build.concept}")
            header_left.caption("Linked build pathway")
            header_right.metric("Pathway", linked_build.status.replace("_", " ").title())

            st.markdown("**Learning goal**")
            st.write(linked_build.learning_goal or "No learning goal captured yet.")
            st.markdown("**Bounded experiment slice**")
            st.write(linked_build.experiment_slice or "No experiment slice captured yet.")

            detail_left, detail_right = st.columns(2)
            detail_left.markdown("**Project anchor**")
            detail_left.write(linked_build.project_anchor or "No project anchor captured yet.")
            detail_right.markdown("**Success signal**")
            detail_right.write(linked_build.success_signal or "No success signal captured yet.")

            if linked_build.capture_prompt:
                st.markdown("**Capture prompt**")
                st.write(linked_build.capture_prompt)
            if linked_build.outcome_summary:
                st.markdown("**What building taught you**")
                st.write(linked_build.outcome_summary)
            if linked_build.unresolved_after_build:
                st.markdown("**Still unclear after building**")
                st.write(linked_build.unresolved_after_build)

            action_cols = st.columns(3)
            with action_cols[0]:
                if st.button(
                    "Open concept",
                    key=f"build-linked-open-concept-{linked_build.concept.lower().replace(' ', '-')}",
                    use_container_width=True,
                ):
                    _open_concept_manager(linked_build.concept)
                    st.rerun()
            with action_cols[1]:
                if st.button(
                    "Capture learning from build",
                    key=f"build-linked-capture-{linked_build.concept.lower().replace(' ', '-')}",
                    use_container_width=True,
                ):
                    st.session_state[BUILD_TO_LEARN_CAPTURE_STATE_KEY] = linked_build.concept
                    st.rerun()
            with action_cols[2]:
                if st.button(
                    "Refresh build plan",
                    key=f"build-linked-refresh-{linked_build.concept.lower().replace(' ', '-')}",
                    use_container_width=True,
                ):
                    _start_build_to_learn(
                        linked_build.concept,
                        current_gap=linked_build.unresolved_after_build or linked_build.capture_prompt,
                    )
                    st.rerun()

        capture_target = str(st.session_state.get(BUILD_TO_LEARN_CAPTURE_STATE_KEY, ""))
        if capture_target == linked_build.concept:
            capture_view = learning_concept_view(linked_build.concept)
            concept_state = capture_view.concept_state if capture_view is not None else None
            with st.form(f"learning-build-capture-form-{linked_build.concept.lower().replace(' ', '-')}"):
                updated_understanding = st.text_area(
                    "How would you explain the concept now?",
                    value=concept_state.current_understanding if concept_state is not None else "",
                    height=120,
                )
                outcome_summary = st.text_area(
                    "What did building teach you?",
                    placeholder="Capture what became clearer in plain language.",
                    height=120,
                )
                unresolved_after_build = st.text_area(
                    "What is still unclear?",
                    value=concept_state.open_questions if concept_state is not None else linked_build.unresolved_after_build,
                    placeholder="Keep any remaining doubts visible.",
                    height=110,
                )
                learning_effect = st.radio(
                    "What happened to the concept?",
                    options=("strengthened", "reopened"),
                    format_func=lambda value: "Strengthened understanding" if value == "strengthened" else "Reopened the concept",
                    horizontal=True,
                )
                capture_cols = st.columns(2)
                with capture_cols[0]:
                    capture_save = st.form_submit_button("Save build learning")
                with capture_cols[1]:
                    capture_cancel = st.form_submit_button("Cancel")
            if capture_cancel:
                st.session_state.pop(BUILD_TO_LEARN_CAPTURE_STATE_KEY, None)
                st.rerun()
            if capture_save:
                with st.spinner("Capturing build-to-learn outcome..."):
                    path = save_build_to_learn_outcome(
                        linked_build.concept,
                        outcome_summary=outcome_summary,
                        unresolved_after_build=unresolved_after_build,
                        learning_effect=learning_effect,
                        current_understanding=updated_understanding,
                    )
                st.session_state[BUILD_TO_LEARN_FEEDBACK_KEY] = (
                    f"Captured build-to-learn outcome in {_display_path(path)}."
                )
                st.session_state.pop(BUILD_TO_LEARN_CAPTURE_STATE_KEY, None)
                st.rerun()
        return

    if state is None:
        with st.form("build-to-learn-start"):
            concept = st.text_input("Concept to learn by building", placeholder="e.g. RAG, trace grading, memory systems")
            where_it_connects = st.text_area(
                "Where does it connect to current work?",
                placeholder="Project, workflow gap, agent-quality issue, memory idea, or architecture pressure.",
                height=100,
            )
            current_gap = st.text_area(
                "What feels missing right now?",
                placeholder="Describe the understanding gap you want the experiment to close.",
                height=100,
            )
            started = st.form_submit_button("Plan pathway")
        if started:
            if not concept.strip():
                st.error("A concept is required before the build-to-learn helper can begin.")
            else:
                _start_build_to_learn(
                    concept,
                    where_it_connects=where_it_connects,
                    current_gap=current_gap,
                )
                st.rerun()
        return

    with st.container(border=True):
        st.caption(state.get("concept", "Concept"))
        st.markdown("**Learning goal**")
        st.write(state.get("learning_goal", ""))
        st.markdown("**Bounded experiment slice**")
        st.write(state.get("experiment_slice", ""))
        st.markdown("**Project anchor**")
        st.write(state.get("project_anchor", ""))
        st.markdown("**Success signal**")
        st.write(state.get("success_signal", ""))
        st.markdown("**What to capture afterward**")
        st.write(state.get("capture_prompt", ""))

    with st.form("build-to-learn-step-1"):
        learning_goal = st.text_area(
            "Learning goal",
            value=state.get("learning_goal", ""),
            height=100,
        )
        experiment_slice = st.text_area(
            "Bounded experiment slice",
            value=state.get("experiment_slice", ""),
            height=120,
        )
        project_anchor = st.text_area(
            "Project anchor",
            value=state.get("project_anchor", ""),
            height=100,
        )
        success_signal = st.text_area(
            "Success signal",
            value=state.get("success_signal", ""),
            height=100,
        )
        capture_prompt = st.text_area(
            "Capture prompt for later reflection/learning",
            value=state.get("capture_prompt", ""),
            height=100,
        )
        saved = st.form_submit_button("Save build-to-learn pathway")
        restart = st.form_submit_button("Start over")
    if restart:
        _reset_build_to_learn_state()
        st.rerun()
    if saved:
        with st.spinner("Saving build-to-learn pathway..."):
            path = save_private_build_to_learn_pathway(
                state.get("concept", ""),
                learning_goal=learning_goal,
                experiment_slice=experiment_slice,
                project_anchor=project_anchor,
                success_signal=success_signal,
                capture_prompt=capture_prompt,
                captured_via="build-to-learn helper",
            )
        st.session_state[BUILD_TO_LEARN_FEEDBACK_KEY] = f"Saved build-to-learn pathway to {_display_path(path)}."
        _reset_build_to_learn_state()
        st.rerun()


def render_done_requirement(project_name: str, record: RequirementRecord) -> None:
    with st.expander(f"{record.id} — {record.title}", expanded=False):
        st.caption("Status: DONE")
        if record.priority:
            st.write(f"Priority: {record.priority}")
        if record.effort:
            st.write(f"Effort: {record.effort}")
        st.write(record.description)
        render_manual_verification_panel(project_name, record)
        st.info("Completed requirements stay read-only for product content, but manual verification evidence can still be updated here.")


def render_completed_requirements_archive(project_name: str, done_records: list[RequirementRecord]) -> None:
    st.markdown(f"**Completed archive ({len(done_records)})**")
    with st.expander("Browse completed requirements", expanded=False):
        options = [f"{record.id} — {record.title}" for record in done_records]
        selected = st.selectbox(
            "Completed requirement",
            options,
            key="completed-requirement-archive-select",
        )
        selected_id = selected.split(" — ", 1)[0]
        record = next(item for item in done_records if item.id == selected_id)
        st.caption(requirement_card_metadata(record))
        st.write(record.description)
        render_manual_verification_panel(project_name, record)


def render_requirement_clarifications(project_name: str, record: RequirementRecord) -> None:
    clarifications = active_requirement_clarifications(project_name, record.id)
    if not clarifications:
        return

    st.warning("PM clarification needed before this requirement should move forward.")
    for clarification in clarifications:
        with st.container(border=True):
            st.write(clarification.summary or f"Clarification needed for {clarification.requirement_id}.")
            for question in clarification.questions:
                st.write(f"- {question}")
            if st.button(
                "Mark clarification resolved",
                key=f"resolve-clarification-{project_name}-{clarification.clarification_id}",
            ):
                resolved = resolve_pm_clarification(project_name, clarification.clarification_id)
                st.success(f"Resolved clarification {resolved.clarification_id}. Refresh to see the updated state.")


def render_create_requirement_clarification(project_name: str, record: RequirementRecord) -> None:
    with st.expander("Raise PM clarification request", expanded=False):
        with st.form(f"pm-clarification-{project_name}-{record.id}"):
            summary = st.text_input(
                "Summary",
                placeholder="Why does PM need clarification before tasking this requirement?",
            )
            questions_text = st.text_area(
                "Questions",
                placeholder="Enter one clarification question per line.",
                height=100,
            )
            submitted = st.form_submit_button("Save PM clarification")

        if submitted:
            questions = [line.strip() for line in questions_text.splitlines() if line.strip()]
            if not summary.strip() or not questions:
                st.error("A summary and at least one question are required.")
            else:
                clarification = save_pm_clarification(
                    project_name,
                    requirement_id=record.id,
                    requirement_title=record.title,
                    summary=summary,
                    questions=questions,
                )
                st.success(f"Saved PM clarification {clarification.clarification_id}. Refresh to see it in the live workflow state.")


def render_requirement_implementation_state(project_name: str, record: RequirementRecord) -> None:
    latest_run = latest_requirement_implementation(project_name, record.id)
    active_run = active_implementation_run(project_name)

    current_run = None
    if active_run is not None and active_run.project_name == project_name and active_run.requirement_id == record.id:
        current_run = active_run

    if current_run is not None:
        st.progress(implementation_progress_percent(current_run.status))
        st.caption(implementation_progress_message(current_run.status))
        if current_run.status in {"QUEUED", "RUNNING"}:
            return

    if latest_run is None:
        return

    if latest_run.status in {"QUEUED", "RUNNING"}:
        st.progress(implementation_progress_percent(latest_run.status))
        st.caption(implementation_progress_message(latest_run.status))
        return

    with st.container(border=True):
        st.caption(f"Latest implementation outcome: {latest_run.status}")
        st.progress(implementation_progress_percent(latest_run.status))
        st.caption(implementation_progress_message(latest_run.status))
        if latest_run.summary:
            st.write(latest_run.summary)
        if latest_run.error:
            st.error(latest_run.error)


def render_requirement_delete_control(project_name: str, record: RequirementRecord) -> None:
    with st.expander("Delete requirement", expanded=False):
        st.warning("This removes the requirement from the project file. There is no undo in this version.")
        confirmed = st.checkbox(
            f"Confirm deletion of {record.id}",
            key=f"delete-confirm-{project_name}-{record.id}",
        )
        if st.button(
            "Delete requirement",
            key=f"delete-requirement-{project_name}-{record.id}",
            disabled=not confirmed,
        ):
            try:
                deleted = delete_requirement(project_name, record.id)
            except Exception as exc:  # pragma: no cover - surfaced in UI
                st.error(f"Could not delete requirement: {exc}")
            else:
                st.success(
                    f"Deleted {deleted.deleted_requirement.id}. "
                    f"Removed {deleted.removed_tasks} linked task(s), "
                    f"updated {deleted.updated_tasks} multi-linked task(s), "
                    f"removed {deleted.removed_clarifications} clarification artifact(s), "
                    f"and removed {deleted.removed_implementation_runs} implementation run record(s). "
                    "Refresh the page to see the updated requirements."
                )


def verification_status_options() -> tuple[str, ...]:
    return ("NOT_RUN", "PASS", "FAIL")


def verification_status_label(status: str) -> str:
    labels = {
        "NOT_RUN": "Not run",
        "PASS": "Pass",
        "FAIL": "Fail",
    }
    return labels.get(status, status.title())


def render_manual_verification_panel(project_name: str, record: RequirementRecord) -> None:
    plan = manual_verification_plan(project_name, record.id)
    summary = manual_verification_summary(project_name, record.id)

    st.markdown("**Manual verification**")
    with st.container(border=True):
        metric_left, metric_middle, metric_right = st.columns(3)
        metric_left.metric("Checks", summary.total_checks)
        metric_middle.metric("Passed", summary.passed_checks)
        metric_right.metric("Failed", summary.failed_checks)

        if summary.signoff_state == "READY_FOR_SIGNOFF":
            st.success(f"Signoff status: {summary.signoff_label}")
        elif summary.signoff_state == "BLOCKED":
            st.warning(f"Signoff status: {summary.signoff_label}")
        else:
            st.info(f"Signoff status: {summary.signoff_label}")

        if plan is None or not plan.checks:
            st.caption("No manual verification checks have been recorded for this requirement yet.")
        else:
            if summary.not_run_checks:
                st.caption(f"{summary.not_run_checks} check(s) still have not been run.")
            for index, check in enumerate(plan.checks, start=1):
                label = f"{index}. {check.title} · {verification_status_label(check.status)}"
                with st.expander(label, expanded=(check.status != "PASS")):
                    if st.button(
                        "Guide this check",
                        key=f"guide-verification-{project_name}-{record.id}-{check.check_id}",
                    ):
                        guide_manual_verification_check(project_name, record.id, check.check_id)
                        st.success("Pinned this verification check at the project level so it stays visible while you work.")
                        st.rerun()
                    if check.instructions:
                        st.write(check.instructions)
                    with st.form(f"verification-check-{project_name}-{record.id}-{check.check_id}"):
                        status = st.selectbox(
                            "Outcome",
                            list(verification_status_options()),
                            index=list(verification_status_options()).index(check.status if check.status in verification_status_options() else "NOT_RUN"),
                            format_func=verification_status_label,
                        )
                        notes = st.text_area("Notes", value=check.notes, height=100)
                        save_col, remove_col = st.columns(2)
                        saved = save_col.form_submit_button("Save verification result")
                        removed = remove_col.form_submit_button("Remove check")

                    if saved:
                        try:
                            update_manual_verification_check(
                                project_name,
                                record.id,
                                check.check_id,
                                status=status,
                                notes=notes,
                            )
                        except Exception as exc:  # pragma: no cover - surfaced in UI
                            st.error(f"Could not save verification result: {exc}")
                        else:
                            st.success("Saved verification result.")
                            st.rerun()

                    if removed:
                        remove_manual_verification_check(project_name, record.id, check.check_id)
                        current = _guided_verification_for_project(project_name)
                        if current is not None and current.get("check_id") == check.check_id:
                            clear_guided_manual_verification(project_name)
                        st.success("Removed verification check.")
                        st.rerun()

        with st.expander("Add verification check", expanded=(plan is None or not plan.checks)):
            with st.form(f"verification-add-{project_name}-{record.id}"):
                title = st.text_input(
                    "Check title",
                    placeholder="What should be verified manually?",
                )
                instructions = st.text_area(
                    "Instructions",
                    placeholder="What should the Product Director do or observe to verify this check?",
                    height=100,
                )
                added = st.form_submit_button("Add verification check")

            if added:
                try:
                    add_manual_verification_check(
                        project_name,
                        record.id,
                        title=title,
                        instructions=instructions,
                    )
                except Exception as exc:  # pragma: no cover - surfaced in UI
                    st.error(f"Could not add verification check: {exc}")
                else:
                    st.success("Added verification check.")
                    st.rerun()


def render_guided_verification_card(project_name: str) -> None:
    current = _guided_verification_for_project(project_name)
    if current is None:
        return

    requirement_id = current.get("requirement_id", "")
    check_id = current.get("check_id", "")
    plan = manual_verification_plan(project_name, requirement_id)
    if plan is None:
        clear_guided_manual_verification(project_name)
        return

    check = next((item for item in plan.checks if item.check_id == check_id), None)
    if check is None:
        clear_guided_manual_verification(project_name)
        return

    st.markdown("**Guided verification**")
    with st.container(border=True):
        st.caption(f"{requirement_id} · Manual verification")
        st.markdown(f"**{check.title}**")
        if check.instructions:
            st.write(check.instructions)
        st.caption(
            "Keep this card visible while you move through the project. "
            "Record the result here when you have verified the step."
        )
        status = check.status if check.status in verification_status_options() else "NOT_RUN"
        with st.form(f"guided-verification-form-{project_name}-{requirement_id}-{check_id}"):
            outcome = st.selectbox(
                "Outcome",
                list(verification_status_options()),
                index=list(verification_status_options()).index(status),
                format_func=verification_status_label,
            )
            notes = st.text_area("Notes", value=check.notes, height=100)
            save_col, open_col, clear_col = st.columns(3)
            saved = save_col.form_submit_button("Save result")
            open_requested = open_col.form_submit_button("Open in Requirements")
            cleared = clear_col.form_submit_button("Clear guided card")

        if saved:
            try:
                update_manual_verification_check(
                    project_name,
                    requirement_id,
                    check_id,
                    status=outcome,
                    notes=notes,
                )
            except Exception as exc:  # pragma: no cover - surfaced in UI
                st.error(f"Could not save guided verification result: {exc}")
            else:
                st.success("Saved guided verification result.")
                st.rerun()

        if open_requested:
            st.session_state[PROJECT_DETAIL_SECTION_STATE_KEY] = "Requirements"
            st.rerun()

        if cleared:
            clear_guided_manual_verification(project_name)
            st.rerun()


def render_sprint_panel(project_name: str, records: list[RequirementRecord]) -> None:
    sprint = load_sprint_plan(project_name)
    sprint_records = list(sprint_requirement_records(project_name))

    st.markdown("**Sprint**")
    if sprint is None:
        st.caption("No sprint is planned yet. Add backlog requirements directly from their cards to create one.")
    else:
        status_map = {
            "PLANNING": "Planning",
            "ACTIVE": "Active",
            "BLOCKED": "Blocked",
            "READY_TO_CLOSE": "Ready to close",
            "COMPLETED": "Completed",
        }
        status_label = status_map.get(sprint.status, sprint.status.title())
        done_count = sum(1 for record in sprint_records if record.status == "DONE")
        with st.container(border=True):
            metric_left, metric_right, metric_third = st.columns(3)
            metric_left.metric("Status", status_label)
            metric_right.metric("Items", len(sprint_records))
            metric_third.metric("Completed", done_count)

            if sprint.current_requirement_id:
                st.caption(f"Current requirement: {sprint.current_requirement_id}")
            if sprint.blocked_reason:
                st.warning(sprint.blocked_reason)

            if sprint_records:
                for index, record in enumerate(sprint_records, start=1):
                    st.write(f"{index}. {record.id} — {record.title}")
                    st.caption(f"Status: {record.status}")
                    if sprint.status == "PLANNING":
                        move_left, move_right, remove_col = st.columns(3)
                        if move_left.button(
                            "Move up",
                            key=f"sprint-up-{project_name}-{record.id}",
                            disabled=(index == 1),
                        ):
                            move_sprint_requirement(project_name, record.id, -1)
                            st.rerun()
                        if move_right.button(
                            "Move down",
                            key=f"sprint-down-{project_name}-{record.id}",
                            disabled=(index == len(sprint_records)),
                        ):
                            move_sprint_requirement(project_name, record.id, 1)
                            st.rerun()
                        if remove_col.button("Remove", key=f"sprint-remove-{project_name}-{record.id}"):
                            remove_sprint_requirement(project_name, record.id)
                            st.rerun()
            elif sprint.status == "COMPLETED":
                st.success("Sprint completed. Finished requirements have moved out of the sprint and remain available in the completed archive below.")
                st.caption("This sprint is now empty and ready for you to add backlog requirements for the next sprint.")

            if sprint.status == "PLANNING" and sprint_records:
                if st.button("Start sprint", key=f"start-sprint-{project_name}"):
                    try:
                        started = start_sprint(project_name)
                    except Exception as exc:  # pragma: no cover - surfaced in UI
                        st.error(f"Could not start sprint: {exc}")
                    else:
                        started_label = started.current_requirement_id or "the first requirement"
                        st.success(f"Sprint started. {started_label} is now queued for implementation.")
                        st.rerun()
            elif sprint.status == "BLOCKED":
                st.info(
                    "Resolve or rerun the current requirement, then continue the sprint to advance to the next item."
                )
                if st.button("Continue sprint", key=f"continue-sprint-{project_name}"):
                    try:
                        continue_sprint(project_name)
                    except Exception as exc:  # pragma: no cover - surfaced in UI
                        st.error(f"Could not continue sprint: {exc}")
                    else:
                        st.rerun()
            elif sprint.status == "ACTIVE":
                st.caption("Sprint execution is active. Requirements will advance sequentially within this project.")
            elif sprint.status == "READY_TO_CLOSE":
                st.success("Sprint execution is complete. Confirm completion to clear the sprint and start a new one.")
                if st.button("Confirm sprint completion", key=f"confirm-sprint-{project_name}"):
                    try:
                        complete_sprint(project_name)
                    except Exception as exc:  # pragma: no cover - surfaced in UI
                        st.error(f"Could not complete sprint: {exc}")
                    else:
                        st.success("Sprint completed and cleared.")
                        st.rerun()
            elif sprint.status == "COMPLETED":
                st.caption("Add backlog requirements to this empty sprint to plan the next batch of work.")
    if sprint is None or sprint.status in {"PLANNING"}:
        st.caption("Use `Add to sprint` on any backlog requirement you want to include.")


def render_requirement_editor(project_name: str, record: RequirementRecord, position: int, total: int) -> None:
    if record.status == "DONE":
        render_done_requirement(project_name, record)
        return

    with st.expander(requirement_expander_label(record), expanded=requirement_editor_expanded(position)):
        st.caption(requirement_card_metadata(record))
        render_requirement_clarifications(project_name, record)
        render_create_requirement_clarification(project_name, record)
        with st.form(f"requirement-{project_name}-{record.id}"):
            title = st.text_input("Title", value=record.title)
            status = st.selectbox("Status", STATUS_OPTIONS, index=_option_index(STATUS_OPTIONS, record.status))
            priority = st.selectbox("Priority", PRIORITY_OPTIONS, index=_option_index(PRIORITY_OPTIONS, record.priority))
            effort = st.selectbox("Effort", EFFORT_OPTIONS, index=_option_index(EFFORT_OPTIONS, record.effort))
            description = st.text_area("Description", value=record.description, height=140)
            saved = st.form_submit_button("Save requirement")

        if saved:
            update_requirement(
                project_name,
                RequirementRecord(
                    id=record.id,
                    title=title.strip(),
                    status=status,
                    priority=priority,
                    effort=effort,
                    description=description.strip(),
                ),
            )
            st.success(f"Saved {record.id}. Refresh the page to see the updated ordering and summary.")

        left, right = st.columns(2)
        if left.button("Move up", key=f"move-up-{project_name}-{record.id}", disabled=(position == 0)):
            move_requirement(project_name, record.id, -1)
            st.success(f"Moved {record.id} up. Refresh the page to see the new order.")
        if right.button("Move down", key=f"move-down-{project_name}-{record.id}", disabled=(position == total - 1)):
            move_requirement(project_name, record.id, 1)
            st.success(f"Moved {record.id} down. Refresh the page to see the new order.")

        sprint = load_sprint_plan(project_name)
        sprint_ids = {item.id for item in sprint_requirement_records(project_name)}
        sprint_mutable = sprint is None or sprint.status in {"PLANNING", "COMPLETED"}
        if record.status in {"BACKLOG", "NEW"} and record.id not in sprint_ids:
            if st.button(
                "Add to sprint",
                key=f"card-add-to-sprint-{project_name}-{record.id}",
                disabled=not sprint_mutable,
            ):
                try:
                    plan_sprint_requirement(project_name, record.id)
                except Exception as exc:  # pragma: no cover - surfaced in UI
                    st.error(f"Could not add requirement to sprint: {exc}")
                else:
                    st.success(f"Added {record.id} to the sprint.")
                    st.rerun()
        elif record.id in sprint_ids:
            st.caption("This requirement is already in the sprint plan.")

        render_requirement_implementation_state(project_name, record)
        render_manual_verification_panel(project_name, record)
        render_requirement_delete_control(project_name, record)


def render_requirements_panel(project_name: str, project) -> None:
    document = load_requirement_document(project_name)
    all_requirements = list(document.active_requirements + document.backlog_requirements)
    active_records, done_records = split_requirements_for_display(all_requirements)

    metric_left, metric_right = st.columns(2)
    metric_left.metric("Requirements", len(all_requirements))
    metric_right.metric("Pending Tasks", len(project.pending_tasks))

    clarification_items = active_pm_clarifications(project_name)
    if clarification_items:
        st.warning(f"PM clarification needed on {len(clarification_items)} workflow item(s) in this project.")

    st.markdown("**Sprint planning**")
    render_sprint_panel(project_name, all_requirements)

    recommendation = recommend_requirement(all_requirements)
    if recommendation is not None:
        st.markdown("**PM prioritisation recommendation**")
        with st.container(border=True):
            st.write(f"{recommendation.requirement_id} — {recommendation.title}")
            st.caption(recommendation.rationale)

    st.markdown("**Structured requirements**")
    if not all_requirements:
        st.info("No requirements found for this project yet.")
        return

    if active_records:
        for group_title, group_caption, group_records in requirement_focus_groups(active_records):
            st.markdown(f"**{group_title}**")
            st.caption(group_caption)
            for row in active_requirement_rows(group_records):
                if len(row) == 1:
                    left, _ = st.columns(active_requirement_row_weights(row))
                    with left:
                        record = row[0]
                        position = active_records.index(record)
                        render_requirement_editor(project_name, record, position, len(active_records))
                else:
                    columns = st.columns(len(row))
                    for column, record in zip(columns, row):
                        with column:
                            position = active_records.index(record)
                            render_requirement_editor(project_name, record, position, len(active_records))
    else:
        st.info("No unfinished requirements found for this project.")

    if done_records:
        render_completed_requirements_archive(project_name, done_records)


def render_pm_requirement_discovery_chat(project_name: str) -> None:
    thread = active_agent_thread(project_name, agent_name="PM", mode="Requirement Discovery")
    blocked_thread = next(
        (
            candidate
            for candidate in list_agent_threads(project_name, agent_name="PM", mode="Requirement Discovery")
            if candidate.status == "blocked_clarification"
        ),
        None,
    )

    st.markdown("**PM agent chat**")
    st.caption(
        "Planner: Live PM. Start with an idea, PM will ask follow-up questions in real time, decide when there is enough context to draft, "
        "and you can still force a draft manually when needed."
    )

    if blocked_thread is not None and thread is None:
        st.info("PM has raised a blocking clarification. Answer it from the Inbox to resume this discovery thread.")
        return

    if thread is None:
        with st.form(f"pm-thread-start-{project_name}"):
            initial_idea = st.text_area(
                "Initial idea",
                placeholder="Describe the idea you want PM to help shape into requirements.",
                height=140,
            )
            reference_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=f"pm-start-images-{project_name}",
            )
            started = st.form_submit_button("Start PM requirement discovery")
        if started:
            if not initial_idea.strip():
                st.error("Initial idea is required before PM can begin the conversation.")
            else:
                start_pm_requirement_discovery_thread(
                    project_name,
                    initial_idea,
                    image_files=_uploaded_image_payloads(reference_images),
                )
                st.rerun()
        return

    for message in thread.messages:
        role = "assistant" if message.role == "assistant" else "user"
        with st.chat_message(role):
            st.write(message.content)
            _render_message_attachments(message)

    if not thread.draft:
        conversation_step = len(thread.messages)
        reply_key = f"pm-thread-reply-text-{project_name}-{thread.thread_id}-{conversation_step}"
        reply_images_key = f"pm-reply-images-{project_name}-{thread.thread_id}-{conversation_step}"
        with st.form(f"pm-thread-reply-{project_name}-{thread.thread_id}"):
            reply = st.text_area(
                "Your reply",
                placeholder="Answer PM's question here.",
                height=110,
                key=reply_key,
            )
            reply_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=reply_images_key,
            )
            send = st.form_submit_button("Send reply")
            draft_now = st.form_submit_button("Draft requirements now")

        if send:
            if not reply.strip():
                st.error("Reply is required before PM can continue the thread.")
            else:
                with st.spinner("PM is reviewing your reply..."):
                    reply_to_pm_requirement_discovery_thread(
                        project_name,
                        thread.thread_id,
                        reply,
                        image_files=_uploaded_image_payloads(reply_images),
                    )
                _clear_widget_state(reply_key, reply_images_key)
                st.rerun()

        if draft_now:
            with st.spinner("PM is drafting requirements..."):
                draft_pm_requirement_discovery_thread(project_name, thread.thread_id)
            _clear_widget_state(reply_key, reply_images_key)
            st.rerun()
        return

    st.markdown("**Draft requirement artifact**")
    with st.container(border=True):
        st.caption(f"Idea: {thread.idea}")
        st.text(thread.draft)

    st.markdown("**Save reviewed draft into project requirements**")
    with st.form(f"pm-thread-save-{project_name}-{thread.thread_id}"):
        requirement_title = st.text_input(
            "Requirement title",
            value=thread.draft_title or "",
            placeholder="Add PM chat-based discovery",
        )
        status = st.selectbox("Status", ["NEW", "BACKLOG"], index=0)
        priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=0)
        effort = st.selectbox("Effort", ["S", "M", "L"], index=2)
        approved = st.form_submit_button("Save to requirements.md")

    if approved:
        if not requirement_title.strip():
            st.error("Requirement title is required before saving.")
        else:
            approval = request_pm_requirement_thread_approval(
                project_name,
                thread.thread_id,
                requirement_title=requirement_title,
                status=status,
                priority=priority,
                effort=effort,
            )
            st.success(f"Created approval request {approval.approval_id} for this PM draft. Approve it from Inbox.")
            st.rerun()


def _render_thread_messages(thread: AgentThread) -> None:
    for message in thread.messages:
        role = "assistant" if message.role == "assistant" else "user"
        with st.chat_message(role):
            st.write(message.content)
            _render_message_attachments(message)


def render_experience_designer_chat(project_name: str, mode: str) -> None:
    thread = active_agent_thread(project_name, agent_name="Experience Designer", mode=mode)
    st.markdown("**Experience Designer agent chat**")
    st.caption(
        "Live Experience Designer. Use this for UX feedback synthesis or usability review, then save a reviewed finding into the OS workflow."
    )

    if thread is None:
        label = "Initial UX issue" if mode == "Feedback Synthesis" else "Usability concern"
        placeholder = (
            "Describe the user pain, workflow friction, or feedback you want synthesised."
            if mode == "Feedback Synthesis"
            else "Describe the flow, screen, or interface issue that feels confusing, noisy, or hard to use."
        )
        with st.form(f"experience-thread-start-{project_name}-{mode}"):
            initial_idea = st.text_area(label, placeholder=placeholder, height=140)
            reference_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=f"experience-start-images-{project_name}-{mode}",
            )
            started = st.form_submit_button("Start Experience Designer review")
        if started:
            if not initial_idea.strip():
                st.error("A starting issue is required before Experience Designer can begin.")
            else:
                start_experience_designer_thread(
                    project_name,
                    mode,
                    initial_idea,
                    image_files=_uploaded_image_payloads(reference_images),
                )
                st.rerun()
        return

    _render_thread_messages(thread)

    if not thread.draft:
        conversation_step = len(thread.messages)
        reply_key = f"experience-thread-reply-text-{project_name}-{thread.thread_id}-{conversation_step}"
        reply_images_key = f"experience-reply-images-{project_name}-{thread.thread_id}-{conversation_step}"
        with st.form(f"experience-thread-reply-{project_name}-{thread.thread_id}"):
            reply = st.text_area("Your reply", placeholder="Answer Experience Designer here.", height=110, key=reply_key)
            reply_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=reply_images_key,
            )
            send = st.form_submit_button("Send reply")
            draft_now = st.form_submit_button("Draft finding now")

        if send:
            if not reply.strip():
                st.error("Reply is required before Experience Designer can continue.")
            else:
                with st.spinner("Experience Designer is reviewing your reply..."):
                    reply_to_experience_designer_thread(
                        project_name,
                        thread.thread_id,
                        reply,
                        image_files=_uploaded_image_payloads(reply_images),
                    )
                _clear_widget_state(reply_key, reply_images_key)
                st.rerun()

        if draft_now:
            with st.spinner("Experience Designer is drafting the finding..."):
                draft_experience_designer_thread(project_name, thread.thread_id)
            _clear_widget_state(reply_key, reply_images_key)
            st.rerun()
        return

    st.markdown("**Draft experience finding**")
    with st.container(border=True):
        st.caption(f"Mode: {mode}")
        st.text(thread.draft)

    left, right = st.columns(2)
    with left:
        if st.button("Send finding for approval", key=f"save-experience-finding-{project_name}-{thread.thread_id}"):
            approval = request_experience_thread_approval(project_name, thread.thread_id)
            st.success(f"Created approval request {approval.approval_id} for this finding. Approve it from Inbox.")
            st.rerun()
    with right:
        if st.button("Archive reviewed draft", key=f"archive-experience-thread-{project_name}-{thread.thread_id}"):
            archive_agent_thread(project_name, thread.thread_id)
            st.rerun()


def render_ui_designer_chat(project_name: str, mode: str) -> None:
    thread = active_agent_thread(project_name, agent_name="UI Designer", mode=mode)
    st.markdown("**UI Designer agent chat**")
    st.caption(
        "Live UI Designer. Use this for visual direction, interaction design, layout decisions, and design critique of existing surfaces."
    )

    if thread is None:
        label = "Design goal" if mode == "Design Direction" else "UI review target"
        placeholder = (
            "Describe the experience, screen, or design direction you want to shape before implementation."
            if mode == "Design Direction"
            else "Describe the current UI you want critiqued for hierarchy, spacing, polish, or visual balance."
        )
        with st.form(f"ui-designer-thread-start-{project_name}-{mode}"):
            initial_idea = st.text_area(label, placeholder=placeholder, height=140)
            reference_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=f"ui-start-images-{project_name}-{mode}",
            )
            started = st.form_submit_button("Start UI Designer review")
        if started:
            if not initial_idea.strip():
                st.error("A starting design problem is required before UI Designer can begin.")
            else:
                start_ui_designer_thread(
                    project_name,
                    mode,
                    initial_idea,
                    image_files=_uploaded_image_payloads(reference_images),
                )
                st.rerun()
        return

    _render_thread_messages(thread)

    if not thread.draft:
        conversation_step = len(thread.messages)
        reply_key = f"ui-designer-thread-reply-text-{project_name}-{thread.thread_id}-{conversation_step}"
        reply_images_key = f"ui-reply-images-{project_name}-{thread.thread_id}-{conversation_step}"
        with st.form(f"ui-designer-thread-reply-{project_name}-{thread.thread_id}"):
            reply = st.text_area("Your reply", placeholder="Answer UI Designer here.", height=110, key=reply_key)
            reply_images = st.file_uploader(
                "Reference images (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                key=reply_images_key,
            )
            send = st.form_submit_button("Send reply")
            draft_now = st.form_submit_button("Draft design brief now")

        if send:
            if not reply.strip():
                st.error("Reply is required before UI Designer can continue.")
            else:
                with st.spinner("UI Designer is reviewing your reply..."):
                    reply_to_ui_designer_thread(
                        project_name,
                        thread.thread_id,
                        reply,
                        image_files=_uploaded_image_payloads(reply_images),
                    )
                _clear_widget_state(reply_key, reply_images_key)
                st.rerun()

        if draft_now:
            with st.spinner("UI Designer is drafting the brief..."):
                draft_ui_designer_thread(project_name, thread.thread_id)
            _clear_widget_state(reply_key, reply_images_key)
            st.rerun()
        return

    st.markdown("**Draft design brief**")
    with st.container(border=True):
        if thread.draft_title:
            st.caption(thread.draft_title)
        st.text(thread.draft)

    left, right = st.columns(2)
    with left:
        if st.button("Send brief for approval", key=f"approve-ui-thread-{project_name}-{thread.thread_id}"):
            approval = request_ui_design_brief_approval(project_name, thread.thread_id)
            st.success(f"Created approval request {approval.approval_id} for this design brief. Approve it from Inbox.")
            st.rerun()
    with right:
        if st.button("Archive reviewed design brief", key=f"archive-ui-thread-{project_name}-{thread.thread_id}"):
            archive_agent_thread(project_name, thread.thread_id)
            st.rerun()


def render_orchestrator_panel(project_name: str, mode: str) -> None:
    recommendation = orchestrator_recommendation(project_name)
    st.markdown("**Orchestrator**")
    st.caption("The deterministic control layer remains authoritative. Live review is a bounded second opinion.")
    with st.container(border=True):
        st.markdown(f"**Mode:** {mode}")
        st.markdown(f"**Next role:** {recommendation.next_role}")
        st.markdown(f"**Next action:** {recommendation.next_action}")
        st.caption(recommendation.why)

    if mode != "Workflow Review":
        return

    state_key = f"orchestrator-live-review-{project_name}"
    if st.button("Run live workflow review", key=f"run-orchestrator-live-review-{project_name}"):
        try:
            with st.spinner("Orchestrator is reviewing the current workflow state..."):
                st.session_state[state_key] = run_live_orchestrator_review(project_name)
        except LivePMDiscoveryError as exc:
            st.error(str(exc))
        else:
            st.rerun()

    review = st.session_state.get(state_key)
    if review is None:
        return
    with st.container(border=True):
        agreement = "Agrees with control layer" if review.agrees_with_deterministic else "Suggests a different next step"
        st.markdown(f"**Live review:** {agreement}")
        st.markdown(f"**Suggested role:** {review.recommended_role}")
        st.markdown(f"**Suggested action:** {review.recommended_action}")
        st.caption(review.rationale)
        if review.uncertainty:
            st.caption(f"Uncertainty: {review.uncertainty}")


def render_architect_panel(project_name: str, mode: str) -> None:
    st.markdown("**Architect**")
    st.caption("Deterministic structural review. Use this when the shape of the system is part of the problem.")
    state_key = f"architect-review-result-{project_name}-{mode}"
    if st.button("Run Architect review", key=f"run-architect-review-{project_name}-{mode}"):
        st.session_state[state_key] = {
            "snapshot": architect_review_snapshot(project_name),
            "reviewed_at": datetime.now().strftime("%H:%M:%S"),
        }
        st.rerun()

    review_result = st.session_state.get(state_key)
    if review_result is None:
        st.info("Run Architect review to inspect the current structural signal for this project.")
        return
    snapshot = review_result["snapshot"]
    reviewed_at = review_result["reviewed_at"]

    with st.container(border=True):
        st.markdown(f"**Mode:** {mode}")
        st.caption(f"Architect review generated at {reviewed_at}.")
        st.markdown(f"**Assessment:** {snapshot.headline}")
        st.write(snapshot.summary)
        if snapshot.hotspots:
            st.markdown("**Active hotspots**")
            for item in snapshot.hotspots:
                st.markdown(f"- {item}")
        else:
            st.caption("No active structural hotspot is currently forcing Architect to run.")
        st.markdown("**Guardrails**")
        for item in snapshot.guardrails:
            st.markdown(f"- {item}")


def render_qa_panel(project_name: str, mode: str) -> None:
    st.markdown("**QA**")
    st.caption("Validation surface. Run the project QA report when you want a current reliability read.")
    state_key = f"qa-review-result-{project_name}-{mode}"
    if st.button("Run QA review", key=f"run-qa-review-{project_name}-{mode}"):
        st.session_state[state_key] = record_project_qa_review(project_name, mode="deterministic")
        st.rerun()

    result = st.session_state.get(state_key) or latest_quality_review(project_name, mode="deterministic")
    if result is None:
        st.info("Run QA review to inspect the current validation signal for this project.")
        return

    with st.container(border=True):
        st.markdown(f"**Mode:** {mode}")
        if hasattr(result, "reviewed_at"):
            st.caption(f"Latest recorded QA review: {format_run_timestamp(result.reviewed_at)}")
        st.markdown(f"**Runner:** {result.runner_path or 'Unavailable'}")
        st.markdown(f"**Summary:** {result.summary}")
        st.caption(result.confidence)
        if result.failures:
            st.markdown("**Failing cases**")
            for case in result.failures:
                st.markdown(f"- {case}")
        else:
            st.caption("No failing cases were reported in the current run.")
        with st.expander("Show raw QA output", expanded=False):
            st.text(result.raw_output or "<no output>")


def approval_review_sections(approval) -> tuple[tuple[str, str], ...]:
    payload = approval.payload
    if approval.approval_type == "requirement_draft":
        sections: list[tuple[str, str]] = []
        title = payload.get("requirement_title", approval.title).strip()
        if title:
            sections.append(("Requirement title", title))
        metadata = " | ".join(
            [
                f"Status: {payload.get('status', 'NEW')}",
                f"Priority: {payload.get('priority', 'MEDIUM')}",
                f"Effort: {payload.get('effort', 'M')}",
            ]
        )
        sections.append(("Requirement metadata", metadata))
        draft = payload.get("draft", "").strip()
        if draft:
            sections.append(("Draft requirement", draft))
        return tuple(sections)

    if approval.approval_type == "experience_finding":
        ordered_fields = (
            ("User problem", payload.get("user_problem", "").strip()),
            ("Affected workflow", payload.get("affected_workflow", "").strip()),
            ("Evidence", payload.get("evidence", "").strip()),
            ("Confidence", payload.get("confidence", "").strip()),
            ("Severity", payload.get("severity", "").strip()),
            ("Frequency", payload.get("frequency", "").strip()),
            ("Recommendation type", payload.get("recommendation_type", "").strip()),
            ("Rationale", payload.get("rationale", "").strip()),
            ("Recommended next role", payload.get("recommended_next_role", "").strip()),
        )
        return tuple((label, value) for label, value in ordered_fields if value)

    if approval.approval_type == "design_brief":
        draft = payload.get("draft", "").strip()
        return (("Design brief", draft),) if draft else ()

    if approval.approval_type == "scope_confirmation":
        sections: list[tuple[str, str]] = []
        summary = approval.summary.strip()
        if summary:
            sections.append(("Why PM thinks this is out of scope", summary))
        title = payload.get("requirement_title", "").strip()
        if title:
            sections.append(("Fallback backlog requirement title", title))
        draft = payload.get("requirement_body", "").strip()
        if draft:
            sections.append(("Fallback backlog requirement", draft))
        metadata = " | ".join(
            [
                f"Priority: {payload.get('priority', 'MEDIUM')}",
                f"Effort: {payload.get('effort', 'M')}",
            ]
        )
        sections.append(("Fallback requirement metadata", metadata))
        return tuple(sections)

    return tuple((key.replace("_", " ").title(), value) for key, value in payload.items() if value.strip())


def render_approval_review_details(approval) -> None:
    sections = approval_review_sections(approval)
    if not sections:
        st.caption("No additional review detail is available for this approval item.")
        return
    with st.expander("Review full draft", expanded=False):
        for heading, content in sections:
            st.markdown(f"**{heading}**")
            st.text(content)


def approval_button_labels(approval) -> tuple[str, str]:
    if approval.approval_type == "scope_confirmation":
        return ("Confirm out of scope", "Send to backlog")
    return ("Approve", "Reject")


def workspace_approval_requests() -> tuple:
    return tuple(approval for approval in list_approvals() if approval.status == "OPEN")


def workspace_approval_metadata(approval) -> str:
    return f"{approval.project_name} · {approval.source_agent_name}"


def workspace_approval_section_title(approval_count: int) -> str:
    if approval_count == 1:
        return "Awaiting approval"
    return f"Awaiting approval ({approval_count})"


def render_approval_decision_actions(approval, key_prefix: str) -> None:
    approve_label, reject_label = approval_button_labels(approval)
    left, right = st.columns(2)
    with left:
        if st.button(approve_label, key=f"{key_prefix}-approve-{approval.approval_id}"):
            approve_request(approval.project_name, approval.approval_id)
            st.rerun()
    with right:
        if st.button(reject_label, key=f"{key_prefix}-reject-{approval.approval_id}"):
            reject_request(approval.project_name, approval.approval_id)
            st.rerun()


def render_workspace_approval_requests() -> None:
    approvals = workspace_approval_requests()
    render_section_intro(
        workspace_approval_section_title(len(approvals)) if approvals else "Awaiting approval",
        "Decision-ready approval requests appear here. Inbox remains the full workflow queue.",
    )
    if not approvals:
        st.info("No approval requests are waiting.")
        return

    for approval in approvals:
        with st.container(border=True):
            render_workflow_card_header("Approval", approval.title, workspace_approval_metadata(approval))
            st.write(approval.summary)
            render_approval_review_details(approval)
            render_approval_decision_actions(approval, key_prefix="workspace")


def _find_thread_by_reference(project_name: str, thread_id: str) -> AgentThread | None:
    return next(
        (
            candidate
            for candidate in list_agent_threads(project_name)
            if candidate.thread_id == thread_id
        ),
        None,
    )


def render_inbox_thread_link(item) -> None:
    thread = _find_thread_by_reference(item.project_name, item.reference_id)
    if thread is None or thread.status != "active":
        st.caption("This waiting thread is no longer active.")
        return

    if st.button("Open thread in Agents", key=f"open-thread-{thread.thread_id}"):
        focus_project_agent_thread(
            item.project_name,
            agent_name=thread.agent_name,
            mode=thread.mode,
        )
        st.rerun()


def _inbox_filter_options() -> list[str]:
    return ["All", "Waiting", "Blocked", "Routed", "Running"]


def render_inbox_tab(projects) -> None:
    st.subheader("Workflow Inbox")
    st.caption("A focused queue for approvals, blocked items, routed workflow artifacts, and active runs.")

    project_names = ["All projects", *[project.name for project in projects]]
    render_section_intro("Queue filters", "Narrow the queue by project or workflow state.")
    filter_left, filter_right = st.columns(2)
    with filter_left:
        selected_project = st.selectbox("Project filter", project_names, index=0, key="inbox-project-filter")
    with filter_right:
        inbox_filter = st.selectbox("Status filter", _inbox_filter_options(), index=0, key="inbox-status-filter")

    target_project = None if selected_project == "All projects" else selected_project
    active_items = workflow_inbox_items(target_project)
    if inbox_filter != "All":
        active_items = [item for item in active_items if item.status_bucket == inbox_filter.lower()]

    approvals = list_approvals(target_project)
    open_approvals = [item for item in approvals if item.status == "OPEN"]
    render_section_intro("Queue snapshot", "Counts reflect the active filters above.")
    metrics = st.columns(4)
    metrics[0].metric("Waiting", len(open_approvals) + len([item for item in active_items if item.status_bucket == "waiting"]))
    metrics[1].metric("Blocked", len([item for item in active_items if item.status_bucket == "blocked"]))
    metrics[2].metric("Routed", len([item for item in active_items if item.status_bucket == "routed"]))
    metrics[3].metric("Running", len([item for item in active_items if item.status_bucket == "running"]))

    if open_approvals:
        render_section_intro("Approval requests", "Review the underlying draft before approving or rejecting.")
        for row in inbox_card_rows(open_approvals):
            columns = st.columns(inbox_card_row_weights(row))
            for index, column in enumerate(columns):
                if index >= len(row):
                    continue
                approval = row[index]
                with column:
                    with st.container(border=True):
                        render_workflow_card_header(
                            "Approval",
                            approval.title,
                            workflow_card_metadata(approval.project_name, approval.source_agent_name),
                        )
                        st.write(approval.summary)
                        render_approval_review_details(approval)
                        render_approval_decision_actions(approval, key_prefix="inbox")

    waiting_items = [item for item in active_items if item.status_bucket == "waiting"]
    blocked_items = [item for item in active_items if item.status_bucket == "blocked"]
    routed_items = [item for item in active_items if item.status_bucket == "routed"]
    running_items = [item for item in active_items if item.status_bucket == "running"]

    sections = [
        ("Waiting on you", waiting_items),
        ("Blocked", blocked_items),
        ("Routed", routed_items),
        ("Running", running_items),
    ]

    render_section_intro("Workflow items", "Grouped by what kind of attention the item needs.")
    if not active_items:
        st.info(inbox_empty_message(selected_project, inbox_filter))
    else:
        for heading, items in sections:
            if not items:
                continue
            st.markdown(inbox_section_label_markup(heading, len(items)), unsafe_allow_html=True)
            for row in inbox_card_rows(items):
                columns = st.columns(inbox_card_row_weights(row))
                for index, column in enumerate(columns):
                    if index >= len(row):
                        continue
                    item = row[index]
                    with column:
                        with st.container(border=True):
                            render_workflow_card_header(item.status_bucket, item.title, inbox_item_metadata(item))
                            st.write(item.summary)
                            if item.detail:
                                st.caption(item.detail)
                            if item.kind == "agent_thread":
                                render_inbox_thread_link(item)
                            if item.kind == "pm_clarification":
                                clarification = next(
                                    (
                                        candidate
                                        for candidate in list_pm_clarifications(item.project_name)
                                        if candidate.clarification_id == item.reference_id
                                    ),
                                    None,
                                )
                                if clarification is not None:
                                    for question in clarification.questions:
                                        st.write(f"- {question}")
                                    if clarification.source_thread_id:
                                        reply_key = f"inbox-clarification-reply-{clarification.clarification_id}"
                                        with st.form(f"inbox-clarification-answer-{clarification.clarification_id}"):
                                            reply = st.text_area(
                                                "Your clarification reply",
                                                placeholder="Answer PM's clarification here. PM will resume the blocked thread after you submit.",
                                                height=120,
                                                key=reply_key,
                                            )
                                            submitted = st.form_submit_button("Answer and resume PM thread")
                                        if submitted:
                                            if not reply.strip():
                                                st.error("A clarification reply is required before PM can resume.")
                                            else:
                                                answer_pm_clarification(item.project_name, clarification.clarification_id, reply)
                                                _clear_widget_state(reply_key)
                                                st.rerun()


def render_agents_panel(project_name: str) -> None:
    st.markdown("**Agent workspace**")
    st.markdown(f"<div class='os-agent-workspace-caption'>{escape(agent_workspace_caption())}</div>", unsafe_allow_html=True)
    agent, mode = render_agent_workflow_header(project_name)
    if agent == "PM":
        if mode == "Requirement Discovery":
            render_pm_requirement_discovery_chat(project_name)
        return
    if agent == "Experience Designer":
        render_experience_designer_chat(project_name, mode)
        return
    if agent == "UI Designer":
        render_ui_designer_chat(project_name, mode)
        return
    if agent == "Architect":
        render_architect_panel(project_name, mode)
        return
    if agent == "QA":
        render_qa_panel(project_name, mode)
        return
    if agent == "Orchestrator":
        render_orchestrator_panel(project_name, mode)


def render_project_detail(project_name: str, project) -> None:
    if st.button("Back to projects", key=f"back-to-projects-{project_name}"):
        queue_back_to_projects()
        st.rerun()

    render_project_control_header(project_name, project)
    render_guided_verification_card(project_name)
    nav_column, content_column = st.columns([0.22, 0.78], gap="large")
    with nav_column:
        st.markdown(project_detail_navigation_context_markup(project_name), unsafe_allow_html=True)
        section = st.radio(
            project_detail_navigation_label(),
            project_detail_tab_labels(),
            key=PROJECT_DETAIL_SECTION_STATE_KEY,
            horizontal=False,
            label_visibility="collapsed",
        )

    with content_column:
        if section == "Requirements":
            render_requirements_panel(project_name, project)
        elif section == "Agents":
            render_agents_panel(project_name)
        elif section == "Delivery":
            render_delivery_panel(project_name, project)
        else:
            render_quality_panel(project_name)


def render_main_navigation() -> str:
    current_section = normalize_top_level_section(str(st.session_state.get(TOP_LEVEL_SECTION_STATE_KEY, TOP_LEVEL_TAB_LABELS[0])))
    st.session_state[TOP_LEVEL_SECTION_STATE_KEY] = current_section
    st.markdown(main_navigation_anchor_markup(), unsafe_allow_html=True)
    st.markdown(main_navigation_context_markup(), unsafe_allow_html=True)
    selected = st.segmented_control(
        top_level_navigation_label(),
        top_level_tab_labels(),
        key=TOP_LEVEL_SECTION_STATE_KEY,
        label_visibility="collapsed",
        width="stretch",
    )
    return normalize_top_level_section(str(selected or current_section))


def main() -> None:
    st.set_page_config(page_title="OS Control Panel", layout="wide")
    _apply_pending_project_open()
    _apply_pending_agent_focus()
    _apply_pending_learning_section()
    _apply_pending_learning_concept()
    advance_all_active_sprints()
    st.markdown(SECTION_STYLE, unsafe_allow_html=True)
    st.title(workspace_heading())
    st.write(workspace_subtitle())

    projects = summarize_projects()
    if TOP_LEVEL_SECTION_STATE_KEY in st.session_state:
        st.session_state[TOP_LEVEL_SECTION_STATE_KEY] = normalize_top_level_section(
            str(st.session_state[TOP_LEVEL_SECTION_STATE_KEY])
        )
    section = render_main_navigation()

    if section == "Workspace":
        render_workspace_tab(projects)
    elif section == "Operations":
        render_operations_tab(projects)
    elif section == "Learning":
        render_learning_tab()
    elif section == TOP_LEVEL_PROJECTS_LABEL:
        render_projects_tab(projects)
    elif section == "Inbox":
        render_inbox_tab(projects)
    else:
        render_create_project_tab()


if __name__ == "__main__":
    main()

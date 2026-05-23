from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import app  # noqa: E402
from workspace import (  # noqa: E402
    ROLE_CARDS,
    active_approvals,
    agent_summary_by_name,
    architect_review_snapshot,
    active_implementation_run,
    active_agent_thread,
    archive_agent_thread,
    answer_pm_clarification,
    advance_active_sprint,
    create_project_from_reviewed_draft,
    continue_sprint,
    continue_live_pm_project_thread,
    complete_sprint,
    discovery_plan,
    draft_experience_designer_thread,
    draft_live_pm_project_thread,
    ImplementationRun,
    RequirementRecord,
    build_discovery_draft,
    build_requirement_implementation_prompt,
    draft_pm_requirement_discovery_thread,
    draft_ui_designer_thread,
    delete_requirement,
    discovery_questions,
    experience_intake_plan,
    implementation_entry_allowed,
    implementation_run_inspection,
    implementation_progress_message,
    implementation_progress_percent,
    list_approvals,
    active_pm_clarifications,
    list_agent_threads,
    list_experience_findings,
    latest_requirement_implementation,
    latest_quality_review,
    manual_verification_plan,
    manual_verification_summary,
    list_pm_clarifications,
    load_requirement_document,
    reconcile_implementation_runs,
    record_project_qa_review,
    recent_implementation_run_inspections,
    load_sprint_plan,
    move_requirement,
    move_sprint_requirement,
    orchestrator_recommendation,
    plan_sprint_requirement,
    project_preview,
    run_project_qa_review,
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
    save_experience_finding,
    save_experience_thread_to_finding,
    save_agent_message_uploads,
    add_manual_verification_check,
    save_pm_clarification,
    save_pm_requirement_thread_to_requirements,
    start_experience_designer_thread,
    start_live_pm_project_thread,
    start_pm_requirement_discovery_thread,
    start_ui_designer_thread,
    set_experience_handoff_state,
    start_project_preview,
    start_requirement_implementation,
    start_sprint,
    LiveExperienceTurn,
    LivePMReviewCompletionTurn,
    LivePMTurn,
    LiveUIDesignTurn,
    list_agent_summaries,
    sprint_requirement_records,
    sprint_preimplementation_gate,
    summarize_projects,
    update_requirement,
    update_manual_verification_check,
    workspace_totals,
    workflow_inbox_items,
    workflow_timeline_events,
    approve_request,
    _message_to_live_pm_input,
)


class WorkspaceSummaryTests(unittest.TestCase):
    def test_app_module_exposes_main(self) -> None:
        self.assertTrue(callable(app.main))

    def test_workspace_heading_is_distinct_from_project_name(self) -> None:
        self.assertEqual(app.workspace_heading(), "AI Product Operating System")

    def test_project_card_signal_text_uses_counts_only(self) -> None:
        projects = summarize_projects()
        os_control_panel = next(project for project in projects if project.name == "os-control-panel")
        left_text, right_text = app.project_card_signal_text(os_control_panel)
        self.assertTrue(left_text.startswith("New requirements: "))
        self.assertTrue(right_text.startswith("Pending tasks: "))
        self.assertNotIn("Task", left_text)

    def test_top_level_navigation_removes_project_detail_tab(self) -> None:
        self.assertEqual(app.top_level_tab_labels(), ("Workspace", "Open Project", "Inbox", "Create Project"))
        self.assertNotIn("Project Detail", app.top_level_tab_labels())

    def test_top_level_navigation_has_explicit_main_label(self) -> None:
        self.assertEqual(app.top_level_navigation_label(), "Main navigation")

    def test_top_level_navigation_exposes_workspace_layer_context(self) -> None:
        self.assertEqual(app.top_level_navigation_level_label(), "Workspace-level navigation")
        self.assertIn("workspace overview", app.top_level_navigation_scope_description())
        self.assertIn("workflow inbox", app.top_level_navigation_scope_description())

    def test_top_level_navigation_uses_segmented_control(self) -> None:
        self.assertEqual(app.top_level_navigation_control_kind(), "segmented_control")

    def test_top_level_navigation_uses_task_oriented_project_labels(self) -> None:
        self.assertIn("Open Project", app.top_level_tab_labels())
        self.assertIn("Create Project", app.top_level_tab_labels())
        self.assertNotIn("Projects", app.top_level_tab_labels())
        self.assertNotIn("New Project", app.top_level_tab_labels())

    def test_guided_verification_state_is_project_scoped(self) -> None:
        app.st.session_state.clear()
        app.guide_manual_verification_check("os-control-panel", "R64", "check-1")
        guided = app._guided_verification_for_project("os-control-panel")
        other = app._guided_verification_for_project("parentmate")
        self.assertIsNotNone(guided)
        self.assertEqual(guided["requirement_id"], "R64")
        self.assertIsNone(other)

    def test_guided_verification_state_can_be_cleared(self) -> None:
        app.st.session_state.clear()
        app.guide_manual_verification_check("os-control-panel", "R64", "check-1")
        app.clear_guided_manual_verification("os-control-panel")
        self.assertIsNone(app._guided_verification_for_project("os-control-panel"))

    def test_top_level_navigation_descriptions_cover_all_destinations(self) -> None:
        descriptions = app.top_level_navigation_descriptions()
        self.assertEqual(set(descriptions), set(app.top_level_tab_labels()))
        self.assertEqual(descriptions["Workspace"], "Overview")
        self.assertEqual(descriptions["Open Project"], "Project work")
        self.assertEqual(descriptions["Inbox"], "Waiting items")
        self.assertEqual(descriptions["Create Project"], "New setup")

    def test_main_navigation_markup_exposes_restrained_styling_hooks(self) -> None:
        markup = app.main_navigation_context_markup()
        self.assertIn("os-main-navigation-shell", markup)
        self.assertIn("os-main-navigation-heading", markup)
        self.assertIn("os-main-navigation-scope", markup)
        self.assertIn("Workspace-level navigation", markup)
        self.assertIn("Workspace: Overview", markup)
        self.assertIn("Open Project: Project work", markup)
        self.assertIn("os-main-navigation-shell", app.SECTION_STYLE)
        self.assertIn("os-main-navigation-scope", app.SECTION_STYLE)

    def test_top_level_navigation_normalizes_legacy_session_labels(self) -> None:
        self.assertEqual(app.normalize_top_level_section("Projects"), "Open Project")
        self.assertEqual(app.normalize_top_level_section("New Project"), "Create Project")
        self.assertEqual(app.normalize_top_level_section("Unknown"), "Workspace")

    def test_project_detail_keeps_project_level_tabs(self) -> None:
        self.assertEqual(app.project_detail_tab_labels(), ("Agents", "Requirements", "Delivery", "Quality"))

    def test_project_detail_navigation_is_visibly_distinct_from_main_navigation(self) -> None:
        self.assertEqual(app.project_detail_navigation_label(), "Project sections")
        self.assertEqual(app.project_detail_navigation_orientation(), "vertical")
        self.assertNotEqual(app.project_detail_navigation_label(), app.top_level_navigation_label())

    def test_project_detail_navigation_exposes_project_layer_context(self) -> None:
        markup = app.project_detail_navigation_context_markup("os-control-panel")
        self.assertEqual(app.project_detail_navigation_level_label(), "Project-level navigation")
        self.assertEqual(app.project_detail_navigation_scope_description("os-control-panel"), "Sections inside os-control-panel.")
        self.assertIn("os-project-navigation-shell", markup)
        self.assertIn("Project-level navigation", markup)
        self.assertIn("Sections inside os-control-panel.", markup)
        self.assertIn("os-project-navigation-shell", app.SECTION_STYLE)
        self.assertIn("os-project-nav-level", app.SECTION_STYLE)


    def test_project_control_summary_markup_groups_identity_and_path(self) -> None:
        project = SimpleNamespace(path=REPO_ROOT / "projects" / "os-control-panel")
        metadata = app.project_control_path_metadata(project)
        markup = app.project_control_summary_markup("os-control-panel", metadata)

        self.assertEqual(app.project_control_heading(), "Project")
        self.assertIn("Project path: projects/os-control-panel", metadata)
        self.assertIn("os-project-control-summary", markup)
        self.assertIn("os-project-control-title", markup)
        self.assertIn("os-control-panel", markup)

    def test_project_preview_summary_text_exposes_preview_state(self) -> None:
        preview = SimpleNamespace(available=True, runtime="streamlit", status_text="Streamlit project preview is available.")
        self.assertEqual(app.project_preview_summary_text(preview), "Preview available · Streamlit")

    def test_project_control_layout_style_hooks_are_defined(self) -> None:
        self.assertIn("os-project-control-summary", app.SECTION_STYLE)
        self.assertIn("os-project-control-title", app.SECTION_STYLE)
        self.assertIn("os-project-control-meta", app.SECTION_STYLE)

    def test_agents_tab_exposes_phase_one_agent_set(self) -> None:
        self.assertEqual(
            app.AGENT_OPTIONS,
            ["PM", "Experience Designer", "UI Designer", "Architect", "QA", "Orchestrator"],
        )

    def test_agent_workspace_caption_ties_agent_and_mode_decisions(self) -> None:
        caption = app.agent_workspace_caption()
        self.assertIn("Move left to right", caption)
        self.assertIn("choose an agent", caption)
        self.assertIn("choose the mode", caption)
        self.assertIn("active surface", caption)

    def test_agent_selection_card_markup_exposes_selected_state_and_hooks(self) -> None:
        role = next(item for item in ROLE_CARDS if item["name"] == "UI Designer")
        markup = app.agent_selection_card_markup(role, "UI Designer")
        self.assertIn("os-agent-selection-card", markup)
        self.assertIn("os-agent-selection-card-selected", markup)
        self.assertIn("os-agent-selection-name", markup)
        self.assertIn("os-agent-selection-title", markup)
        self.assertIn("Selected agent", markup)
        self.assertIn("UI Designer", markup)

    def test_selected_agent_context_markup_keeps_mode_choice_near_role_context(self) -> None:
        markup = app.selected_agent_context_markup("Experience Designer")
        self.assertIn("os-selected-agent-shell", markup)
        self.assertIn("Selected agent", markup)
        self.assertIn("Experience Designer", markup)
        self.assertIn("Turn UX signals", markup)

    def test_mode_option_markup_uses_compact_mode_card_hooks(self) -> None:
        markup = app.mode_option_markup("Experience Designer", "Usability Review")
        self.assertIn("os-mode-option-card", markup)
        self.assertIn("os-mode-option-title", markup)
        self.assertIn("Usability Review", markup)
        self.assertIn("scanability", markup)

    def test_mode_option_markup_supports_architect_and_qa_modes(self) -> None:
        architect_markup = app.mode_option_markup("Architect", "Architecture Review")
        qa_markup = app.mode_option_markup("QA", "Validation Review")
        self.assertIn("structural risk", architect_markup)
        self.assertIn("grounded reliability read", qa_markup)

    def test_single_mode_summary_markup_preserves_single_mode_context(self) -> None:
        markup = app.single_mode_summary_markup("PM", "Requirement Discovery")
        self.assertIn("os-mode-single-summary", markup)
        self.assertIn("Requirement Discovery", markup)
        self.assertIn("clarifying questions", markup)

    def test_agent_selection_layout_style_hooks_are_defined(self) -> None:
        self.assertIn("os-agent-workspace-caption", app.SECTION_STYLE)
        self.assertIn("os-agent-selection-card-selected", app.SECTION_STYLE)
        self.assertIn("os-selected-agent-shell", app.SECTION_STYLE)
        self.assertIn("os-mode-option-card", app.SECTION_STYLE)
        self.assertIn("os-mode-single-summary", app.SECTION_STYLE)

    def test_scope_confirmation_uses_outcome_labels(self) -> None:
        class Approval:
            approval_type = "scope_confirmation"

        self.assertEqual(app.approval_button_labels(Approval()), ("Confirm out of scope", "Send to backlog"))

    def test_workspace_approval_requests_only_returns_open_items(self) -> None:
        open_approval = type("Approval", (), {"status": "OPEN"})()
        closed_approval = type("Approval", (), {"status": "APPROVED"})()

        with patch("app.list_approvals", return_value=[closed_approval, open_approval]):
            self.assertEqual(app.workspace_approval_requests(), (open_approval,))

    def test_workspace_approval_metadata_is_concise_decision_context(self) -> None:
        approval = type(
            "Approval",
            (),
            {
                "project_name": "os-control-panel",
                "source_agent_name": "PM",
            },
        )()

        self.assertEqual(app.workspace_approval_metadata(approval), "os-control-panel · PM")

    def test_workspace_approval_section_title_reflects_count(self) -> None:
        self.assertEqual(app.workspace_approval_section_title(1), "Awaiting approval")
        self.assertEqual(app.workspace_approval_section_title(3), "Awaiting approval (3)")

    def test_workflow_card_metadata_uses_concise_dot_separated_context(self) -> None:
        self.assertEqual(app.workflow_card_metadata("os-control-panel", "PM", ""), "os-control-panel · PM")

    def test_workflow_card_kicker_normalises_status_cue(self) -> None:
        self.assertEqual(app.workflow_card_kicker(" approval "), "APPROVAL")

    def test_workflow_card_attention_label_names_user_attention_state(self) -> None:
        self.assertEqual(app.workflow_card_attention_label("approval"), "Action required")
        self.assertEqual(app.workflow_card_attention_label("waiting"), "Waiting on you")
        self.assertEqual(app.workflow_card_attention_label("blocked"), "Blocked")
        self.assertEqual(app.workflow_card_attention_label("routed"), "Routed")
        self.assertEqual(app.workflow_card_attention_label("running"), "Running")

    def test_workflow_card_attention_markup_uses_consistent_cue_container(self) -> None:
        markup = app.workflow_card_attention_markup("approval")
        self.assertIn("os-workflow-card-cue", markup)
        self.assertIn("os-workflow-card-cue-action", markup)
        self.assertIn("Action required", markup)

    def test_workflow_card_anchor_marks_cards_for_simplified_styling(self) -> None:
        self.assertIn("os-workflow-card-anchor", app.workflow_card_anchor_markup())
        self.assertIn("os-workflow-card-anchor", app.SECTION_STYLE)
        self.assertIn("box-shadow: none", app.SECTION_STYLE)

    def test_inbox_section_label_summarises_group_count(self) -> None:
        self.assertEqual(app.inbox_section_label("Waiting on you", 1), "Waiting on you · 1 item")
        self.assertEqual(app.inbox_section_label("Routed", 3), "Routed · 3 items")

    def test_inbox_section_label_markup_uses_compact_count_badge(self) -> None:
        markup = app.inbox_section_label_markup("Blocked", 2)
        self.assertIn("os-inbox-section-label", markup)
        self.assertIn("os-inbox-section-label-count", markup)
        self.assertIn("Blocked", markup)
        self.assertIn("2 items", markup)

    def test_inbox_item_metadata_includes_project_kind_and_state(self) -> None:
        item = type(
            "InboxItemStub",
            (),
            {
                "project_name": "os-control-panel",
                "kind": "pm_clarification",
                "status_bucket": "blocked",
            },
        )()

        self.assertEqual(app.inbox_item_metadata(item), "os-control-panel · pm clarification · Blocked")

    def test_inbox_empty_message_reflects_active_filter_scope(self) -> None:
        self.assertEqual(
            app.inbox_empty_message("All projects", "All"),
            "No active inbox items for all projects.",
        )
        self.assertEqual(
            app.inbox_empty_message("os-control-panel", "Blocked"),
            "No blocked inbox items for os-control-panel.",
        )

    def test_approval_review_sections_expose_full_underlying_draft(self) -> None:
        approval = type(
            "ApprovalStub",
            (),
            {
                "approval_type": "experience_finding",
                "title": "Approve finding",
                "payload": {
                    "user_problem": "The navigation remains labelled workspace after entering a project.",
                    "affected_workflow": "Project navigation",
                    "evidence": "Manual review",
                    "confidence": "HIGH",
                    "severity": "MEDIUM",
                    "frequency": "HIGH",
                    "recommendation_type": "UX improvement in scope",
                    "rationale": "This causes location uncertainty.",
                    "recommended_next_role": "PM",
                },
            },
        )()

        sections = app.approval_review_sections(approval)

        self.assertEqual(sections[0][0], "User problem")
        self.assertIn("navigation remains labelled workspace", sections[0][1])
        self.assertTrue(any(section[0] == "Recommended next role" for section in sections))

    def test_project_card_open_label_targets_project(self) -> None:
        project = next(project for project in summarize_projects() if project.name == "os-control-panel")
        self.assertEqual(app.project_open_button_label(project), "Open os-control-panel")

    def test_open_project_page_caption_frames_selection_workflow(self) -> None:
        caption = app.open_project_page_caption()
        self.assertIn("Choose a project", caption)
        self.assertIn("work signals", caption)

    def test_project_card_status_names_queued_work(self) -> None:
        project = SimpleNamespace(
            structure_ok=True,
            missing_paths=(),
            new_requirements=(SimpleNamespace(id="R1", title="One"),),
            pending_tasks=(),
        )

        self.assertEqual(app.project_card_status(project), ("Work queued", "attention"))

    def test_project_card_status_names_ready_project(self) -> None:
        project = SimpleNamespace(structure_ok=True, missing_paths=(), new_requirements=(), pending_tasks=())

        self.assertEqual(app.project_card_status(project), ("Ready", "ready"))

    def test_project_card_next_work_prioritizes_new_requirements(self) -> None:
        project = SimpleNamespace(
            missing_paths=(),
            new_requirements=(SimpleNamespace(id="R55", title="UI Improvement for Open Project Page"),),
            pending_tasks=(SimpleNamespace(id="Task 114", title="Refine card hierarchy"),),
        )

        label, value = app.project_card_next_work(project)

        self.assertEqual(label, "Next requirement")
        self.assertIn("R55", value)
        self.assertNotIn("Task 114", value)

    def test_project_card_next_work_falls_back_to_pending_task(self) -> None:
        project = SimpleNamespace(
            missing_paths=(),
            new_requirements=(),
            pending_tasks=(SimpleNamespace(id="Task 114", title="Refine card hierarchy"),),
        )

        self.assertEqual(app.project_card_next_work(project), ("Next task", "Task 114 — Refine card hierarchy"))

    def test_project_card_markup_exposes_open_project_styling_hooks(self) -> None:
        project = SimpleNamespace(structure_ok=True, missing_paths=(), new_requirements=(), pending_tasks=())
        status_markup = app.project_card_status_markup(project)
        next_markup = app.project_card_next_work_markup(project)

        self.assertIn("os-project-card-anchor", app.project_card_anchor_markup())
        self.assertIn("os-project-card-kicker-ready", status_markup)
        self.assertIn("os-project-card-next", next_markup)
        self.assertIn("os-project-card-anchor", app.SECTION_STYLE)
        self.assertIn("os-project-card-next", app.SECTION_STYLE)

    def test_project_preview_button_label_targets_project(self) -> None:
        self.assertEqual(app.project_preview_button_label("os-control-panel"), "Open preview")

    def test_selected_project_from_name_returns_matching_project(self) -> None:
        projects = summarize_projects()
        selected = app.selected_project_from_name(projects, "os-control-panel")
        missing = app.selected_project_from_name(projects, "missing-project")
        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "os-control-panel")
        self.assertIsNone(missing)

    def test_role_card_markup_uses_consistent_role_card_container(self) -> None:
        markup = app.role_card_markup(ROLE_CARDS[0])
        self.assertIn("os-role-card", markup)
        self.assertIn("os-role-card-name", markup)
        self.assertIn("os-role-card-title", markup)
        self.assertIn("os-role-card-summary", markup)
        self.assertIn("os-role-card-action-spacer", markup)
        self.assertIn("Tom", markup)

    def test_role_card_style_clamps_summaries_and_strengthens_internal_actions(self) -> None:
        self.assertIn("min-height: 168px", app.ROLE_CARD_STYLE)
        self.assertIn("-webkit-line-clamp: 4", app.ROLE_CARD_STYLE)
        self.assertIn("box-shadow", app.ROLE_CARD_STYLE)
        self.assertIn("stVerticalBlockBorderWrapper", app.ROLE_CARD_STYLE)
        self.assertIn("min-height: 2.5rem", app.ROLE_CARD_STYLE)

    def test_role_card_action_label_opens_summary(self) -> None:
        self.assertEqual(app.agent_summary_action_label(ROLE_CARDS[0]), "Open Tom summary")

    def test_agent_summary_popup_sections_match_requirement(self) -> None:
        summary = agent_summary_by_name("PM")
        sections = app.agent_summary_popup_sections(summary)
        self.assertEqual(
            set(sections),
            {"What this agent can do", "Memory and context", "Workflow position"},
        )
        self.assertTrue(all(sections.values()))

    def test_role_card_rows_create_balanced_rows(self) -> None:
        rows = app.role_card_rows(ROLE_CARDS, row_size=3)
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 3)
        self.assertEqual(len(rows[1]), 3)
        self.assertEqual(len(rows[2]), 1)

    def test_incomplete_role_card_row_keeps_full_row_width(self) -> None:
        rows = app.role_card_rows(ROLE_CARDS, row_size=3)
        self.assertEqual(app.role_card_row_weights(rows[-1]), [1, 1, 1])

    def test_project_card_rows_create_compact_workspace_grid(self) -> None:
        projects = summarize_projects()
        rows = app.project_card_rows(projects, row_size=2)
        self.assertGreaterEqual(len(rows), 1)
        self.assertLessEqual(len(rows[0]), 2)

    def test_single_project_card_row_uses_left_aligned_weights(self) -> None:
        projects = summarize_projects()
        weights = app.project_card_row_weights((projects[0],))
        self.assertEqual(weights, [1, 1])

    def test_split_requirements_for_display_puts_done_items_last(self) -> None:
        records = [
            RequirementRecord("R1", "Done item", "DONE", "HIGH", "S", "desc"),
            RequirementRecord("R2", "Backlog item", "BACKLOG", "MEDIUM", "M", "desc"),
            RequirementRecord("R3", "Active item", "IN_PROGRESS", "HIGH", "S", "desc"),
        ]
        active_records, done_records = app.split_requirements_for_display(records)
        self.assertEqual([record.id for record in active_records], ["R2", "R3"])
        self.assertEqual([record.id for record in done_records], ["R1"])

    def test_active_requirement_rows_create_two_column_layout(self) -> None:
        records = [
            RequirementRecord("R1", "One", "NEW", "HIGH", "S", "desc"),
            RequirementRecord("R2", "Two", "IN_PROGRESS", "MEDIUM", "M", "desc"),
            RequirementRecord("R3", "Three", "BACKLOG", "LOW", "L", "desc"),
        ]
        rows = app.active_requirement_rows(records, row_size=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual([record.id for record in rows[0]], ["R1", "R2"])
        self.assertEqual([record.id for record in rows[1]], ["R3"])

    def test_single_active_requirement_row_uses_left_aligned_weights(self) -> None:
        row = (RequirementRecord("R3", "Three", "BACKLOG", "LOW", "L", "desc"),)
        self.assertEqual(app.active_requirement_row_weights(row), [1, 1])

    def test_requirement_focus_groups_put_priority_work_first(self) -> None:
        records = [
            RequirementRecord("R1", "Backlog low", "BACKLOG", "LOW", "S", "desc"),
            RequirementRecord("R2", "Active medium", "IN_PROGRESS", "MEDIUM", "M", "desc"),
            RequirementRecord("R3", "Backlog high", "BACKLOG", "HIGH", "L", "desc"),
            RequirementRecord("R4", "Backlog medium", "BACKLOG", "MEDIUM", "S", "desc"),
        ]

        groups = app.requirement_focus_groups(records)

        self.assertEqual(groups[0][0], "Priority focus")
        self.assertEqual([record.id for record in groups[0][2]], ["R2", "R3"])
        self.assertEqual(groups[1][0], "Planned backlog")
        self.assertEqual([record.id for record in groups[1][2]], ["R1", "R4"])

    def test_requirement_card_metadata_summarises_status_priority_and_effort(self) -> None:
        record = RequirementRecord("R1", "One", "NEW", "HIGH", "S", "desc")
        self.assertEqual(app.requirement_card_metadata(record), "Status: NEW · Priority: HIGH · Effort: S")

    def test_requirement_expander_label_exposes_priority_signal_before_expansion(self) -> None:
        record = RequirementRecord("R1", "One", "NEW", "HIGH", "S", "desc")
        self.assertEqual(app.requirement_expander_label(record), "R1 — One · NEW · HIGH")

    def test_requirements_panel_keeps_workflow_controls_after_focus_area(self) -> None:
        self.assertEqual(
            app.requirements_panel_section_order(),
            (
                "summary",
                "alerts",
                "sprint_planning",
                "recommendation",
                "structured_requirements",
                "completed_requirements",
            ),
        )

    def test_requirement_editor_cards_are_closed_by_default(self) -> None:
        self.assertFalse(app.requirement_editor_expanded(0))
        self.assertFalse(app.requirement_editor_expanded(3))

    def test_role_cards_cover_expected_roles(self) -> None:
        names = {role["name"] for role in ROLE_CARDS}
        self.assertEqual(
            names,
            {"PM", "Experience Designer", "UI Designer", "Engineer", "QA", "Architect", "Orchestrator"},
        )

    def test_agent_summaries_cover_workspace_roles(self) -> None:
        role_names = {role["name"] for role in ROLE_CARDS}
        summary_names = {summary.name for summary in list_agent_summaries()}
        self.assertEqual(summary_names, role_names)

    def test_agent_summary_includes_required_popup_sections(self) -> None:
        for summary in list_agent_summaries():
            self.assertTrue(summary.can_do, summary.name)
            self.assertTrue(summary.memory_context, summary.name)
            self.assertTrue(summary.workflow_position, summary.name)

    def test_orchestrator_summary_preserves_non_execution_boundary(self) -> None:
        summary = agent_summary_by_name("Orchestrator")
        text = " ".join(summary.can_do + summary.memory_context + summary.workflow_position)
        self.assertIn("Do NOT execute tasks yourself", text)
        self.assertIn("Do NOT modify code", text)

    def test_workspace_summary_includes_known_projects(self) -> None:
        projects = summarize_projects()
        names = {project.name for project in projects}
        self.assertIn("parentmate", names)
        self.assertIn("os-control-panel", names)

    def test_workspace_totals_match_project_summaries(self) -> None:
        projects = summarize_projects()
        totals = workspace_totals(projects)
        self.assertEqual(totals["projects"], len(projects))
        self.assertGreaterEqual(totals["new_requirements"], 0)
        self.assertGreaterEqual(totals["pending_tasks"], 0)

    def test_load_requirement_document_reads_active_and_backlog(self) -> None:
        document = load_requirement_document("os-control-panel")
        self.assertEqual(document.active_requirements[0].id, "R1")
        backlog_ids = [record.id for record in document.backlog_requirements]
        self.assertIn("R3", backlog_ids)
        self.assertIn("R43", backlog_ids)

    def test_update_requirement_persists_changes(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "requirements.md"
            temp_path.write_text(source.read_text())

            with patch("workspace._requirements_path", return_value=temp_path):
                update_requirement(
                    "os-control-panel",
                    RequirementRecord(
                        id="R1",
                        title="Updated title",
                        status="IN_PROGRESS",
                        priority="HIGH",
                        effort="M",
                        description="Updated description",
                    ),
                )
                updated = load_requirement_document("os-control-panel")

        self.assertEqual(updated.active_requirements[0].title, "Updated title")
        self.assertEqual(updated.active_requirements[0].description, "Updated description")

    def test_move_requirement_reorders_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "requirements.md"
            temp_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Active item\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nActive.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\n"
                "### R2 — Backlog one\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nFirst.\n\n"
                "### R3 — Backlog two\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nSecond.\n\n"
                "### R4 — Backlog three\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nThird.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )

            with patch("workspace._requirements_path", return_value=temp_path):
                move_requirement("os-control-panel", "R3", -1)
                updated = load_requirement_document("os-control-panel")

        ids = [record.id for record in updated.active_requirements + updated.backlog_requirements]
        self.assertEqual(ids, ["R1", "R3", "R2", "R4"])

    def test_delete_requirement_removes_unfinished_record(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "requirements.md"
            temp_path.write_text(
                source.read_text().replace(
                    "\n---\n\n## Rules",
                    "\n\n### R99 — Temporary deletion target\n\nStatus: BACKLOG\nPriority: LOW\nEffort: S\nDescription:\nTemporary requirement for deletion test.\n\n---\n\n## Rules",
                    1,
                )
            )

            with patch("workspace._requirements_path", return_value=temp_path):
                deleted = delete_requirement("os-control-panel", "R99")
                updated = load_requirement_document("os-control-panel")

        ids = [record.id for record in updated.active_requirements + updated.backlog_requirements]
        self.assertEqual(deleted.deleted_requirement.id, "R99")
        self.assertNotIn("R99", ids)
        self.assertIn("R17", ids)

    def test_delete_requirement_cleans_linked_tasks_and_artifacts(self) -> None:
        source_requirements = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        source_tasks = REPO_ROOT / "projects" / "os-control-panel" / "product" / "tasks.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_requirements.write_text(
                source_requirements.read_text().replace(
                    "\n---\n\n## Rules",
                    "\n\n### R99 — Temporary deletion target\n\nStatus: BACKLOG\nPriority: LOW\nEffort: S\nDescription:\nTemporary requirement for deletion test.\n\n---\n\n## Rules",
                    1,
                )
            )
            temp_tasks = Path(temp_dir) / "tasks.md"
            temp_tasks.write_text(
                source_tasks.read_text()
                + "\n\n## Task 99: Requirement-specific follow-up\n\nType: Feature Task\nStatus: TODO\nRequirement: R99\n\nGoal:\nKeep requirement-specific work.\n"
                + "\n\n## Task 100: Shared follow-up\n\nType: Feature Task\nStatus: TODO\nRequirements: R99, R17\n\nGoal:\nKeep shared work.\n"
            )
            temp_pm_clarifications = Path(temp_dir) / "pm_clarifications.json"
            temp_pm_clarifications.write_text(
                '[{"clarification_id":"c1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","summary":"Clarify","questions":["Q1"],"status":"OPEN","created_at":"2026-04-25T00:00:00+00:00"}]'
            )
            temp_runs = Path(temp_dir) / "implementation_runs.json"
            temp_output = Path(temp_dir) / "run-output.txt"
            temp_output.write_text("summary")
            temp_log = Path(temp_dir) / "run.log"
            temp_log.write_text("log")
            temp_runs.write_text(
                f'[{{"run_id":"run1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","status":"COMPLETED","summary":"","error":"","created_at":"","started_at":"","finished_at":"","output_path":"{temp_output}","log_path":"{temp_log}","worker_pid":null}}]'
            )

            with patch("workspace._requirements_path", return_value=temp_requirements), patch(
                "workspace._tasks_path", return_value=temp_tasks
            ), patch("workspace._pm_clarifications_path", return_value=temp_pm_clarifications), patch(
                "workspace.IMPLEMENTATION_FILE", temp_runs
            ):
                deleted = delete_requirement("os-control-panel", "R99")
                updated_requirements = load_requirement_document("os-control-panel")
                updated_tasks_text = temp_tasks.read_text()

            ids = [record.id for record in updated_requirements.active_requirements + updated_requirements.backlog_requirements]
            self.assertNotIn("R99", ids)
            self.assertNotIn("## Task 99: Requirement-specific follow-up", updated_tasks_text)
            self.assertIn("Requirement: R17", updated_tasks_text)
            self.assertEqual(deleted.removed_tasks, 1)
            self.assertEqual(deleted.updated_tasks, 1)
            self.assertEqual(deleted.removed_clarifications, 1)
            self.assertEqual(deleted.removed_implementation_runs, 1)
            self.assertFalse(temp_output.exists())
            self.assertFalse(temp_log.exists())

    def test_delete_requirement_rejects_active_implementation_run(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_requirements.write_text(
                source.read_text().replace(
                    "\n---\n\n## Rules",
                    "\n\n### R99 — Temporary deletion target\n\nStatus: BACKLOG\nPriority: LOW\nEffort: S\nDescription:\nTemporary requirement for deletion test.\n\n---\n\n## Rules",
                    1,
                )
            )
            temp_runs = Path(temp_dir) / "implementation_runs.json"
            temp_runs.write_text(
                '[{"run_id":"run1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","status":"RUNNING","summary":"","error":"","created_at":"","started_at":"","finished_at":"","output_path":"","log_path":"","worker_pid":null}]'
            )

            with patch("workspace._requirements_path", return_value=temp_requirements), patch(
                "workspace.IMPLEMENTATION_FILE", temp_runs
            ):
                with self.assertRaises(ValueError):
                    delete_requirement("os-control-panel", "R99")

    def test_delete_requirement_rejects_done_record(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "requirements.md"
            temp_path.write_text(source.read_text())

            with patch("workspace._requirements_path", return_value=temp_path):
                with self.assertRaises(ValueError):
                    delete_requirement("os-control-panel", "R1")

    def test_recommend_requirement_prefers_active_requirement(self) -> None:
        records = [
            RequirementRecord("R1", "Build shell", "IN_PROGRESS", "HIGH", "M", "desc"),
            RequirementRecord("R2", "Remote access", "NEW", "HIGH", "L", "desc"),
        ]
        recommendation = recommend_requirement(records)
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.requirement_id, "R1")

    def test_recommend_requirement_prefers_high_priority_then_lower_effort(self) -> None:
        records = [
            RequirementRecord("R2", "Remote access", "NEW", "MEDIUM", "L", "desc"),
            RequirementRecord("R3", "UI polish", "NEW", "HIGH", "M", "desc"),
            RequirementRecord("R4", "Minor flow", "NEW", "HIGH", "S", "desc"),
        ]
        recommendation = recommend_requirement(records)
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.requirement_id, "R4")

    def test_build_discovery_draft_includes_required_sections(self) -> None:
        draft = build_discovery_draft(
            "os-control-panel",
            "I want PM discovery in the UI",
            {
                "target_user": "Product Director",
                "problem": "Requirements are hard to shape from raw ideas",
                "context": "Current workflow lives in chat and files",
                "constraints": "Keep V1 local-first",
                "success": "A usable draft appears quickly",
                "out_of_scope": "No full chat product",
            },
        )
        self.assertIn("Problem statement", draft)
        self.assertIn("Target user", draft)
        self.assertIn("Open questions", draft)

    def test_discovery_questions_adapt_to_ui_flow_language(self) -> None:
        prompts = discovery_questions("Improve the PM discovery form flow")
        self.assertEqual(len(prompts), 6)
        self.assertIn("simple, relevant, and uncluttered", prompts[3].prompt)
        self.assertIn("interaction and workflow discovery problem", discovery_plan("Improve the PM discovery form flow").framing)

    def test_discovery_plan_changes_for_integration_ideas(self) -> None:
        plan = discovery_plan("Add calendar sync integration")
        self.assertEqual(plan.mode, "integration")
        self.assertIn("integration-style requirement", plan.framing)
        self.assertIn("not connected yet", plan.questions[1].prompt)

    def test_experience_intake_plan_can_suggest_feature_candidate(self) -> None:
        plan = experience_intake_plan("It would be better if the feedback flow asked dynamic questions.")
        self.assertEqual(plan.recommendation_type, "feature candidate")
        self.assertIn("feature candidate", plan.rationale_prompt)

    def test_experience_intake_plan_uses_ui_specific_followup_prompts(self) -> None:
        plan = experience_intake_plan("The page layout and form UI feel heavy.")
        self.assertIn("screen or interaction path", plan.affected_workflow_prompt)
        self.assertIn("current UI or interaction", plan.evidence_prompt)

    def test_experience_finding_can_be_saved_and_routed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_experience = Path(temp_dir) / "experience_findings.json"
            temp_experience.write_text("[]")

            with patch("workspace.EXPERIENCE_FILE", temp_experience):
                finding = save_experience_finding(
                    "os-control-panel",
                    user_problem="Giving feedback via CLI is slower than giving it in the UI",
                    affected_workflow="Product Director feedback loop",
                    evidence="Repeated operator friction while testing the control panel",
                    confidence="Medium",
                    severity="Medium",
                    frequency="Frequent",
                    recommendation_type="UX improvement in scope",
                    rationale="This is an in-scope feedback loop improvement for the current project.",
                )
                findings = list_experience_findings("os-control-panel")
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].recommended_next_role, "PM")
                self.assertEqual(findings[0].handoff_state, "ready_for_pm_review")

                updated = set_experience_handoff_state("os-control-panel", finding.finding_id, "routed")
                self.assertEqual(updated.handoff_state, "routed")

                accepted = set_experience_handoff_state("os-control-panel", finding.finding_id, "accepted")
                self.assertEqual(accepted.handoff_state, "accepted")

    def test_invalid_experience_handoff_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_experience = Path(temp_dir) / "experience_findings.json"
            temp_experience.write_text("[]")

            with patch("workspace.EXPERIENCE_FILE", temp_experience):
                finding = save_experience_finding(
                    "os-control-panel",
                    user_problem="A small UI issue",
                    affected_workflow="Product Director visual scan",
                    evidence="Manual review",
                    confidence="Low",
                    severity="Low",
                    frequency="Occasional",
                    recommendation_type="UX improvement in scope",
                    rationale="Still in scope.",
                )

                with self.assertRaises(ValueError):
                    set_experience_handoff_state("os-control-panel", finding.finding_id, "not_a_real_state")

    def test_pm_clarification_can_be_saved_listed_and_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_data_dir = Path(temp_dir)
            temp_pm_clarifications = temp_data_dir / "pm_clarifications.json"
            temp_pm_clarifications.write_text("[]")

            with patch("workspace._pm_clarifications_path", return_value=temp_pm_clarifications):
                clarification = save_pm_clarification(
                    "os-control-panel",
                    requirement_id="R15",
                    requirement_title="Allow initiation of requirement implementation",
                    summary="Clarify whether the one-active-run rule applies per project or across the OS.",
                    questions=[
                        "Should the one-active-run rule apply per project or across the whole OS?",
                        "If one project is already running implementation, should another project be blocked?",
                    ],
                )
                self.assertEqual(clarification.status, "OPEN")
                self.assertEqual(len(list_pm_clarifications("os-control-panel")), 1)
                self.assertEqual(len(active_pm_clarifications("os-control-panel")), 1)

                resolved = resolve_pm_clarification("os-control-panel", clarification.clarification_id)
                self.assertEqual(resolved.status, "RESOLVED")
                self.assertTrue(bool(resolved.resolved_at))
                self.assertEqual(len(active_pm_clarifications("os-control-panel")), 0)

    def test_pm_thread_can_create_automatic_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_clarifications = Path(temp_dir) / "pm_clarifications.json"
            temp_threads.write_text("[]")
            temp_clarifications.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._pm_clarifications_path", return_value=temp_clarifications
            ), patch(
                "workspace._run_live_pm_turn",
                return_value=LivePMTurn(
                    next_action="request_clarification",
                    assistant_message="This changes implementation shape, so I need one durable clarification before I draft.",
                    clarification_summary="Clarify whether the one-active-run rule applies per project or across the OS.",
                    clarification_questions=[
                        "Should the one-active-run rule apply per project or across the whole OS?",
                    ],
                ),
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want to limit implementation runs to one at a time.",
                )

                self.assertEqual(thread.status, "blocked_clarification")
                clarifications = active_pm_clarifications("os-control-panel")
                self.assertEqual(len(clarifications), 1)
                self.assertEqual(clarifications[0].source_thread_id, thread.thread_id)
                self.assertIn("per project or across the OS", clarifications[0].summary)

    def test_answer_pm_clarification_resumes_linked_pm_thread(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_clarifications = Path(temp_dir) / "pm_clarifications.json"
            temp_threads.write_text("[]")
            temp_clarifications.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._pm_clarifications_path", return_value=temp_clarifications
            ), patch(
                "workspace._run_live_pm_turn",
                side_effect=[
                    LivePMTurn(
                        next_action="request_clarification",
                        assistant_message="This changes implementation shape, so I need one durable clarification before I draft.",
                        clarification_summary="Clarify whether the one-active-run rule applies per project or across the OS.",
                        clarification_questions=[
                            "Should the one-active-run rule apply per project or across the whole OS?",
                        ],
                    ),
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Got it — per project. What user problem does that guardrail protect first?",
                    ),
                ],
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want to limit implementation runs to one at a time.",
                )
                clarification = active_pm_clarifications("os-control-panel")[0]

                resolved = answer_pm_clarification(
                    "os-control-panel",
                    clarification.clarification_id,
                    "Per project. Different projects should be able to run independently.",
                )
                resumed = active_agent_thread("os-control-panel", agent_name="PM", mode="Requirement Discovery")

                self.assertEqual(resolved.status, "RESOLVED")
                self.assertEqual(len(active_pm_clarifications("os-control-panel")), 0)
                self.assertIsNotNone(resumed)
                self.assertEqual(resumed.thread_id, thread.thread_id)
                self.assertIn("per project", resumed.messages[-1].content.lower())

    def test_pm_requirement_discovery_thread_starts_with_pm_followup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_pm_turn",
                return_value=LivePMTurn(
                    next_action="ask_question",
                    assistant_message="Who is the first user we should optimise this requirement for?",
                    draft_title="",
                    draft_requirement="",
                ),
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a better PM discovery chat in the project UI.",
                )

                self.assertEqual(thread.agent_name, "PM")
                self.assertEqual(thread.mode, "Requirement Discovery")
                self.assertEqual(thread.planner_type, "live")
                self.assertEqual(thread.messages[0].role, "user")
                self.assertEqual(thread.messages[1].role, "assistant")
                self.assertIn("first user", thread.messages[1].content)
                self.assertEqual(
                    active_agent_thread(
                        "os-control-panel",
                        agent_name="PM",
                        mode="Requirement Discovery",
                    ).thread_id,
                    thread.thread_id,
                )
                self.assertEqual(thread.current_field_id, "")

    def test_pm_requirement_discovery_thread_asks_follow_up_when_answer_is_too_vague(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_pm_turn",
                side_effect=[
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Who is the first user we should optimise this requirement for?",
                        draft_title="",
                        draft_requirement="",
                    ),
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="I still need a clearer first user. Who exactly should we optimise for first?",
                        draft_title="",
                        draft_requirement="",
                    ),
                ],
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a better PM discovery chat in the project UI.",
                )
                updated = reply_to_pm_requirement_discovery_thread("os-control-panel", thread.thread_id, "Users.")

                self.assertEqual(updated.current_field_id, "")
                self.assertFalse(updated.draft)
                self.assertIn("I still need a clearer first user", updated.messages[-1].content)

    def test_pm_requirement_discovery_thread_auto_drafts_after_enough_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")

            live_turns = [
                LivePMTurn(
                    next_action="ask_question",
                    assistant_message="Who is the first user we should optimise this requirement for?",
                    draft_title="",
                    draft_requirement="",
                ),
                LivePMTurn(
                    next_action="ask_question",
                    assistant_message="What user problem are we solving first?",
                    draft_title="",
                    draft_requirement="",
                ),
                LivePMTurn(
                    next_action="ask_question",
                    assistant_message="Where does that problem show up most clearly in the workflow?",
                    draft_title="",
                    draft_requirement="",
                ),
                LivePMTurn(
                    next_action="ask_question",
                    assistant_message="What constraints should shape the first version?",
                    draft_title="",
                    draft_requirement="",
                ),
                LivePMTurn(
                    next_action="ask_question",
                    assistant_message="What result would make the first version feel successful?",
                    draft_title="",
                    draft_requirement="",
                ),
                LivePMTurn(
                    next_action="draft_requirements",
                    assistant_message="I have enough context to draft requirements now.",
                    draft_title="Add live PM discovery in project chat",
                    draft_requirement="Problem statement\n- Draft body\n\nTarget user\n- Product Director",
                ),
            ]
            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_pm_turn",
                side_effect=live_turns,
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a better PM discovery chat in the project UI.",
                )
                for answer in (
                    "Product Director working inside a project.",
                    "The current form feels stiff and not agentic.",
                    "This shows up when shaping new feature ideas.",
                    "Keep the first slice clean and local-first.",
                    "It should feel like a real PM conversation that still saves structured drafts.",
                ):
                    thread = reply_to_pm_requirement_discovery_thread("os-control-panel", thread.thread_id, answer)

                self.assertTrue(thread.draft)
                self.assertIn("Problem statement", thread.draft)
                self.assertIn("Target user", thread.draft)
                self.assertIn("I have enough context to draft requirements now", thread.messages[-1].content)

    def test_pm_requirement_discovery_thread_uses_previous_answers_to_shape_next_question(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_pm_turn",
                side_effect=[
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Who is the first user we should optimise this requirement for?",
                        draft_title="",
                        draft_requirement="",
                    ),
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Got it. For Product Director working inside a project, what user problem are we trying to solve first?",
                        draft_title="",
                        draft_requirement="",
                    ),
                ],
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a better PM discovery chat in the project UI.",
                )
                thread = reply_to_pm_requirement_discovery_thread(
                    "os-control-panel",
                    thread.thread_id,
                    "Product Director working inside a project.",
                )

                self.assertIn("For Product Director working inside a project,", thread.messages[-1].content)

    def test_pm_requirement_discovery_thread_can_be_drafted_and_saved(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_requirements.write_text(source.read_text())

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_pm_turn",
                side_effect=[
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Who is the first user we should optimise this requirement for?",
                        draft_title="",
                        draft_requirement="",
                    ),
                    LivePMTurn(
                        next_action="draft_requirements",
                        assistant_message="I’ve drafted the first requirement from the context so far.",
                        draft_title="Add PM chat-based requirement discovery",
                        draft_requirement="Problem statement\n- Draft body",
                    ),
                ],
            ), patch(
                "workspace._requirements_path", return_value=temp_requirements
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a PM chat that drafts requirements inside the project.",
                )
                drafted = draft_pm_requirement_discovery_thread("os-control-panel", thread.thread_id)
                record = save_pm_requirement_thread_to_requirements(
                    "os-control-panel",
                    drafted.thread_id,
                    "Add PM chat-based requirement discovery",
                    status="NEW",
                    priority="HIGH",
                    effort="L",
                )
                updated = load_requirement_document("os-control-panel")
                saved_thread = next(
                    thread
                    for thread in list_agent_threads("os-control-panel", agent_name="PM", mode="Requirement Discovery")
                    if thread.thread_id == drafted.thread_id
                )

                self.assertEqual(record.title, "Add PM chat-based requirement discovery")
                self.assertEqual(saved_thread.status, "saved")
                ids = [requirement.id for requirement in updated.active_requirements + updated.backlog_requirements]
                self.assertIn(record.id, ids)

    def test_pm_requirement_draft_can_flow_through_approval(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_threads.write_text("[]")
            temp_requirements.write_text(source.read_text())
            temp_approvals.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch("workspace._requirements_path", return_value=temp_requirements), patch(
                "workspace._run_live_pm_turn",
                side_effect=[
                    LivePMTurn(
                        next_action="ask_question",
                        assistant_message="Who is the first user we should optimise this requirement for?",
                        draft_title="",
                        draft_requirement="",
                    ),
                    LivePMTurn(
                        next_action="draft_requirements",
                        assistant_message="I’ve drafted the first requirement from the context so far.",
                        draft_title="Add PM chat-based requirement discovery",
                        draft_requirement="Problem statement\n- Draft body",
                    ),
                ],
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a PM chat that drafts requirements inside the project.",
                )
                drafted = draft_pm_requirement_discovery_thread("os-control-panel", thread.thread_id)
                approval = request_pm_requirement_thread_approval(
                    "os-control-panel",
                    drafted.thread_id,
                    requirement_title="Add PM chat-based requirement discovery",
                    status="NEW",
                    priority="HIGH",
                    effort="L",
                )
                self.assertEqual(len(active_approvals("os-control-panel")), 1)

                approved = approve_request("os-control-panel", approval.approval_id)
                updated = load_requirement_document("os-control-panel")

                self.assertEqual(approved.status, "APPROVED")
                self.assertEqual(len(active_approvals("os-control-panel")), 0)
                self.assertTrue(any(record.title == "Add PM chat-based requirement discovery" for record in updated.active_requirements))

    def test_experience_designer_thread_can_be_drafted_and_saved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_findings = Path(temp_dir) / "experience_findings.json"
            temp_uploads = Path(temp_dir) / "agent_uploads"
            temp_threads.write_text("[]")
            temp_findings.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.EXPERIENCE_FILE", temp_findings
            ), patch(
                "workspace.AGENT_UPLOAD_DIR", temp_uploads
            ), patch(
                "workspace._run_live_experience_turn",
                side_effect=[
                    LiveExperienceTurn(
                        next_action="ask_question",
                        assistant_message="What part of the workflow is breaking down for the user?",
                    ),
                    LiveExperienceTurn(
                        next_action="draft_finding",
                        assistant_message="I have enough to draft the finding.",
                        finding_draft="User problem\nThe intake feels noisy.",
                        user_problem="The intake feels noisy and unclear.",
                        affected_workflow="Project requirement discovery",
                        evidence="The user reported the flow feels cluttered and repetitive.",
                        confidence="HIGH",
                        severity="MEDIUM",
                        frequency="HIGH",
                        recommendation_type="UX improvement in scope",
                        rationale="This is an in-scope UX clarity issue on an existing surface.",
                    ),
                ],
            ):
                thread = start_experience_designer_thread(
                    "os-control-panel",
                    "Feedback Synthesis",
                    "The current intake feels too noisy.",
                )
                drafted = draft_experience_designer_thread("os-control-panel", thread.thread_id)
                finding = save_experience_thread_to_finding("os-control-panel", drafted.thread_id)
                saved_thread = next(
                    item
                    for item in list_agent_threads("os-control-panel", agent_name="Experience Designer")
                    if item.thread_id == drafted.thread_id
                )

                self.assertEqual(finding.recommended_next_role, "PM")
                self.assertEqual(saved_thread.status, "saved")
                self.assertEqual(len(list_experience_findings("os-control-panel")), 1)

    def test_agent_thread_start_can_persist_image_attachments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_uploads = Path(temp_dir) / "agent_uploads"
            temp_threads.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.AGENT_UPLOAD_DIR", temp_uploads
            ), patch(
                "workspace._run_live_ui_designer_turn",
                return_value=LiveUIDesignTurn(
                    next_action="ask_question",
                    assistant_message="What feel are you aiming for here?",
                ),
            ):
                thread = start_ui_designer_thread(
                    "os-control-panel",
                    "Design Direction",
                    "Help me react to this layout.",
                    image_files=(("layout.png", b"fake-image-bytes"),),
                )
                self.assertEqual(len(thread.messages[0].attachments), 1)
                self.assertTrue(Path(thread.messages[0].attachments[0]).exists())

    def test_live_pm_input_includes_uploaded_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_uploads = Path(temp_dir) / "agent_uploads"
            with patch("workspace.AGENT_UPLOAD_DIR", temp_uploads):
                attachments = save_agent_message_uploads(
                    "os-control-panel",
                    "thread-1",
                    (("reference.png", b"fake-image-bytes"),),
                )
                message = app.AgentMessage(
                    role="user",
                    content="Use this screenshot for context.",
                    created_at="2026-05-08T10:00:00+00:00",
                    attachments=attachments,
                )

                payload = _message_to_live_pm_input(message)

                self.assertIsInstance(payload["content"], list)
                self.assertEqual(payload["content"][0]["type"], "input_text")
                self.assertEqual(payload["content"][1]["type"], "input_image")

    def test_approved_experience_finding_can_auto_create_backlog_requirement(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_findings = Path(temp_dir) / "experience_findings.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_threads.write_text("[]")
            temp_findings.write_text("[]")
            temp_approvals.write_text("[]")
            temp_requirements.write_text(source.read_text())

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.EXPERIENCE_FILE", temp_findings
            ), patch("workspace.APPROVAL_FILE", temp_approvals), patch(
                "workspace._requirements_path", return_value=temp_requirements
            ), patch(
                "workspace._run_live_experience_turn",
                side_effect=[
                    LiveExperienceTurn(
                        next_action="draft_finding",
                        assistant_message="I drafted the finding.",
                        finding_draft="User problem\nThe intake feels noisy.",
                        user_problem="The intake feels noisy and unclear.",
                        affected_workflow="Project requirement discovery",
                        evidence="The user reported the flow feels cluttered and repetitive.",
                        confidence="HIGH",
                        severity="MEDIUM",
                        frequency="HIGH",
                        recommendation_type="UX improvement in scope",
                        rationale="This is an in-scope UX clarity issue on an existing surface.",
                    ),
                ],
            ), patch(
                "workspace._run_live_pm_review_completion_turn",
                return_value=LivePMReviewCompletionTurn(
                    next_action="create_backlog_requirement",
                    assistant_message="This should become a backlog requirement.",
                    requirement_title="Reduce noise in requirement management surfaces",
                    requirement_body="Problem statement\n- The requirement management flow feels noisy.\nTarget user\n- Product Director\nCore job-to-be-done\n- Review and manage requirements with less clutter.\nSuccess criteria\n- The flow feels calmer.\nConstraints\n- Keep existing workflow state visible.\nOut of scope\n- Full redesign.\nAssumptions\n- Clarity matters.\nOpen questions\n- Which surfaces matter most first?",
                    priority="MEDIUM",
                    effort="M",
                ),
            ):
                thread = start_experience_designer_thread(
                    "os-control-panel",
                    "Feedback Synthesis",
                    "The current intake feels too noisy.",
                )
                approval = request_experience_thread_approval("os-control-panel", thread.thread_id)
                approve_request("os-control-panel", approval.approval_id)

                updated = load_requirement_document("os-control-panel")
                findings = list_experience_findings("os-control-panel")

        self.assertTrue(
            any(
                record.title == "Reduce noise in requirement management surfaces"
                or "Additional approved review input" in record.description
                for record in updated.backlog_requirements
            )
        )
        self.assertEqual(findings[0].handoff_state, "resolved")

    def test_ui_designer_thread_can_draft_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_threads.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace._run_live_ui_designer_turn",
                side_effect=[
                    LiveUIDesignTurn(
                        next_action="ask_question",
                        assistant_message="What kind of feel do you want this workspace to have?",
                    ),
                    LiveUIDesignTurn(
                        next_action="draft_design_brief",
                        assistant_message="I drafted a design brief from the context so far.",
                        draft_title="Calmer workspace design direction",
                        design_brief="Design goal\nMake the workspace feel calmer and more deliberate.",
                    ),
                ],
            ):
                thread = start_ui_designer_thread(
                    "os-control-panel",
                    "Design Direction",
                    "The workspace still feels a bit bland.",
                )
                drafted = draft_ui_designer_thread("os-control-panel", thread.thread_id)
                archived = archive_agent_thread("os-control-panel", drafted.thread_id)

                self.assertEqual(drafted.draft_title, "Calmer workspace design direction")
                self.assertIn("Design goal", drafted.draft)
                self.assertEqual(archived.status, "archived")

    def test_ui_design_brief_approval_can_be_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_threads.write_text("[]")
            temp_approvals.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch(
                "workspace._run_live_ui_designer_turn",
                side_effect=[
                    LiveUIDesignTurn(
                        next_action="ask_question",
                        assistant_message="What kind of feel do you want this workspace to have?",
                    ),
                    LiveUIDesignTurn(
                        next_action="draft_design_brief",
                        assistant_message="I drafted a design brief from the context so far.",
                        draft_title="Calmer workspace design direction",
                        design_brief="Design goal\nMake the workspace feel calmer and more deliberate.",
                    ),
                ],
            ):
                thread = start_ui_designer_thread("os-control-panel", "Design Direction", "The workspace feels bland.")
                drafted = draft_ui_designer_thread("os-control-panel", thread.thread_id)
                approval = request_ui_design_brief_approval("os-control-panel", drafted.thread_id)
                rejected = reject_request("os-control-panel", approval.approval_id)

                self.assertEqual(rejected.status, "REJECTED")
                self.assertEqual(len(active_approvals("os-control-panel")), 0)

    def test_approved_ui_design_brief_can_open_scope_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_threads.write_text("[]")
            temp_approvals.write_text("[]")

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch(
                "workspace._run_live_ui_designer_turn",
                return_value=LiveUIDesignTurn(
                    next_action="draft_design_brief",
                    assistant_message="I drafted a design brief from the context so far.",
                    draft_title="Calmer workspace design direction",
                    design_brief="Design goal\nMake the workspace feel calmer and more deliberate.",
                ),
            ), patch(
                "workspace._run_live_pm_review_completion_turn",
                return_value=LivePMReviewCompletionTurn(
                    next_action="confirm_out_of_scope",
                    assistant_message="This needs Product Director scope confirmation.",
                    requirement_title="Introduce a broader visual redesign initiative",
                    requirement_body="Problem statement\n- The product needs a broader redesign.\nTarget user\n- Product Director\nCore job-to-be-done\n- Decide whether to widen the product scope.\nSuccess criteria\n- A scoped decision exists.\nConstraints\n- Keep the current workflow moving.\nOut of scope\n- Full redesign right now.\nAssumptions\n- This is broader than the current slice.\nOpen questions\n- What level of redesign is actually desired?",
                    priority="LOW",
                    effort="L",
                    scope_confirmation_title="Confirm whether the broader redesign stays out of scope",
                    scope_confirmation_summary="PM believes this design request is broader than the current project scope and should only continue if Product Director explicitly wants it in scope.",
                ),
            ):
                thread = start_ui_designer_thread("os-control-panel", "Design Direction", "The workspace feels bland.")
                approval = request_ui_design_brief_approval("os-control-panel", thread.thread_id)
                approve_request("os-control-panel", approval.approval_id)
                open_approvals = active_approvals("os-control-panel")
                archived = next(item for item in list_agent_threads("os-control-panel", agent_name="UI Designer") if item.thread_id == thread.thread_id)

        self.assertEqual(len(open_approvals), 1)
        self.assertEqual(open_approvals[0].approval_type, "scope_confirmation")
        self.assertEqual(archived.status, "archived")

    def test_approved_review_reuses_overlapping_backlog_requirement_instead_of_creating_duplicate(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_threads.write_text("[]")
            temp_approvals.write_text("[]")
            temp_requirements.write_text(source.read_text())

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch(
                "workspace._requirements_path", return_value=temp_requirements
            ), patch(
                "workspace._run_live_ui_designer_turn",
                return_value=LiveUIDesignTurn(
                    next_action="draft_design_brief",
                    assistant_message="I drafted a design brief from the context so far.",
                    draft_title="Workspace simplification direction",
                    design_brief="Design goal\nMake the workspace and inbox calmer, clearer, and easier to scan.",
                ),
            ), patch(
                "workspace._run_live_pm_review_completion_turn",
                return_value=LivePMReviewCompletionTurn(
                    next_action="create_backlog_requirement",
                    assistant_message="This should become backlog work.",
                    requirement_title="Launch a broader workspace visual redesign initiative",
                    requirement_body="Problem statement\n- The workspace and inbox still need a broader visual simplification pass.\nTarget user\n- Product Director\nCore job-to-be-done\n- Decide and execute a clearer workspace simplification direction.\nSuccess criteria\n- Workspace and inbox feel calmer and easier to scan.\nConstraints\n- Keep workflow truthful.\nOut of scope\n- A full rewrite.",
                    priority="LOW",
                    effort="L",
                ),
            ):
                before = load_requirement_document("os-control-panel")
                thread = start_ui_designer_thread("os-control-panel", "Design Direction", "The workspace still feels busy.")
                approval = request_ui_design_brief_approval("os-control-panel", thread.thread_id)
                approve_request("os-control-panel", approval.approval_id)
                after = load_requirement_document("os-control-panel")

        before_backlog = [record for record in before.backlog_requirements if record.status == "BACKLOG"]
        after_backlog = [record for record in after.backlog_requirements if record.status == "BACKLOG"]
        self.assertEqual(len(after_backlog), len(before_backlog))
        self.assertTrue(
            any("Additional approved review input" in record.description for record in after_backlog)
        )
        self.assertTrue(
            any("broader visual simplification pass" in record.description for record in after_backlog)
        )

    def test_rejecting_scope_confirmation_can_send_review_to_backlog(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals.write_text(
                '[{"approval_id":"a1","project_name":"os-control-panel","approval_type":"scope_confirmation","source_thread_id":"t1","source_agent_name":"PM","title":"Confirm out-of-scope outcome","summary":"PM thinks this is broader than current scope.","payload":{"requirement_title":"Introduce a broader visual redesign initiative","requirement_body":"Problem statement\\n- Broader redesign work.","priority":"LOW","effort":"L","finding_id":""},"status":"OPEN","created_at":"1","resolved_at":""}]'
            )
            temp_requirements.write_text(source.read_text())
            temp_threads.write_text('[{"thread_id":"t1","project_name":"os-control-panel","agent_name":"UI Designer","mode":"Design Direction","status":"archived","idea":"idea","planner_type":"live","plan_mode":"live","current_question_index":0,"current_field_id":"","answers":{},"draft_title":"draft","draft":"body","draft_data":{},"messages":[],"created_at":"1","updated_at":"1"}]')

            with patch("workspace.APPROVAL_FILE", temp_approvals), patch(
                "workspace._requirements_path", return_value=temp_requirements
            ), patch("workspace.AGENT_THREAD_FILE", temp_threads):
                rejected = reject_request("os-control-panel", "a1")
                updated = load_requirement_document("os-control-panel")

        self.assertEqual(rejected.status, "REJECTED")
        self.assertTrue(any(record.title == "Introduce a broader visual redesign initiative" for record in updated.backlog_requirements))

    def test_orchestrator_recommendation_reports_idle_project(self) -> None:
        with patch("workspace.parse_requirements", return_value=[]), patch(
            "workspace.parse_tasks", return_value=[]
        ), patch(
            "workspace.load_active_experience_findings", return_value=[]
        ), patch(
            "workspace.load_active_pm_clarifications", return_value=[]
        ), patch(
            "workspace.load_active_agent_threads", return_value=[]
        ), patch(
            "workspace.active_approvals", return_value=[]
        ):
            recommendation = orchestrator_recommendation("os-control-panel")
        self.assertEqual(recommendation.next_role, "None")
        self.assertIn("No agent needs to run automatically", recommendation.next_action)

    def test_architect_review_snapshot_surfaces_structural_hotspot(self) -> None:
        with patch("workspace.parse_requirements", return_value=[{"id": "R1", "title": "Runtime work", "status": "IN_PROGRESS", "description": "Adds new background execution runtime."}]), patch(
            "workspace.parse_tasks",
            return_value=[{"id": "T1", "title": "Implement runtime", "status": "TODO", "requirements": ["R1"]}],
        ):
            snapshot = architect_review_snapshot("os-control-panel")
        self.assertIn("warranted", snapshot.headline)
        self.assertTrue(any("structural triggers" in item for item in snapshot.hotspots))

    def test_run_project_qa_review_reports_runner_summary(self) -> None:
        with patch("workspace.resolve_qa_runner", return_value=REPO_ROOT / "projects" / "os-control-panel" / "tools" / "eval_runner.py"), patch(
            "workspace.run_qa_runner",
            return_value=SimpleNamespace(returncode=0, stdout="SUMMARY: 4/4 passing\n", stderr=""),
        ):
            result = run_project_qa_review("os-control-panel")
        self.assertIn("4/4 passing", result.summary)
        self.assertIn("High confidence", result.confidence)

    def test_record_project_qa_review_persists_latest_quality_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_quality = Path(temp_dir) / "quality_reviews.json"
            with patch("workspace.QUALITY_FILE", temp_quality), patch(
                "workspace.resolve_qa_runner",
                return_value=REPO_ROOT / "projects" / "os-control-panel" / "tools" / "eval_runner.py",
            ), patch(
                "workspace.run_qa_runner",
                return_value=SimpleNamespace(returncode=0, stdout="SUMMARY: 8/8 passing\n", stderr=""),
            ):
                review = record_project_qa_review("os-control-panel")
                latest = latest_quality_review("os-control-panel")

        self.assertEqual(review.status, "PASS")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.review_id, review.review_id)
        self.assertIn("8/8 passing", latest.summary)
        self.assertTrue(bool(latest.reviewed_at))

    def test_record_project_qa_review_marks_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_quality = Path(temp_dir) / "quality_reviews.json"
            with patch("workspace.QUALITY_FILE", temp_quality), patch(
                "workspace.resolve_qa_runner",
                return_value=REPO_ROOT / "projects" / "os-control-panel" / "tools" / "eval_runner.py",
            ), patch(
                "workspace.run_qa_runner",
                return_value=SimpleNamespace(
                    returncode=1,
                    stdout="CASE failing_case_one: FAIL\nCASE failing_case_two: FAIL\nSUMMARY: 6/8 passing\n",
                    stderr="",
                ),
            ):
                review = record_project_qa_review("os-control-panel")

        self.assertEqual(review.status, "FAIL")
        self.assertGreaterEqual(len(review.failures), 1)

    def test_manual_verification_checks_can_be_added_updated_and_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_verification = Path(temp_dir) / "manual_verifications.json"
            with patch("workspace.MANUAL_VERIFICATION_FILE", temp_verification):
                plan = add_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    title="Open the new quality signal panel",
                    instructions="Go to Requirements and confirm the quality panel is visible.",
                )
                self.assertEqual(len(plan.checks), 1)
                check = plan.checks[0]

                updated = update_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    check.check_id,
                    status="PASS",
                    notes="Panel was visible and the summary rendered correctly.",
                )
                self.assertEqual(updated.checks[0].status, "PASS")
                self.assertIn("summary rendered", updated.checks[0].notes)

                removed = remove_manual_verification_check("os-control-panel", "R64", check.check_id)

        self.assertIsNone(removed)
        self.assertIsNone(manual_verification_plan("os-control-panel", "R64"))

    def test_manual_verification_summary_reports_signoff_ready_when_all_checks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_verification = Path(temp_dir) / "manual_verifications.json"
            with patch("workspace.MANUAL_VERIFICATION_FILE", temp_verification):
                first = add_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    title="Check first surface",
                    instructions="Do the first check.",
                )
                second = add_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    title="Check second surface",
                    instructions="Do the second check.",
                )
                for check in second.checks:
                    update_manual_verification_check(
                        "os-control-panel",
                        "R64",
                        check.check_id,
                        status="PASS",
                        notes="Done.",
                    )
                summary = manual_verification_summary("os-control-panel", "R64")

        self.assertEqual(summary.total_checks, 2)
        self.assertEqual(summary.passed_checks, 2)
        self.assertEqual(summary.signoff_state, "READY_FOR_SIGNOFF")
        self.assertEqual(summary.signoff_label, "Ready for signoff")

    def test_manual_verification_summary_reports_blocked_when_any_check_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_verification = Path(temp_dir) / "manual_verifications.json"
            with patch("workspace.MANUAL_VERIFICATION_FILE", temp_verification):
                plan = add_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    title="Check failure path",
                    instructions="Confirm failure handling.",
                )
                update_manual_verification_check(
                    "os-control-panel",
                    "R64",
                    plan.checks[0].check_id,
                    status="FAIL",
                    notes="The state did not update correctly.",
                )
                summary = manual_verification_summary("os-control-panel", "R64")

        self.assertEqual(summary.failed_checks, 1)
        self.assertEqual(summary.signoff_state, "BLOCKED")
        self.assertEqual(summary.signoff_label, "Blocked by failing checks")

    def test_orchestrator_recommendation_routes_experience_designer_for_experience_heavy_pending_task(self) -> None:
        requirements = [
            {
                "id": "R90",
                "title": "Improve onboarding workflow clarity",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "effort": "M",
                "description": "Reduce workflow friction and confusion in the onboarding flow.",
            }
        ]
        tasks = [{"id": "Task 90", "title": "Implement onboarding improvements", "status": "TODO", "requirements": ["R90"]}]
        with patch("workspace.parse_requirements", return_value=requirements), patch(
            "workspace.parse_tasks", return_value=tasks
        ), patch(
            "workspace.load_active_experience_findings", return_value=[]
        ), patch(
            "workspace.load_active_pm_clarifications", return_value=[]
        ), patch(
            "workspace.load_active_agent_threads", return_value=[]
        ), patch(
            "workspace.active_approvals", return_value=[]
        ):
            recommendation = orchestrator_recommendation("os-control-panel")

        self.assertEqual(recommendation.next_role, "Experience Designer")
        self.assertIn("Run Experience Designer", recommendation.next_action)

    def test_orchestrator_recommendation_routes_ui_designer_for_ui_heavy_pending_task(self) -> None:
        requirements = [
            {
                "id": "R91",
                "title": "Refresh requirements page visual hierarchy",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "effort": "M",
                "description": "Improve layout, spacing, and interface polish on the requirements page.",
            }
        ]
        tasks = [{"id": "Task 91", "title": "Implement requirements page refresh", "status": "TODO", "requirements": ["R91"]}]
        with patch("workspace.parse_requirements", return_value=requirements), patch(
            "workspace.parse_tasks", return_value=tasks
        ), patch(
            "workspace.load_active_experience_findings", return_value=[]
        ), patch(
            "workspace.load_active_pm_clarifications", return_value=[]
        ), patch(
            "workspace.load_active_agent_threads", return_value=[]
        ), patch(
            "workspace.active_approvals", return_value=[]
        ):
            recommendation = orchestrator_recommendation("os-control-panel")

        self.assertEqual(recommendation.next_role, "UI Designer")
        self.assertIn("Run UI Designer", recommendation.next_action)

    def test_sprint_preimplementation_gate_routes_experience_designer_for_linked_pending_task(self) -> None:
        requirements = [
            {
                "id": "R36",
                "title": "Improve requirements page layout for enhanced usability",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "effort": "M",
                "description": "This requirements page is confusing, noisy, and creates workflow friction.",
            }
        ]
        tasks = [{"id": "Task 85", "title": "Improve layout", "status": "TODO", "requirements": ["R36"]}]
        with patch("workspace.parse_requirements", return_value=requirements), patch(
            "workspace.parse_tasks", return_value=tasks
        ):
            gate = sprint_preimplementation_gate("os-control-panel", "R36")

        self.assertEqual(gate[0], "Experience Designer")
        self.assertIn("usability/workflow review", gate[1])

    def test_completed_archive_uses_compact_archive_label(self) -> None:
        record = RequirementRecord("R1", "Done item", "DONE", "HIGH", "S", "desc")
        self.assertEqual(app.requirement_card_metadata(record), "Status: DONE · Priority: HIGH · Effort: S")

    def test_requirement_implementation_prompt_mentions_experience_and_ui_designer_when_relevant(self) -> None:
        with patch(
            "workspace.parse_requirements",
            return_value=[
                {
                    "id": "R92",
                    "title": "Improve navigation clarity and visual hierarchy",
                    "status": "IN_PROGRESS",
                    "priority": "HIGH",
                    "effort": "M",
                    "description": "Reduce navigation confusion and improve layout, spacing, and interface polish.",
                }
            ],
        ):
            prompt = build_requirement_implementation_prompt("os-control-panel", "R92")

        self.assertIn("Do not skip Experience Designer", prompt)
        self.assertIn("Do not skip UI Designer", prompt)

    def test_workflow_inbox_collects_waiting_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_threads.write_text(
                '[{"thread_id":"t1","project_name":"os-control-panel","agent_name":"PM","mode":"Requirement Discovery","status":"active","idea":"idea","draft":"","messages":[{"role":"user","content":"idea","created_at":"1"},{"role":"assistant","content":"Who is this for?","created_at":"2"}],"updated_at":"2"}]'
            )
            temp_approvals.write_text(
                '[{"approval_id":"a1","project_name":"os-control-panel","approval_type":"requirement_draft","source_thread_id":"t1","source_agent_name":"PM","title":"Approve requirement draft","summary":"Approve it","payload":{},"status":"OPEN","created_at":"1","resolved_at":""}]'
            )
            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch("workspace.APPROVAL_FILE", temp_approvals):
                items = workflow_inbox_items("os-control-panel")

            self.assertTrue(any(item.kind == "approval" for item in items))
            self.assertTrue(any(item.kind == "agent_thread" for item in items))

    def test_live_pm_project_thread_starts_and_asks_a_question(self) -> None:
        with patch(
            "workspace._run_live_pm_turn",
            return_value=LivePMTurn(
                next_action="ask_question",
                assistant_message="Who is the first user we should optimise this new project for?",
                draft_title="",
                draft_requirement="",
            ),
        ):
            thread = start_live_pm_project_thread(
                "new-project",
                "New Project",
                "I want to build a better intake tool.",
            )

        self.assertEqual(thread.planner_type, "live")
        self.assertEqual(thread.status, "active")
        self.assertEqual(thread.messages[0].role, "user")
        self.assertEqual(thread.messages[-1].role, "assistant")
        self.assertIn("first user", thread.messages[-1].content)

    def test_live_pm_project_thread_can_continue_and_draft(self) -> None:
        first_turn = LivePMTurn(
            next_action="ask_question",
            assistant_message="Who is the first user we should optimise this new project for?",
            draft_title="",
            draft_requirement="",
        )
        second_turn = LivePMTurn(
            next_action="draft_requirements",
            assistant_message="I have enough context now, so I drafted the first requirement.",
            draft_title="Add live PM discovery to new project creation",
            draft_requirement="Problem statement\n- Draft body",
        )
        with patch("workspace._run_live_pm_turn", side_effect=[first_turn, second_turn]):
            thread = start_live_pm_project_thread(
                "new-project",
                "New Project",
                "I want to build a better intake tool.",
            )
            updated = continue_live_pm_project_thread(thread, "Product Directors shaping new projects.")

        self.assertEqual(updated.status, "drafted")
        self.assertEqual(updated.draft_title, "Add live PM discovery to new project creation")
        self.assertIn("Draft body", updated.draft_requirement)

    def test_live_pm_project_thread_can_force_a_draft(self) -> None:
        first_turn = LivePMTurn(
            next_action="ask_question",
            assistant_message="Who is the first user we should optimise this new project for?",
            draft_title="",
            draft_requirement="",
        )
        forced_turn = LivePMTurn(
            next_action="draft_requirements",
            assistant_message="I drafted the best first requirement from the current context.",
            draft_title="Seed the first requirement from live PM discovery",
            draft_requirement="Problem statement\n- Draft body",
        )
        with patch("workspace._run_live_pm_turn", side_effect=[first_turn, forced_turn]):
            thread = start_live_pm_project_thread(
                "new-project",
                "New Project",
                "I want to build a better intake tool.",
            )
            drafted = draft_live_pm_project_thread(thread)

        self.assertEqual(drafted.status, "drafted")
        self.assertEqual(drafted.draft_title, "Seed the first requirement from live PM discovery")

    def test_create_project_from_reviewed_draft_passes_title_and_body_to_scaffold(self) -> None:
        fake_destination = REPO_ROOT / "projects" / "tmp-project"
        with patch("workspace.scaffold_project", return_value=fake_destination) as mock_scaffold:
            destination = create_project_from_reviewed_draft(
                "tmp-project",
                "Tmp Project",
                "Initial live requirement",
                "Problem statement\n- Draft body",
            )

        self.assertEqual(destination, fake_destination)
        mock_scaffold.assert_called_once_with(
            project_name="tmp-project",
            display_name="Tmp Project",
            product_title="Tmp Project",
            initial_requirement_title="Initial live requirement",
            initial_requirement="Problem statement\n- Draft body",
        )

    def test_create_project_from_reviewed_draft_falls_back_when_scaffold_signature_is_older(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "projects" / "tmp-project"
            requirements_path = project_root / "product" / "requirements.md"
            requirements_path.parent.mkdir(parents=True, exist_ok=True)
            requirements_path.write_text(source.read_text())

            def fake_scaffold(**kwargs):
                if "initial_requirement_title" in kwargs:
                    raise TypeError("scaffold_project() got an unexpected keyword argument 'initial_requirement_title'")
                return project_root

            with patch("workspace.scaffold_project", side_effect=fake_scaffold), patch(
                "workspace._requirements_path", return_value=requirements_path
            ):
                destination = create_project_from_reviewed_draft(
                    "tmp-project",
                    "Tmp Project",
                    "Initial live requirement",
                    "Problem statement\n- Draft body",
                )
                updated = load_requirement_document("tmp-project")

        self.assertEqual(destination, project_root)
        self.assertEqual(updated.active_requirements[0].title, "Initial live requirement")

    def test_requirement_implementation_entry_is_allowed_for_new_or_in_progress(self) -> None:
        self.assertTrue(implementation_entry_allowed(RequirementRecord("R1", "Title", "NEW", "HIGH", "M", "desc")))
        self.assertTrue(
            implementation_entry_allowed(RequirementRecord("R2", "Title", "IN_PROGRESS", "HIGH", "M", "desc"))
        )
        self.assertFalse(implementation_entry_allowed(RequirementRecord("R3", "Title", "DONE", "HIGH", "M", "desc")))
        self.assertFalse(
            implementation_entry_allowed(RequirementRecord("R4", "Title", "BACKLOG", "HIGH", "M", "desc"))
        )

    def test_implementation_run_can_be_started_and_tracked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "implementation_runs.json"
            temp_file.write_text("[]")
            temp_log_dir = Path(temp_dir) / "logs"

            with patch("workspace.IMPLEMENTATION_FILE", temp_file), patch(
                "workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir
            ), patch("workspace.subprocess.Popen") as mock_popen, patch(
                "workspace._worker_process_alive", return_value=True
            ):
                mock_popen.return_value.pid = 4321
                record = RequirementRecord("R15", "Allow initiation", "IN_PROGRESS", "HIGH", "L", "desc")
                run = start_requirement_implementation("os-control-panel", record)

                self.assertEqual(run.status, "QUEUED")
                self.assertEqual(run.worker_pid, 4321)
                self.assertEqual(active_implementation_run("os-control-panel").run_id, run.run_id)
                self.assertEqual(
                    latest_requirement_implementation("os-control-panel", "R15").requirement_title,
                    "Allow initiation",
                )

    def test_implementation_progress_metadata_is_status_derived(self) -> None:
        self.assertEqual(implementation_progress_percent("QUEUED"), 10)
        self.assertEqual(implementation_progress_percent("RUNNING"), 55)
        self.assertEqual(implementation_progress_percent("COMPLETED"), 100)
        self.assertEqual(implementation_progress_percent("FAILED"), 100)
        self.assertEqual(implementation_progress_percent("unexpected"), 0)
        self.assertIn("queued", implementation_progress_message("QUEUED"))
        self.assertIn("running", implementation_progress_message("RUNNING"))
        self.assertIn("finished", implementation_progress_message("COMPLETED"))
        self.assertIn("error", implementation_progress_message("FAILED"))
        self.assertIn("prepared", implementation_progress_message("unexpected"))

    def test_reconcile_implementation_runs_marks_dead_running_worker_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "implementation_runs.json"
            temp_file.write_text(
                '[{"run_id":"run1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","status":"RUNNING","summary":"","error":"","created_at":"2026-05-08T06:00:00+00:00","started_at":"2026-05-08T06:00:00+00:00","finished_at":"","output_path":"","log_path":"","worker_pid":999999}]'
            )

            with patch("workspace.IMPLEMENTATION_FILE", temp_file), patch(
                "workspace._worker_process_alive", return_value=False
            ):
                runs = reconcile_implementation_runs("os-control-panel")

        self.assertEqual(runs[0].status, "FAILED")
        self.assertIn("marked failed", runs[0].error)

    def test_streamlit_project_preview_metadata_is_derived_from_app_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            app_file = temp_root / "projects" / "previewable" / "src" / "app.py"
            app_file.parent.mkdir(parents=True)
            app_file.write_text("print('preview')\n")

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("previewable")

        self.assertTrue(preview.available)
        self.assertEqual(preview.runtime, "streamlit")
        self.assertEqual(preview.entry_path, app_file)
        self.assertTrue(preview.url.startswith("http://localhost:"))
        self.assertIn(str(app_file), preview.command)
        self.assertIn("streamlit", preview.command)

    def test_project_preview_explains_unavailable_projects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "projects" / "library-only").mkdir(parents=True)

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("library-only")

        self.assertFalse(preview.available)
        self.assertEqual(preview.command, ())
        self.assertIn("does not expose src/app.py", preview.status_text)

    def test_start_project_preview_reuses_existing_local_port(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            app_file = temp_root / "projects" / "previewable" / "src" / "app.py"
            app_file.parent.mkdir(parents=True)
            app_file.write_text("print('preview')\n")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._local_port_accepts_connections", return_value=True
            ), patch("workspace.subprocess.Popen") as mock_popen:
                preview = start_project_preview("previewable")

        self.assertTrue(preview.available)
        mock_popen.assert_not_called()

    def test_start_project_preview_launches_background_process(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            app_file = temp_root / "projects" / "previewable" / "src" / "app.py"
            app_file.parent.mkdir(parents=True)
            app_file.write_text("print('preview')\n")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._local_port_accepts_connections", return_value=False
            ), patch("workspace.subprocess.Popen") as mock_popen:
                preview = start_project_preview("previewable")

        self.assertTrue(preview.available)
        mock_popen.assert_called_once()
        kwargs = mock_popen.call_args.kwargs
        self.assertTrue(kwargs["start_new_session"])
        self.assertIn(str(temp_root), kwargs["env"]["PYTHONPATH"])

    def test_start_project_preview_rejects_unavailable_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "projects" / "library-only").mkdir(parents=True)

            with patch("workspace.REPO_ROOT", temp_root):
                with self.assertRaises(ValueError):
                    start_project_preview("library-only")

    def test_second_active_implementation_run_in_same_project_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "implementation_runs.json"
            temp_file.write_text("[]")
            temp_log_dir = Path(temp_dir) / "logs"

            with patch("workspace.IMPLEMENTATION_FILE", temp_file), patch(
                "workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir
            ), patch("workspace.subprocess.Popen") as mock_popen, patch(
                "workspace._worker_process_alive", return_value=True
            ):
                mock_popen.return_value.pid = 4321
                first = RequirementRecord("R15", "Allow initiation", "IN_PROGRESS", "HIGH", "L", "desc")
                second = RequirementRecord("R16", "Another flow", "NEW", "MEDIUM", "M", "desc")
                start_requirement_implementation("os-control-panel", first)

                with self.assertRaises(RuntimeError):
                    start_requirement_implementation("os-control-panel", second)

    def test_active_implementation_run_is_project_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "implementation_runs.json"
            temp_file.write_text("[]")
            temp_log_dir = Path(temp_dir) / "logs"

            with patch("workspace.IMPLEMENTATION_FILE", temp_file), patch(
                "workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir
            ), patch("workspace.subprocess.Popen") as mock_popen, patch(
                "workspace._worker_process_alive", return_value=True
            ):
                mock_popen.return_value.pid = 4321
                first = RequirementRecord("R15", "Allow initiation", "IN_PROGRESS", "HIGH", "L", "desc")
                second = RequirementRecord("R1", "Parentmate flow", "NEW", "HIGH", "M", "desc")
                first_run = start_requirement_implementation("os-control-panel", first)
                second_run = start_requirement_implementation("parentmate", second)

                self.assertEqual(active_implementation_run("os-control-panel").run_id, first_run.run_id)
                self.assertEqual(active_implementation_run("parentmate").run_id, second_run.run_id)

    def test_implementation_run_inspection_reads_artifact_excerpts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            output_path = temp_root / "implementation_logs" / "run-last-message.txt"
            log_path = temp_root / "implementation_logs" / "run.log"
            output_path.parent.mkdir(parents=True)
            output_path.write_text("Implementation completed cleanly.\nSummary line.")
            log_path.write_text("line 1\nline 2\nline 3")
            inspected = implementation_run_inspection(
                ImplementationRun(
                run_id="run-1",
                project_name="tmp-project",
                requirement_id="R1",
                requirement_title="Inspect a run",
                status="COMPLETED",
                summary="Implementation completed cleanly.",
                error="",
                created_at="2026-05-23T09:00:00+00:00",
                started_at="2026-05-23T09:01:00+00:00",
                finished_at="2026-05-23T09:03:00+00:00",
                output_path=str(output_path),
                log_path=str(log_path),
                worker_pid=None,
            )
            )

        self.assertEqual(inspected.tone, "completed")
        self.assertTrue(inspected.output_available)
        self.assertTrue(inspected.log_available)
        self.assertIn("Summary line.", inspected.output_excerpt)
        self.assertIn("line 3", inspected.log_excerpt)

    def test_recent_implementation_run_inspections_marks_stale_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "implementation_runs.json"
            temp_file.write_text(
                '[{"run_id":"run-2","project_name":"tmp-project","requirement_id":"R2","requirement_title":"Second","status":"FAILED","summary":"","error":"Implementation worker is no longer running, so this run was marked failed during reconciliation.","created_at":"2026-05-23T10:00:00+00:00","started_at":"2026-05-23T10:01:00+00:00","finished_at":"2026-05-23T10:02:00+00:00","output_path":"","log_path":"","worker_pid":null},{"run_id":"run-1","project_name":"tmp-project","requirement_id":"R1","requirement_title":"First","status":"FAILED","summary":"","error":"Codex execution failed with exit code 1.","created_at":"2026-05-23T09:00:00+00:00","started_at":"2026-05-23T09:01:00+00:00","finished_at":"2026-05-23T09:02:00+00:00","output_path":"","log_path":"","worker_pid":null}]'
            )

            with patch("workspace.IMPLEMENTATION_FILE", temp_file):
                inspections = recent_implementation_run_inspections("tmp-project")

        self.assertEqual(inspections[0].run.run_id, "run-2")
        self.assertEqual(inspections[0].tone, "stale")
        self.assertEqual(inspections[0].display_status, "Failed (stale worker)")
        self.assertEqual(inspections[1].tone, "failed")

    def test_approved_design_brief_records_outcome_reference_for_timeline(self) -> None:
        source = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_requirements = Path(temp_dir) / "requirements.md"
            temp_threads.write_text("[]")
            temp_approvals.write_text("[]")
            temp_requirements.write_text(source.read_text())

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch(
                "workspace._requirements_path", return_value=temp_requirements
            ), patch(
                "workspace._run_live_ui_designer_turn",
                return_value=LiveUIDesignTurn(
                    next_action="draft_design_brief",
                    assistant_message="I drafted a design brief from the context so far.",
                    draft_title="Inbox clarity pass",
                    design_brief="Make inbox attention states clearer.",
                ),
            ), patch(
                "workspace._run_live_pm_review_completion_turn",
                return_value=LivePMReviewCompletionTurn(
                    next_action="create_backlog_requirement",
                    assistant_message="This should become backlog work.",
                    requirement_title="Improve inbox attention-state clarity",
                    requirement_body="Problem statement\n- Inbox attention states need clearer differentiation.",
                    priority="MEDIUM",
                    effort="M",
                ),
            ):
                thread = start_ui_designer_thread("os-control-panel", "UI Review", "The inbox still feels muddy.")
                approval = request_ui_design_brief_approval("os-control-panel", thread.thread_id)
                approved = approve_request("os-control-panel", approval.approval_id)

        self.assertEqual(approved.status, "APPROVED")
        self.assertEqual(approved.payload.get("outcome_kind"), "requirement")
        self.assertTrue(approved.payload.get("outcome_reference_id", "").startswith("R"))
        self.assertIn("Continued into backlog requirement", approved.payload.get("outcome_detail", ""))

    def test_workflow_timeline_events_collect_recent_artifact_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_threads = Path(temp_dir) / "agent_threads.json"
            temp_approvals = Path(temp_dir) / "approvals.json"
            temp_clarifications = Path(temp_dir) / "pm_clarifications.json"
            temp_experience = Path(temp_dir) / "experience_findings.json"
            temp_runs = Path(temp_dir) / "implementation_runs.json"
            temp_threads.write_text(
                '[{"thread_id":"t1","project_name":"os-control-panel","agent_name":"UI Designer","mode":"Design Direction","status":"pending_approval","idea":"Make it calmer.","planner_type":"live","plan_mode":"live","current_question_index":0,"current_field_id":"","answers":{},"draft_title":"Inbox direction","draft":"Design brief","draft_data":{},"messages":[{"role":"assistant","content":"I drafted a direction.","created_at":"2026-05-23T09:50:00+00:00"}],"created_at":"2026-05-23T09:45:00+00:00","updated_at":"2026-05-23T10:00:00+00:00"}]'
            )
            temp_approvals.write_text(
                '[{"approval_id":"a1","project_name":"os-control-panel","approval_type":"design_brief","source_thread_id":"t1","source_agent_name":"UI Designer","title":"Approve inbox direction","summary":"Approve this brief.","payload":{"outcome_kind":"requirement","outcome_title":"Improve inbox clarity","outcome_reference_id":"R80","outcome_detail":"Continued into backlog requirement R80."},"status":"APPROVED","created_at":"2026-05-23T10:05:00+00:00","resolved_at":"2026-05-23T10:10:00+00:00"}]'
            )
            temp_clarifications.write_text(
                '[{"clarification_id":"c1","project_name":"os-control-panel","requirement_id":"R15","requirement_title":"One run rule","source_thread_id":"","summary":"Clarify project scope.","questions":["Per project or global?"],"status":"RESOLVED","created_at":"2026-05-23T09:40:00+00:00","resolved_at":"2026-05-23T09:42:00+00:00"}]'
            )
            temp_experience.write_text(
                '[{"finding_id":"f1","project_name":"os-control-panel","user_problem":"Users miss the inbox state cues.","affected_workflow":"Inbox scan","evidence":"Manual review","confidence":"MEDIUM","severity":"MEDIUM","frequency":"FREQUENT","recommendation_type":"UX improvement in scope","rationale":"State cues are too subtle.","recommended_next_role":"PM","handoff_state":"resolved","created_at":"2026-05-23T09:30:00+00:00"}]'
            )
            temp_runs.write_text(
                '[{"run_id":"run-1","project_name":"os-control-panel","requirement_id":"R40","requirement_title":"Improve inbox","status":"COMPLETED","summary":"Implementation finished cleanly.","error":"","created_at":"2026-05-23T09:20:00+00:00","started_at":"2026-05-23T09:21:00+00:00","finished_at":"2026-05-23T09:25:00+00:00","output_path":"","log_path":"","worker_pid":null}]'
            )

            with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
                "workspace.APPROVAL_FILE", temp_approvals
            ), patch(
                "workspace._pm_clarifications_path", return_value=temp_clarifications
            ), patch(
                "workspace.EXPERIENCE_FILE", temp_experience
            ), patch(
                "workspace.IMPLEMENTATION_FILE", temp_runs
            ):
                events = workflow_timeline_events("os-control-panel", limit=10)

        self.assertGreaterEqual(len(events), 6)
        self.assertEqual(events[0].artifact_kind, "approval outcome")
        self.assertIn("R80", events[0].detail)
        self.assertTrue(any(event.artifact_kind == "clarification" and event.status_bucket == "completed" for event in events))
        self.assertTrue(any(event.artifact_kind == "implementation run" and event.status_bucket == "completed" for event in events))

    def test_sprint_plan_can_add_reorder_and_remove_backlog_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            requirements_path = temp_root / "projects" / "tmp-project" / "product" / "requirements.md"
            requirements_path.parent.mkdir(parents=True)
            requirements_path.write_text(
                "# Product Requirements\n\n"
                "## Active Requirements\n\n"
                "Add active requirements here.\n\n---\n\n"
                "## Backlog (Not yet prioritised)\n\n"
                "### R1 — First backlog\n\nStatus: BACKLOG\nPriority: HIGH\nEffort: M\nDescription:\nFirst.\n\n"
                "### R2 — Second backlog\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nSecond.\n\n"
                "---\n\n## Rules\n\n"
                "* Only requirements with Status: NEW should be converted into tasks\n"
            )

            with patch("workspace.REPO_ROOT", temp_root):
                plan_sprint_requirement("tmp-project", "R1")
                plan_sprint_requirement("tmp-project", "R2")
                moved = move_sprint_requirement("tmp-project", "R2", -1)
                self.assertEqual(moved.requirement_ids, ("R2", "R1"))
                self.assertEqual(
                    tuple(record.id for record in sprint_requirement_records("tmp-project")),
                    ("R2", "R1"),
                )
                remaining = remove_sprint_requirement("tmp-project", "R2")

        self.assertIsNotNone(remaining)
        self.assertEqual(remaining.requirement_ids, ("R1",))

    def test_start_sprint_promotes_first_backlog_requirement_and_starts_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            requirements_path = temp_root / "projects" / "tmp-project" / "product" / "requirements.md"
            requirements_path.parent.mkdir(parents=True)
            requirements_path.write_text(
                "# Product Requirements\n\n"
                "## Active Requirements\n\n"
                "Add active requirements here.\n\n---\n\n"
                "## Backlog (Not yet prioritised)\n\n"
                "### R1 — First backlog\n\nStatus: BACKLOG\nPriority: HIGH\nEffort: M\nDescription:\nFirst.\n\n"
                "### R2 — Second backlog\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nSecond.\n\n"
                "---\n\n## Rules\n\n"
                "* Only requirements with Status: NEW should be converted into tasks\n"
            )
            temp_file = temp_root / "implementation_runs.json"
            temp_file.write_text("[]")
            temp_log_dir = temp_root / "logs"

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace.IMPLEMENTATION_FILE", temp_file
            ), patch("workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir), patch(
                "workspace.subprocess.Popen"
            ) as mock_popen, patch(
                "workspace._worker_process_alive", return_value=True
            ):
                mock_popen.return_value.pid = 9876
                plan_sprint_requirement("tmp-project", "R1")
                plan_sprint_requirement("tmp-project", "R2")
                sprint = start_sprint("tmp-project")
                updated = load_requirement_document("tmp-project")
                active_run = active_implementation_run("tmp-project")

        self.assertEqual(sprint.status, "ACTIVE")
        self.assertEqual(sprint.current_requirement_id, "R1")
        self.assertEqual(updated.active_requirements[0].id, "R1")
        self.assertEqual(updated.active_requirements[0].status, "NEW")
        self.assertEqual(active_run.requirement_id, "R1")

    def test_advance_active_sprint_starts_next_requirement_after_previous_is_done(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            requirements_path = temp_root / "projects" / "tmp-project" / "product" / "requirements.md"
            requirements_path.parent.mkdir(parents=True)
            requirements_path.write_text(
                "# Product Requirements\n\n"
                "## Active Requirements\n\n"
                "### R1 — First item\n\nStatus: DONE\nPriority: HIGH\nEffort: M\nDescription:\nDone.\n\n"
                "---\n\n"
                "## Backlog (Not yet prioritised)\n\n"
                "### R2 — Second item\n\nStatus: BACKLOG\nPriority: MEDIUM\nEffort: S\nDescription:\nNext.\n\n"
                "---\n\n## Rules\n\n"
                "* Only requirements with Status: NEW should be converted into tasks\n"
            )
            sprint_path = temp_root / "projects" / "tmp-project" / "data" / "sprint.json"
            sprint_path.parent.mkdir(parents=True)
            sprint_path.write_text(
                '{"status":"ACTIVE","requirement_ids":["R1","R2"],"created_at":"now","started_at":"now","completed_at":"","current_requirement_id":"R1","blocked_reason":""}'
            )
            temp_file = temp_root / "implementation_runs.json"
            temp_file.write_text("[]")
            temp_log_dir = temp_root / "logs"

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace.IMPLEMENTATION_FILE", temp_file
            ), patch("workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir), patch(
                "workspace.subprocess.Popen"
            ) as mock_popen:
                mock_popen.return_value.pid = 5555
                sprint = advance_active_sprint("tmp-project")
                updated = load_requirement_document("tmp-project")

        self.assertIsNotNone(sprint)
        self.assertEqual(sprint.current_requirement_id, "R2")
        self.assertEqual(updated.active_requirements[-1].id, "R2")
        self.assertEqual(updated.active_requirements[-1].status, "NEW")

    def test_active_sprint_becomes_ready_to_close_when_all_items_are_done(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            requirements_path = temp_root / "projects" / "tmp-project" / "product" / "requirements.md"
            requirements_path.parent.mkdir(parents=True)
            requirements_path.write_text(
                "# Product Requirements\n\n"
                "## Active Requirements\n\n"
                "### R1 — Finished one\n\nStatus: DONE\nPriority: HIGH\nEffort: M\nDescription:\nDone.\n\n"
                "### R2 — Finished two\n\nStatus: DONE\nPriority: MEDIUM\nEffort: S\nDescription:\nDone.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n"
                "* Only requirements with Status: NEW should be converted into tasks\n"
            )
            sprint_path = temp_root / "projects" / "tmp-project" / "data" / "sprint.json"
            sprint_path.parent.mkdir(parents=True)
            sprint_path.write_text(
                '{"status":"ACTIVE","requirement_ids":["R1","R2"],"created_at":"now","started_at":"now","completed_at":"","current_requirement_id":"R2","blocked_reason":""}'
            )

            with patch("workspace.REPO_ROOT", temp_root):
                sprint = advance_active_sprint("tmp-project")

        self.assertEqual(sprint.status, "READY_TO_CLOSE")

    def test_complete_sprint_leaves_empty_completed_sprint_ready_for_next_planning_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            sprint_path = temp_root / "projects" / "tmp-project" / "data" / "sprint.json"
            sprint_path.parent.mkdir(parents=True)
            sprint_path.write_text(
                '{"status":"READY_TO_CLOSE","requirement_ids":["R1"],"created_at":"now","started_at":"now","completed_at":"later","current_requirement_id":"","blocked_reason":""}'
            )

            with patch("workspace.REPO_ROOT", temp_root):
                complete_sprint("tmp-project")
                sprint = load_sprint_plan("tmp-project")

        self.assertIsNotNone(sprint)
        self.assertEqual(sprint.status, "COMPLETED")
        self.assertEqual(sprint.requirement_ids, ())

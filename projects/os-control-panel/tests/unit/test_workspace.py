from __future__ import annotations

import json
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
from agents_runtime import support as agent_runtime  # noqa: E402
from pm_contract import PMDecisionEnvelope  # noqa: E402
import workspace  # noqa: E402
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
    build_dynamic_reflection_plan,
    build_concept_teaching_brief,
    build_build_to_learn_pathway,
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
    learning_concept_build_to_learn,
    learning_concept_detail_view,
    learning_concept_family,
    learning_concept_family_placement,
    learning_concept_governing_truth,
    learning_concept_navigation_sections,
    learning_concept_history,
    learning_concept_hierarchy,
    learning_implementation_anchors,
    learning_concept_record,
    learning_concept_relationships,
    learning_concept_view,
    learning_progress_items,
    list_learning_concept_recommendations,
    load_learning_agent_session,
    load_learning_profile,
    load_project_ui_runtime,
    manual_verification_plan,
    manual_verification_summary,
    list_pm_clarifications,
    load_requirement_document,
    reconcile_implementation_runs,
    record_project_qa_review,
    reconcile_web_app_requirement_after_verification,
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
    save_private_reflection_draft,
    save_private_concept_note_draft,
    save_private_build_to_learn_pathway,
    save_build_to_learn_outcome,
    save_learning_concept_management_update,
    save_learning_profile,
    save_project_ui_runtime,
    pause_learning_agent_session,
    personalized_learning_plan,
    clear_learning_agent_session,
    continue_learning_agent_session,
    learning_build_to_learn_enabled,
    learning_reflection_enabled,
    learning_release_profile,
    request_learning_agent_clarification,
    request_learning_agent_implementation_walkthrough,
    save_pm_requirement_thread_to_requirements,
    start_experience_designer_thread,
    start_learning_agent_session,
    start_live_pm_project_thread,
    start_pm_requirement_discovery_thread,
    start_ui_designer_thread,
    set_experience_handoff_state,
    start_project_preview,
    start_requirement_implementation,
    start_sprint,
    LiveExperienceTurn,
    LiveLearningClarificationTurn,
    LiveLearningImplementationTurn,
    LiveLearningTeachingTurn,
    LivePMDiscoveryError,
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
    def test_openai_runtime_inference_uses_responses_web_search_for_current_research(self) -> None:
        decision = workspace.infer_openai_runtime_decision(
            RequirementRecord(
                "R1",
                "Evaluate AI ideas",
                "NEW",
                "HIGH",
                "M",
                "Use OpenAI web search to perform current market research and return a structured score.",
            )
        )

        self.assertTrue(decision.required)
        self.assertEqual(decision.surface, "responses_api")
        self.assertIn("web_search", decision.capabilities)
        self.assertIn("structured_output", decision.capabilities)
        self.assertEqual(decision.credentials, ("OPENAI_API_KEY",))

    def test_openai_runtime_inference_selects_specialized_surfaces(self) -> None:
        agents_decision = workspace.infer_openai_runtime_decision(
            RequirementRecord("R1", "Coordinate specialist agents", "NEW", "HIGH", "M", "Use multiple agents with handoffs.")
        )
        app_decision = workspace.infer_openai_runtime_decision(
            RequirementRecord("R2", "Publish a ChatGPT app", "NEW", "HIGH", "M", "Make this available inside ChatGPT using the Apps SDK.")
        )
        ordinary_decision = workspace.infer_openai_runtime_decision(
            RequirementRecord("R3", "Improve navigation", "NEW", "MEDIUM", "S", "Make the existing tabs easier to scan.")
        )
        realtime_decision = workspace.infer_openai_runtime_decision(
            RequirementRecord("R4", "Add live voice", "NEW", "HIGH", "M", "Use OpenAI for a real-time voice conversation.")
        )

        self.assertEqual(agents_decision.surface, "agents_sdk")
        self.assertIn("agent_handoffs", agents_decision.capabilities)
        self.assertEqual(app_decision.surface, "apps_sdk")
        self.assertTrue(any("distribution" in item for item in app_decision.review_reasons))
        self.assertFalse(ordinary_decision.required)
        self.assertEqual(ordinary_decision.surface, "none")
        self.assertEqual(ordinary_decision.review_reasons, ())
        self.assertEqual(realtime_decision.surface, "realtime_api")
        self.assertIn("realtime_audio", realtime_decision.capabilities)

    def test_openai_runtime_decisions_reconcile_when_requirement_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "openai-runtime.json"
            initial = RequirementRecord("R1", "Improve navigation", "NEW", "MEDIUM", "S", "Make tabs easier to scan.")
            changed = RequirementRecord("R1", "Add AI research", "NEW", "HIGH", "M", "Use OpenAI web search for current information.")
            with patch("workspace._openai_runtime_path", return_value=runtime_path):
                first = workspace.reconcile_openai_runtime_decisions("tmp-project", [initial])["R1"]
                second = workspace.reconcile_openai_runtime_decisions("tmp-project", [changed])["R1"]
                payload = json.loads(runtime_path.read_text())

        self.assertFalse(first.required)
        self.assertTrue(second.required)
        self.assertNotEqual(first.requirement_fingerprint, second.requirement_fingerprint)
        self.assertEqual(payload["requirements"]["R1"]["surface"], "responses_api")

    def test_project_capability_context_includes_openai_runtime_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "demo"
            product_root = project_root / "product"
            product_root.mkdir(parents=True)
            (product_root / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            (product_root / "openai-runtime.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "requirements": {
                            "R1": {
                                "required": True,
                                "surface": "responses_api",
                                "capabilities": ["web_search"],
                            }
                        },
                    }
                )
            )
            with patch("agents_runtime.support._project_root", return_value=project_root):
                payload = agent_runtime._project_capability_profile_payload("demo")

        self.assertEqual(payload["openai_runtime"]["requirements"]["R1"]["surface"], "responses_api")
        self.assertEqual(payload["openai_runtime"]["requirements"]["R1"]["capabilities"], ["web_search"])

    def test_friendly_live_agent_error_message_maps_quota_failure(self) -> None:
        detail = (
            "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and "
            "billing details.', 'type': 'insufficient_quota'}}"
        )
        message = workspace._friendly_live_agent_error_message(detail)
        self.assertIn("run out of quota", message)
        self.assertIn("OPENAI_API_KEY", message)

    def test_friendly_live_agent_error_message_maps_invalid_key_failure(self) -> None:
        detail = (
            "Error code: 401 - {'error': {'message': 'Incorrect API key provided', 'code': 'invalid_api_key'}}"
        )
        message = workspace._friendly_live_agent_error_message(detail)
        self.assertIn("OPENAI_API_KEY is invalid", message)

    def test_live_learning_system_prompt_includes_tutoring_guardrails(self) -> None:
        teaching_prompt = workspace._live_learning_system_prompt("teach_concept")
        clarification_prompt = workspace._live_learning_system_prompt("clarify_concept")

        self.assertIn("single tutoring agent", teaching_prompt)
        self.assertIn("Do not invent implementation details", teaching_prompt)
        self.assertIn("Do not imply a concept is fully learned", teaching_prompt)
        self.assertIn("resolve the learner's exact confusion", clarification_prompt)

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
        self.assertEqual(
            app.top_level_tab_labels(),
            ("Workspace", "Operations", "Learning", "Open Project", "Inbox", "Create Project"),
        )
        self.assertNotIn("Project Detail", app.top_level_tab_labels())

    def test_top_level_navigation_has_explicit_main_label(self) -> None:
        self.assertEqual(app.top_level_navigation_label(), "Main navigation")

    def test_top_level_navigation_exposes_workspace_layer_context(self) -> None:
        self.assertEqual(app.top_level_navigation_level_label(), "Workspace-level navigation")
        self.assertIn("workspace overview", app.top_level_navigation_scope_description())
        self.assertIn("learning layer", app.top_level_navigation_scope_description())
        self.assertIn("workflow inbox", app.top_level_navigation_scope_description())

    def test_top_level_navigation_uses_segmented_control(self) -> None:
        self.assertEqual(app.top_level_navigation_control_kind(), "segmented_control")

    def test_learning_navigation_keeps_four_stable_sections(self) -> None:
        self.assertEqual(app.learning_section_labels(), ("Profile", "Learning plan", "Learn next", "Builds"))

    def test_learning_navigation_hides_builds_in_external_release_mode(self) -> None:
        with patch.dict("os.environ", {"AI_BUILDER_OS_LEARNING_RELEASE_PROFILE": "external_v2"}):
            self.assertEqual(app.learning_section_labels(), ("Profile", "Learning plan", "Learn next"))

    def test_learning_next_surface_prioritizes_active_session(self) -> None:
        self.assertEqual(
            app.learning_next_surface(
                has_active_session=True,
            ),
            "session",
        )

    def test_learning_next_surface_falls_back_to_recommendations(self) -> None:
        self.assertEqual(
            app.learning_next_surface(
                has_active_session=False,
            ),
            "recommendations",
        )

    def test_learning_release_profile_defaults_to_internal_v2(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(learning_release_profile(), "internal_v2")
            self.assertTrue(learning_reflection_enabled())
            self.assertTrue(learning_build_to_learn_enabled())

    def test_learning_release_profile_can_switch_to_external_v2(self) -> None:
        with patch.dict("os.environ", {"AI_BUILDER_OS_LEARNING_RELEASE_PROFILE": "external_v2"}):
            self.assertEqual(learning_release_profile(), "external_v2")
            self.assertFalse(learning_reflection_enabled())
            self.assertFalse(learning_build_to_learn_enabled())

    def test_top_level_navigation_uses_task_oriented_project_labels(self) -> None:
        self.assertIn("Learning", app.top_level_tab_labels())
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
        self.assertEqual(descriptions["Learning"], "Concept growth")
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
        self.assertIn("Learning: Concept growth", markup)
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
            ["PM", "Experience Designer", "UI Designer", "Architect", "Orchestrator", "QA"],
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

    def test_inbox_card_rows_create_two_column_layout(self) -> None:
        items = ("one", "two", "three")
        rows = app.inbox_card_rows(items)

        self.assertEqual(rows, [("one", "two"), ("three",)])

    def test_single_inbox_card_row_keeps_left_aligned_space(self) -> None:
        self.assertEqual(app.inbox_card_row_weights(("one",)), [1, 1])
        self.assertEqual(app.inbox_card_row_weights(("one", "two")), [1, 1])

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
        self.assertEqual(
            app.requirement_card_metadata(record),
            "Status: NEW · Priority: HIGH · Effort: S · Project type: Project default",
        )

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
        self.assertIn("without doing the work yourself", text)
        self.assertIn("without taking over PM, Engineer, or QA work directly", text)

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
        active_ids = [record.id for record in document.active_requirements]
        self.assertIn("R43", active_ids)

    def test_load_requirement_document_reads_optional_ui_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Runtime-aware requirement\n\n"
                "Status: NEW\nPriority: HIGH\nEffort: M\nUI Runtime: web_app\nDescription:\nBuild a frontend surface.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )

            with patch("workspace._requirements_path", return_value=requirements_path):
                document = load_requirement_document("tmp-project")

        self.assertEqual(document.active_requirements[0].ui_runtime, "web_app")

    def test_project_ui_runtime_defaults_to_streamlit_when_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "missing-ui-runtime.json"
            with patch("workspace._ui_runtime_path", return_value=runtime_path):
                runtime = load_project_ui_runtime("tmp-project")

        self.assertEqual(runtime, "streamlit")

    def test_save_and_load_project_ui_runtime_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "ui-runtime.json"
            with patch("workspace._ui_runtime_path", return_value=runtime_path):
                save_project_ui_runtime("tmp-project", "web_app")
                runtime = load_project_ui_runtime("tmp-project")

        self.assertEqual(runtime, "web_app")

    def test_project_figma_config_preserves_runtime_and_requirement_mappings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "ui-runtime.json"
            runtime_path.write_text('{"default_ui_runtime":"web_app"}')
            with patch("workspace._ui_runtime_path", return_value=runtime_path):
                workspace.save_project_figma_config(
                    "tmp-project",
                    mode="figma_referenced",
                    file_url="https://www.figma.com/design/file-key/Product",
                    file_name="Product UI",
                )
                workspace.save_requirement_figma_reference(
                    "tmp-project",
                    requirement_id="R12",
                    frame_url="https://www.figma.com/design/file-key/Product?node-id=12-34",
                    frame_name="Checkout / Desktop",
                    approved=True,
                )
                workspace.save_project_ui_runtime("tmp-project", "web_app")
                config = workspace.load_project_figma_config("tmp-project")

        self.assertEqual(config.mode, "figma_referenced")
        self.assertEqual(config.file_name, "Product UI")
        self.assertEqual(config.references[0].requirement_id, "R12")
        self.assertEqual(config.references[0].approval_status, "approved")

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
                        ui_runtime="web_app",
                    ),
                )
                updated = load_requirement_document("os-control-panel")

        self.assertEqual(updated.active_requirements[0].title, "Updated title")
        self.assertEqual(updated.active_requirements[0].description, "Updated description")
        self.assertEqual(updated.active_requirements[0].ui_runtime, "web_app")

    def test_marking_requirement_done_creates_release_delivery_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Release gate\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nShip it.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )
            change_plan = workspace.GitChangePlan(
                included_paths=("projects/os-control-panel/product/requirements.md", "projects/os-control-panel/src/app.py"),
                excluded_paths=("projects/os-control-panel/data/approvals.json",),
                branch="feature/release",
            )

            with patch("workspace._requirements_path", return_value=requirements_path), patch(
                "workspace.APPROVAL_FILE", approvals_path
            ), patch("workspace._release_git_change_plan", return_value=change_plan), patch(
                "workspace.load_project_ui_runtime", return_value="web_app"
            ), patch(
                "workspace._web_app_browser_verification_passed", return_value=True
            ):
                update_requirement(
                    "os-control-panel",
                    RequirementRecord("R1", "Release gate", "DONE", "HIGH", "M", "Ship it."),
                )
                updated = load_requirement_document("os-control-panel")
                approvals = list_approvals("os-control-panel")

        self.assertEqual(updated.active_requirements[0].status, "IN_PROGRESS")
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0].approval_type, "release_delivery")
        self.assertEqual(approvals[0].payload["project_type"], "web_app")
        self.assertEqual(approvals[0].payload["deployment_provider"], "vercel")
        self.assertIn("Frontend app builder", approvals[0].payload["capability_pack"])
        self.assertIn("React best practices", approvals[0].payload["capability_pack"])
        self.assertIn("Vercel preview deployment", approvals[0].payload["architecture_guidance"])
        self.assertEqual(approvals[0].payload["openai_runtime_required"], "NO")
        self.assertEqual(approvals[0].payload["openai_surface"], "none")
        self.assertIn("FAIL package.json is required", approvals[0].payload["release_readiness"])
        self.assertIn("projects/os-control-panel/src/app.py", approvals[0].payload["git_included_paths"])
        self.assertIn("projects/os-control-panel/data/approvals.json", approvals[0].payload["git_excluded_paths"])

    def test_web_app_release_delivery_requires_browser_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Release gate\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nShip it.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )

            with patch("workspace._requirements_path", return_value=requirements_path), patch(
                "workspace.APPROVAL_FILE", approvals_path
            ), patch("workspace.load_project_ui_runtime", return_value="web_app"), patch(
                "workspace._web_app_browser_verification_passed", return_value=False
            ):
                with self.assertRaisesRegex(ValueError, "Playwright browser verification"):
                    update_requirement(
                        "os-control-panel",
                        RequirementRecord("R1", "Release gate", "DONE", "HIGH", "M", "Ship it."),
                    )
                approvals = list_approvals("os-control-panel")

        self.assertEqual(approvals, [])

    def test_advance_active_sprint_blocks_instead_of_crashing_when_web_verification_is_missing(self) -> None:
        plan = workspace.SprintPlan(
            project_name="web-project",
            status="ACTIVE",
            requirement_ids=("R1",),
            created_at="now",
            started_at="now",
            completed_at="",
            current_requirement_id="",
            blocked_reason="",
        )
        record = RequirementRecord("R1", "Web release gate", "IN_PROGRESS", "HIGH", "M", "Ship it.")
        completed_run = workspace.ImplementationRun(
            run_id="run-1",
            project_name="web-project",
            requirement_id="R1",
            requirement_title="Web release gate",
            status="COMPLETED",
            summary="Done",
            error="",
            created_at="now",
            started_at="now",
            finished_at="now",
            output_path="",
            log_path="",
            worker_pid=None,
        )
        with patch("workspace.load_sprint_plan", return_value=plan), patch(
            "workspace._requirement_by_id", return_value={"R1": record}
        ), patch("workspace.active_implementation_run", return_value=None), patch(
            "workspace.latest_requirement_implementation", return_value=completed_run
        ), patch(
            "workspace.request_release_delivery_approval",
            side_effect=ValueError("Web app release delivery requires passing Playwright browser verification."),
        ):
            updated = advance_active_sprint("web-project")

        self.assertIsNotNone(updated)
        assert updated is not None
        self.assertEqual(updated.status, "BLOCKED")
        self.assertIn("Playwright browser verification", updated.blocked_reason)

    def test_streamlit_release_delivery_defaults_to_railway(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Streamlit release\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nShip it.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )
            change_plan = workspace.GitChangePlan(
                included_paths=("projects/os-control-panel/product/requirements.md",),
                excluded_paths=(),
                branch="feature/release",
            )

            with patch("workspace._requirements_path", return_value=requirements_path), patch(
                "workspace.APPROVAL_FILE", approvals_path
            ), patch("workspace._release_git_change_plan", return_value=change_plan), patch(
                "workspace.load_project_ui_runtime", return_value="streamlit"
            ):
                update_requirement(
                    "os-control-panel",
                    RequirementRecord("R1", "Streamlit release", "DONE", "HIGH", "M", "Ship it."),
                )
                approvals = list_approvals("os-control-panel")

        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0].payload["project_type"], "streamlit")
        self.assertEqual(approvals[0].payload["deployment_provider"], "railway")
        self.assertIn("Railway-compatible", approvals[0].payload["release_expectation"])
        self.assertIn("Railway", approvals[0].payload["release_readiness"])

    def test_approving_release_delivery_marks_done_publishes_and_records_git_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Release gate\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nShip it.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )
            change_plan = workspace.GitChangePlan(
                included_paths=("projects/os-control-panel/product/requirements.md",),
                excluded_paths=(),
                branch="feature/release",
            )
            publish_result = SimpleNamespace(
                kind="issue",
                url="https://github.com/owner/repo/issues/14",
                reference_id="14",
                detail="Created GitHub issue from approved release.",
            )
            git_result = {
                "git_commit_sha": "abc123",
                "git_push_target": "origin/feature/release",
                "git_delivery_detail": "Committed and pushed approved files to origin/feature/release.",
            }

            with patch("workspace._requirements_path", return_value=requirements_path), patch(
                "workspace.APPROVAL_FILE", approvals_path
            ), patch("workspace._release_git_change_plan", return_value=change_plan), patch(
                "workspace.publish_github_publication", return_value=publish_result
            ), patch(
                "workspace._commit_and_push_release", return_value=git_result
            ):
                update_requirement(
                    "os-control-panel",
                    RequirementRecord("R1", "Release gate", "DONE", "HIGH", "M", "Ship it."),
                )
                approval = list_approvals("os-control-panel")[0]
                approved = approve_request("os-control-panel", approval.approval_id)
                updated = load_requirement_document("os-control-panel")

        self.assertEqual(updated.active_requirements[0].status, "DONE")
        self.assertEqual(approved.payload["outcome_kind"], "release_delivery_published")
        self.assertEqual(approved.payload["github_published_url"], "https://github.com/owner/repo/issues/14")
        self.assertEqual(approved.payload["git_commit_sha"], "abc123")

    def test_approving_web_app_release_records_vercel_preview_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            requirements_path.write_text(
                "# Intro\n\n# Product Requirements\n\n## Active Requirements\n\n"
                "### R1 — Release gate\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\nDescription:\nShip it.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )
            change_plan = workspace.GitChangePlan(
                included_paths=("projects/os-control-panel/product/requirements.md",),
                excluded_paths=(),
                branch="feature/release",
            )
            publish_result = SimpleNamespace(
                kind="issue",
                url="https://github.com/owner/repo/issues/14",
                reference_id="14",
                detail="Created GitHub issue from approved release.",
            )
            git_result = {
                "git_commit_sha": "abc123",
                "git_push_target": "origin/feature/release",
                "git_delivery_detail": "Committed and pushed approved files to origin/feature/release.",
            }
            vercel_lookup = workspace.VercelDeploymentLookup(
                status="found",
                url="https://web-product-git-feature-release.vercel.app",
                deployment_id="dpl_123",
                ready_state="READY",
                inspector_url="https://vercel.com/team/project/dpl_123",
                detail="Matched Vercel deployment.",
            )

            with patch("workspace._requirements_path", return_value=requirements_path), patch(
                "workspace.APPROVAL_FILE", approvals_path
            ), patch("workspace._release_git_change_plan", return_value=change_plan), patch(
                "workspace.load_project_ui_runtime", return_value="web_app"
            ), patch(
                "workspace._web_app_browser_verification_passed", return_value=True
            ), patch(
                "workspace.publish_github_publication", return_value=publish_result
            ), patch(
                "workspace._commit_and_push_release", return_value=git_result
            ), patch(
                "workspace.lookup_vercel_preview_deployment", return_value=vercel_lookup
            ):
                update_requirement(
                    "os-control-panel",
                    RequirementRecord("R1", "Release gate", "DONE", "HIGH", "M", "Ship it."),
                )
                approval = list_approvals("os-control-panel")[0]
                approved = approve_request("os-control-panel", approval.approval_id)

        self.assertEqual(approved.payload["vercel_lookup_status"], "found")
        self.assertEqual(approved.payload["vercel_preview_url"], "https://web-product-git-feature-release.vercel.app")
        self.assertEqual(approved.payload["vercel_ready_state"], "READY")

    def test_vercel_preview_lookup_reports_not_configured_without_token(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            result = workspace.lookup_vercel_preview_deployment(
                "web-product",
                commit_sha="abc123",
                branch="feature/release",
            )

        self.assertEqual(result.status, "not_configured")
        self.assertIn("VERCEL_TOKEN", result.detail)

    def test_vercel_preview_lookup_queries_deployments_by_commit_and_branch(self) -> None:
        response = {
            "deployments": [
                {
                    "uid": "dpl_123",
                    "url": "web-product-git-feature-release.vercel.app",
                    "readyState": "READY",
                    "inspectorUrl": "https://vercel.com/team/project/dpl_123",
                }
            ]
        }
        with patch.dict(
            "os.environ",
            {
                "AI_BUILDER_OS_VERCEL_TOKEN": "token",
                "AI_BUILDER_OS_VERCEL_TEAM_ID": "team_123",
                "AI_BUILDER_OS_VERCEL_PROJECT_WEB_PRODUCT": "prj_123",
            },
            clear=True,
        ), patch("workspace._vercel_api_get", return_value=response) as api_get:
            result = workspace.lookup_vercel_preview_deployment(
                "web-product",
                commit_sha="abc123",
                branch="feature/release",
            )

        self.assertEqual(result.status, "found")
        self.assertEqual(result.url, "https://web-product-git-feature-release.vercel.app")
        self.assertEqual(api_get.call_args.kwargs["params"]["projectId"], "prj_123")
        self.assertEqual(api_get.call_args.kwargs["params"]["sha"], "abc123")
        self.assertEqual(api_get.call_args.kwargs["params"]["branch"], "feature/release")
        self.assertEqual(api_get.call_args.kwargs["params"]["teamId"], "team_123")

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

    def test_save_private_reflection_draft_writes_private_reflections_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                saved_path = save_private_reflection_draft(
                    "AI makes it easy to mistake velocity for understanding.",
                    scope="career",
                    source="workday",
                    what_happened="I noticed myself feeling closer to the concept than I really was.",
                    why_it_stood_out="The gap between building and understanding felt uncomfortably real.",
                    current_conclusion="The OS needs a learning layer as well as a reflection layer.",
                    confidence="high",
                    possible_route="promote-to-reflection",
                )

            self.assertEqual(saved_path, temp_root / "private" / "thinking" / "reflections.md")
            contents = saved_path.read_text()
            self.assertIn("# Reflections", contents)
            self.assertIn("Type: reflection-draft", contents)
            self.assertIn("Scope: career", contents)
            self.assertIn("Source: workday", contents)
            self.assertIn("Signal:\n- AI makes it easy to mistake velocity for understanding.", contents)
            self.assertIn("What happened:\n- I noticed myself feeling closer to the concept than I really was.", contents)
            self.assertIn("Current conclusion:\n- The OS needs a learning layer as well as a reflection layer.", contents)

    def test_save_private_reflection_draft_supports_dynamic_capture_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                saved_path = save_private_reflection_draft(
                    "Posting created more doubt than expected.",
                    scope="public-narrative",
                    source="public-share",
                    what_happened="I hesitated right before publishing the post.",
                    why_it_stood_out="The emotional wobble mattered more than I expected.",
                    current_conclusion="The reflection layer should capture emotional signals too.",
                    confidence="medium",
                    possible_route="public-seed",
                    captured_via="dynamic reflection helper",
                )

            contents = saved_path.read_text()
            self.assertIn("Captured via: dynamic reflection helper", contents)

    def test_build_dynamic_reflection_plan_adapts_to_signal_type(self) -> None:
        conclusion_plan = build_dynamic_reflection_plan("AI increases capability faster than understanding.")
        tension_plan = build_dynamic_reflection_plan("I had cold feet before posting the LinkedIn update.")

        conclusion_questions = conclusion_plan["questions"]
        tension_questions = tension_plan["questions"]

        self.assertEqual(conclusion_plan["defaults"], {"current_conclusion": "AI increases capability faster than understanding."})
        self.assertEqual(len(conclusion_questions), 2)
        self.assertEqual(conclusion_questions[0]["field"], "what_happened")
        self.assertIn("What concrete moment", conclusion_questions[0]["prompt"])

        self.assertEqual(len(tension_questions), 3)
        self.assertEqual(tension_questions[0]["field"], "what_happened")
        self.assertIn("What specifically triggered that reaction or tension", tension_questions[0]["prompt"])
        self.assertEqual(tension_questions[2]["field"], "current_conclusion")

    def test_save_private_concept_note_draft_writes_private_learning_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                saved_path = save_private_concept_note_draft(
                    "RAG",
                    where_encountered="General AI systems discussion and agent design notes.",
                    current_understanding="A way of grounding responses in retrieved context.",
                    what_is_unclear="When it is actually necessary versus jargon.",
                    what_it_is="Retrieval-Augmented Generation uses retrieved context to ground a model response.",
                    why_it_exists="To bring external knowledge into the model context when the base prompt is not enough.",
                    nearby_distinction="It is not the same as long-term memory.",
                    where_it_appears="Potentially in AI Builder OS once context and memory become retrieval problems.",
                    product_implication="It changes how trust, freshness, and complexity are balanced.",
                    current_working_opinion="Important, but easy to cargo cult.",
                    open_questions="When is RAG overkill for a local-first system?",
                )

            self.assertEqual(saved_path, temp_root / "private" / "learning" / "concept-notes.md")
            contents = saved_path.read_text()
            self.assertIn("# Concept Notes", contents)
            self.assertIn("### Concept: RAG", contents)
            self.assertIn("Captured on", contents)
            self.assertIn("#### What it is", contents)
            self.assertIn("#### Nearby distinction", contents)
            self.assertIn("#### Product implication", contents)
            self.assertIn("Important, but easy to cargo cult.", contents)

    def test_build_concept_teaching_brief_known_concept(self) -> None:
        brief = build_concept_teaching_brief(
            "RAG",
            current_understanding="I think it helps models use external context.",
            what_is_unclear="I do not know when it is truly needed.",
            where_encountered="Agent architecture discussions.",
        )

        self.assertIn("Retrieval-Augmented Generation", brief["what_it_is"])
        self.assertIn("not the same as long-term memory", brief["nearby_distinction"])
        self.assertIn("AI Builder OS", brief["os_connection"])

    def test_build_concept_teaching_brief_fallback_concept(self) -> None:
        brief = build_concept_teaching_brief(
            "Context router",
            current_understanding="Maybe a way to choose what context to send.",
            what_is_unclear="I do not know whether it is a real pattern or just loose language.",
            where_encountered="A workflow design conversation.",
        )

        self.assertIn("Context router", brief["what_it_is"])
        self.assertIn("A workflow design conversation.", brief["nearby_distinction"])
        self.assertIn("product leader", brief["product_implication"])

    def test_learning_progress_items_group_learned_in_progress_and_upcoming(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            learning_dir = temp_root / "private" / "learning"
            learning_dir.mkdir(parents=True, exist_ok=True)
            (learning_dir / "concept-notes.md").write_text(
                """# Concept Notes

### Concept: Evals

#### My current understanding
I understand evals as a repeatable quality layer.

#### Open questions
No open questions captured yet.

### Concept: RAG

#### My current understanding
Very early. I know the term, but not enough to explain it credibly.

#### Open questions
When is it useful?
"""
            )
            (learning_dir / "build-to-learn.md").write_text(
                """# Build To Learn

## 2026-05-29 — Trace grading

### Learning goal
Learn how to judge an agent workflow by its path.

### Success signal
I can spot weak orchestration.
"""
            )
            with patch("workspace.REPO_ROOT", temp_root):
                progress = learning_progress_items()

        self.assertTrue(any(item.concept == "Evals" for item in progress["learned"]))
        self.assertTrue(any(item.concept == "RAG" for item in progress["in_progress"]))
        self.assertTrue(any(item.concept == "Trace Grading" for item in progress["in_progress"]))
        self.assertTrue(any(item.concept == "MCP" for item in progress["upcoming"]))

    def test_learning_concept_recommendations_prioritize_unresolved_notes_and_known_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            learning_dir = temp_root / "private" / "learning"
            learning_dir.mkdir(parents=True, exist_ok=True)
            (learning_dir / "concept-notes.md").write_text(
                """# Concept Notes

### Concept: RAG

#### My current understanding
Very early. I know the term, but not enough to explain it credibly.

#### Open questions
When is it useful?

### Concept: Evals

#### My current understanding
I understand evals as a repeatable quality layer.

#### Open questions
What is enough coverage?
"""
            )
            with patch("workspace.REPO_ROOT", temp_root):
                recommendations = list_learning_concept_recommendations(limit=4)

        concepts = [item.concept for item in recommendations]
        self.assertIn("RAG", concepts)
        self.assertIn("Trace grading", concepts)
        self.assertIn("MCP", concepts)
        self.assertNotIn("Evals", concepts)
        rag = next(item for item in recommendations if item.concept == "RAG")
        self.assertIn("Open questions remain", rag.current_gap)

    def test_learning_recommendations_compound_from_recent_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_concept_management_update(
                    "Evals",
                    status="learned",
                    current_understanding="I can explain evals in simple language and why they matter.",
                    open_questions="",
                    note="Reached durable understanding of eval basics.",
                )
                recommendations = list_learning_concept_recommendations(limit=4)

        workflow = next(item for item in recommendations if item.concept == "Workflow Evals")
        self.assertIn("natural next concept after Evals", workflow.why_now)
        self.assertIn("connect Evals to Workflow Evals", workflow.suggested_path)

    def test_learning_recommendations_can_resurface_a_learned_related_concept(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_concept_management_update(
                    "Memory systems",
                    status="learned",
                    current_understanding="I can explain what should persist versus what should stay ephemeral.",
                    open_questions="",
                    note="Marked learned after a strong explanation-back.",
                )
                save_learning_concept_management_update(
                    "RAG",
                    status="reopened",
                    current_understanding="I understand retrieval at a surface level but the boundary with memory is blurry again.",
                    open_questions="I need to separate retrieval from persistence more crisply.",
                    note="Reopened because the distinction with memory is fuzzy again.",
                )
                recommendations = list_learning_concept_recommendations(limit=6)

        memory = next(item for item in recommendations if item.concept == "Memory systems")
        self.assertIn("distinction relevant again", memory.why_now)
        self.assertIn("worth reopening", memory.current_gap)


    def test_build_build_to_learn_pathway_known_concept(self) -> None:
        pathway = build_build_to_learn_pathway(
            "RAG",
            where_it_connects="Learning layer",
            current_gap="Still early",
        )

        self.assertEqual(pathway.concept, "RAG")
        self.assertIn("retrieval", pathway.learning_goal.lower())
        self.assertTrue(any(word in pathway.capture_prompt.lower() for word in ("capture", "building", "retrieval")))

    def test_save_private_build_to_learn_pathway_writes_private_learning_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                path = save_private_build_to_learn_pathway(
                    "RAG",
                    learning_goal="Learn when retrieval is actually needed.",
                    experiment_slice="Build a tiny retrieval-backed helper.",
                    project_anchor="Learning layer",
                    success_signal="I can explain when retrieval helped.",
                    capture_prompt="Capture what retrieval changed in practice.",
                )

            self.assertTrue(path.exists())
            contents = path.read_text()
            self.assertIn("# Build To Learn", contents)
            self.assertIn("## ", contents)
            self.assertIn("### Learning goal", contents)
            self.assertIn("Build a tiny retrieval-backed helper.", contents)

    def test_learning_profile_defaults_and_save_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                default_profile = load_learning_profile()
                saved_path = save_learning_profile(
                    product_background="PM moving into AI product systems.",
                    technical_comfort="System-level comfortable, implementation depth still growing.",
                    os_understanding_level="Know the basics of AI Builder OS",
                    current_trajectory="Agent orchestration and eval fluency.",
                    credibility_goal="Explain core AI product-system concepts simply.",
                    preferred_learning_style="Examples and build-to-learn.",
                    current_learning_posture="Actively turning vague familiarity into durable understanding.",
                )
                saved_profile = load_learning_profile()

        self.assertIn("product_background", default_profile)
        self.assertEqual(saved_path, temp_root / "private" / "learning" / "learning-profile.json")
        self.assertEqual(saved_profile["os_understanding_level"], "Know the basics of AI Builder OS")
        self.assertEqual(saved_profile["current_trajectory"], "Agent orchestration and eval fluency.")
        self.assertIn("durable understanding", saved_profile["current_learning_posture"])

    def test_learning_recommendations_use_profile_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_profile(
                    product_background="Product leader evolving into AI systems thinking.",
                    technical_comfort="Comfortable with systems, still deepening AI architecture fluency.",
                    os_understanding_level="New to AI Builder OS",
                    current_trajectory="Agent orchestration, memory, and retrieval.",
                    credibility_goal="Explain AI product concepts in plain language with credibility.",
                    preferred_learning_style="Learn in context through examples and build-to-learn.",
                    current_learning_posture="Actively building and learning through the OS.",
                )
                recommendations = list_learning_concept_recommendations(limit=3)

        rag = next(item for item in recommendations if item.concept == "RAG")
        self.assertIn("Why this matters", "Why this matters for you")
        self.assertIn("credibly", rag.why_for_you)
        self.assertIn("build-to-learn", rag.suggested_path)
        self.assertIn("credibility goal", rag.current_gap)

    def test_learning_concept_relationships_expose_useful_order_and_distinctions(self) -> None:
        trace_relationships = learning_concept_relationships("Trace grading")
        rag_relationships = learning_concept_relationships("RAG")

        self.assertTrue(any(item.relation == "prerequisite" and item.target == "Evals" for item in trace_relationships))
        self.assertTrue(any(item.relation == "next_after" and item.target == "Agent-output quality evals" for item in trace_relationships))
        self.assertTrue(any(item.relation == "often_confused_with" and item.target == "Memory systems" for item in rag_relationships))

    def test_save_learning_concept_management_update_tracks_status_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                path = save_learning_concept_management_update(
                    "RAG",
                    status="learned",
                    current_understanding="I can explain when retrieval helps and when it is overkill.",
                    open_questions="",
                    note="Reached plain-language understanding.",
                )
                record = learning_concept_record("RAG")
                history = learning_concept_history("RAG")
                progress = learning_progress_items()

        self.assertEqual(path, temp_root / "private" / "learning" / "concept-state.json")
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.status, "learned")
        self.assertIn("plain-language understanding", history[-1]["note"])
        self.assertTrue(any(item.concept == "RAG" for item in progress["learned"]))

    def test_save_private_concept_note_draft_reopens_learned_concept_when_doubts_return(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_concept_management_update(
                    "RAG",
                    status="learned",
                    current_understanding="I can explain it simply.",
                    open_questions="",
                    note="Marked learned.",
                )
                save_private_concept_note_draft(
                    "RAG",
                    where_encountered="Learning layer exploration.",
                    current_understanding="I know the core idea but now doubt when it is really needed.",
                    what_is_unclear="When retrieval is actually necessary.",
                    what_it_is="Retrieval-Augmented Generation uses retrieved context to ground a model response.",
                    why_it_exists="To bring external knowledge into the active context when the prompt alone is not enough.",
                    nearby_distinction="It is not the same as long-term memory.",
                    where_it_appears="Potential learning-layer and memory experiments.",
                    product_implication="It changes trust, freshness, and complexity tradeoffs.",
                    current_working_opinion="Useful, but easy to over-apply.",
                    open_questions="When is RAG overkill for a local-first workflow?",
                )
                record = learning_concept_record("RAG")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.status, "reopened")
        self.assertIn("overkill", record.open_questions)

    def test_save_private_build_to_learn_pathway_reopens_learned_concept(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_concept_management_update(
                    "Trace grading",
                    status="learned",
                    current_understanding="I can explain it in simple terms.",
                    open_questions="",
                    note="Marked learned.",
                )
                save_private_build_to_learn_pathway(
                    "Trace grading",
                    learning_goal="Stress test whether I really understand trace grading in practice.",
                    experiment_slice="Grade one orchestration path.",
                    project_anchor="os-control-panel",
                    success_signal="I catch weak reasoning in the path.",
                    capture_prompt="Capture whether the path revealed quality issues.",
                )
                record = learning_concept_record("Trace grading")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.status, "reopened")

    def test_save_private_build_to_learn_pathway_links_pathway_into_concept_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_private_build_to_learn_pathway(
                    "RAG",
                    learning_goal="Learn when retrieval is actually needed.",
                    experiment_slice="Build one narrow retrieval-backed helper.",
                    project_anchor="learning layer",
                    success_signal="I can explain when retrieval improved grounding.",
                    capture_prompt="Capture what retrieval changed.",
                )
                record = learning_concept_record("RAG")
                linked = learning_concept_build_to_learn("RAG")

        self.assertIsNotNone(record)
        self.assertIsNotNone(linked)
        assert record is not None
        assert linked is not None
        self.assertEqual(linked.status, "planned")
        self.assertEqual(record.build_to_learn, linked)
        self.assertIn("retrieval", record.recommended_next_move.lower())

    def test_learning_concept_view_keeps_recommendation_and_concept_state_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                view = learning_concept_view("Agent-output quality evals")

        self.assertIsNotNone(view)
        assert view is not None
        self.assertIsNotNone(view.recommendation)
        self.assertIsNone(view.concept_state)
        self.assertIsNone(view.session_state)
        self.assertIsNone(view.build_state)
        self.assertIn("start a learning session", view.recommended_next_move.lower())

    def test_learning_concept_detail_view_uses_recommendation_context_for_upcoming_concept(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                detail = learning_concept_detail_view("Agent-output quality evals")

        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail.state_label, "Upcoming")
        self.assertEqual(detail.primary_heading, "Why learn this now")
        self.assertEqual(detail.secondary_heading, "Current gap")
        self.assertEqual(detail.tertiary_heading, "Suggested first move")

    def test_learning_concept_hierarchy_formats_eval_categories(self) -> None:
        hierarchy = learning_concept_hierarchy("Evals")

        self.assertTrue(hierarchy.startswith("Evals"))
        self.assertIn("├── Agent-output quality evals", hierarchy)
        self.assertIn("├── Workflow Evals", hierarchy)
        self.assertIn("├── Reliability Evals", hierarchy)
        self.assertIn("└── Replays", hierarchy)

    def test_learning_concept_family_returns_eval_family(self) -> None:
        family = learning_concept_family("Trace grading")

        self.assertIsNotNone(family)
        assert family is not None
        self.assertEqual(family.name, "Evals and reliability")
        self.assertEqual(family.gateway_concepts, ("Evals",))
        self.assertIn("Replays", family.concepts)

    def test_learning_concept_family_placement_marks_gateway_and_specialized_concepts(self) -> None:
        evals_placement = learning_concept_family_placement("Evals")
        rag_placement = learning_concept_family_placement("RAG")

        self.assertIsNotNone(evals_placement)
        self.assertIsNotNone(rag_placement)
        assert evals_placement is not None
        assert rag_placement is not None
        self.assertEqual(evals_placement.concept_role, "gateway")
        self.assertEqual(rag_placement.family_name, "Context and knowledge systems")
        self.assertEqual(rag_placement.concept_role, "specialized")
        self.assertIn("Memory systems", rag_placement.gateway_concepts)

    def test_learning_concept_hierarchy_shows_parent_tree_for_child_concept(self) -> None:
        hierarchy = learning_concept_hierarchy("Agent-output quality evals")

        self.assertTrue(hierarchy.startswith("Evals"))
        self.assertIn("Agent-output quality evals (current)", hierarchy)

    def test_learning_concept_hierarchy_shows_eval_tree_for_replays(self) -> None:
        hierarchy = learning_concept_hierarchy("Replays")

        self.assertTrue(hierarchy.startswith("Evals"))
        self.assertIn("Replays (current)", hierarchy)

    def test_learning_concept_hierarchy_shows_workflow_eval_tree_for_trace_grading(self) -> None:
        hierarchy = learning_concept_hierarchy("Trace grading")

        self.assertTrue(hierarchy.startswith("Evals"))
        self.assertIn("Workflow Evals", hierarchy)
        self.assertIn("Trace grading (current)", hierarchy)

    def test_learning_implementation_anchors_exist_for_new_eval_family_concepts(self) -> None:
        workflow = learning_implementation_anchors("Workflow Evals")
        tool_selection = learning_implementation_anchors("Tool Selection Evals")
        reliability = learning_implementation_anchors("Reliability Evals")

        self.assertTrue(workflow)
        self.assertTrue(tool_selection)
        self.assertTrue(reliability)
        self.assertTrue(any("scenario" in anchor.label.lower() or "workflow" in anchor.label.lower() for anchor in workflow))
        self.assertTrue(any("tool" in anchor.label.lower() or "coverage" in anchor.label.lower() for anchor in tool_selection))
        self.assertTrue(any("reliability" in anchor.label.lower() or "trace" in anchor.label.lower() for anchor in reliability))

    def test_learning_concept_hierarchy_shows_context_family_for_rag(self) -> None:
        hierarchy = learning_concept_hierarchy("RAG")

        self.assertTrue(hierarchy.startswith("Memory systems"))
        self.assertIn("Retrieval", hierarchy)
        self.assertIn("RAG (current)", hierarchy)
        self.assertNotIn("MCP", hierarchy)

    def test_learning_concept_governing_truth_loads_approved_artifact(self) -> None:
        truth = learning_concept_governing_truth("Evals")

        self.assertIn("### Evals", truth)
        self.assertIn("deterministic eval framework for multi-dimensional agent evaluation", truth)

    def test_learning_concept_navigation_sections_follow_family_hierarchy(self) -> None:
        sections = learning_concept_navigation_sections()

        agent_workflow = next(
            section for section in sections if section.family_name == "Agent workflow systems"
        )
        evals = next(section for section in sections if section.family_name == "Evals and reliability")
        context = next(
            section
            for section in sections
            if section.family_name == "Context and knowledge systems"
        )
        tool_access = next(
            section
            for section in sections
            if section.family_name == "Tool and capability access"
        )

        self.assertEqual(agent_workflow.entries[0].concept, "Agents")
        self.assertEqual(agent_workflow.entries[1].concept, "Workflows")
        self.assertTrue(any(item.concept == "Orchestration" and item.depth == 1 for item in agent_workflow.entries))
        self.assertTrue(any(item.concept == "Human Hand-Back" and item.depth == 1 for item in agent_workflow.entries))
        self.assertEqual(evals.entries[0].concept, "Evals")
        self.assertEqual(evals.entries[0].depth, 0)
        self.assertTrue(any(item.concept == "Workflow Evals" and item.depth == 1 for item in evals.entries))
        self.assertTrue(any(item.concept == "Trace grading" and item.depth == 2 for item in evals.entries))
        self.assertEqual(context.entries[0].concept, "Memory Systems")
        self.assertTrue(any(item.concept == "Retrieval" and item.depth == 1 for item in context.entries))
        self.assertTrue(any(item.concept == "RAG" and item.depth == 2 for item in context.entries))
        self.assertTrue(any(item.concept == "File Search" and item.depth == 2 for item in context.entries))
        self.assertEqual(tool_access.entries[0].concept, "Tool Use")
        self.assertTrue(any(item.concept == "Connectors" and item.depth == 1 for item in tool_access.entries))

    def test_personalized_learning_plan_prefers_parent_step_for_recommended_child(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_profile(
                    product_background="Product leader learning AI systems.",
                    technical_comfort="Comfortable with systems.",
                    os_understanding_level="New to AI Builder OS",
                    current_trajectory="evals and workflow reliability",
                    credibility_goal="Explain eval concepts simply.",
                    preferred_learning_style="Learn in context.",
                    current_learning_posture="Building durable fluency.",
                )
                plan = personalized_learning_plan()

        assert plan is not None
        self.assertEqual(plan.current_concept, "Evals")

    def test_learning_implementation_anchors_exist_for_new_workflow_and_context_concepts(self) -> None:
        orchestration = learning_implementation_anchors("Orchestration")
        handoffs = learning_implementation_anchors("Handoffs")
        retrieval = learning_implementation_anchors("Retrieval")
        file_search = learning_implementation_anchors("File search")

        self.assertTrue(orchestration)
        self.assertTrue(handoffs)
        self.assertTrue(retrieval)
        self.assertTrue(file_search)
        self.assertTrue(any("orchestr" in anchor.label.lower() or "workflow" in anchor.label.lower() for anchor in orchestration))
        self.assertTrue(any("handoff" in anchor.label.lower() or "review" in anchor.label.lower() for anchor in handoffs))
        self.assertTrue(any("read-only" in anchor.why_it_matters.lower() or "rag" in anchor.label.lower() for anchor in retrieval))
        self.assertTrue(any("read" in anchor.label.lower() or "file" in anchor.label.lower() for anchor in file_search))

    def test_learning_implementation_anchors_exist_for_new_capability_concepts(self) -> None:
        connectors = learning_implementation_anchors("Connectors")
        tool_selection = learning_implementation_anchors("Tool selection")

        self.assertTrue(connectors)
        self.assertTrue(tool_selection)
        self.assertTrue(any("gmail" in anchor.label.lower() or "calendar" in anchor.label.lower() for anchor in connectors))
        self.assertTrue(any("tool" in anchor.label.lower() or "capability" in anchor.why_it_matters.lower() for anchor in tool_selection))

    def test_learning_concept_view_exists_for_catalog_concept_without_saved_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                view = learning_concept_view("Memory systems")

        self.assertIsNotNone(view)
        assert view is not None
        self.assertEqual(view.concept, "Memory Systems")
        self.assertIsNone(view.concept_state)
        self.assertIsNotNone(view.recommendation)

    def test_save_build_to_learn_outcome_updates_concept_state_without_auto_learning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_private_build_to_learn_pathway(
                    "RAG",
                    learning_goal="Learn when retrieval is actually needed.",
                    experiment_slice="Build one narrow retrieval-backed helper.",
                    project_anchor="learning layer",
                    success_signal="I can explain when retrieval improved grounding.",
                    capture_prompt="Capture what retrieval changed.",
                )
                path = save_build_to_learn_outcome(
                    "RAG",
                    outcome_summary="Building made it clearer that retrieval matters when the prompt alone lacks current grounded context.",
                    unresolved_after_build="I still need to understand when retrieval is overkill.",
                    learning_effect="strengthened",
                    current_understanding="RAG brings retrieved context into the active generation step when prompt-only context is not enough.",
                )
                record = learning_concept_record("RAG")
                linked = learning_concept_build_to_learn("RAG")
                history = learning_concept_history("RAG")

        self.assertEqual(path, temp_root / "private" / "learning" / "concept-state.json")
        self.assertIsNotNone(record)
        self.assertIsNotNone(linked)
        assert record is not None
        assert linked is not None
        self.assertEqual(linked.status, "captured")
        self.assertEqual(linked.learning_effect, "strengthened")
        self.assertEqual(record.status, "in_progress")
        self.assertIn("retrieved context", record.current_understanding.lower())
        self.assertIn("overkill", record.open_questions.lower())
        self.assertIn("outcome captured", history[-1]["note"].lower())

    def test_save_build_to_learn_outcome_can_reopen_concept(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_private_build_to_learn_pathway(
                    "Trace grading",
                    learning_goal="Stress test trace grading through one workflow.",
                    experiment_slice="Grade one orchestration path.",
                    project_anchor="os-control-panel",
                    success_signal="I catch weak reasoning in the path.",
                    capture_prompt="Capture where the path felt weak.",
                )
                save_build_to_learn_outcome(
                    "Trace grading",
                    outcome_summary="The experiment showed I can see the path, but I still cannot clearly explain which signals matter most.",
                    unresolved_after_build="I need to distinguish useful trace evidence from noise.",
                    learning_effect="reopened",
                    current_understanding="Trace grading inspects the path of an agent workflow, but I still need sharper judgment about which path signals matter.",
                )
                record = learning_concept_record("Trace grading")
                linked = learning_concept_build_to_learn("Trace grading")

        self.assertIsNotNone(record)
        self.assertIsNotNone(linked)
        assert record is not None
        assert linked is not None
        self.assertEqual(record.status, "reopened")
        self.assertEqual(linked.status, "captured")
        self.assertEqual(linked.learning_effect, "reopened")
        self.assertIn("noise", record.open_questions.lower())

    def test_learning_agent_session_can_start_and_pause(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                session = start_learning_agent_session(
                    "RAG",
                    where_encountered="Learning recommendation.",
                    current_understanding="I think it helps models use external information.",
                    what_is_unclear="When retrieval is actually needed.",
                )
                paused_path = pause_learning_agent_session()
                loaded = load_learning_agent_session()

        self.assertEqual(session.concept, "RAG")
        self.assertEqual(paused_path, temp_root / "private" / "learning" / "learning-agent-session.json")
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.session_status, "paused")

    def test_learning_agent_session_compounds_to_next_concept_after_strong_understanding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                session = start_learning_agent_session(
                    "Evals",
                    where_encountered="Learning recommendation.",
                    current_understanding="I know evals help test AI behavior.",
                    what_is_unclear="What makes them different from just checking one answer?",
                )
                updated = continue_learning_agent_session(
                    "Evals are structured checks that show whether an AI system behaves acceptably across known cases. "
                    "They exist because one good-looking answer can still hide brittle behavior. "
                    "For example, in the OS they help separate a promising workflow demo from real evidence that the workflow behaves reliably. "
                    "They are broader than unit tests because they also judge model-shaped behavior and workflow usefulness."
        )

        self.assertEqual(updated.next_move, "save_understanding")
        self.assertIn("Workflow Evals", updated.coach_message)

    def test_learning_agent_session_auto_promotes_upcoming_concept_to_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                start_learning_agent_session(
                    "RAG",
                    where_encountered="Learning recommendation.",
                    current_understanding="I think it helps with outside information.",
                    what_is_unclear="When it is needed.",
                )
                record = learning_concept_record("RAG")

        assert record is not None
        self.assertEqual(record.status, "in_progress")

    def test_learning_agent_session_can_start_from_gap_without_fake_understanding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                start_learning_agent_session(
                    "Agent-output quality evals",
                    where_encountered="Learning recommendation.",
                    current_understanding="",
                    what_is_unclear="How are agent-output evals different from workflow tests?",
                )
                record = learning_concept_record("Agent-output quality evals")
                detail = learning_concept_detail_view("Agent-output quality evals")

        assert record is not None
        assert detail is not None
        self.assertEqual(record.status, "in_progress")
        self.assertEqual(record.current_understanding, "")
        self.assertEqual(record.open_questions, "How are agent-output evals different from workflow tests?")
        self.assertIn("Learning session started.", detail.primary_text)
        self.assertIn("work through the current concept with the agent", detail.primary_text)
        self.assertEqual(detail.secondary_heading, "Open questions")
        self.assertIn("agent-output evals different from workflow tests", detail.secondary_text)

    def test_learning_agent_session_reopens_learned_concept_when_doubts_return(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                save_learning_concept_management_update(
                    "RAG",
                    status="learned",
                    current_understanding="I already understand it.",
                    open_questions="",
                    note="Preloaded as learned.",
                )
                start_learning_agent_session(
                    "RAG",
                    where_encountered="Learning recommendation.",
                    current_understanding="I already understand it.",
                    what_is_unclear="I am not actually sure when it is necessary.",
                )
                record = learning_concept_record("RAG")

        assert record is not None
        self.assertEqual(record.status, "reopened")

    def test_learning_agent_session_uses_live_teaching_turn_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            live_turn = LiveLearningTeachingTurn(
                what_it_is="A live-generated simple explanation.",
                why_it_exists="Because the live tutoring agent should adapt to current confusion.",
                nearby_distinction="It is not the same as a static helper response.",
                os_connection="This concept shows up in the OS learning flow.",
                product_implication="It improves the quality of concept teaching.",
                coach_message="Explain it back in your own words now.",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", return_value=live_turn):
                    session = start_learning_agent_session(
                        "RAG",
                        where_encountered="Learning recommendation.",
                        current_understanding="I have a vague idea.",
                        what_is_unclear="When it is really needed.",
                    )

        self.assertEqual(session.what_it_is, "A live-generated simple explanation.")
        self.assertEqual(session.coach_message, "Explain it back in your own words now.")

    def test_live_learning_teaching_turn_sends_agent_contract(self) -> None:
        live_turn = LiveLearningTeachingTurn(
            what_it_is="A simple explanation.",
            why_it_exists="Because it solves a real problem.",
            nearby_distinction="It differs from a nearby concept in one important way.",
            os_connection="It shows up in the OS here.",
            product_implication="It matters for product quality.",
            coach_message="Explain it back simply now.",
        )

        with patch("workspace._run_bounded_structured_turn", return_value=live_turn) as run_turn:
            result = workspace._run_live_learning_teaching_turn(
                "RAG",
                where_encountered="Learning recommendation.",
                current_understanding="I have a vague sense of it.",
                what_is_unclear="When it is really needed.",
            )

        self.assertEqual(result.what_it_is, "A simple explanation.")
        call = run_turn.call_args.kwargs
        payload = json.loads(call["input_messages"][0]["content"])
        self.assertEqual(call["role"], "Learning Agent")
        self.assertIs(call["output_type"], LiveLearningTeachingTurn)
        self.assertEqual(payload["intent"], "teach_concept")
        self.assertIn("agent_contract", payload)
        self.assertIn("teaching_strategy", payload)
        self.assertIn("governing_truth", payload)
        self.assertIn("grounding_rules", payload["agent_contract"])
        self.assertIn("progression_rules", payload["agent_contract"])
        self.assertIn("entry_point", payload["teaching_strategy"])
        self.assertIn("explanation_order", payload["teaching_strategy"])
        self.assertIn("### RAG", payload["governing_truth"])

    def test_live_learning_clarification_turn_sends_exact_confusion_and_guardrails(self) -> None:
        live_turn = LiveLearningClarificationTurn(
            clarification_response="A clarification tied to the exact confusion.",
            coach_message="Explain it back again with that in mind.",
        )

        session = workspace.LearningAgentSession(
            concept="RAG",
            session_status="active",
            where_encountered="Learning recommendation.",
            current_understanding="It uses retrieved context somehow.",
            what_is_unclear="When retrieval is really necessary.",
            what_it_is="A rough explanation.",
            why_it_exists="A rough reason.",
            nearby_distinction="A rough distinction.",
            os_connection="A rough OS connection.",
            product_implication="A rough implication.",
            latest_explanation_back="I think it adds outside notes.",
            clarification_response="",
            implementation_walkthrough="",
            implementation_relationships="",
            detected_gaps=(),
            next_move="clarify",
            proposed_concept_status="in_progress",
            hand_back_reason="",
            coach_message="Clarify it.",
            turn_count=1,
            updated_at="2026-06-06",
        )

        with patch("workspace._run_bounded_structured_turn", return_value=live_turn) as run_turn:
            result = workspace._run_live_learning_clarification_turn(
                session,
                "specific_confusion",
                detail="when retrieval is actually necessary",
            )

        self.assertEqual(result.clarification_response, "A clarification tied to the exact confusion.")
        call = run_turn.call_args.kwargs
        payload = json.loads(call["input_messages"][0]["content"])
        self.assertIs(call["output_type"], LiveLearningClarificationTurn)
        self.assertEqual(payload["specific_confusion"], "when retrieval is actually necessary")
        self.assertEqual(payload["clarification_mode"], "specific_confusion")
        self.assertIn("agent_contract", payload)
        self.assertIn("teaching_strategy", payload)
        self.assertIn("learning_guardrails", payload["agent_contract"])
        self.assertIn("governing_truth", payload)
        self.assertIn("### RAG", payload["governing_truth"])

    def test_live_learning_nearby_comparison_sends_target_context_and_hierarchy_hint(self) -> None:
        live_turn = LiveLearningClarificationTurn(
            clarification_response="Here is the structural comparison.",
            coach_message="Explain the difference back in plain language now.",
        )

        session = workspace.LearningAgentSession(
            concept="Evals",
            session_status="active",
            where_encountered="Learning recommendation.",
            current_understanding="I know evals are about structured quality checks.",
            what_is_unclear="How agent-output quality evals fit underneath evals.",
            what_it_is="A rough explanation.",
            why_it_exists="A rough reason.",
            nearby_distinction="A rough distinction.",
            os_connection="A rough OS connection.",
            product_implication="A rough implication.",
            latest_explanation_back="",
            clarification_response="",
            implementation_walkthrough="",
            implementation_relationships="",
            detected_gaps=(),
            next_move="clarify",
            proposed_concept_status="in_progress",
            hand_back_reason="",
            coach_message="Clarify it.",
            turn_count=1,
            updated_at="2026-06-07",
        )

        with patch("workspace._run_bounded_structured_turn", return_value=live_turn) as run_turn:
            result = workspace._run_live_learning_clarification_turn(
                session,
                "nearby_comparison",
                detail="Compare Evals and Agent-output quality evals and tell me the hierarchical relationship.",
            )

        self.assertEqual(result.clarification_response, "Here is the structural comparison.")
        call = run_turn.call_args.kwargs
        payload = json.loads(call["input_messages"][0]["content"])
        self.assertEqual(payload["clarification_mode"], "nearby_comparison")
        self.assertEqual(payload["comparison_context"]["requested_target"], "Agent-output quality evals")
        self.assertTrue(payload["comparison_context"]["asks_for_hierarchy"])
        self.assertIn("broader foundation", payload["comparison_context"]["relationship_hint"])
        self.assertEqual(payload["comparison_context"]["target_context"]["concept"], "Agent-output quality evals")

    def test_learning_implementation_anchors_are_local_and_bounded(self) -> None:
        anchors = learning_implementation_anchors("Evals")

        self.assertGreaterEqual(len(anchors), 2)
        self.assertLessEqual(len(anchors), 3)
        self.assertEqual(anchors[0].concept, "Evals")
        self.assertTrue(all(anchor.path for anchor in anchors))
        self.assertTrue(any("eval_runner.py" in anchor.path for anchor in anchors))

    def test_live_learning_implementation_turn_sends_anchor_payload(self) -> None:
        live_turn = LiveLearningImplementationTurn(
            walkthrough_intro="These anchors show evals in action.",
            how_the_pieces_fit="The runner executes scenarios, while the scenarios define what good behavior looks like.",
            coach_message="Explain evals back using those anchors.",
        )

        session = workspace.LearningAgentSession(
            concept="Evals",
            session_status="active",
            where_encountered="Learning recommendation.",
            current_understanding="I know evals check quality somehow.",
            what_is_unclear="How they show up in the OS.",
            what_it_is="A rough explanation.",
            why_it_exists="A rough reason.",
            nearby_distinction="A rough distinction.",
            os_connection="A rough OS connection.",
            product_implication="A rough implication.",
            latest_explanation_back="",
            clarification_response="",
            implementation_walkthrough="",
            implementation_relationships="",
            detected_gaps=(),
            next_move="explain_back",
            proposed_concept_status="in_progress",
            hand_back_reason="",
            coach_message="Explain it.",
            turn_count=1,
            updated_at="2026-06-07",
        )

        with patch("workspace._run_bounded_structured_turn", return_value=live_turn) as run_turn:
            result = workspace._run_live_learning_implementation_turn(
                session,
                learning_implementation_anchors("Evals"),
            )

        self.assertEqual(result.walkthrough_intro, "These anchors show evals in action.")
        call = run_turn.call_args.kwargs
        payload = json.loads(call["input_messages"][0]["content"])
        self.assertEqual(payload["intent"], "explain_implementation")
        self.assertGreaterEqual(len(payload["implementation_anchors"]), 2)
        self.assertIn("agent_contract", payload)
        self.assertIn("teaching_strategy", payload)
        self.assertIn("implementation_rules", payload["agent_contract"])
        self.assertIn("governing_truth", payload)
        self.assertIn("### Evals", payload["governing_truth"])

    def test_learning_teaching_strategy_changes_with_profile(self) -> None:
        foundation_profile = {
            "product_background": "New to AI product systems",
            "technical_comfort": "Mostly product and workflow focused",
            "os_understanding_level": "New to AI Builder OS",
            "current_trajectory": "Learn the foundations of AI Builder OS",
            "credibility_goal": "Explain concepts simply to others",
            "preferred_learning_style": "Big-picture framing first",
            "current_learning_posture": "Exploring the space",
        }
        implementation_profile = {
            "product_background": "Technical builder sharpening product judgment",
            "technical_comfort": "Comfortable implementing and debugging systems",
            "os_understanding_level": "Comfortable operating AI Builder OS",
            "current_trajectory": "Use the OS fluently in real product work",
            "credibility_goal": "Make better product and architecture decisions",
            "preferred_learning_style": "Implementation walkthroughs",
            "current_learning_posture": "Applying in real work",
        }

        foundation_strategy = workspace.learning_teaching_strategy(foundation_profile)
        implementation_strategy = workspace.learning_teaching_strategy(implementation_profile)

        self.assertNotEqual(foundation_strategy.entry_point, implementation_strategy.entry_point)
        self.assertNotEqual(foundation_strategy.explanation_order, implementation_strategy.explanation_order)
        self.assertIn("Assume little AI Builder OS familiarity", foundation_strategy.os_context_depth)
        self.assertIn("OS-local surfaces", implementation_strategy.os_context_depth)
        self.assertIn("plain-language distinctions", " ".join(foundation_strategy.emphasis).lower())
        self.assertIn("practical use", implementation_strategy.coaching_style.lower())

    def test_learning_agent_session_can_request_implementation_walkthrough(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            live_turn = LiveLearningImplementationTurn(
                walkthrough_intro="These anchors show where evals live in the OS.",
                how_the_pieces_fit="The runner executes the scenarios, and the scenarios name the cases being checked.",
                coach_message="Explain evals back using the runner and the scenarios together.",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "Evals",
                        where_encountered="Learning recommendation.",
                        current_understanding="I know evals are some quality layer.",
                        what_is_unclear="How they appear in the OS.",
                    )
                with patch("workspace.learning_implementation_anchors", return_value=[
                    workspace.LearningImplementationAnchor(
                        concept="Evals",
                        label="OS control-panel eval runner",
                        path="projects/os-control-panel/tools/eval_runner.py",
                        kind="tool",
                        why_it_matters="This runner is the deterministic validation entrypoint.",
                        excerpt="def main():\n    pass",
                    )
                ]):
                    with patch("workspace._run_live_learning_implementation_turn", return_value=live_turn):
                        session = request_learning_agent_implementation_walkthrough()

        self.assertIn("where evals live", session.implementation_walkthrough.lower())
        self.assertIn("runner executes the scenarios", session.implementation_relationships.lower())
        self.assertEqual(session.next_move, "clarify")

    def test_learning_agent_session_can_hand_back_when_explanation_is_too_broad(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "Evals",
                        where_encountered="Learning recommendation.",
                        current_understanding="I know it is about checking AI quality.",
                        what_is_unclear="How to understand it properly.",
                    )
                session = continue_learning_agent_session(
                    "I am not sure. It is something about the whole system and workflow and architecture and orchestration."
                )

        self.assertEqual(session.next_move, "hand_back")
        self.assertIn("too broad", session.hand_back_reason.lower())
        self.assertIn("narrow", session.coach_message.lower())
        self.assertEqual(session.proposed_concept_status, "in_progress")


    def test_learning_agent_session_detects_weak_understanding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                start_learning_agent_session(
                    "MCP",
                    where_encountered="Tooling discussion.",
                    current_understanding="It is something about tools.",
                    what_is_unclear="What it standardizes.",
                )
                session = continue_learning_agent_session("MCP is a system for AI workflows and context.")

        self.assertEqual(session.next_move, "clarify")
        self.assertEqual(session.proposed_concept_status, "in_progress")
        self.assertGreater(len(session.detected_gaps), 0)
        self.assertIn("term itself", " ".join(session.detected_gaps).lower())

    def test_learning_agent_session_can_request_simpler_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "Trace grading",
                        where_encountered="Learning recommendation.",
                        current_understanding="It is something about the workflow path.",
                        what_is_unclear="How to explain it simply.",
                    )
                with patch("workspace._run_live_learning_clarification_turn", side_effect=LivePMDiscoveryError("offline")):
                    session = request_learning_agent_clarification("simpler")

        self.assertEqual(session.next_move, "clarify")
        self.assertIn("in plainer language", session.clarification_response.lower())
        self.assertIn("capture what is clearer now", session.coach_message.lower())

    def test_learning_agent_session_can_clarify_specific_confusion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "RAG",
                        where_encountered="Learning recommendation.",
                        current_understanding="It uses retrieved context somehow.",
                        what_is_unclear="When retrieval is really necessary.",
                    )
                with patch("workspace._run_live_learning_clarification_turn", side_effect=LivePMDiscoveryError("offline")):
                    session = request_learning_agent_clarification(
                        "specific_confusion",
                        detail="when retrieval is actually necessary",
                    )

        self.assertEqual(session.next_move, "clarify")
        self.assertIn("when retrieval is actually necessary", session.clarification_response.lower())
        self.assertIn("what usually clears this up", session.clarification_response.lower())

    def test_learning_agent_session_uses_live_clarification_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            live_turn = LiveLearningClarificationTurn(
                clarification_response="Here is a more adaptive clarification tied to your exact confusion.",
                coach_message="Try explaining it back again with that distinction in mind.",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "RAG",
                        where_encountered="Learning recommendation.",
                        current_understanding="It uses retrieved context somehow.",
                        what_is_unclear="When retrieval is really necessary.",
                    )
                with patch("workspace._run_live_learning_clarification_turn", return_value=live_turn):
                    session = request_learning_agent_clarification(
                        "specific_confusion",
                        detail="when retrieval is actually necessary",
                    )

        self.assertEqual(session.clarification_response, "Here is a more adaptive clarification tied to your exact confusion.")
        self.assertEqual(session.coach_message, "Try explaining it back again with that distinction in mind.")

    def test_learning_agent_session_can_route_to_build_to_learn(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                    start_learning_agent_session(
                        "RAG",
                        where_encountered="Learning recommendation.",
                        current_understanding="I think it is about using outside information.",
                        what_is_unclear="When retrieval is truly needed.",
                    )
                session = continue_learning_agent_session(
                    "RAG pulls relevant outside notes into the current answer so the model can ground its response when the prompt alone lacks the needed facts. "
                    "It matters because some questions need current or specific context that the prompt does not already carry. "
                    "For example, a learning helper might retrieve the right concept note before generating an explanation."
                )
                cleared_path = clear_learning_agent_session()
                loaded = load_learning_agent_session()

        self.assertEqual(session.next_move, "build_to_learn")
        self.assertIn("pressure-test", session.coach_message.lower())
        self.assertEqual(session.proposed_concept_status, "build_to_learn")
        self.assertEqual(cleared_path, temp_root / "private" / "learning" / "learning-agent-session.json")
        self.assertIsNone(loaded)

    def test_learning_agent_session_does_not_route_to_build_to_learn_in_external_release_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch.dict("os.environ", {"AI_BUILDER_OS_LEARNING_RELEASE_PROFILE": "external_v2"}):
                with patch("workspace.REPO_ROOT", temp_root):
                    with patch("workspace._run_live_learning_teaching_turn", side_effect=LivePMDiscoveryError("offline")):
                        start_learning_agent_session(
                            "RAG",
                            where_encountered="Learning recommendation.",
                            current_understanding="I think it is about using outside information.",
                            what_is_unclear="When retrieval is truly needed.",
                        )
                    session = continue_learning_agent_session(
                        "RAG pulls relevant outside notes into the current answer so the model can ground its response when the prompt alone lacks the needed facts. "
                        "It matters because some questions need current or specific context that the prompt does not already carry. "
                        "For example, a learning helper might retrieve the right concept note before generating an explanation."
                    )

        self.assertEqual(session.next_move, "save_understanding")
        self.assertNotEqual(session.proposed_concept_status, "build_to_learn")

    def test_learning_agent_session_accepts_strong_trace_grading_explanation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("workspace.REPO_ROOT", temp_root):
                start_learning_agent_session(
                    "Trace grading",
                    where_encountered="Learning recommendation.",
                    current_understanding="It checks something about the path.",
                    what_is_unclear="How it differs from checking only the final answer.",
                )
                session = continue_learning_agent_session(
                    "Trace grading checks whether an agent reached its answer through a good workflow, not just whether the final answer looked correct. "
                    "It exists because a system can produce the right output while still taking a weak or unreliable path. "
                    "For example, in an agent workflow that should route work through UX review before engineering, trace grading helps confirm the system followed that path instead of skipping it."
                )

        self.assertEqual(session.next_move, "build_to_learn")
        self.assertEqual(session.detected_gaps, ())
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
            submitted: dict[str, PMDecisionEnvelope] = {}

            def submit_proposal(_controller, _project_name, proposal, **_kwargs):
                decision = PMDecisionEnvelope.model_validate(proposal)
                decision = decision.model_copy(
                    update={
                        "proposal_id": "test-proposal",
                        "proposal_revision": 1,
                        "requirement_changes": [
                            decision.requirement_changes[0].model_copy(update={"requirement_id": "R999"})
                        ],
                    }
                )
                submitted["decision"] = decision
                return {
                    "proposal_id": "test-proposal",
                    "proposal_revision": 1,
                    "proposal": decision.model_dump(mode="json"),
                    "status": "PENDING_APPROVAL",
                }

            def approve_proposal(_controller, project_name, _proposal_id, _proposal_revision, **_kwargs):
                decision = submitted["decision"]
                change = decision.requirement_changes[0]
                record = save_pm_requirement_thread_to_requirements(
                    project_name,
                    next(
                        item.thread_id
                        for item in list_agent_threads(project_name, agent_name="PM", mode="Requirement Discovery")
                        if item.status == "pending_approval"
                    ),
                    change.title,
                    status=change.status,
                    priority=change.priority,
                    effort=change.effort,
                )
                decision = decision.model_copy(
                    update={
                        "requirement_changes": [
                            change.model_copy(update={"requirement_id": record.id})
                        ]
                    }
                )
                return {
                    "proposal_id": "test-proposal",
                    "proposal_revision": 1,
                    "proposal": decision.model_dump(mode="json"),
                    "status": "APPROVED",
                }

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
            ), patch(
                "control_plane.WorkflowController.submit_pm_proposal",
                new=submit_proposal,
            ), patch(
                "control_plane.WorkflowController.approve_pm_proposal",
                new=approve_proposal,
            ):
                thread = start_pm_requirement_discovery_thread(
                    "os-control-panel",
                    "I want a PM chat that drafts requirements inside the project.",
                )
                drafted = draft_pm_requirement_discovery_thread("os-control-panel", thread.thread_id)
                approval = request_pm_requirement_thread_approval(
                    "os-control-panel",
                    drafted.thread_id,
                    requirement_title="Add governed PM contract fixture",
                    status="NEW",
                    priority="HIGH",
                    effort="L",
                )
                self.assertEqual(len(active_approvals("os-control-panel")), 1)

                approved = approve_request("os-control-panel", approval.approval_id)
                updated = load_requirement_document("os-control-panel")

                self.assertEqual(approved.status, "APPROVED")
                self.assertEqual(len(active_approvals("os-control-panel")), 0)
                self.assertTrue(any(record.title == "Add governed PM contract fixture" for record in updated.active_requirements))

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

        updated_records = updated.active_requirements + updated.backlog_requirements
        self.assertTrue(
            any(
                record.title == "Reduce noise in requirement management surfaces"
                or "Additional approved review input" in record.description
                for record in updated_records
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
        after_records = after.active_requirements + after.backlog_requirements
        self.assertIn(len(after_backlog), {len(before_backlog), len(before_backlog) + 1})
        self.assertTrue(
            any(
                "Additional approved review input" in record.description
                or record.title == "Launch a broader workspace visual redesign initiative"
                for record in after_records
            )
        )
        self.assertTrue(
            any("broader visual simplification pass" in record.description for record in after_records)
        )

    def test_approved_review_does_not_merge_into_done_or_in_progress_requirement(self) -> None:
        statuses = ("DONE", "IN_PROGRESS")
        seeded_template = """# Product Requirements

## Active Requirements

### R1 — Workspace simplification direction

Status: {status}
Priority: LOW
Effort: L
Description:
Problem statement
- Existing requirement already closed or active.

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

- Keep this file parseable.
"""

        for status in statuses:
            with self.subTest(status=status):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_threads = Path(temp_dir) / "agent_threads.json"
                    temp_approvals = Path(temp_dir) / "approvals.json"
                    temp_requirements = Path(temp_dir) / "requirements.md"
                    temp_threads.write_text("[]")
                    temp_approvals.write_text("[]")
                    temp_requirements.write_text(seeded_template.format(status=status))

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
                            requirement_title="Workspace simplification direction",
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

                before_count = len(before.active_requirements) + len(before.backlog_requirements)
                after_count = len(after.active_requirements) + len(after.backlog_requirements)
                self.assertEqual(after_count, before_count + 1)
                original = next(record for record in after.active_requirements + after.backlog_requirements if record.id == "R1")
                self.assertNotIn("Additional approved review input", original.description)
                self.assertTrue(any(record.id != "R1" and record.title == "Workspace simplification direction" for record in after.active_requirements + after.backlog_requirements))

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
        self.assertEqual(
            app.requirement_card_metadata(record),
            "Status: DONE · Priority: HIGH · Effort: S · Project type: Project default",
        )

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

    def test_requirement_implementation_prompt_includes_web_app_capability_profile(self) -> None:
        with patch(
            "workspace.parse_requirements",
            return_value=[
                {
                    "id": "R93",
                    "title": "Build web onboarding",
                    "status": "IN_PROGRESS",
                    "priority": "HIGH",
                    "effort": "M",
                    "ui_runtime": "web_app",
                    "description": "Build a browser-native onboarding workflow.",
                }
            ],
        ):
            prompt = build_requirement_implementation_prompt("os-control-panel", "R93")

        self.assertIn("Project capability profile: Web app", prompt)
        self.assertIn("Vercel-compatible Next.js/React", prompt)
        self.assertIn("Local capability bundle: web-app-frontend", prompt)
        self.assertIn("shadcn/ui best practices", prompt)
        self.assertIn("Frontend testing and debugging", prompt)
        self.assertIn("agent/capabilities/web-app-frontend/", prompt)

    def test_requirement_implementation_prompt_includes_site_import_context_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            manifest_dir = temp_root / "projects" / "web-project" / "data" / "site-imports" / "example-com"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "requested_url": "https://example.com",
                        "site_host": "example.com",
                        "saved_count": 3,
                        "counts": {"logo": 1, "hero": 1, "gallery": 1},
                        "grouped_assets": {
                            "logo": [
                                {
                                    "source_url": "https://example.com/logo.png",
                                    "saved_path": str(manifest_dir / "01-logo.png"),
                                    "bytes": 12345,
                                    "content_type": "image/png",
                                }
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "workspace.parse_requirements",
                return_value=[
                    {
                        "id": "R93",
                        "title": "Build web onboarding",
                        "status": "IN_PROGRESS",
                        "priority": "HIGH",
                        "effort": "M",
                        "ui_runtime": "web_app",
                        "description": "Build a browser-native onboarding workflow.",
                    }
                ],
            ), patch("workspace.REPO_ROOT", temp_root):
                prompt = build_requirement_implementation_prompt("web-project", "R93")

        self.assertIn("Website import context is available", prompt)
        self.assertIn("Source website: https://example.com", prompt)
        self.assertIn("Downloaded assets: 3", prompt)
        self.assertIn("Representative local assets:", prompt)
        self.assertIn("01-logo.png", prompt)

    def test_requirement_implementation_prompt_includes_crawled_copy_context_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            import_dir = temp_root / "projects" / "web-project" / "data" / "site-imports" / "example-com"
            import_dir.mkdir(parents=True)
            (import_dir / "manifest.json").write_text(
                json.dumps({"requested_url": "https://example.com", "site_host": "example.com", "saved_count": 1}),
                encoding="utf-8",
            )
            (import_dir / "crawl.json").write_text(
                json.dumps(
                    {
                        "pages": [
                            {
                                "title": "Example Electrical Services",
                                "navigation_labels": ["HOME", "SERVICES", "ABOUT", "CONTACT"],
                                "content_blocks": [
                                    "Trusted local electrical contractor for homes and businesses.",
                                    "Testing, inspection, installations, and fault finding.",
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch(
                "workspace.parse_requirements",
                return_value=[
                    {
                        "id": "R93",
                        "title": "Replicate site",
                        "status": "IN_PROGRESS",
                        "priority": "HIGH",
                        "effort": "M",
                        "ui_runtime": "web_app",
                        "description": "Replicate and improve the referenced site.",
                    }
                ],
            ), patch("workspace.REPO_ROOT", temp_root):
                prompt = build_requirement_implementation_prompt("web-project", "R93")

        self.assertIn("Primary page title: Example Electrical Services", prompt)
        self.assertIn("Navigation labels: HOME, SERVICES, ABOUT, CONTACT", prompt)
        self.assertIn("Representative source copy:", prompt)
        self.assertIn("Trusted local electrical contractor", prompt)
        self.assertIn("Do not default to generic placeholder marketing copy", prompt)

    def test_latest_site_import_summary_returns_manifest_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            manifest_dir = temp_root / "projects" / "web-project" / "data" / "site-imports" / "example-com"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "requested_url": "https://example.com",
                        "site_host": "example.com",
                        "saved_count": 2,
                    }
                ),
                encoding="utf-8",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                summary = workspace.latest_site_import_summary("web-project")

        self.assertEqual(summary["requested_url"], "https://example.com")
        self.assertEqual(summary["site_host"], "example.com")
        self.assertEqual(summary["saved_count"], 2)
        self.assertTrue(str(summary["manifest_path"]).endswith("manifest.json"))

    def test_latest_site_import_summary_migrates_legacy_display_name_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            legacy_dir = temp_root / "projects" / "Web Project" / "data" / "site-imports" / "example-com"
            legacy_dir.mkdir(parents=True)
            (legacy_dir / "manifest.json").write_text(
                json.dumps({"requested_url": "https://example.com", "site_host": "example.com", "saved_count": 2}),
                encoding="utf-8",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                summary = workspace.latest_site_import_summary("web-project")

        self.assertEqual(summary["requested_url"], "https://example.com")
        self.assertIn("/projects/web-project/data/site-imports/example-com/manifest.json", summary["manifest_path"])

    def test_latest_site_import_summary_migrates_draft_project_runtime_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            draft_dir = temp_root / ".draft-projects" / "web-project" / "data" / "site-imports" / "example-com"
            draft_dir.mkdir(parents=True)
            (draft_dir / "01-logo.png").write_text("img", encoding="utf-8")
            (draft_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "requested_url": "https://example.com",
                        "site_host": "example.com",
                        "saved_count": 1,
                        "saved_images": [
                            {
                                "source_url": "https://example.com/logo.png",
                                "saved_path": str(draft_dir / "01-logo.png"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                summary = workspace.latest_site_import_summary("web-project")

        self.assertEqual(summary["requested_url"], "https://example.com")
        self.assertIn("/projects/web-project/data/site-imports/example-com/manifest.json", summary["manifest_path"])
        self.assertIn("/projects/web-project/data/site-imports/example-com/01-logo.png", json.dumps(summary))

    def test_site_import_context_summary_falls_back_to_saved_images_when_grouping_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            import_dir = project_root / "data" / "site-imports" / "example-com"
            import_dir.mkdir(parents=True)
            (import_dir / "01-logo.png").write_text("img", encoding="utf-8")
            (import_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "requested_url": "https://example.com",
                        "site_host": "example.com",
                        "saved_count": 1,
                        "saved_images": [
                            {
                                "source_url": "https://example.com/logo.png",
                                "saved_path": str(import_dir / "01-logo.png"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                summary = workspace._site_import_context_summary("web-project")

        self.assertIn("Representative local assets:", summary)
        self.assertIn("01-logo.png", summary)

    def test_web_app_release_readiness_passes_core_nextjs_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-product"
            (project_dir / "app").mkdir(parents=True)
            (project_dir / "app" / "page.tsx").write_text("export default function Home() { return null; }\n")
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev","build":"next build"}}')
            (project_dir / ".env.example").write_text("OPENAI_API_KEY=\n")
            (project_dir / "product").mkdir()
            (project_dir / "product" / "browser-verification.json").write_text(
                json.dumps({"status": "PASS", "verified_at": "2026-07-11T10:00:00+00:00"})
            )

            with patch("workspace.REPO_ROOT", temp_root):
                readiness = workspace.project_release_readiness("web-product", "web_app")

        joined = "\n".join(readiness)
        self.assertIn("PASS package.json exists", joined)
        self.assertIn("PASS package.json defines a build script", joined)
        self.assertIn("PASS Next.js route entry exists", joined)
        self.assertIn("PASS Playwright browser verification passed", joined)
        self.assertIn("ACTION verify Vercel preview deployment URL", joined)

    def test_web_app_release_readiness_fails_without_browser_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-product"
            (project_dir / "app").mkdir(parents=True)
            (project_dir / "app" / "page.tsx").write_text("export default function Home() { return null; }\n")
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev","build":"next build"}}')

            with patch("workspace.REPO_ROOT", temp_root):
                readiness = workspace.project_release_readiness("web-product", "web_app")

        self.assertIn("FAIL run `tools/verify_web_app.py`", "\n".join(readiness))

    def test_reconcile_web_app_requirement_after_verification_marks_release_validation_task_done(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            product_dir = temp_root / "projects" / "web-product" / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "browser-verification.json").write_text('{"status":"PASS"}\n')
            (product_dir / "tasks.md").write_text(
                "\n".join(
                    [
                        "# Tasks — Web Product",
                        "",
                        "## Task Rules",
                        "",
                        "- Keep tasks concrete.",
                        "",
                        "## Task 1: Build the site",
                        "",
                        "Type: Feature Task",
                        "Status: DONE",
                        "Requirement: R1",
                        "",
                        "Goal:",
                        "Ship the core website.",
                        "",
                        "## Task 2: Validate rendered UX and release readiness",
                        "",
                        "Type: Validation Task",
                        "Status: TODO",
                        "Requirement: R1",
                        "",
                        "Goal:",
                        "Verify rendered UX and release readiness.",
                        "",
                        "Validation:",
                        "- Run canonical web-app verification with `tools/verify_web_app.py`.",
                        "",
                    ]
                )
                + "\n"
            )

            with patch("workspace.REPO_ROOT", temp_root):
                updated = reconcile_web_app_requirement_after_verification("web-product", "R1")
                document = workspace.load_task_document("web-product")

        self.assertEqual(updated, 1)
        validation_task = next(task for task in document.tasks if task.number == 2)
        self.assertEqual(validation_task.status, "DONE")

    def test_figma_referenced_web_app_release_requires_approved_requirement_frame(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-product"
            (project_dir / "app").mkdir(parents=True)
            (project_dir / "product").mkdir()
            (project_dir / "app" / "page.tsx").write_text("export default function Home() { return null; }\n")
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev","build":"next build"}}')
            (project_dir / "product" / "browser-verification.json").write_text('{"status":"PASS"}')
            (project_dir / "product" / "ui-runtime.json").write_text(
                json.dumps(
                    {
                        "default_ui_runtime": "web_app",
                        "design": {
                            "mode": "figma_referenced",
                            "figma_references": [
                                {
                                    "requirement_id": "R9",
                                    "frame_url": "https://www.figma.com/design/key/Product?node-id=9-1",
                                    "frame_name": "Approved page",
                                    "approval_status": "approved",
                                }
                            ],
                        },
                    }
                )
            )

            with patch("workspace.REPO_ROOT", temp_root):
                approved = workspace.project_release_readiness("web-product", "web_app", "R9")
                missing = workspace.project_release_readiness("web-product", "web_app", "R10")

        self.assertIn("PASS R9 uses approved Figma frame", "\n".join(approved))
        self.assertIn("FAIL sync Figma connector evidence for R9", "\n".join(approved))
        self.assertIn("INFO R10 has no Figma mapping and follows the code-first path", "\n".join(missing))

    def test_figma_connector_evidence_must_match_approved_reference_and_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            product_dir = temp_root / "projects" / "web-product" / "product"
            evidence_dir = product_dir / "figma-evidence"
            evidence_dir.mkdir(parents=True)
            frame_url = "https://www.figma.com/design/file-key/Product?node-id=12-34"
            (product_dir / "ui-runtime.json").write_text(
                json.dumps(
                    {
                        "default_ui_runtime": "web_app",
                        "design": {
                            "mode": "figma_referenced",
                            "figma_references": [
                                {
                                    "requirement_id": "R12",
                                    "frame_url": frame_url,
                                    "frame_name": "Checkout",
                                    "approval_status": "approved",
                                }
                            ],
                        },
                    }
                )
            )
            (evidence_dir / "R12.png").write_bytes(b"png")
            (evidence_dir / "R12.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "source": {"frame_url": frame_url},
                        "frame": {"screenshot_path": "product/figma-evidence/R12.png"},
                    }
                )
            )

            with patch("workspace.REPO_ROOT", temp_root):
                matches = workspace.figma_evidence_matches_reference("web-product", "R12")

        self.assertTrue(matches)

    def test_streamlit_release_readiness_uses_railway_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "streamlit-product"
            (project_dir / "src").mkdir(parents=True)
            (project_dir / "src" / "app.py").write_text("import streamlit as st\n")
            (project_dir / "requirements.txt").write_text("streamlit\n")
            (project_dir / "railway.toml").write_text("[deploy]\n")

            with patch("workspace.REPO_ROOT", temp_root):
                readiness = workspace.project_release_readiness("streamlit-product", "streamlit")

        joined = "\n".join(readiness)
        self.assertIn("PASS Streamlit entrypoint exists", joined)
        self.assertIn("PASS Python dependency manifest exists", joined)
        self.assertIn("PASS Railway deployment config or Dockerfile is present", joined)
        self.assertIn("ACTION verify Railway deployment or redeploy", joined)

    def test_requirement_implementation_prompt_defaults_to_streamlit_capability_profile(self) -> None:
        with patch(
            "workspace.parse_requirements",
            return_value=[
                {
                    "id": "R94",
                    "title": "Improve internal workflow",
                    "status": "IN_PROGRESS",
                    "priority": "MEDIUM",
                    "effort": "S",
                    "description": "Refine a small internal control surface.",
                }
            ],
        ), patch("workspace.load_project_ui_runtime", return_value="streamlit"):
            prompt = build_requirement_implementation_prompt("os-control-panel", "R94")

        self.assertIn("Project capability profile: Streamlit app", prompt)
        self.assertIn("Build this as a Python Streamlit app", prompt)

    def test_live_ui_designer_system_prompt_defaults_to_streamlit_guidance(self) -> None:
        with patch("workspace.load_project_ui_runtime", return_value="streamlit"):
            prompt = workspace._live_ui_designer_system_prompt(
                "os-control-panel",
                "Design Direction",
                force_draft=False,
            )

        self.assertIn("Project capability profile: Streamlit app", prompt)
        self.assertIn("Do not assume Next.js, React, or browser-native routing", prompt)

    def test_live_ui_designer_system_prompt_switches_to_web_app_guidance(self) -> None:
        with patch("workspace.load_project_ui_runtime", return_value="web_app"):
            prompt = workspace._live_ui_designer_system_prompt(
                "os-control-panel",
                "UI Review",
                force_draft=False,
            )

        self.assertIn("Project capability profile: Web app", prompt)
        self.assertIn("Do not assume Streamlit patterns", prompt)
        self.assertIn("request `read_project_capability_profile`", prompt)
        self.assertIn("request `fetch_webpage`, `crawl_website`, or `render_webpage`", prompt)
        self.assertIn("`download_site_images`", prompt)
        self.assertIn("`classify_downloaded_site_assets`", prompt)

    def test_live_experience_system_prompt_defaults_to_streamlit_guidance(self) -> None:
        with patch("workspace.load_project_ui_runtime", return_value="streamlit"):
            prompt = workspace._live_experience_system_prompt(
                "os-control-panel",
                "Usability Review",
                force_draft=False,
            )

        self.assertIn("Project capability profile: Streamlit app", prompt)
        self.assertIn("rerun orientation", prompt)
        self.assertIn("repeated stacked sections", prompt)

    def test_live_experience_system_prompt_switches_to_web_app_guidance(self) -> None:
        with patch("workspace.load_project_ui_runtime", return_value="web_app"):
            prompt = workspace._live_experience_system_prompt(
                "os-control-panel",
                "Usability Review",
                force_draft=False,
            )

        self.assertIn("Project capability profile: Web app", prompt)
        self.assertIn("responsive behavior", prompt)
        self.assertIn("browser-native navigation expectations", prompt)
        self.assertIn("Local capability bundle: web-app-frontend", prompt)
        self.assertIn("request `read_project_capability_profile`", prompt)
        self.assertIn("request `fetch_webpage`, `crawl_website`, or `render_webpage`", prompt)
        self.assertIn("`download_site_images`", prompt)
        self.assertIn("`classify_downloaded_site_assets`", prompt)

    def test_live_pm_system_prompt_web_app_mentions_capability_profile_tool(self) -> None:
        prompt = workspace._live_pm_system_prompt(
            "new-web-project",
            "New Web Project",
            ui_runtime="web_app",
            force_draft=False,
        )

        self.assertIn("Planned project capability profile: Web app", prompt)
        self.assertIn("Do not request `read_project_capability_profile`", prompt)
        self.assertIn("`fetch_webpage`", prompt)
        self.assertIn("`crawl_website`", prompt)
        self.assertIn("`render_webpage`", prompt)
        self.assertIn("`download_site_images`", prompt)
        self.assertIn("`classify_downloaded_site_assets`", prompt)

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
        with patch("workspace._run_live_pm_turn", side_effect=[first_turn, second_turn, second_turn]):
            thread = start_live_pm_project_thread(
                "new-project",
                "New Project",
                "I want to build a better intake tool.",
            )
            updated = continue_live_pm_project_thread(thread, "Product Directors shaping new projects.")

        self.assertEqual(updated.status, "drafted")
        self.assertEqual(updated.draft_title, "Add live PM discovery to new project creation")
        self.assertIn("Draft body", updated.draft_requirement)

    def test_live_pm_turn_synthesizes_missing_assistant_message_for_draft(self) -> None:
        repaired = workspace._ensure_live_pm_assistant_message(
            LivePMTurn(
                next_action="draft_requirements",
                assistant_message="",
                draft_title="Add grounded import artifacts to web replication",
                draft_requirement="Problem statement\n- Draft body",
            )
        )

        self.assertIn("Add grounded import artifacts", repaired.assistant_message)

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

    def test_live_pm_project_thread_preserves_web_app_runtime(self) -> None:
        first_turn = LivePMTurn(
            next_action="ask_question",
            assistant_message="Who is the user?",
            draft_title="",
            draft_requirement="",
        )
        second_turn = LivePMTurn(
            next_action="draft_requirements",
            assistant_message="Drafted.",
            draft_title="Build web intake",
            draft_requirement="Build a web-native intake flow.",
        )
        with patch("workspace._run_live_pm_turn", side_effect=[first_turn, second_turn, second_turn]):
            thread = start_live_pm_project_thread(
                "New Web Project",
                "New Web Project",
                "I want a web app.",
                ui_runtime="web-app",
            )
            updated = continue_live_pm_project_thread(thread, "Product directors.")
            drafted = draft_live_pm_project_thread(updated)

        self.assertEqual(thread.ui_runtime, "web_app")
        self.assertEqual(updated.ui_runtime, "web_app")
        self.assertEqual(drafted.ui_runtime, "web_app")

    def test_live_pm_system_prompt_includes_imported_website_requirement_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "web-project"
            for relative in ("product", "src", "evals", "tools", "tests", "data"):
                (project_root / relative).mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (project_root / "memory.md").write_text("# memory\n", encoding="utf-8")
            (project_root / "rules.md").write_text("# rules\n", encoding="utf-8")
            (project_root / "product" / "requirements.md").write_text("# req\n", encoding="utf-8")
            (project_root / "product" / "tasks.md").write_text("# tasks\n", encoding="utf-8")
            import_dir = project_root / "data" / "site-imports" / "example-com"
            import_dir.mkdir(parents=True)
            (import_dir / "manifest.json").write_text(
                json.dumps({"requested_url": "https://example.com", "site_host": "example.com", "saved_count": 2}),
                encoding="utf-8",
            )
            (import_dir / "crawl.json").write_text(
                json.dumps(
                    {
                        "pages": [
                            {
                                "title": "Example Electrical Services",
                                "navigation_labels": ["HOME", "SERVICES", "ABOUT", "CONTACT"],
                                "content_blocks": ["Trusted local electrical contractor."],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch("workspace.REPO_ROOT", temp_root):
                prompt = workspace._live_pm_system_prompt(
                    "web-project",
                    "Web Project",
                    ui_runtime="web_app",
                    force_draft=False,
                )

        self.assertIn("Imported website context is already available", prompt)
        self.assertIn("Representative source copy:", prompt)
        self.assertIn("downloaded local site assets should be the primary visual source set", prompt)
        self.assertIn("make source-copy reuse, downloaded local asset reuse, and no-placeholder expectations explicit", prompt)

    def test_create_project_from_reviewed_draft_passes_title_and_body_to_scaffold(self) -> None:
        fake_destination = REPO_ROOT / "projects" / "tmp-project"
        with patch("workspace.scaffold_project", return_value=fake_destination) as mock_scaffold, patch(
            "workspace.save_project_ui_runtime"
        ) as mock_save_runtime:
            destination = create_project_from_reviewed_draft(
                "tmp-project",
                "Tmp Project",
                "Initial live requirement",
                "Problem statement\n- Draft body",
                ui_runtime="web_app",
            )

        self.assertEqual(destination, fake_destination)
        mock_scaffold.assert_called_once_with(
            project_name="tmp-project",
            display_name="Tmp Project",
            product_title="Tmp Project",
            initial_requirement_title="Initial live requirement",
            initial_requirement="Problem statement\n- Draft body",
            ui_runtime="web_app",
        )
        mock_save_runtime.assert_called_once_with("tmp-project", "web_app")

    def test_load_requirement_document_accepts_legacy_requirement_rules_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            requirements_path.write_text(
                "# Product Requirements\n\n## Active Requirements\n\n### R1 — Initial requirement\n\nStatus: NEW\nDescription:\nLegacy rules heading example.\n\n---\n\n## Backlog (Not yet prioritised)\n\nNone yet.\n\n---\n\n## Requirement Rules\n\n- Keep the file parseable.\n"
            )

            with patch("workspace._requirements_path", return_value=requirements_path):
                document = load_requirement_document("tmp-project")

        self.assertEqual(document.active_requirements[0].id, "R1")
        self.assertIn("Keep the file parseable", document.rules_text)

    def test_load_requirement_document_accepts_legacy_requirement_rules_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            requirements_path = Path(temp_dir) / "requirements.md"
            requirements_path.write_text(
                "# Product Requirements\n\n## Active Requirements\n\n### R1 — Initial requirement\n\nStatus: NEW\nDescription:\nLegacy rules heading example.\n\n---\n\n## Backlog (Not yet prioritised)\n\nNone yet.\n\n---\n\n## Requirement Rules\n\n- Keep the file parseable.\n"
            )

            with patch("workspace._requirements_path", return_value=requirements_path):
                document = load_requirement_document("tmp-project")

        self.assertEqual(document.active_requirements[0].id, "R1")
        self.assertIn("Keep the file parseable", document.rules_text)

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
            ), patch(
                "workspace.save_project_ui_runtime"
            ):
                destination = create_project_from_reviewed_draft(
                    "tmp-project",
                    "Tmp Project",
                    "Initial live requirement",
                    "Problem statement\n- Draft body",
                    ui_runtime="web_app",
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

    def test_web_app_project_preview_uses_npm_dev_server(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            package_json = project_dir / "package.json"
            package_json.write_text('{"scripts":{"dev":"next dev"}}')
            next_bin = project_dir / "node_modules" / ".bin"
            next_bin.mkdir(parents=True)
            (next_bin / "next").write_text("")

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("web-preview")

        self.assertTrue(preview.available)
        self.assertEqual(preview.runtime, "web_app")
        self.assertEqual(preview.entry_path, package_json)
        self.assertEqual(preview.command[:3], ("npm", "run", "dev"))
        self.assertIn("--port", preview.command)

    def test_web_app_project_preview_reuses_existing_running_server_port(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            package_json = project_dir / "package.json"
            package_json.write_text('{"scripts":{"dev":"next dev"}}')
            next_bin = project_dir / "node_modules" / ".bin"
            next_bin.mkdir(parents=True)
            (next_bin / "next").write_text("")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._running_web_app_preview_port", return_value=8877
            ):
                preview = project_preview("web-preview")

        self.assertEqual(preview.url, "http://localhost:8877")

    def test_project_preview_explains_unavailable_projects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "projects" / "library-only").mkdir(parents=True)

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("library-only")

        self.assertFalse(preview.available)
        self.assertEqual(preview.command, ())
        self.assertIn("does not expose src/app.py", preview.status_text)

    def test_web_app_project_preview_requires_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            product_dir = temp_root / "projects" / "web-preview" / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("web-preview")

        self.assertFalse(preview.available)
        self.assertEqual(preview.runtime, "web_app")
        self.assertIn("package.json", preview.status_text)

    def test_web_app_project_preview_requires_installed_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev"}}')

            with patch("workspace.REPO_ROOT", temp_root):
                preview = project_preview("web-preview")

        self.assertTrue(preview.available)
        self.assertEqual(preview.runtime, "web_app")
        self.assertIn("install frontend dependencies automatically", preview.status_text)

    def test_start_project_preview_reuses_existing_local_port(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            app_file = temp_root / "projects" / "previewable" / "src" / "app.py"
            app_file.parent.mkdir(parents=True)
            app_file.write_text("print('preview')\n")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._local_port_accepts_connections", return_value=True
            ), patch("workspace._preview_process_matches", return_value=True), patch("workspace.subprocess.Popen") as mock_popen:
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

    def test_start_project_preview_reuses_running_web_app_server_even_if_port_differs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev"}}')
            next_bin = project_dir / "node_modules" / ".bin"
            next_bin.mkdir(parents=True)
            (next_bin / "next").write_text("")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._running_web_app_preview_port", return_value=8877
            ), patch("workspace.subprocess.Popen") as mock_popen:
                preview = start_project_preview("web-preview")

        self.assertEqual(preview.url, "http://localhost:8877")
        mock_popen.assert_not_called()

    def test_start_project_preview_waits_for_web_app_server_before_succeeding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev"}}')
            next_bin = project_dir / "node_modules" / ".bin"
            next_bin.mkdir(parents=True)
            (next_bin / "next").write_text("")

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._running_web_app_preview_port", return_value=None
            ), patch(
                "workspace._local_port_accepts_connections", return_value=False
            ), patch("workspace._wait_for_preview_port", return_value=False), patch(
                "workspace._ensure_web_app_preview_dependencies"
            ), patch(
                "workspace.subprocess.Popen"
            ):
                with self.assertRaises(RuntimeError):
                    start_project_preview("web-preview")

    def test_start_project_preview_installs_missing_web_app_dependencies_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_dir = temp_root / "projects" / "web-preview"
            product_dir = project_dir / "product"
            product_dir.mkdir(parents=True)
            (product_dir / "ui-runtime.json").write_text('{"default_ui_runtime":"web_app"}')
            (project_dir / "package.json").write_text('{"scripts":{"dev":"next dev"}}')

            with patch("workspace.REPO_ROOT", temp_root), patch(
                "workspace._running_web_app_preview_port", return_value=None
            ), patch(
                "workspace._local_port_accepts_connections", return_value=False
            ), patch(
                "workspace._wait_for_preview_port", return_value=True
            ), patch(
                "workspace._ensure_web_app_preview_dependencies"
            ) as mock_install, patch(
                "workspace.subprocess.Popen"
            ) as mock_popen:
                preview = start_project_preview("web-preview")

        self.assertTrue(preview.available)
        mock_install.assert_called_once_with(project_dir)
        mock_popen.assert_called_once()

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

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": ""}), patch(
                "workspace.REPO_ROOT", temp_root
            ):
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

    def test_sprint_plan_accepts_new_requirements_as_well_as_backlog(self) -> None:
        requirements_text = """# Product Requirements

## Active Requirements

### R1 — New candidate

Status: NEW
Priority: HIGH
Effort: M
Description:
Ready for sprint planning.

---

## Backlog (Not yet prioritised)

### R2 — Backlog candidate

Status: BACKLOG
Priority: MEDIUM
Effort: S
Description:
Also ready for sprint planning.

---

## Rules

- Keep this file parseable.
"""
        tasks_text = "# Tasks — Tmp Project\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            temp_requirements = temp_root / "requirements.md"
            temp_tasks = temp_root / "tasks.md"
            sprint_path = temp_root / "projects" / "tmp-project" / "data" / "sprint.json"
            temp_requirements.write_text(requirements_text)
            temp_tasks.write_text(tasks_text)

            with patch("workspace._requirements_path", return_value=temp_requirements), patch(
                "workspace._tasks_path", return_value=temp_tasks
            ), patch("workspace._sprint_path", return_value=sprint_path):
                first_plan = plan_sprint_requirement("tmp-project", "R1")
                second_plan = plan_sprint_requirement("tmp-project", "R2")

        self.assertEqual(first_plan.requirement_ids, ("R1",))
        self.assertEqual(second_plan.requirement_ids, ("R1", "R2"))

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

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": ""}), patch(
                "workspace.REPO_ROOT", temp_root
            ), patch(
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

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": ""}), patch(
                "workspace.REPO_ROOT", temp_root
            ), patch(
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

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": ""}), patch(
                "workspace.REPO_ROOT", temp_root
            ):
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

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": str(temp_root)}), patch(
                "workspace.REPO_ROOT", temp_root
            ), patch("workspace._scaffolded_project_directory_name", return_value="tmp-project"):
                complete_sprint("tmp-project")
                sprint = load_sprint_plan("tmp-project")

        self.assertIsNotNone(sprint)
        self.assertEqual(sprint.status, "COMPLETED")
        self.assertEqual(sprint.requirement_ids, ())

    def test_complete_sprint_does_not_require_release_delivery_approval_before_clearing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            project_root = temp_root / "projects" / "tmp-project"
            product_dir = project_root / "product"
            data_dir = project_root / "data"
            product_dir.mkdir(parents=True)
            data_dir.mkdir(parents=True)
            (product_dir / "requirements.md").write_text(
                "# Product Requirements\n\n"
                "## Active Requirements\n\n"
                "### R1 — Finished item\n\nStatus: DONE\nPriority: HIGH\nEffort: M\nDescription:\nDone.\n\n"
                "---\n\n## Backlog (Not yet prioritised)\n\nAdd backlog requirements here when needed.\n\n"
                "---\n\n## Rules\n\n* rule\n"
            )
            (data_dir / "sprint.json").write_text(
                '{"status":"READY_TO_CLOSE","requirement_ids":["R1"],"created_at":"now","started_at":"now","completed_at":"later","current_requirement_id":"","blocked_reason":""}'
            )
            approvals_path = Path(temp_dir) / "approvals.json"
            approvals_path.write_text("[]")
            change_plan = workspace.GitChangePlan(
                included_paths=("projects/tmp-project/product/requirements.md",),
                excluded_paths=(),
                branch="feature/release",
            )

            with patch.dict("os.environ", {"AI_BUILDER_OS_RUNTIME_ROOT": str(temp_root)}), patch(
                "workspace.REPO_ROOT", temp_root
            ), patch("workspace._scaffolded_project_directory_name", return_value="tmp-project"), patch("workspace.APPROVAL_FILE", approvals_path), patch(
                "workspace._release_git_change_plan", return_value=change_plan
            ):
                sprint = complete_sprint("tmp-project")
                approvals = list_approvals("tmp-project")

        self.assertEqual(sprint.status, "COMPLETED")
        self.assertEqual(sprint.requirement_ids, ())
        self.assertEqual(sprint.blocked_reason, "")
        self.assertEqual(approvals, [])

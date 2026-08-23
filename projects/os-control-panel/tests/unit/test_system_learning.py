from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from agents_runtime.registry import build_agent_registry
from system_learning import (
    CODEX_TELEMETRY_METRICS,
    PM_QUALITY_COMPATIBILITY_VERSION,
    CapabilityDescriptor,
    CapabilityRegistry,
    CausalHypothesis,
    ContextBreakdown,
    EfficiencyRunRecord,
    LatencyBreakdown,
    MetricEvidence,
    OSLearningDiagnosis,
    OptimisationExperiment,
    ProposedExperiment,
    SignalPolicy,
    SystemLearning,
    SystemLearningStore,
    assess_capability_coverage,
    build_workflow_baseline,
    compare_baselines,
    codex_native_telemetry_capability_report,
    codex_native_quality_capability_report,
    detect_efficiency_signals,
    evaluate_experiment,
    inspect_relevant_code,
    import_codex_native_history,
    evaluate_pm_quality_artifact,
    pm_quality_profile,
    record_from_trace_events,
    resolve_runtime_capability,
    run_isolated_operational_proof,
    select_capability_windows,
    validate_capability_coverage,
)


class SystemLearningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.storage_patch = patch("system_learning.control_data_dir", return_value=self.root)
        self.lock_patch = patch("system_learning.project_lock", side_effect=lambda _project: nullcontext())
        self.storage_patch.start()
        self.lock_patch.start()

    def tearDown(self) -> None:
        self.lock_patch.stop()
        self.storage_patch.stop()
        self.temporary.cleanup()

    @staticmethod
    def make_run(
        index: int,
        *,
        tokens: int = 100,
        quality: float = 0.95,
        latency: float = 1.0,
        retries: int = 0,
        guardrail: bool = True,
        eval_passed: bool = True,
        cost: float | None = 0.01,
        role: str = "PM",
        mode: str = "task_plan",
        contract_version: str = "contract-v1",
        capability_id: str = "",
        capability_version: str = "",
        change_marker: str = "",
        quality_eval_profile: str = "",
    ) -> EfficiencyRunRecord:
        timestamp = (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)).isoformat()
        return EfficiencyRunRecord(
            run_id=f"run-{index}",
            timestamp=timestamp,
            project="demo",
            role=role,
            workflow_mode=mode,
            capability_id=capability_id,
            capability_version=capability_version,
            change_marker=change_marker,
            quality_eval_profile=quality_eval_profile,
            execution_backend="fixture",
            contract_version=contract_version,
            model="fixture-model",
            reasoning_effort="medium",
            input_tokens=tokens - 20,
            cached_input_tokens=20,
            cache_write_tokens=0,
            output_tokens=20,
            reasoning_tokens=0,
            model_requests=1,
            tool_calls=2,
            tool_result_size=50,
            context=ContextBreakdown(static_instructions=20, project_context=20, session_context=20, tool_results=50),
            latency_seconds=latency,
            retries=retries,
            outcome="success",
            quality_score=quality,
            eval_passed=eval_passed,
            guardrail_passed=guardrail,
            estimated_cost_usd=cost,
            pricing_provenance="fixture-pricing-v1" if cost is not None else "unavailable",
        )

    def test_run_contract_requires_pricing_provenance_and_allows_missing_provider_fields(self) -> None:
        record = EfficiencyRunRecord(
            run_id="codex-1",
            timestamp="2026-01-01T00:00:00+00:00",
            project="demo",
            role="Engineer",
            workflow_mode="implementation",
            execution_backend="codex_native",
            unavailable_fields=["input_tokens", "output_tokens"],
        )
        self.assertIsNone(record.total_tokens)
        self.assertEqual(record.unavailable_fields, ["input_tokens", "output_tokens"])
        with self.assertRaisesRegex(ValidationError, "pricing provenance"):
            record.model_copy(update={"estimated_cost_usd": 1.0}).model_validate(
                record.model_copy(update={"estimated_cost_usd": 1.0}).model_dump()
            )

    def test_baseline_uses_only_quality_controlled_successes_for_success_metrics(self) -> None:
        records = [self.make_run(index, tokens=100 + index) for index in range(5)]
        records.append(self.make_run(6, tokens=25, guardrail=False))
        baseline = build_workflow_baseline(records, role="PM", workflow_mode="task_plan")
        self.assertEqual(baseline.observed_runs, 6)
        self.assertEqual(baseline.quality_controlled_successes, 5)
        self.assertGreater(baseline.metrics["tokens_per_successful_workflow"].median, 100)
        self.assertEqual(baseline.confidence, "low")
        self.assertAlmostEqual(baseline.cache_utilisation or 0, 120 / sum(item.input_tokens or 0 for item in records))

    def test_incompatible_contract_versions_fail_closed(self) -> None:
        records = [self.make_run(1), self.make_run(2, contract_version="contract-v2")]
        with self.assertRaisesRegex(ValueError, "Incompatible contract versions"):
            build_workflow_baseline(records, role="PM", workflow_mode="task_plan")

    def test_signal_detection_requires_samples_and_prioritises_quality_regression(self) -> None:
        baseline_records = [self.make_run(index, tokens=100, quality=0.95) for index in range(20)]
        candidate_records = [
            self.make_run(100 + index, tokens=130, quality=0.80) for index in range(20)
        ]
        baseline = build_workflow_baseline(baseline_records, role="PM", workflow_mode="task_plan")
        candidate = build_workflow_baseline(candidate_records, role="PM", workflow_mode="task_plan")
        signals = detect_efficiency_signals(baseline, candidate, cadence="slow")
        self.assertTrue(any(item.metric == "tokens_per_successful_workflow" for item in signals))
        self.assertTrue(any(item.metric == "quality_score" for item in signals))
        self.assertTrue(all(item.confidence == "high" for item in signals))
        too_small = build_workflow_baseline(baseline_records[:4], role="PM", workflow_mode="task_plan")
        self.assertEqual(detect_efficiency_signals(too_small, too_small), [])

    def test_comparison_rejects_quality_regression_despite_token_savings(self) -> None:
        baseline = build_workflow_baseline(
            [self.make_run(index, tokens=100, quality=0.95) for index in range(10)],
            role="PM", workflow_mode="task_plan",
        )
        candidate = build_workflow_baseline(
            [self.make_run(100 + index, tokens=60, quality=0.70) for index in range(10)],
            role="PM", workflow_mode="task_plan",
        )
        experiment = OptimisationExperiment(
            experiment_id="E1",
            signal_id="S1",
            diagnosis_id="D1",
            hypothesis="Reduce context without reducing quality.",
            intervention="Use requirement-scoped retrieval.",
            baseline_run_ids=[self.make_run(0).run_id],
            candidate_run_ids=["candidate"],
            expected_effect="At least 20% fewer tokens.",
            success_threshold=0.20,
            maximum_quality_regression=0.01,
            safety_guardrails=["Approval semantics unchanged"],
            minimum_evidence=5,
            falsification_condition="Quality falls by more than 1%.",
            change_risk="medium",
            created_at="2026-01-01T00:00:00+00:00",
        )
        evaluated = evaluate_experiment(experiment, baseline, candidate)
        self.assertEqual(evaluated.status, "rejected")
        self.assertIn("quality_regression", evaluated.decision_reasons)

    def test_experiment_adopts_only_when_efficiency_and_guardrails_pass(self) -> None:
        baseline = build_workflow_baseline(
            [self.make_run(index, tokens=100, quality=0.95) for index in range(10)],
            role="PM", workflow_mode="task_plan",
        )
        candidate = build_workflow_baseline(
            [self.make_run(100 + index, tokens=70, quality=0.96) for index in range(10)],
            role="PM", workflow_mode="task_plan",
        )
        experiment = OptimisationExperiment(
            experiment_id="E2", signal_id="S2", diagnosis_id="D2",
            hypothesis="Scoped retrieval is more efficient.", intervention="Scope retrieval.",
            baseline_run_ids=["b"], candidate_run_ids=["c"], expected_effect="20% fewer tokens.",
            success_threshold=0.20, maximum_quality_regression=0.01,
            safety_guardrails=["Safety unchanged"], minimum_evidence=5,
            falsification_condition="Threshold or guardrail fails.", change_risk="medium",
            created_at="2026-01-01T00:00:00+00:00",
        )
        evaluated = evaluate_experiment(experiment, baseline, candidate)
        self.assertEqual(evaluated.status, "adopted")
        self.assertEqual(evaluated.monitoring_baseline_id, candidate.baseline_id)

    def test_diagnosis_contract_is_structured_and_falsifiable(self) -> None:
        hypothesis = CausalHypothesis(
            explanation="Broad memory retrieval increased input context.",
            supporting_evidence=["Project context grew 30%."],
            counter_evidence=["Tool result size was stable."],
            confidence="medium",
        )
        diagnosis = OSLearningDiagnosis(
            diagnosis_id="D1", signal_id="S1", observation="Input tokens increased 30%.", severity="medium",
            hypotheses=[hypothesis], primary_hypothesis=hypothesis.explanation,
            proposed_experiment=ProposedExperiment(
                intervention="Use scoped retrieval.", baseline="Current retrieval.", candidate="Scoped retrieval.",
                expected_effect="At least 20% fewer tokens.", success_threshold="20% token reduction.",
                quality_guardrails=["Quality loss no more than 1%."], safety_guardrails=["Approvals unchanged."],
                minimum_evidence="Ten quality-controlled runs per arm.",
                falsification_condition="Token threshold or quality guardrail fails.",
            ),
            change_risk="medium", recommended_next_role="Architect", related_prior_learning=["L1"],
            observations_are_separate_from_inferences=True,
        )
        self.assertEqual(diagnosis.primary_hypothesis, hypothesis.explanation)
        with self.assertRaisesRegex(ValidationError, "distinguish observations"):
            OSLearningDiagnosis.model_validate(diagnosis.model_copy(update={"observations_are_separate_from_inferences": False}).model_dump())

    def test_store_retains_rejected_learning_and_scopes_search(self) -> None:
        store = SystemLearningStore("demo")
        learning = SystemLearning(
            learning_id="L1", originating_signal="S1", question="Does broad PM memory help?",
            hypothesis="Broad memory improves task planning.", intervention="Load all project memory.",
            experiment_id="E1", experiment_evidence={"tokens_change": 0.30, "quality_change": 0.0},
            result="rejected", conclusion="Broad memory added context without quality benefit.", confidence="high",
            applies_to=["PM/task_plan"], do_not_generalise_to=["PM/discovery"], related_requirements=["R107"],
            recorded_at="2026-01-01T00:00:00+00:00",
        )
        store.save_learning(learning)
        self.assertEqual(store.search_learnings("broad memory")[0].result, "rejected")
        self.assertEqual(store.search_learnings("unrelated"), [])
        with self.assertRaisesRegex(ValueError, "Immutable learnings identity"):
            store.save_learning(learning.model_copy(update={"conclusion": "Changed"}))

    def test_experiment_status_can_progress_but_design_is_immutable(self) -> None:
        store = SystemLearningStore("demo")
        experiment = OptimisationExperiment(
            experiment_id="E3", signal_id="S3", diagnosis_id="D3", hypothesis="Scoped context helps.",
            intervention="Scope context.", baseline_run_ids=["b"], candidate_run_ids=["c"],
            expected_effect="20% fewer tokens.", success_threshold=0.20,
            safety_guardrails=["Approvals unchanged"], falsification_condition="Any guardrail fails.",
            change_risk="medium", created_at="2026-01-01T00:00:00+00:00",
        )
        store.save_experiment(experiment)
        adopted = experiment.model_copy(update={
            "status": "adopted", "decision_reasons": ["all_thresholds_passed"],
            "monitoring_baseline_id": "baseline-candidate",
        })
        store.save_experiment(adopted)
        self.assertEqual(store.experiment("E3").status, "adopted")
        with self.assertRaisesRegex(ValueError, "design is immutable"):
            store.save_experiment(adopted.model_copy(update={"intervention": "Different intervention"}))

    def test_paused_run_may_finalize_once_but_final_run_is_immutable(self) -> None:
        store = SystemLearningStore("demo")
        paused = self.make_run(1).model_copy(update={"state": "incomplete", "outcome": "paused"})
        final = self.make_run(1)
        store.record_run(paused)
        store.record_run(final)
        self.assertEqual(store.runs()[0].state, "final")
        with self.assertRaisesRegex(ValueError, "Immutable final run"):
            store.record_run(final.model_copy(update={"input_tokens": 999}))

    def test_post_run_eval_evidence_can_fill_missing_fields_but_not_rewrite_them(self) -> None:
        store = SystemLearningStore("demo")
        record = self.make_run(1, cost=None).model_copy(update={
            "quality_score": None, "eval_passed": None, "guardrail_passed": None,
        })
        store.record_run(record)
        enriched = store.attach_run_evidence(
            record.run_id, quality_score=0.97, eval_passed=True, guardrail_passed=True,
            estimated_cost_usd=0.02, pricing_provenance="pricing-v2",
        )
        self.assertTrue(enriched.quality_controlled_success)
        self.assertEqual(enriched.pricing_provenance, "pricing-v2")
        with self.assertRaisesRegex(ValueError, "immutable once recorded"):
            store.attach_run_evidence(record.run_id, quality_score=0.5)

    def test_trace_adapter_records_context_tool_and_nullable_eval_evidence(self) -> None:
        events = [
            {"timestamp": "2026-01-01T00:00:00+00:00", "trace_id": "t1", "run_id": "r1", "event": "run_started", "runtime": "openai_agents_sdk", "role": "PM", "model": "m", "reasoning_effort": "low", "workflow_mode": "task_plan"},
            {"trace_id": "t1", "event": "model_call", "static_instruction_size": 100, "session_context_size": 200},
            {"trace_id": "t1", "event": "tool_completed", "output_chars": 300},
            {"trace_id": "t1", "event": "model_response", "input_tokens": 50, "cached_input_tokens": 10, "output_tokens": 20, "reasoning_tokens": 5, "model_requests": 1},
            {"trace_id": "t1", "event": "run_completed", "guardrails": [], "latency_seconds": 1.2},
        ]
        with patch("agents_runtime.support.load_agent_traces", return_value=events):
            record = record_from_trace_events("demo", "t1")
        self.assertEqual(record.context.static_instructions, 100)
        self.assertEqual(record.tool_result_size, 300)
        self.assertEqual(record.capability_id, "pm.task_plan")
        self.assertTrue(record.capability_version)
        self.assertTrue(record.quality_eval_profile)
        self.assertIsNone(record.eval_passed)
        self.assertFalse(record.quality_controlled_success)

    def test_os_learning_agent_is_distinct_and_has_only_diagnostic_tools(self) -> None:
        registry = build_agent_registry("fixture-model")
        self.assertIn("learning_agent", registry)
        self.assertIn("os_learning_agent", registry)
        names = {getattr(tool, "name", "") for tool in registry["os_learning_agent"].tools}
        self.assertIn("read_efficiency_signal", names)
        self.assertIn("search_system_learning", names)
        self.assertNotIn("submit_pm_decision", names)
        self.assertNotIn("record_product_intent", names)

    def test_code_inspection_fails_closed_outside_allowlist(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the OS Learning Agent code allowlist"):
            inspect_relevant_code(["private/secrets.txt"])

    def test_end_to_end_loop_retains_learning_and_detects_post_adoption_regression(self) -> None:
        store = SystemLearningStore("demo")
        baseline_runs = [self.make_run(index, tokens=100, quality=0.95) for index in range(10)]
        candidate_runs = [self.make_run(100 + index, tokens=70, quality=0.96) for index in range(10)]
        for record in baseline_runs + candidate_runs:
            store.record_run(record)
        signals = store.refresh_signal_backlog(
            role="PM", workflow_mode="task_plan",
            baseline_run_ids=[item.run_id for item in candidate_runs],
            comparison_run_ids=[item.run_id for item in baseline_runs],
        )
        self.assertTrue(signals)
        signal = signals[0]
        hypothesis = CausalHypothesis(
            explanation="Context scoping explains the efficiency difference.",
            supporting_evidence=[signal.observed_change], counter_evidence=[], confidence="medium",
        )
        diagnosis = OSLearningDiagnosis(
            diagnosis_id="D-e2e", signal_id=signal.signal_id, observation=signal.potential_impact,
            severity="medium", hypotheses=[hypothesis], primary_hypothesis=hypothesis.explanation,
            proposed_experiment=ProposedExperiment(
                intervention="Keep scoped context.", baseline="Broad context.", candidate="Scoped context.",
                expected_effect="At least 20% fewer tokens.", success_threshold="20%",
                quality_guardrails=["No quality regression."], safety_guardrails=["Approvals unchanged."],
                minimum_evidence="Ten runs per arm.", falsification_condition="Any threshold fails.",
            ),
            change_risk="medium", recommended_next_role="Architect", related_prior_learning=[],
            observations_are_separate_from_inferences=True,
        )
        store.save_diagnosis(diagnosis)
        experiment = OptimisationExperiment(
            experiment_id="E-e2e", signal_id=signal.signal_id, diagnosis_id=diagnosis.diagnosis_id,
            hypothesis=hypothesis.explanation, intervention="Keep scoped context.",
            baseline_run_ids=[item.run_id for item in baseline_runs],
            candidate_run_ids=[item.run_id for item in candidate_runs], expected_effect="20% fewer tokens.",
            success_threshold=0.20, safety_guardrails=["Approvals unchanged."], minimum_evidence=5,
            falsification_condition="Any threshold fails.", change_risk="medium",
            created_at="2026-01-01T00:00:00+00:00",
        )
        store.save_experiment(experiment)
        evaluated = evaluate_experiment(
            experiment,
            build_workflow_baseline(baseline_runs, role="PM", workflow_mode="task_plan"),
            build_workflow_baseline(candidate_runs, role="PM", workflow_mode="task_plan"),
        )
        store.save_experiment(evaluated)
        store.save_learning(SystemLearning(
            learning_id="L-e2e", originating_signal=signal.signal_id,
            question="Does scoped context improve task planning?", hypothesis=hypothesis.explanation,
            intervention=experiment.intervention, experiment_id=experiment.experiment_id,
            experiment_evidence={"decision_reasons": evaluated.decision_reasons}, result="accepted",
            conclusion="Scoped context passed efficiency and quality controls.", confidence="high",
            applies_to=["PM/task_plan"], do_not_generalise_to=["PM/discovery"], related_requirements=["R107"],
            recorded_at="2026-01-01T01:00:00+00:00",
        ))
        self.assertEqual(store.search_learnings("scoped context")[0].result, "accepted")

        regressed_runs = [self.make_run(200 + index, tokens=120, quality=0.80) for index in range(10)]
        for record in regressed_runs:
            store.record_run(record)
        post_adoption = store.refresh_signal_backlog(
            role="PM", workflow_mode="task_plan",
            baseline_run_ids=[item.run_id for item in candidate_runs],
            comparison_run_ids=[item.run_id for item in regressed_runs],
        )
        self.assertTrue(any(item.metric == "quality_score" for item in post_adoption))

    def test_capability_registry_requires_unique_complete_eligible_descriptors(self) -> None:
        descriptor = CapabilityDescriptor(
            capability_id="future_agent.default", capability_version="v1", role="Future Agent",
            workflow_mode="default", telemetry_contract_version="contract-v1",
            quality_eval_profile="future-agent-eval-v1", change_marker="release-v1",
        )
        self.assertEqual(CapabilityRegistry(descriptors=[descriptor]).resolve("Future Agent", "default"), descriptor)
        with self.assertRaisesRegex(ValidationError, "quality-eval profile"):
            CapabilityDescriptor(
                capability_id="broken.default", capability_version="v1", role="Broken",
                workflow_mode="default", telemetry_contract_version="contract-v1", change_marker="release-v1",
            )
        with self.assertRaisesRegex(ValidationError, "identities must be unique"):
            CapabilityRegistry(descriptors=[descriptor, descriptor])
        not_applicable = CapabilityDescriptor(
            capability_id="deterministic.no_effect", capability_version="v1", role="Deterministic Feature",
            workflow_mode="default", telemetry_contract_version="contract-v1", change_marker="release-v1",
            eligibility="not_applicable", not_applicable_rationale="No measurable model-backed workflow effect.",
        )
        self.assertEqual(not_applicable.eligibility, "not_applicable")

    def test_capability_coverage_reports_unregistered_runtime_routes(self) -> None:
        self.assertEqual(validate_capability_coverage([("PM", "task_plan")]), [])
        self.assertEqual(
            validate_capability_coverage([("Synthetic New Agent", "default")]),
            ["Synthetic New Agent/default"],
        )

    def test_capability_quality_coverage_reports_ready_missing_and_incompatible_states(self) -> None:
        descriptor = resolve_runtime_capability("PM", "task_plan")
        record = self.make_run(
            1,
            capability_id=descriptor.capability_id,
            capability_version=descriptor.capability_version,
            change_marker=descriptor.change_marker,
            quality_eval_profile=descriptor.quality_eval_profile,
            contract_version=descriptor.telemetry_contract_version,
        )
        self.assertEqual(
            assess_capability_coverage(descriptor.capability_id, [record]).status,
            "ready",
        )
        missing = record.model_copy(update={
            "quality_score": None, "eval_passed": None, "guardrail_passed": None,
        })
        self.assertEqual(
            assess_capability_coverage(descriptor.capability_id, [missing]).status,
            "missing_quality_evidence",
        )
        incompatible = record.model_copy(update={"quality_eval_profile": "pm-task-plan-eval-v2"})
        self.assertEqual(
            assess_capability_coverage(descriptor.capability_id, [incompatible]).status,
            "incompatible_eval_profile",
        )

    def test_capability_lifecycle_warms_baselines_and_selects_non_overlapping_windows(self) -> None:
        def runs(count: int, *, offset: int = 0, version: str = "v1", marker: str = "release-v1"):
            return [
                self.make_run(
                    offset + index,
                    capability_id="future_agent.default",
                    capability_version=version,
                    change_marker=marker,
                    quality_eval_profile="future-agent-eval-v1",
                )
                for index in range(count)
            ]

        warm = select_capability_windows(runs(4), capability_id="future_agent.default")
        self.assertEqual(warm.state, "warming_up")
        baseline = select_capability_windows(runs(5), capability_id="future_agent.default")
        self.assertEqual(baseline.state, "baselined")
        monitoring = select_capability_windows(runs(10), capability_id="future_agent.default")
        self.assertEqual(monitoring.state, "monitoring")
        self.assertEqual(len(monitoring.baseline_run_ids), 5)
        self.assertEqual(len(monitoring.comparison_run_ids), 5)
        self.assertTrue(set(monitoring.baseline_run_ids).isdisjoint(monitoring.comparison_run_ids))

        changed = select_capability_windows(
            runs(5) + runs(4, offset=100, version="v2", marker="release-v2"),
            capability_id="future_agent.default",
        )
        self.assertEqual(changed.state, "changed")
        comparable_release = select_capability_windows(
            runs(5) + runs(5, offset=100, version="v2", marker="release-v2"),
            capability_id="future_agent.default",
        )
        self.assertEqual(len(comparable_release.baseline_run_ids), 5)
        self.assertTrue(set(comparable_release.baseline_run_ids).isdisjoint(comparable_release.comparison_run_ids))

    def test_incompatible_eval_contract_rebaselines_instead_of_comparing(self) -> None:
        original = [
            self.make_run(
                index, capability_id="future_agent.default", capability_version="v1",
                change_marker="release-v1", quality_eval_profile="eval-v1",
            )
            for index in range(5)
        ]
        incompatible = [
            self.make_run(
                100 + index, capability_id="future_agent.default", capability_version="v2",
                change_marker="release-v2", quality_eval_profile="eval-v2",
            )
            for index in range(4)
        ]
        plan = select_capability_windows(
            original + incompatible, capability_id="future_agent.default"
        )
        self.assertEqual(plan.state, "rebaselining")
        self.assertEqual(plan.baseline_run_ids, [])
        self.assertEqual(plan.comparison_run_ids, [])

    def test_event_driven_detection_and_diagnostic_queue_are_idempotent(self) -> None:
        store = SystemLearningStore("demo")
        baseline = [
            self.make_run(
                index, tokens=100, capability_id="future_agent.default", capability_version="v1",
                change_marker="release-v1", quality_eval_profile="eval-v1",
            )
            for index in range(5)
        ]
        candidate = [
            self.make_run(
                100 + index, tokens=140, capability_id="future_agent.default", capability_version="v2",
                change_marker="release-v2", quality_eval_profile="eval-v1",
            )
            for index in range(5)
        ]
        for record in baseline + candidate:
            store.record_run(record)
        with (
            patch("control_plane.service.control_data_dir", return_value=self.root),
            patch("control_plane.service.project_lock", side_effect=lambda _project: nullcontext()),
            patch("control_plane.service.append_history"),
        ):
            first = store.process_capability("future_agent.default", queue_diagnosis=True)
            second = store.process_capability("future_agent.default", queue_diagnosis=True)
        self.assertTrue(first.signal_ids)
        self.assertEqual(first.signal_ids, second.signal_ids)
        self.assertEqual(first.queued_request_ids, second.queued_request_ids)
        self.assertEqual(len(first.queued_request_ids), len(first.signal_ids))

    def test_detector_failure_is_bounded_and_cannot_rewrite_final_run(self) -> None:
        store = SystemLearningStore("demo")
        record = self.make_run(
            1, capability_id="future_agent.default", capability_version="v1",
            change_marker="release-v1", quality_eval_profile="eval-v1",
        )
        with patch.object(store, "process_capability", side_effect=RuntimeError("detector unavailable")):
            stored = store.record_run(record)
        self.assertEqual(stored.outcome, "success")
        events = store._read("detection_events")
        self.assertEqual(len(events), 1)
        self.assertIn("detector unavailable", events[0]["detail"])

    @staticmethod
    def codex_history_cohorts(count: int = 5) -> list[dict[str, object]]:
        events: list[dict[str, object]] = []
        origin = datetime(2026, 8, 1, tzinfo=timezone.utc)
        for index in range(count):
            submitted = origin + timedelta(hours=index * 2)
            proposal_id = f"requirement-proposal-{index}"
            events.extend([
                {
                    "event_id": f"rs-{index}", "event_type": "pm_proposal_submitted",
                    "proposal_id": proposal_id, "proposal_revision": 1, "mode": "requirement_draft",
                    "source": "codex-mcp", "actor": "codex-pm", "origin_sdk_run_id": "",
                    "recorded_at": submitted.isoformat(),
                },
                {
                    "event_id": f"ra-{index}", "event_type": "pm_proposal_approved",
                    "proposal_id": proposal_id, "proposal_revision": 1, "mode": "requirement_draft",
                    "source": "codex-mcp", "actor": "product-director",
                    "recorded_at": (submitted + timedelta(minutes=4)).isoformat(),
                },
            ])
            request_id = f"task-request-{index}"
            task_proposal = f"task-proposal-{index}"
            events.extend([
                {
                    "event_id": f"tq-{index}", "event_type": "codex_work_requested",
                    "request_id": request_id, "request_kind": "pm_decision", "requested_role": "pm",
                    "source": "controller-autonomous", "recorded_at": (submitted + timedelta(minutes=5)).isoformat(),
                },
                {
                    "event_id": f"tc-{index}", "event_type": "codex_work_claimed",
                    "request_id": request_id, "requested_role": "pm", "actor": "codex",
                    "recorded_at": (submitted + timedelta(minutes=6)).isoformat(),
                },
                {
                    "event_id": f"ta-{index}", "event_type": "pm_derived_task_plan_auto_applied",
                    "origin_request_id": request_id, "proposal_id": task_proposal, "proposal_revision": 1,
                    "mode": "task_plan", "source": "codex-mcp", "actor": "codex-pm",
                    "origin_sdk_run_id": "", "recorded_at": (submitted + timedelta(minutes=9)).isoformat(),
                },
                {
                    "event_id": f"tr-{index}", "event_type": "codex_work_resolved",
                    "request_id": request_id, "status": "COMPLETED", "result_proposal_id": task_proposal,
                    "result_proposal_revision": 1, "recorded_at": (submitted + timedelta(minutes=9, seconds=1)).isoformat(),
                },
            ])
        return events

    @staticmethod
    def codex_quality_artifacts(count: int = 5) -> list[dict[str, object]]:
        artifacts: list[dict[str, object]] = []
        source_state = {
            "requirements_sha256": "requirements-v1",
            "tasks_sha256": "tasks-v1",
            "memory_sha256": "memory-v1",
            "history_event_id": "history-v1",
        }
        description = """Problem statement:
The workflow needs attributable quality evidence.

Target user:
OS maintainers.

Core job-to-be-done:
Evaluate exact typed artifacts.

Desired outcome:
Quality-controlled comparisons fail closed.

Success and acceptance evidence:
- Exact artifacts produce deterministic evidence.

Constraints:
- Approval contributes no score.

Out of scope:
- Model judging.

Assumptions:
- Typed artifacts are retained.

Open questions:
None."""
        for index in range(count):
            requirement_id = f"requirement-proposal-{index}"
            requirement = {
                "schema_version": "2026-07-19.pm.v2",
                "proposal_id": requirement_id,
                "proposal_revision": 1,
                "project_name": "demo",
                "mode": "requirement_draft",
                "status": "READY_FOR_APPROVAL",
                "next_action": "draft_requirement",
                "assistant_message": "The requirement is ready.",
                "source_state": source_state,
                "facts": ["The exact typed artifact is retained."],
                "evidence": ["Controller proposal record."],
                "assumptions": ["The deterministic dimensions are compatible."],
                "rationale": "Add attributable quality evidence.",
                "requirement_changes": [{
                    "action": "create", "requirement_id": f"R{index + 1}",
                    "title": "Quality evidence", "status": "IN_PROGRESS",
                    "priority": "HIGH", "effort": "M", "description": description,
                }],
                "approval_summary": "Approve the exact requirement artifact.",
            }
            artifacts.append({
                "proposal_id": requirement_id, "proposal_revision": 1,
                "project_name": "demo", "status": "APPROVED",
                "submitted_at": f"2026-08-01T{index:02d}:00:00+00:00",
                "proposal": requirement,
            })
            task_id = f"task-proposal-{index}"
            task = {
                "schema_version": "2026-07-19.pm.v2",
                "proposal_id": task_id,
                "proposal_revision": 1,
                "project_name": "demo",
                "mode": "task_plan",
                "status": "READY_FOR_APPROVAL",
                "next_action": "plan_tasks",
                "assistant_message": "The task plan is ready.",
                "source_state": source_state,
                "work_request": {
                    "schema_version": "2026-07-18.pm-work.v1", "mode": "task_plan",
                    "target_requirement_ids": [f"R{index + 1}"],
                    "operator_context": "Derive bounded tasks.",
                    "authorization_proposal_id": requirement_id,
                    "authorization_proposal_revision": 1,
                    "parent_proposal_id": "", "parent_proposal_revision": 0,
                },
                "facts": ["The approved requirement authorizes bounded planning."],
                "evidence": ["Exact requirement proposal authorization."],
                "assumptions": ["Task numbering is available."],
                "rationale": "Create bounded verifiable work.",
                "task_changes": [{
                    "action": "create", "task_number": index + 1, "title": "Evaluate quality",
                    "task_type": "Validation Task", "status": "TODO",
                    "requirement_ids": [f"R{index + 1}"],
                    "goal": "Prove attributable deterministic workflow quality.",
                    "requirements": ["Evaluate the exact artifact."],
                    "constraints": ["Do not infer quality from approval."],
                    "validation": ["The evidence is exact and reproducible."],
                }],
                "approval_summary": "Automatically apply the bounded task plan.",
            }
            artifacts.append({
                "proposal_id": task_id, "proposal_revision": 1,
                "project_name": "demo", "status": "AUTO_APPLIED",
                "submitted_at": f"2026-08-01T{index:02d}:09:00+00:00",
                "proposal": task,
            })
        return artifacts

    def test_codex_native_history_import_builds_two_real_cohorts_without_inventing_usage(self) -> None:
        events = self.codex_history_cohorts()
        artifacts = self.codex_quality_artifacts()
        first = import_codex_native_history("demo", events=events, artifacts=artifacts)
        second = import_codex_native_history("demo", events=events, artifacts=artifacts)
        self.assertEqual(first.capability_counts, {"pm.requirement_draft": 5, "pm.task_plan": 5})
        self.assertEqual(set(first.baseline_ids), {"pm.requirement_draft"})
        self.assertEqual(len(first.imported_run_ids), 10)
        self.assertEqual(second.imported_run_ids, [])
        self.assertEqual(len(second.existing_run_ids), 10)
        records = SystemLearningStore("demo").runs()
        self.assertTrue(all(item.observation_kind == "operational" for item in records))
        self.assertTrue(all(item.evidence_source == "canonical_codex_lifecycle" for item in records))
        self.assertTrue(all(item.input_tokens is None and "input_tokens" in item.unavailable_fields for item in records))
        self.assertTrue(all(item.model_requests is None and item.tool_calls is None for item in records))
        self.assertTrue(all(item.tool_result_size is None and item.retries is None for item in records))
        self.assertTrue(all(item.quality_score == 1.0 for item in records))
        self.assertTrue(all(item.eval_passed is True and item.guardrail_passed is True for item in records))
        self.assertTrue(all(item.quality_evidence and item.quality_evidence.status == "attributable" for item in records))
        requirement_baseline = SystemLearningStore("demo").baseline(role="PM", workflow_mode="requirement_draft")
        self.assertEqual(requirement_baseline.metrics["latency_seconds"].sample_count, 0)
        self.assertIn("latency_seconds", requirement_baseline.missing_metrics)
        self.assertIn("5 more compatible quality-controlled observations", first.below_threshold["pm.task_plan"])

    def test_codex_telemetry_audit_classifies_every_metric_once(self) -> None:
        requirement = codex_native_telemetry_capability_report("requirement_draft")
        task_plan = codex_native_telemetry_capability_report("task_plan")
        self.assertEqual({item.metric for item in requirement.assessments}, set(CODEX_TELEMETRY_METRICS))
        self.assertEqual(len(requirement.assessments), len(CODEX_TELEMETRY_METRICS))
        requirement_status = {item.metric: item.status for item in requirement.assessments}
        task_status = {item.metric: item.status for item in task_plan.assessments}
        self.assertEqual(requirement_status["latency.governance_wait"], "derived")
        self.assertEqual(requirement_status["latency.agent_execution"], "unavailable")
        self.assertEqual(task_status["latency.agent_execution"], "derived")
        self.assertEqual(task_status["latency.queue_wait"], "derived")
        self.assertEqual(task_status["input_tokens"], "unavailable")
        self.assertEqual(task_status["estimated_cost_usd"], "unavailable")

    def test_quality_profiles_classify_only_r100_compatible_structural_dimensions(self) -> None:
        requirement = pm_quality_profile("requirement_draft")
        task_plan = pm_quality_profile("task_plan")
        self.assertEqual(task_plan.compatibility_version, PM_QUALITY_COMPATIBILITY_VERSION)
        self.assertAlmostEqual(sum(item.weight for item in requirement.dimensions), 1.0)
        self.assertAlmostEqual(sum(item.weight for item in task_plan.dimensions), 1.0)
        self.assertIn("authorization_lineage", {item.dimension for item in task_plan.dimensions})
        report = codex_native_quality_capability_report("task_plan")
        statuses = {item.dimension: item.status for item in report.assessments}
        self.assertEqual(statuses["tool_choice"], "unavailable")
        self.assertEqual(statuses["specialist_and_trajectory_judgment"], "incompatible")
        self.assertEqual(statuses["subjective_product_strategy"], "unavailable")

    def test_exact_quality_artifact_is_deterministic_and_approval_status_contributes_no_score(self) -> None:
        artifact = self.codex_quality_artifacts(1)[1]
        first = evaluate_pm_quality_artifact(
            "demo", artifact, workflow_mode="task_plan",
            proposal_id="task-proposal-0", proposal_revision=1,
        )
        pending = deepcopy(artifact)
        pending["status"] = "PENDING_APPROVAL"
        second = evaluate_pm_quality_artifact(
            "demo", pending, workflow_mode="task_plan",
            proposal_id="task-proposal-0", proposal_revision=1,
        )
        self.assertEqual(first.quality_score, 1.0)
        self.assertEqual(first.quality_score, second.quality_score)
        self.assertEqual(first.deterministic_input_fingerprint, second.deterministic_input_fingerprint)
        self.assertTrue(first.eval_passed and first.guardrail_passed)

    def test_quality_evaluator_fails_closed_for_missing_cross_project_and_adversarial_artifacts(self) -> None:
        missing = evaluate_pm_quality_artifact(
            "demo", None, workflow_mode="task_plan",
            proposal_id="missing", proposal_revision=1,
        )
        self.assertEqual(missing.status, "unavailable")
        cross_project = deepcopy(self.codex_quality_artifacts(1)[1])
        cross_project["project_name"] = "another-project"
        incompatible = evaluate_pm_quality_artifact(
            "demo", cross_project, workflow_mode="task_plan",
            proposal_id="task-proposal-0", proposal_revision=1,
        )
        self.assertEqual(incompatible.status, "incompatible")
        adversarial = deepcopy(self.codex_quality_artifacts(1)[1])
        proposal = adversarial["proposal"]
        assert isinstance(proposal, dict)
        proposal["assumptions"] = list(proposal["facts"])
        degraded = evaluate_pm_quality_artifact(
            "demo", adversarial, workflow_mode="task_plan",
            proposal_id="task-proposal-0", proposal_revision=1,
        )
        self.assertEqual(degraded.status, "attributable")
        self.assertFalse(degraded.eval_passed)
        self.assertFalse(degraded.guardrail_passed)
        self.assertIn("evidence_classification_failed", degraded.findings)

    def test_ten_exact_task_plan_artifacts_enable_quality_windows_without_false_signal(self) -> None:
        report = import_codex_native_history(
            "demo", events=self.codex_history_cohorts(10), artifacts=self.codex_quality_artifacts(10)
        )
        store = SystemLearningStore("demo")
        task_records = store.runs(workflow_mode="task_plan")
        self.assertEqual(len(task_records), 10)
        self.assertTrue(all(item.quality_evidence and item.quality_evidence.status == "attributable" for item in task_records))
        self.assertEqual(report.quality_coverage["task_plan"]["attributable"], 10)
        self.assertIn("pm.task_plan", report.baseline_ids)
        self.assertEqual(store.baseline(role="PM", workflow_mode="task_plan").metrics["latency_seconds"].sample_count, 10)
        self.assertIn("Detected signals: 0", report.comparison_status["pm.task_plan"])
        self.assertEqual(store.signals(), [])

    def test_quality_compatibility_change_requires_separate_baseline(self) -> None:
        artifact = self.codex_quality_artifacts(1)[1]
        evidence = evaluate_pm_quality_artifact(
            "demo", artifact, workflow_mode="task_plan",
            proposal_id="task-proposal-0", proposal_revision=1,
        )
        first = self.make_run(1).model_copy(update={"quality_evidence": evidence})
        second_evidence = evidence.model_copy(update={
            "profile_version": "quality-v2", "compatibility_version": "quality-v2",
        })
        second = self.make_run(2).model_copy(update={"quality_evidence": second_evidence})
        with self.assertRaisesRegex(ValueError, "Incompatible quality evidence semantics"):
            build_workflow_baseline([first, second], role="PM", workflow_mode="task_plan")

    def test_codex_import_attaches_provenance_and_non_overlapping_latency_phases(self) -> None:
        report = import_codex_native_history("demo", events=self.codex_history_cohorts(1))
        records = {item.workflow_mode: item for item in SystemLearningStore("demo").runs()}
        requirement = records["requirement_draft"]
        task_plan = records["task_plan"]
        self.assertEqual(set(requirement.metric_evidence), set(CODEX_TELEMETRY_METRICS))
        self.assertEqual(requirement.latency_breakdown.governance_wait_seconds, 240.0)
        self.assertEqual(requirement.latency_breakdown.total_lifecycle_seconds, 240.0)
        self.assertIsNone(requirement.latency_breakdown.agent_execution_seconds)
        self.assertEqual(task_plan.latency_breakdown.queue_wait_seconds, 60.0)
        self.assertEqual(task_plan.latency_breakdown.agent_execution_seconds, 180.0)
        self.assertEqual(task_plan.latency_breakdown.controller_seconds, 1.0)
        self.assertEqual(task_plan.latency_breakdown.total_lifecycle_seconds, 241.0)
        self.assertEqual(task_plan.metric_evidence["input_tokens"].status, "unavailable")
        self.assertEqual(task_plan.metric_evidence["outcome"].status, "attributable")
        self.assertEqual(report.metric_coverage["task_plan"]["unavailable"], 21)

    def test_latency_and_unavailable_metric_evidence_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValidationError, "cannot overlap"):
            LatencyBreakdown(
                agent_execution_seconds=2,
                controller_seconds=2,
                total_lifecycle_seconds=3,
            )
        with self.assertRaisesRegex(ValidationError, "requires a reason"):
            MetricEvidence(status="unavailable", privacy_classification="unavailable")

    def test_ten_genuine_task_plan_runs_do_not_signal_without_numeric_quality_evidence(self) -> None:
        report = import_codex_native_history("demo", events=self.codex_history_cohorts(10))
        self.assertEqual(report.quality_coverage["task_plan"]["unavailable"], 10)
        self.assertNotIn("pm.task_plan", report.baseline_ids)
        self.assertIn("10 more compatible quality-controlled observations", report.below_threshold["pm.task_plan"])
        self.assertEqual(SystemLearningStore("demo").signals(), [])

    def test_codex_native_history_import_rejects_incomplete_and_cross_project_evidence(self) -> None:
        events = self.codex_history_cohorts(1)
        events = [item for item in events if item.get("event_type") != "codex_work_resolved"]
        events[0]["project_name"] = "another-project"
        report = import_codex_native_history("demo", events=events)
        self.assertEqual(report.imported_run_ids, [])
        self.assertEqual(report.rejected_candidates["cross_project_requirement_draft"], 1)
        self.assertEqual(report.rejected_candidates["incomplete_or_ambiguous_task_plan_sequence"], 1)
        self.assertEqual(report.baseline_ids, {})

    def test_codex_import_bounds_malformed_timing_and_ignores_private_payload_fields(self) -> None:
        events = self.codex_history_cohorts(1)
        events[0]["prompt"] = "private prompt content must not persist"
        events[1]["recorded_at"] = "not-a-timestamp"
        report = import_codex_native_history("demo", events=events)
        self.assertEqual(report.rejected_candidates["invalid_requirement_draft_telemetry"], 1)
        self.assertEqual(report.capability_counts["pm.requirement_draft"], 0)
        self.assertEqual(report.capability_counts["pm.task_plan"], 1)
        persisted = " ".join(item.model_dump_json() for item in SystemLearningStore("demo").runs())
        self.assertNotIn("private prompt content", persisted)

    def test_isolated_operational_proof_retains_learning_and_rebaselines_incompatible_change(self) -> None:
        with (
            patch("control_plane.service.control_data_dir", return_value=self.root),
            patch("control_plane.service.project_lock", side_effect=lambda _project: nullcontext()),
            patch("control_plane.service.append_history"),
        ):
            proof = run_isolated_operational_proof("demo", queue_diagnosis=True)
            replay = run_isolated_operational_proof("demo", queue_diagnosis=True)
        self.assertEqual(proof, replay)
        self.assertEqual(len(proof.queued_request_ids), 1)
        self.assertEqual(proof.experiment_status, "adopted")
        self.assertIn(proof.learning_id, proof.related_learning_ids)
        self.assertTrue(proof.post_monitoring_signal_ids)
        self.assertEqual(proof.incompatible_state, "rebaselining")
        operational = SystemLearningStore("demo")
        controlled = SystemLearningStore("demo", namespace="r109-controlled-v1")
        self.assertEqual(operational.runs(), [])
        self.assertTrue(all(item.observation_kind == "controlled_validation" for item in controlled.runs()))


if __name__ == "__main__":
    unittest.main()

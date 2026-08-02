from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = REPO_ROOT / "projects" / "os-control-panel"
for path in (PROJECT_ROOT / "src", PROJECT_ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from agents_runtime.registry import build_agent_registry  # noqa: E402
from app import _pm_model_configuration_status  # noqa: E402
from pm_behavioral_evals import grade_pm_behavior, load_pm_behavior_catalog  # noqa: E402
from pm_behavioral_eval_runner import run_pm_behavioral_evals  # noqa: E402
from pm_model_selection import (  # noqa: E402
    PMCandidateReport,
    PMModelConfiguration,
    build_campaign_manifest,
    candidate_report_from_behavior_report,
    load_pm_model_configuration,
    materialize_no_selection_configuration,
    materialize_selected_configuration,
    select_pm_model,
)
from pm_contract import PMDecisionEnvelope  # noqa: E402
from pm_failure_analysis import classify_campaign_failures  # noqa: E402
from pm_live_campaign import (  # noqa: E402
    AUTHORIZED_SCOPE,
    blocked_trial_observation,
    build_authorized_sentinel_manifest,
    campaign_accounting,
    estimate_standard_cost_usd,
    live_case,
    live_case_context,
    live_contract_fingerprint,
    load_live_contract,
    load_pricing_snapshot,
    trial_observation,
)
from agents_runtime.runner import StructuredAgentRunResult  # noqa: E402


CASES_FILE = PROJECT_ROOT / "evals" / "pm_behavioral_cases.json"


def awaiting_config() -> PMModelConfiguration:
    payload = load_pm_model_configuration().model_dump(mode="json")
    payload.update(
        {
            "status": "awaiting_live_evidence",
            "selection_report_id": "",
            "selected_at": "",
            "pricing_source_url": "",
            "pricing_observed_at": "",
        }
    )
    return PMModelConfiguration.model_validate(payload)


def report(
    candidate_id: str,
    model: str,
    effort: str,
    *,
    cost: float,
    latency: float = 2.0,
    mean_score: float = 100.0,
    critical_score: float = 100.0,
    complete: bool = True,
) -> PMCandidateReport:
    _, cases = load_pm_behavior_catalog(CASES_FILE)
    return PMCandidateReport(
        report_id=f"report-{candidate_id}",
        candidate_id=candidate_id,
        model=model,
        reasoning_effort=effort,
        dataset_version="pm-baseline-2026-07-22.v1",
        fingerprints={
            "dataset": "dataset-hash", "prompt": "prompt-hash", "tool_policy": "tools-hash",
            "guardrails": "guardrails-hash", "model": f"model-hash-{candidate_id}",
            "reasoning": f"reasoning-hash-{effort}", "live_contract": "live-contract-hash",
        },
        case_pass_rates={case.case_id: 1.0 for case in cases},
        dimension_scores={
            "typed_output": 100.0, "evidence_use": 100.0, "tool_choice": 100.0,
            "consultations": 100.0, "approval_behavior": critical_score,
            "guardrail_response": critical_score, "trace_trajectory": 100.0,
            "canonical_outcome": critical_score,
        },
        overall_pass_rate=1.0,
        mean_score=mean_score,
        trial_count=48,
        successful_trials=48,
        input_tokens=4800,
        output_tokens=1200,
        reported_cost_usd=cost,
        latencies_seconds=[latency] * 48,
        pricing_source_url="https://openai.com/api/pricing/",
        pricing_observed_at="2026-07-22",
        complete=complete,
    )


class PMModelSelectionTests(unittest.TestCase):
    def test_configuration_records_no_selection_and_separates_codex_billing(self) -> None:
        config = load_pm_model_configuration()

        self.assertEqual(config.status, "no_selection")
        self.assertEqual(config.effective.model, "gpt-5-mini")
        self.assertEqual(config.effective, config.rollback)
        self.assertEqual(
            config.selection_report_id,
            "r101-remediated-sentinel-2026-07-30-v1",
        )
        self.assertEqual(config.codex_native.billing_boundary, "codex_plan_or_credits")
        self.assertFalse(config.codex_native.exact_token_counts_available)
        self.assertEqual(sum(item.kind == "baseline" for item in config.candidates), 1)

    def test_configuration_rejects_unknown_models_and_weakened_thresholds(self) -> None:
        raw = load_pm_model_configuration().model_dump(mode="json")
        invalid_model = deepcopy(raw)
        invalid_model["candidates"][1]["model"] = "unapproved-model"
        with self.assertRaisesRegex(ValueError, "Unsupported PM model"):
            PMModelConfiguration.model_validate(invalid_model)

        weak = deepcopy(raw)
        weak["thresholds"]["minimum_cost_reduction"] = 0.01
        with self.assertRaises(ValueError):
            PMModelConfiguration.model_validate(weak)

    def test_registry_uses_central_pm_configuration_and_preserves_explicit_test_model(self) -> None:
        registry = build_agent_registry()

        self.assertEqual(registry["pm"].model, "gpt-5-mini")
        self.assertEqual(registry["pm"].model_settings.reasoning.effort, "medium")
        self.assertEqual(registry["qa"].model, "gpt-5-mini")

        explicit = build_agent_registry("scripted-model")
        self.assertEqual(explicit["pm"].model, "scripted-model")
        self.assertIsNone(explicit["pm"].model_settings.reasoning)

        status = _pm_model_configuration_status()
        self.assertEqual(status["model"], "gpt-5-mini")
        self.assertEqual(status["rollback_model"], "gpt-5-mini")
        self.assertIn("Codex plan or credits", status["codex_billing"])

    def test_sentinel_and_full_manifests_are_bounded_stable_and_unauthorized(self) -> None:
        config = load_pm_model_configuration()
        _, cases = load_pm_behavior_catalog(CASES_FILE)

        sentinel = build_campaign_manifest(
            config, cases=list(cases), dataset_fingerprint="dataset-hash"
        )
        full = build_campaign_manifest(
            config,
            cases=list(cases),
            dataset_fingerprint="dataset-hash",
            stage="full",
            qualifying_candidate_ids=["terra-medium"],
        )

        self.assertFalse(sentinel["authorized"])
        self.assertEqual(len(sentinel["work"]), 20)
        self.assertEqual(len(full["work"]), 96)
        self.assertEqual(
            {item["candidate_id"] for item in full["work"]},
            {"sol-medium", "terra-medium"},
        )
        self.assertEqual(len({item["work_id"] for item in full["work"]}), 96)
        with self.assertRaisesRegex(ValueError, "unknown candidate"):
            build_campaign_manifest(
                config,
                cases=list(cases),
                dataset_fingerprint="dataset-hash",
                stage="full",
                qualifying_candidate_ids=["invented"],
            )

    def test_authorized_sentinel_is_exactly_bounded_and_uses_current_pricing_snapshot(self) -> None:
        config = awaiting_config()
        _, cases = load_pm_behavior_catalog(CASES_FILE)

        manifest = build_authorized_sentinel_manifest(config, list(cases))
        pricing = load_pricing_snapshot()
        contract = load_live_contract()

        self.assertTrue(manifest["authorized"])
        self.assertEqual(manifest["authorization_scope"], AUTHORIZED_SCOPE)
        self.assertEqual(len(manifest["work"]), 20)
        self.assertEqual(manifest["live_contract_version"], contract["contract_version"])
        self.assertEqual(manifest["live_contract_fingerprint"], live_contract_fingerprint())
        self.assertFalse(manifest["retry_policy"]["automatic_retries"])
        self.assertEqual(
            manifest["finite_exit_policy"]["maximum_additional_remediated_sentinels"],
            1,
        )
        self.assertEqual(
            manifest["retry_policy"]["failed_work_item_retry"],
            "new_batch_and_new_explicit_authorization_required",
        )
        self.assertEqual(pricing["observed_at"], "2026-07-30")
        self.assertEqual(
            estimate_standard_cost_usd(
                "gpt-5.6-sol",
                {
                    "input_tokens": 1_000_000,
                    "cached_input_tokens": 100_000,
                    "cache_write_tokens": 100_000,
                    "output_tokens": 100_000,
                },
                pricing,
            ),
            7.675,
        )

    def test_live_contract_adapts_production_tools_without_mutating_r100_cases(self) -> None:
        contract = load_live_contract()
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        case = next(item for item in cases if item.case_id == "pm-prompt-injection-treated-as-data")
        original_allowed = list(case.expectations["tool_choice"]["allowed"])

        adapted = live_case(case, contract)
        observation = deepcopy(adapted.mock_trial)
        observation["tool_choice"]["tools"] = [
            "read_requirements",
            "read_tasks",
            "read_project_memory",
            "read_project_summary",
            "read_pm_evidence",
            "get_pm_review_evidence",
            "preflight_pm_decision",
        ]

        self.assertEqual(case.expectations["tool_choice"]["allowed"], original_allowed)
        self.assertNotIn("read_project_summary", original_allowed)
        self.assertTrue(grade_pm_behavior(adapted, observation).passed)
        self.assertEqual(
            contract["case_context"][case.case_id]["artifact_id"],
            "eval-artifact-prompt-injection-001",
        )
        self.assertEqual(
            contract["finite_exit_policy"]["maximum_additional_remediated_sentinels"],
            1,
        )
        self.assertEqual(
            contract["case_context"][case.case_id]["review_evidence"]["target_id"],
            "eval-artifact-prompt-injection-001",
        )
        prompt_context = live_case_context(adapted, contract)
        self.assertIn("eval-artifact-prompt-injection-001", prompt_context)
        self.assertNotIn("review_evidence", prompt_context)
        self.assertNotIn("Synthetic prompt-injection artifact", prompt_context)

    def test_live_contract_grades_equivalent_safe_handback_actions(self) -> None:
        contract = load_live_contract()
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        source = next(
            item for item in cases if item.case_id == "pm-ownership-concurrency-ambiguity"
        )
        adapted = live_case(source, contract)

        for action in ("ask_question", "request_clarification"):
            observation = deepcopy(source.mock_trial)
            observation["typed_output"]["next_action"] = action
            self.assertTrue(grade_pm_behavior(adapted, observation).passed)

    def test_failure_classifier_preserves_mixed_model_failures(self) -> None:
        contract = load_live_contract()
        campaign = {
            "batch_id": "sentinel-test",
            "manifest": {"live_contract_version": "pm-live-production-2026-07-30.v1"},
            "attempts": [
                {
                    "candidate_id": "sol-medium",
                    "case_id": "pm-prompt-injection-treated-as-data",
                    "observation": {"typed_output": {"next_action": "ask_question"}},
                    "grade": {
                        "dimensions": [
                            {
                                "dimension": "typed_output",
                                "passed": False,
                                "failures": ["unexpected_status"],
                            }
                        ]
                    },
                },
                {
                    "candidate_id": "terra-medium",
                    "case_id": "pm-ownership-concurrency-ambiguity",
                    "observation": {"typed_output": {"next_action": "ask_question"}},
                    "grade": {
                        "dimensions": [
                            {
                                "dimension": "typed_output",
                                "passed": False,
                                "failures": ["unexpected_next_action"],
                            }
                        ]
                    },
                },
                {
                    "candidate_id": "terra-low",
                    "case_id": "pm-ownership-concurrency-ambiguity",
                    "observation": {"typed_output": {"next_action": "ask_question"}},
                    "grade": {
                        "dimensions": [
                            {
                                "dimension": "typed_output",
                                "passed": False,
                                "failures": [
                                    "unexpected_next_action",
                                    "missing_field:assumptions",
                                ],
                            }
                        ]
                    },
                },
            ],
        }

        matrix = classify_campaign_failures(campaign, contract)

        self.assertEqual(
            matrix["summary"],
            {
                "failed_dimensions": 3,
                "classifications": {
                    "fixture": 1,
                    "grader": 1,
                    "model_behavior": 1,
                },
            },
        )
        self.assertNotIn("observation", matrix["records"][0])
        self.assertNotIn("trace_id", matrix["records"][0])

        current = deepcopy(campaign)
        current["manifest"]["live_contract_version"] = contract["contract_version"]
        current_matrix = classify_campaign_failures(current, contract)
        self.assertEqual(
            current_matrix["summary"]["classifications"],
            {"model_behavior": 3},
        )

    def test_campaign_accounting_separates_attempts_responses_trials_and_billing(self) -> None:
        attempts = [
            {
                "accounting": {
                    "transport_attempts": 1,
                    "provider_responses": 0,
                    "completed_evaluation_trials": 0,
                    "billable_model_requests": 0,
                }
            },
            {
                "accounting": {
                    "transport_attempts": 1,
                    "provider_responses": 2,
                    "completed_evaluation_trials": 1,
                    "billable_model_requests": 2,
                }
            },
        ]

        self.assertEqual(
            campaign_accounting(attempts, [attempts[1]]),
            {
                "transport_attempts": 2,
                "provider_responses": 2,
                "completed_evaluation_trials": 1,
                "billable_model_requests": 2,
            },
        )

    def test_live_trial_observation_is_derived_from_typed_output_and_sdk_metadata(self) -> None:
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        case = next(item for item in cases if item.case_id == "pm-vague-discovery-needs-input")
        decision = PMDecisionEnvelope(
            project_name="os-control-panel",
            mode="discovery",
            status="NEEDS_INPUT",
            next_action="ask_question",
            assistant_message="Which team and outcome should this focus on?",
            facts=["The request does not identify a team."],
            evidence=["requirements.md"],
            assumptions=["The request may concern an internal team."],
            open_questions=["Which team needs help?"],
        )
        metadata = StructuredAgentRunResult(
            output=decision,
            run_id="run-1",
            trace_id="trace-1",
            model="gpt-5.6-sol",
            usage={"input_tokens": 10, "output_tokens": 5},
            latency_seconds=1.0,
            tools=("read_requirements", "read_tasks", "read_project_memory"),
            guardrails=(),
        )

        observation = trial_observation(case, decision, metadata)

        self.assertEqual(observation["approval_behavior"]["action"], "none")
        self.assertEqual(observation["canonical_outcome"]["outcome"], "unchanged")
        self.assertEqual(observation["trace_trajectory"]["events"][-1], "human_hand_back")
        self.assertEqual(
            observation["tool_choice"]["tools"],
            ["read_requirements", "read_tasks", "read_project_memory"],
        )

    def test_input_blocked_prompt_injection_is_recorded_as_a_failed_sentinel(self) -> None:
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        case = next(item for item in cases if item.case_id == "pm-prompt-injection-treated-as-data")

        observation = blocked_trial_observation(case, "input_guardrail_blocked")

        self.assertIn("prompt_injection_blocked", observation["guardrail_response"]["codes"])
        self.assertFalse(grade_pm_behavior(case, observation).passed)

    def test_selection_chooses_least_costly_qualifying_candidate(self) -> None:
        config = awaiting_config()
        reports = [
            report("sol-medium", "gpt-5.6-sol", "medium", cost=10.0),
            report("terra-medium", "gpt-5.6-terra", "medium", cost=7.0, latency=2.1),
            report("luna-low", "gpt-5.6-luna", "low", cost=5.0, critical_score=80.0),
        ]

        decision = select_pm_model(config, reports, case_count=16)

        self.assertEqual(decision.selected_candidate_id, "terra-medium")
        self.assertFalse(decision.retained_baseline)
        self.assertIn("critical_dimension_failed:approval_behavior", decision.rejected["luna-low"])
        selected = materialize_selected_configuration(config, decision, reports)
        self.assertEqual(selected.status, "selected")
        self.assertEqual(selected.effective.model, "gpt-5.6-terra")
        self.assertEqual(selected.rollback.model, "gpt-5-mini")
        self.assertEqual(selected.selection_report_id, "report-terra-medium")

    def test_agents_sdk_behavior_report_converts_with_provider_telemetry(self) -> None:
        config = awaiting_config()
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        records = [
            {"case_id": case.case_id, "trial": case.mock_trial}
            for case in cases
            for _ in range(3)
        ]
        behavior = run_pm_behavioral_evals(
            backend="agents-sdk",
            model_label="gpt-5.6-sol",
            live=True,
            billing_acknowledged=True,
            trial_records=records,
        )
        behavior["fingerprints"]["reasoning"] = "sol-medium-reasoning"
        behavior["fingerprints"]["live_contract"] = live_contract_fingerprint()
        converted = candidate_report_from_behavior_report(
            config,
            behavior,
            report_id="authorized-sol-report",
            candidate_id="sol-medium",
            input_tokens=4800,
            output_tokens=1200,
            reported_cost_usd=10.0,
            latencies_seconds=[2.0] * 48,
            pricing_source_url="https://openai.com/api/pricing/",
            pricing_observed_at="2026-07-22",
        )

        self.assertTrue(converted.complete)
        self.assertEqual(converted.trial_count, 48)
        self.assertEqual(converted.dimension_scores["approval_behavior"], 100)
        self.assertEqual(converted.cost_per_successful_trial, 10.0 / 48)

    def test_selection_retains_baseline_for_cost_latency_or_quality_failure(self) -> None:
        config = awaiting_config()
        reports = [
            report("sol-medium", "gpt-5.6-sol", "medium", cost=10.0),
            report("terra-medium", "gpt-5.6-terra", "medium", cost=8.5),
            report("luna-medium", "gpt-5.6-luna", "medium", cost=6.0, latency=2.5),
            report("luna-low", "gpt-5.6-luna", "low", cost=6.0, mean_score=95.0),
        ]

        decision = select_pm_model(config, reports, case_count=16)

        self.assertTrue(decision.retained_baseline)
        self.assertIn("cost_reduction_below_threshold", decision.rejected["terra-medium"])
        self.assertIn("latency_regression_above_threshold", decision.rejected["luna-medium"])
        self.assertIn("mean_score_regression", decision.rejected["luna-low"])

        stale = report("terra-low", "gpt-5.6-terra", "low", cost=6.0)
        stale.fingerprints["prompt"] = "different-prompt"
        stale_decision = select_pm_model(
            config,
            [reports[0], stale],
            case_count=16,
        )
        self.assertIn("fingerprint_mismatch:prompt", stale_decision.rejected["terra-low"])

    def test_selection_fails_closed_for_missing_or_incomplete_baseline_evidence(self) -> None:
        config = awaiting_config()
        with self.assertRaisesRegex(ValueError, "baseline report"):
            select_pm_model(config, [], case_count=16)
        with self.assertRaisesRegex(ValueError, "incomplete_trial_set"):
            select_pm_model(
                config,
                [report("sol-medium", "gpt-5.6-sol", "medium", cost=10.0, complete=False)],
                case_count=16,
            )

    def test_no_selection_closure_retains_fallback_and_blocks_further_sentinels(self) -> None:
        closed = materialize_no_selection_configuration(
            awaiting_config(),
            report_id="sentinel-no-selection",
            decided_at="2026-07-30T18:38:24+00:00",
            pricing_source_url="https://developers.openai.com/api/docs/pricing",
            pricing_observed_at="2026-07-30",
        )
        _, cases = load_pm_behavior_catalog(CASES_FILE)

        self.assertEqual(closed.status, "no_selection")
        self.assertEqual(closed.effective, closed.rollback)
        with self.assertRaisesRegex(ValueError, "no further sentinel"):
            build_authorized_sentinel_manifest(closed, list(cases))


if __name__ == "__main__":
    unittest.main()

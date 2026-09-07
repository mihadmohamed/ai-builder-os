from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from pydantic import ValidationError

import context_attribution
from agents_runtime.hooks import OSRunHooks
from context_attribution import (
    CONTEXT_ATTRIBUTION_VERSION,
    ContextAttributionStore,
    ContextContribution,
    aggregate_contributions,
    compare_context_windows,
    context_attribution_capability_report,
    extract_named_contributions,
    measured_contribution,
    record_mcp_result_contribution,
    unavailable_host_context,
)


class ContextAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.data_patch = patch.object(
            context_attribution, "control_data_dir", lambda project: self.root / project
        )
        self.lock_patch = patch.object(context_attribution, "project_lock")
        self.data_patch.start()
        lock = self.lock_patch.start()
        lock.return_value.__enter__.return_value = None
        lock.return_value.__exit__.return_value = False

    def tearDown(self) -> None:
        self.lock_patch.stop()
        self.data_patch.stop()
        self.temporary.cleanup()

    def test_character_and_byte_measurements_keep_units_and_omit_content(self) -> None:
        secret = "private-£"
        characters = measured_contribution(
            "requirements_context", secret, source="test", unit="characters"
        )
        byte_count = measured_contribution(
            "requirements_context", secret, source="test", unit="bytes"
        )

        self.assertEqual(characters.value, len(secret))
        self.assertEqual(byte_count.value, len(secret.encode("utf-8")))
        self.assertNotEqual(characters.unit, byte_count.unit)
        self.assertNotIn(secret, str(characters.model_dump(mode="json")))

    def test_unavailable_host_context_is_explicit_and_cannot_claim_a_value(self) -> None:
        unavailable = unavailable_host_context(workflow_identity={"run_id": "run-1"})
        self.assertIsNone(unavailable.value)
        self.assertEqual(unavailable.evidence_class, "unavailable")
        self.assertEqual(unavailable.completeness, "unknown_host_context")
        with self.assertRaises(ValidationError):
            ContextContribution(
                contribution_id="invalid",
                category="other",
                value=0,
                unit="tokens",
                evidence_class="unavailable",
                completeness="unknown_host_context",
                privacy_classification="unavailable",
                limitation="not observable",
            )

    def test_named_context_extraction_is_bounded_to_known_categories(self) -> None:
        secret = "sensitive requirement content"
        contributions = extract_named_contributions(
            {
                "requirements": [secret],
                "nested": '{"tasks":["T1"],"memory":"decision"}',
                "rules": "rule",
                "workflow_state": {"phase": "implementation"},
                "specialist_result": "review",
                "unrelated": "ignored",
            },
            source="test-packet",
            workflow_identity={"run_id": "run-1"},
        )
        self.assertEqual(
            {item.category for item in contributions},
            {
                "requirements_context",
                "tasks_context",
                "memory_context",
                "rules_context",
                "active_workflow_context",
                "specialist_results",
            },
        )
        self.assertNotIn(secret, str([item.model_dump(mode="json") for item in contributions]))

    def test_aggregation_deduplicates_stable_contributions(self) -> None:
        item = measured_contribution("tasks_context", ["T1"], source="packet")
        self.assertEqual(
            aggregate_contributions([item, item], unit="characters"),
            {"tasks_context": float(item.value)},
        )

    def test_window_comparison_requires_compatible_versions_and_units(self) -> None:
        baseline = measured_contribution("memory_context", "1234", source="packet")
        candidate = measured_contribution("memory_context", "12", source="packet")
        comparison = compare_context_windows({"a": [baseline]}, {"b": [candidate]})
        self.assertTrue(comparison.compatible)
        self.assertEqual(comparison.changes_percent["memory_context"], -50.0)

        different_unit = measured_contribution(
            "memory_context", "12", source="packet", unit="bytes"
        )
        self.assertFalse(
            compare_context_windows({"a": [baseline]}, {"b": [different_unit]}).compatible
        )
        incompatible_version = candidate.model_copy(
            update={"attribution_version": "future-context-contract"}
        )
        self.assertFalse(
            compare_context_windows({"a": [baseline]}, {"b": [incompatible_version]}).compatible
        )

    def test_capability_report_distinguishes_sdk_and_codex_boundaries(self) -> None:
        sdk = context_attribution_capability_report("openai_agents_sdk")
        codex = context_attribution_capability_report("codex_native")
        sdk_by_category = {item.category: item for item in sdk.assessments}
        codex_by_category = {item.category: item for item in codex.assessments}
        self.assertEqual(sdk_by_category["session_context"].availability, "available")
        self.assertEqual(
            sdk_by_category["requirements_context"].availability, "available_when_supplied"
        )
        self.assertEqual(codex_by_category["session_context"].evidence_class, "unavailable")
        self.assertEqual(codex_by_category["tool_results"].unit, "bytes")

    def test_store_is_idempotent_immutable_and_privacy_safe(self) -> None:
        contribution = measured_contribution(
            "rules_context", "private rule", source="test", workflow_identity={"run_id": "r1"}
        )
        store = ContextAttributionStore("demo")
        self.assertTrue(store.record(contribution))
        self.assertFalse(store.record(contribution))
        conflict = contribution.model_copy(update={"value": int(contribution.value or 0) + 1})
        with self.assertRaisesRegex(ValueError, "Immutable context contribution"):
            store.record(conflict)
        self.assertEqual(store.for_run_ids(["r1"]), [contribution])
        self.assertNotIn("private rule", store.path.read_text(encoding="utf-8"))

    def test_mcp_result_records_named_and_total_sizes_without_raw_content(self) -> None:
        secret = "do-not-retain"
        record_mcp_result_contribution(
            "demo",
            "inspect_project",
            {"requirements": [secret], "status": "ok"},
            workflow_identity={"request_id": "request-1"},
        )
        records = ContextAttributionStore("demo").records()
        self.assertEqual(
            {item.category for item in records}, {"tool_results", "requirements_context"}
        )
        self.assertTrue(all(item.attribution_version == CONTEXT_ATTRIBUTION_VERSION for item in records))
        self.assertNotIn(secret, ContextAttributionStore("demo").path.read_text(encoding="utf-8"))


class SDKContextAttributionHookTests(unittest.IsolatedAsyncioTestCase):
    async def test_llm_hook_populates_project_context_and_emits_safe_contributions(self) -> None:
        secret = "requirement body"
        requirement = measured_contribution(
            "requirements_context", secret, source="runtime-input"
        )
        context = SimpleNamespace(context={
            "project_name": "demo",
            "run_id": "run-1",
            "trace_id": "trace-1",
            "context_contributions": [requirement.model_dump(mode="json")],
        })
        agent = SimpleNamespace(name="PM")
        with patch("agents_runtime.hooks.append_agent_trace") as append_trace:
            await OSRunHooks().on_llm_start(context, agent, "system", [{"role": "user"}])

        event = append_trace.call_args.args[1]
        self.assertEqual(event["project_context_size"], requirement.value)
        self.assertEqual(context.context["project_context_size"], requirement.value)
        self.assertIn("requirements_context", str(event["context_contributions"]))
        self.assertNotIn(secret, str(event))

    async def test_tool_hook_records_sizes_but_not_raw_output(self) -> None:
        context = SimpleNamespace(context={
            "project_name": "demo", "run_id": "run-1", "trace_id": "trace-1"
        })
        agent = SimpleNamespace(name="PM")
        tool = SimpleNamespace(name="inspect_project")
        secret = "private tool output"
        with patch("agents_runtime.hooks.append_agent_trace") as append_trace:
            await OSRunHooks().on_tool_end(context, agent, tool, secret)

        event = append_trace.call_args.args[1]
        self.assertEqual(event["output_chars"], len(secret))
        self.assertEqual(event["output_bytes"], len(secret.encode("utf-8")))
        self.assertNotIn(secret, str(event))


if __name__ == "__main__":
    unittest.main()

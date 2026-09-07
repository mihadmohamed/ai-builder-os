from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import codex_telemetry
from codex_telemetry import (
    CodexTelemetryStore,
    ingest_codex_local_session,
    ingest_codex_otel,
    summarize_correlated_telemetry,
)


class CodexTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.data_patch = patch.object(codex_telemetry, "control_data_dir", lambda project: self.root / project)
        self.lock_patch = patch.object(codex_telemetry, "project_lock")
        self.data_patch.start()
        lock = self.lock_patch.start()
        lock.return_value.__enter__.return_value = None
        lock.return_value.__exit__.return_value = False
        self.now = datetime(2026, 8, 23, 21, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.lock_patch.stop()
        self.data_patch.stop()
        self.temporary.cleanup()

    @staticmethod
    def otel_event(name: str, *, event_id: str = "evt-1", attributes: dict | None = None) -> dict:
        return {
            "event_name": name,
            "event_id": event_id,
            "timestamp": "2026-08-23T20:59:00+00:00",
            "attributes": {
                "app.version": "0.134.0",
                "ai_builder_os.project": "demo",
                "ai_builder_os.work_request_id": "work-1",
                **(attributes or {}),
            },
        }

    def test_otel_ingestion_is_attributable_correlated_and_idempotent(self) -> None:
        payload = [
            self.otel_event("codex.conversation_starts", attributes={"model": "gpt-test", "reasoning_effort": "medium"}),
            self.otel_event(
                "codex.tool_result", event_id="evt-2",
                attributes={"mcp_server": "ai_builder_os", "mcp_tool": "get_next_action", "success": True, "duration_ms": 12},
            ),
            self.otel_event("codex.api_request", event_id="evt-3", attributes={"attempt": 1, "success": True}),
        ]
        first = ingest_codex_otel("demo", payload, now=self.now)
        second = ingest_codex_otel("demo", payload, now=self.now)
        self.assertEqual(len(first.accepted_ids), 3)
        self.assertEqual(second.accepted_ids, [])
        self.assertEqual(len(second.duplicate_ids), 3)
        records = CodexTelemetryStore("demo").records()
        self.assertTrue(all(item.evidence_class == "attributable" for item in records))
        self.assertTrue(all(item.correlation.status == "correlated" for item in records))
        tool = next(item for item in records if item.event_name == "codex.tool_result")
        self.assertEqual((tool.mcp_server, tool.tool_name), ("ai_builder_os", "get_next_action"))
        summary = summarize_correlated_telemetry("demo", work_request_id="work-1")
        self.assertEqual(summary.metric_values["model"], "gpt-test")
        self.assertEqual(summary.metric_values["tool_calls"], 1.0)
        self.assertEqual(summary.metric_values["model_requests"], 1.0)

    def test_otel_omits_raw_prompt_arguments_and_output(self) -> None:
        secret = "PRIVATE-CONTENT-SHOULD-NOT-PERSIST"
        payload = [self.otel_event(
            "codex.tool_result",
            attributes={
                "tool": "shell", "success": True, "prompt": secret,
                "arguments": secret, "output_snippet": secret, "output_size": 42,
            },
        )]
        result = ingest_codex_otel("demo", payload, now=self.now)
        self.assertEqual(len(result.accepted_ids), 1)
        stored = (self.root / "demo" / "system_learning" / "codex_telemetry.json").read_text()
        self.assertNotIn(secret, stored)
        record = CodexTelemetryStore("demo").records()[0]
        self.assertEqual(record.metric_values["tool_result_observed_characters"], 42)
        self.assertEqual(len(record.context_contributions), 1)
        contribution = record.context_contributions[0]
        self.assertEqual(contribution.category, "tool_results")
        self.assertEqual((contribution.value, contribution.unit), (42, "characters"))
        summary = summarize_correlated_telemetry("demo", work_request_id="work-1")
        self.assertTrue(any(item.evidence_class == "unavailable" for item in summary.context_contributions))

    def test_standard_otlp_json_log_shape_is_supported(self) -> None:
        payload = {
            "resourceLogs": [{
                "resource": {"attributes": [
                    {"key": "app.version", "value": {"stringValue": "0.134.0"}},
                    {"key": "ai_builder_os.project", "value": {"stringValue": "demo"}},
                    {"key": "ai_builder_os.work_request_id", "value": {"stringValue": "work-1"}},
                ]},
                "scopeLogs": [{"logRecords": [{
                    "timeUnixNano": "1787518740000000000",
                    "body": {"stringValue": "codex.tool_result"},
                    "attributes": [
                        {"key": "event_id", "value": {"stringValue": "otel-1"}},
                        {"key": "tool", "value": {"stringValue": "apply_patch"}},
                        {"key": "success", "value": {"boolValue": True}},
                    ],
                }]}],
            }],
        }
        result = ingest_codex_otel("demo", payload, now=self.now)
        self.assertEqual(len(result.accepted_ids), 1)
        self.assertEqual(CodexTelemetryStore("demo").records()[0].tool_name, "apply_patch")

    def test_otel_unknown_malformed_cross_project_and_stale_are_quarantined(self) -> None:
        unknown = self.otel_event("codex.future_unknown")
        malformed = self.otel_event("codex.tool_result", event_id="bad-time")
        malformed["timestamp"] = "not-a-time"
        cross_project = self.otel_event(
            "codex.tool_result", event_id="cross",
            attributes={"ai_builder_os.project": "different"},
        )
        stale = self.otel_event("codex.tool_result", event_id="stale")
        stale["timestamp"] = "2026-01-01T00:00:00+00:00"
        result = ingest_codex_otel("demo", [unknown, malformed, cross_project, stale], now=self.now)
        self.assertEqual(result.accepted_ids, [])
        self.assertEqual(len(result.quarantined_ids), 4)
        reasons = {item.reason for item in CodexTelemetryStore("demo").quarantined()}
        self.assertEqual(
            reasons,
            {"unsupported_event_type", "missing_or_malformed_timestamp", "cross_project_identity", "stale_event"},
        )

    def test_otel_normalization_errors_and_repeated_quarantine_never_raise(self) -> None:
        invalid_revision = self.otel_event(
            "codex.tool_result", attributes={"ai_builder_os.proposal_revision": "not-an-integer"}
        )
        negative_duration = self.otel_event(
            "codex.tool_result", event_id="negative", attributes={"duration_ms": -1}
        )
        first = ingest_codex_otel("demo", [invalid_revision, negative_duration], now=self.now)
        second = ingest_codex_otel("demo", [invalid_revision, negative_duration], now=self.now)
        self.assertEqual(first.accepted_ids, [])
        self.assertEqual(len(first.quarantined_ids), 2)
        self.assertEqual(second.accepted_ids, [])
        self.assertEqual(len(second.quarantined_ids), 2)
        self.assertEqual(
            {item.reason for item in CodexTelemetryStore("demo").quarantined()},
            {"normalization_error"},
        )

    def test_timestamp_only_otel_is_never_silently_correlated(self) -> None:
        event = self.otel_event("codex.tool_result", attributes={"tool": "shell"})
        event["attributes"].pop("ai_builder_os.project")
        event["attributes"].pop("ai_builder_os.work_request_id")
        ingest_codex_otel("demo", [event], now=self.now)
        record = CodexTelemetryStore("demo").records()[0]
        self.assertEqual(record.correlation.status, "uncorrelated")
        self.assertEqual(record.project_name, "")

    def test_disabled_otel_adapter_writes_nothing(self) -> None:
        result = ingest_codex_otel("demo", [self.otel_event("codex.tool_result")], enabled=False)
        self.assertEqual(result.availability, "disabled")
        self.assertEqual(CodexTelemetryStore("demo").records(), [])

    @staticmethod
    def local_records() -> list[dict]:
        return [
            {
                "timestamp": "2026-08-23T20:58:00+00:00", "type": "session_meta",
                "payload": {"cli_version": "0.134.0", "session_id": "session-1", "model_provider": "openai"},
            },
            {
                "timestamp": "2026-08-23T20:58:01+00:00", "type": "turn_context",
                "payload": {"turn_id": "turn-1", "model": "gpt-test", "effort": "high"},
            },
            {
                "timestamp": "2026-08-23T20:58:02+00:00", "type": "event_msg",
                "payload": {"type": "token_count", "info": {
                    "model_context_window": 100000,
                    "last_token_usage": {
                        "input_tokens": 1000, "cached_input_tokens": 400,
                        "cache_write_input_tokens": 50, "output_tokens": 100,
                        "reasoning_output_tokens": 25, "total_tokens": 1125,
                    },
                }},
            },
            {
                "timestamp": "2026-08-23T20:58:03+00:00", "type": "response_item",
                "payload": {"type": "message", "content": "raw content must be ignored"},
            },
        ]

    def test_local_adapter_imports_only_numeric_metadata_as_experimental(self) -> None:
        result = ingest_codex_local_session("demo", self.local_records())
        self.assertEqual(len(result.accepted_ids), 3)
        self.assertEqual(result.ignored_count, 1)
        records = CodexTelemetryStore("demo").records()
        self.assertTrue(all(item.evidence_class == "experimental" for item in records))
        self.assertTrue(all(item.correlation.status == "uncorrelated" for item in records))
        usage = next(item for item in records if item.event_name == "codex.local.token_count")
        self.assertEqual(usage.metric_values["cached_input_tokens"], 400)
        self.assertEqual(usage.metric_values["cache_write_tokens"], 50)
        stored = (self.root / "demo" / "system_learning" / "codex_telemetry.json").read_text()
        self.assertNotIn("raw content must be ignored", stored)

    def test_local_adapter_quarantines_incompatible_or_unapproved_schema(self) -> None:
        incompatible = self.local_records()[2]
        del incompatible["payload"]["info"]["last_token_usage"]["cached_input_tokens"]
        first = ingest_codex_local_session("demo", [incompatible])
        self.assertEqual(first.accepted_ids, [])
        self.assertEqual(len(first.quarantined_ids), 1)
        second = ingest_codex_local_session(
            "demo-two", self.local_records()[:1], accepted_fingerprints={"different-fingerprint"}
        )
        self.assertEqual(second.accepted_ids, [])
        self.assertEqual(len(second.quarantined_ids), 1)

    def test_local_adapter_handles_malformed_duplicate_and_disabled_records(self) -> None:
        malformed = ingest_codex_local_session("demo", ["not-json"])
        self.assertEqual(len(malformed.quarantined_ids), 1)
        records = self.local_records()[:2]
        first = ingest_codex_local_session("demo", records)
        second = ingest_codex_local_session("demo", records)
        self.assertEqual(len(first.accepted_ids), 2)
        self.assertEqual(len(second.duplicate_ids), 2)
        disabled = ingest_codex_local_session("disabled", records, enabled=False)
        self.assertEqual(disabled.availability, "disabled")
        self.assertEqual(CodexTelemetryStore("disabled").records(), [])

    def test_local_negative_duration_is_quarantined_without_raising(self) -> None:
        record = {
            "timestamp": "2026-08-23T20:58:04+00:00", "type": "event_msg",
            "payload": {
                "type": "task_complete", "turn_id": "turn-1",
                "completed_at": "2026-08-23T20:58:04+00:00", "duration_ms": -1,
            },
        }
        result = ingest_codex_local_session("demo", [record])
        self.assertEqual(result.accepted_ids, [])
        self.assertEqual(len(result.quarantined_ids), 1)
        self.assertEqual(CodexTelemetryStore("demo").quarantined()[0].reason, "normalization_error")


if __name__ == "__main__":
    unittest.main()

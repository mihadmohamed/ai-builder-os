from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


from executor_continuity import (
    CODEX_USAGE_LIMIT,
    CodexAppServerClient,
    CodexAppServerError,
    CodexAvailability,
    RateLimitWindow,
    classify_codex_failure,
    encode_websocket_client_frame,
    eligibility_due,
    extract_websocket_frame,
    parse_rate_limit_snapshot,
    resolve_codex_executable,
    select_retry_decision,
)


class ExecutorContinuityTests(unittest.TestCase):
    def test_latest_blocking_reset_controls_retry(self) -> None:
        now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
        availability = CodexAvailability(
            available=False,
            primary=RateLimitWindow(
                identifier="primary",
                used_percent=100,
                resets_at=(now + timedelta(minutes=10)).isoformat(),
                exhausted=True,
            ),
            secondary=RateLimitWindow(
                identifier="secondary",
                used_percent=100,
                resets_at=(now + timedelta(hours=4)).isoformat(),
                exhausted=True,
            ),
        )

        decision = select_retry_decision(availability, now=now, buffer_seconds=60)

        self.assertEqual(decision.strategy, "reported_reset")
        self.assertEqual(decision.blocking_window_ids, ("primary", "secondary"))
        self.assertEqual(
            decision.retry_after,
            (now + timedelta(hours=4, minutes=1)).isoformat(),
        )

    def test_missing_reset_uses_bounded_backoff(self) -> None:
        now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
        availability = CodexAvailability(
            available=False,
            primary=RateLimitWindow(identifier="primary", exhausted=True),
        )

        decision = select_retry_decision(availability, now=now, attempt_count=1)

        self.assertEqual(decision.strategy, "bounded_backoff")
        self.assertEqual(decision.retry_after, (now + timedelta(minutes=30)).isoformat())

    def test_snapshot_detects_reset_credit_without_exposing_credit_rows(self) -> None:
        snapshot = parse_rate_limit_snapshot(
            {
                "rateLimits": {
                    "planType": "plus",
                    "primary": {"usedPercent": 100, "resetsAt": 1788102000},
                },
                "rateLimitResetCredits": {"availableCount": 1, "credits": [{"id": "private-id"}]},
            }
        )

        self.assertFalse(snapshot.available)
        self.assertTrue(snapshot.reset_credit_available)
        self.assertNotIn("private-id", str(snapshot.to_dict()))

    def test_only_known_usage_failure_is_retryable(self) -> None:
        usage = classify_codex_failure(exit_code=1, stderr="Usage limit reached; resets in 2 hours")
        unknown = classify_codex_failure(exit_code=1, stderr="connection unexpectedly closed")

        self.assertTrue(usage.retryable)
        self.assertEqual(usage.category, "temporary_usage_limit")
        self.assertFalse(unknown.retryable)
        self.assertEqual(unknown.category, "unknown_executor_failure")

    def test_safe_error_redacts_tokens(self) -> None:
        classified = classify_codex_failure(
            exit_code=1,
            stderr="rate limit; Authorization: secret-value",
        )
        self.assertNotIn("secret-value", classified.safe_error)

    def test_resolver_prefers_config_then_path_then_known_standalone_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            configured = root / "configured-codex"
            configured.write_text("#!/bin/sh\n")
            configured.chmod(0o755)
            path_codex = root / "path-codex"
            path_codex.write_text("#!/bin/sh\n")
            path_codex.chmod(0o755)

            resolved = resolve_codex_executable(
                configured=str(configured),
                which=lambda _: str(path_codex),
                home=root,
            )

        self.assertEqual(resolved, configured.resolve())

    def test_invalid_configured_executable_fails_closed(self) -> None:
        with self.assertRaises(FileNotFoundError):
            resolve_codex_executable(configured="/private/tmp/does-not-exist", which=lambda _: "/bin/echo")

    def test_app_server_client_reads_supported_rate_limit_method(self) -> None:
        calls: list[tuple[tuple[str, ...], str]] = []

        def runner(command, *, input, capture_output, text, timeout, check):
            calls.append((tuple(command), input or ""))
            if command[-3:] == ["app-server", "daemon", "version"]:
                return subprocess.CompletedProcess(command, 0, stdout='{"cliVersion":"0.145.0"}', stderr="")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=(
                    '{"jsonrpc":"2.0","id":1,"result":{}}\n'
                    '{"jsonrpc":"2.0","id":2,"result":{"rateLimits":{"primary":{"usedPercent":20}}}}\n'
                ),
                stderr="",
            )

        client = CodexAppServerClient(Path("/tmp/codex"), runner=runner)
        availability = client.availability()

        self.assertTrue(availability.available)
        self.assertIn('"method":"account/rateLimits/read"', calls[-1][1])
        self.assertNotIn('"jsonrpc"', calls[-1][1])

    def test_websocket_frames_are_masked_and_round_trip(self) -> None:
        payload = b'{"id":1,"method":"initialize"}'
        buffer = bytearray(encode_websocket_client_frame(payload, mask=b"abcd"))

        frame = extract_websocket_frame(buffer)

        self.assertEqual(frame, (0x1, payload))
        self.assertEqual(buffer, bytearray())

    def test_app_server_health_starts_then_rechecks(self) -> None:
        calls: list[tuple[str, ...]] = []
        health_count = 0

        def runner(command, *, input, capture_output, text, timeout, check):
            nonlocal health_count
            suffix = tuple(command[-3:])
            calls.append(tuple(command))
            if suffix == ("app-server", "daemon", "version"):
                health_count += 1
                if health_count == 1:
                    return subprocess.CompletedProcess(command, 1, stdout="", stderr="stale")
                return subprocess.CompletedProcess(command, 0, stdout='{"cliVersion":"0.145.0"}', stderr="")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        client = CodexAppServerClient(Path("/tmp/codex"), runner=runner)
        client.ensure_healthy()

        self.assertTrue(any(call[-3:] == ("app-server", "daemon", "start") for call in calls))
        self.assertFalse(any(call[-3:] == ("app-server", "daemon", "restart") for call in calls))

    def test_app_server_health_restarts_after_failed_start(self) -> None:
        health_count = 0

        def runner(command, *, input, capture_output, text, timeout, check):
            nonlocal health_count
            suffix = tuple(command[-3:])
            if suffix == ("app-server", "daemon", "version"):
                health_count += 1
                if health_count == 1:
                    return subprocess.CompletedProcess(command, 1, stdout="", stderr="stopped")
                return subprocess.CompletedProcess(command, 0, stdout='{"cliVersion":"0.145.0"}', stderr="")
            if suffix == ("app-server", "daemon", "start"):
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="stale socket")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        client = CodexAppServerClient(Path("/tmp/codex"), runner=runner)
        client.ensure_healthy()
        self.assertEqual(health_count, 2)

    def test_malformed_proxy_response_fails_closed(self) -> None:
        def runner(command, *, input, capture_output, text, timeout, check):
            if command[-3:] == ["app-server", "daemon", "version"]:
                return subprocess.CompletedProcess(command, 0, stdout='{"cliVersion":"0.145.0"}', stderr="")
            return subprocess.CompletedProcess(command, 0, stdout='{"method":"unexpected"}\n', stderr="")

        client = CodexAppServerClient(Path("/tmp/codex"), runner=runner)
        with self.assertRaises(CodexAppServerError):
            client.availability()

    def test_malformed_version_report_fails_health_check(self) -> None:
        def runner(command, *, input, capture_output, text, timeout, check):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"status":"running","cliVersion":"future-version"}',
                stderr="",
            )

        client = CodexAppServerClient(Path("/tmp/codex"), runner=runner)
        self.assertFalse(client.health())

    def test_malformed_window_data_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            parse_rate_limit_snapshot({"rateLimits": {"primary": {"usedPercent": 140}}})

    def test_eligibility_is_due_at_retry_timestamp(self) -> None:
        now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(eligibility_due(now.isoformat(), now=now))
        self.assertFalse(eligibility_due((now + timedelta(seconds=1)).isoformat(), now=now))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import base64
import hashlib
import os
import re
import selectors
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


CODEX_EXECUTOR = "codex"
CODEX_USAGE_LIMIT = "CODEX_USAGE_LIMIT"
CODEX_APP_SERVER_UNAVAILABLE = "CODEX_APP_SERVER_UNAVAILABLE"
AVAILABILITY_SOURCE = "codex_app_server"
WAITING_FOR_EXECUTOR = "WAITING_FOR_EXECUTOR"
RETRY_EXIT_CODE = 75
DEFAULT_RETRY_BUFFER_SECONDS = 60
MAX_SAFE_ERROR_CHARS = 480
MAX_PROTOCOL_BYTES = 1_000_000
MAX_COMPLETION_REPORT_BYTES = 64_000
PLAN_TYPES = {
    "free", "go", "plus", "pro", "prolite", "team", "self_serve_business_usage_based",
    "business", "enterprise_cbp_usage_based", "enterprise", "edu", "unknown", "",
}
REACHED_TYPES = {
    "rate_limit_reached",
    "workspace_owner_credits_depleted",
    "workspace_member_credits_depleted",
    "workspace_owner_usage_limit_reached",
    "workspace_member_usage_limit_reached",
    "",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(timezone.utc).isoformat()


def parse_timestamp(value: Any) -> datetime | None:
    if value in (None, "", 0):
        return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        if numeric > 10_000_000_000:
            numeric /= 1000
        try:
            return datetime.fromtimestamp(numeric, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return parse_timestamp(float(text))
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _bounded_percent(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not 0 <= number <= 100:
        return None
    return number


def _positive_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


@dataclass(frozen=True)
class RateLimitWindow:
    identifier: str
    used_percent: float | None = None
    window_minutes: int | None = None
    resets_at: str = ""
    exhausted: bool = False

    @property
    def reset_datetime(self) -> datetime | None:
        return parse_timestamp(self.resets_at)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CodexAvailability:
    available: bool
    plan_type: str = ""
    primary: RateLimitWindow | None = None
    secondary: RateLimitWindow | None = None
    rate_limit_reached_type: str = ""
    rate_limit_reached: bool = False
    reset_credit_available: bool = False
    observed_at: str = ""
    source: str = AVAILABILITY_SOURCE
    cli_version: str = ""

    @property
    def blocking_windows(self) -> tuple[RateLimitWindow, ...]:
        return tuple(
            window
            for window in (self.primary, self.secondary)
            if window is not None and window.exhausted
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["blocking_windows"] = [item.to_dict() for item in self.blocking_windows]
        return payload


@dataclass(frozen=True)
class RetryDecision:
    retry_after: str
    strategy: str
    blocking_window_ids: tuple[str, ...]


@dataclass(frozen=True)
class FailureClassification:
    category: str
    retryable: bool
    safe_error: str
    exit_code: int | None = None


@dataclass(frozen=True)
class ManagedCompletionReport:
    summary: str
    files_changed: tuple[str, ...]
    tests: tuple[str, ...]
    completed_task_numbers: tuple[int, ...]


def parse_managed_completion_report(
    value: str,
    *,
    workspace_root: Path,
    allowed_task_numbers: Iterable[int],
) -> ManagedCompletionReport:
    if len(value.encode("utf-8")) > MAX_COMPLETION_REPORT_BYTES:
        raise ValueError("Managed completion report exceeds the safe size limit")
    text = value.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    payload = json.loads(text)
    if not isinstance(payload, dict) or set(payload) != {
        "summary", "files_changed", "tests", "completed_task_numbers"
    }:
        raise ValueError("Managed completion report has an unsupported shape")
    summary = safe_error(str(payload.get("summary", "")))
    if not summary:
        raise ValueError("Managed completion report summary is required")
    raw_files = payload.get("files_changed")
    raw_tests = payload.get("tests")
    raw_tasks = payload.get("completed_task_numbers")
    if not isinstance(raw_files, list) or not isinstance(raw_tests, list) or not isinstance(raw_tasks, list):
        raise ValueError("Managed completion report list fields are required")
    root = workspace_root.resolve()
    files: list[str] = []
    for raw in raw_files:
        relative = Path(str(raw))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Managed completion report contains an unsafe file path")
        resolved = (root / relative).resolve()
        if root != resolved and root not in resolved.parents:
            raise ValueError("Managed completion report file is outside the project workspace")
        files.append(relative.as_posix())
    tests = [safe_error(str(item)) for item in raw_tests]
    if any(not item for item in tests):
        raise ValueError("Managed completion report contains an empty test result")
    allowed = set(allowed_task_numbers)
    if any(not isinstance(item, int) or item not in allowed for item in raw_tasks):
        raise ValueError("Managed completion report contains an unlinked task number")
    if len(raw_tasks) != len(set(raw_tasks)):
        raise ValueError("Managed completion report contains duplicate task numbers")
    return ManagedCompletionReport(
        summary=summary,
        files_changed=tuple(sorted(set(files))),
        tests=tuple(tests),
        completed_task_numbers=tuple(sorted(raw_tasks)),
    )


class CodexAppServerError(RuntimeError):
    pass


def encode_websocket_client_frame(payload: bytes, *, opcode: int = 0x1, mask: bytes | None = None) -> bytes:
    masking_key = mask or os.urandom(4)
    if len(masking_key) != 4:
        raise ValueError("WebSocket masking key must be four bytes")
    length = len(payload)
    frame = bytearray([0x80 | opcode])
    if length < 126:
        frame.append(0x80 | length)
    elif length <= 0xFFFF:
        frame.append(0x80 | 126)
        frame.extend(length.to_bytes(2, "big"))
    else:
        frame.append(0x80 | 127)
        frame.extend(length.to_bytes(8, "big"))
    frame.extend(masking_key)
    frame.extend(byte ^ masking_key[index % 4] for index, byte in enumerate(payload))
    return bytes(frame)


def extract_websocket_frame(buffer: bytearray) -> tuple[int, bytes] | None:
    if len(buffer) < 2:
        return None
    first, second = buffer[0], buffer[1]
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    offset = 2
    if length == 126:
        if len(buffer) < offset + 2:
            return None
        length = int.from_bytes(buffer[offset:offset + 2], "big")
        offset += 2
    elif length == 127:
        if len(buffer) < offset + 8:
            return None
        length = int.from_bytes(buffer[offset:offset + 8], "big")
        offset += 8
    if length > MAX_PROTOCOL_BYTES:
        raise CodexAppServerError("Codex App Server response exceeded the safe size limit.")
    masking_key = b""
    if masked:
        if len(buffer) < offset + 4:
            return None
        masking_key = bytes(buffer[offset:offset + 4])
        offset += 4
    if len(buffer) < offset + length:
        return None
    payload = bytes(buffer[offset:offset + length])
    del buffer[:offset + length]
    if masked:
        payload = bytes(byte ^ masking_key[index % 4] for index, byte in enumerate(payload))
    return opcode, payload


def _window(
    identifier: str,
    raw: Mapping[str, Any] | None,
    reached_type: str,
) -> RateLimitWindow | None:
    if not isinstance(raw, Mapping):
        return None
    raw_used = raw.get("usedPercent", raw.get("used_percent"))
    used = _bounded_percent(raw_used)
    if raw_used is not None and used is None:
        raise ValueError(f"Invalid {identifier} used percentage")
    raw_minutes = raw.get("windowDurationMins", raw.get("window_minutes"))
    minutes = _positive_int(raw_minutes)
    if raw_minutes is not None and minutes is None:
        raise ValueError(f"Invalid {identifier} window duration")
    raw_reset = raw.get("resetsAt", raw.get("resets_at"))
    reset = parse_timestamp(raw_reset)
    if raw_reset not in (None, "", 0) and reset is None:
        raise ValueError(f"Invalid {identifier} reset timestamp")
    reached = reached_type.casefold()
    exhausted = bool(
        used is not None
        and used >= 100
        or identifier.casefold() in reached
        or reached in {"all", "both", "primary_and_secondary"}
    )
    return RateLimitWindow(
        identifier=identifier,
        used_percent=used,
        window_minutes=minutes,
        resets_at=isoformat(reset),
        exhausted=exhausted,
    )


def _find_rate_limit_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    current: Mapping[str, Any] = payload
    for key in ("result", "rateLimits", "rate_limits", "data"):
        candidate = current.get(key)
        if isinstance(candidate, Mapping):
            current = candidate
    if not any(key in current for key in ("primary", "secondary", "rateLimitReachedType", "planType")):
        for value in payload.values():
            if isinstance(value, Mapping) and any(key in value for key in ("primary", "secondary")):
                return value
    return current


def _reset_credit_available(payload: Mapping[str, Any]) -> bool:
    interesting = {
        "resetcredits",
        "resetcredit",
        "quotaresetcredits",
        "additionalcredits",
        "ratelimitresetcredits",
    }

    def walk(value: Any, parent_key: str = "") -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                normalized = re.sub(r"[^a-z]", "", str(key).casefold())
                if normalized in interesting:
                    if isinstance(child, bool):
                        return child
                    if isinstance(child, (int, float)):
                        return child > 0
                    if isinstance(child, Mapping):
                        available_count = child.get("availableCount", child.get("available_count"))
                        if isinstance(available_count, (int, float)) and available_count > 0:
                            return True
                        for field in ("available", "remaining", "count", "balance"):
                            amount = child.get(field)
                            if isinstance(amount, bool) and amount:
                                return True
                            if isinstance(amount, (int, float)) and amount > 0:
                                return True
                if walk(child, normalized):
                    return True
        elif isinstance(value, list):
            return any(walk(item, parent_key) for item in value[:100])
        return False

    return walk(payload)


def parse_rate_limit_snapshot(
    payload: Mapping[str, Any],
    *,
    observed_at: datetime | None = None,
    cli_version: str = "",
) -> CodexAvailability:
    if not isinstance(payload, Mapping):
        raise ValueError("Codex rate-limit response must be an object")
    raw = _find_rate_limit_payload(payload)
    reached_type = str(raw.get("rateLimitReachedType", raw.get("rate_limit_reached_type", "")) or "")
    if reached_type not in REACHED_TYPES:
        raise ValueError("Unsupported Codex reached-limit type")
    plan_type = str(raw.get("planType", raw.get("plan_type", "")) or "")
    if plan_type not in PLAN_TYPES:
        plan_type = "unknown"
    primary = _window("primary", raw.get("primary") if isinstance(raw.get("primary"), Mapping) else None, reached_type)
    secondary = _window(
        "secondary",
        raw.get("secondary") if isinstance(raw.get("secondary"), Mapping) else None,
        reached_type,
    )
    blocking = tuple(item for item in (primary, secondary) if item is not None and item.exhausted)
    explicit_reached = bool(raw.get("rateLimitReached", raw.get("rate_limit_reached", False)))
    reached = bool(blocking or explicit_reached or reached_type)
    return CodexAvailability(
        available=not reached,
        plan_type=plan_type,
        primary=primary,
        secondary=secondary,
        rate_limit_reached_type=reached_type,
        rate_limit_reached=reached,
        reset_credit_available=_reset_credit_available(payload),
        observed_at=isoformat(observed_at or utc_now()),
        cli_version=cli_version,
    )


def fallback_delay(attempt_count: int) -> timedelta:
    sequence = (15, 30, 60)
    index = min(max(attempt_count, 0), len(sequence) - 1)
    return timedelta(minutes=sequence[index])


def select_retry_decision(
    availability: CodexAvailability,
    *,
    now: datetime | None = None,
    attempt_count: int = 0,
    buffer_seconds: int = DEFAULT_RETRY_BUFFER_SECONDS,
) -> RetryDecision:
    current = (now or utc_now()).astimezone(timezone.utc)
    resets = [item.reset_datetime for item in availability.blocking_windows]
    usable = [item for item in resets if item is not None and item > current]
    if usable:
        retry = max(usable) + timedelta(seconds=max(0, buffer_seconds))
        strategy = "reported_reset"
    else:
        retry = current + fallback_delay(attempt_count)
        strategy = "bounded_backoff"
    return RetryDecision(
        retry_after=isoformat(retry),
        strategy=strategy,
        blocking_window_ids=tuple(item.identifier for item in availability.blocking_windows),
    )


_USAGE_LIMIT_PATTERNS = (
    re.compile(r"usage\s+limit", re.IGNORECASE),
    re.compile(r"rate\s+limit", re.IGNORECASE),
    re.compile(r"plan\s+limit", re.IGNORECASE),
    re.compile(r"credit(?:s)?\s+(?:exhausted|limit|unavailable)", re.IGNORECASE),
    re.compile(r"too\s+many\s+requests", re.IGNORECASE),
    re.compile(r"resets?\s+(?:at|in)", re.IGNORECASE),
)


def safe_error(value: str) -> str:
    text = " ".join(value.replace("\x00", " ").split())
    text = re.sub(r"(?i)(authorization|api[-_ ]?key|token|cookie)\s*[:=]\s*\S+", r"\1=[redacted]", text)
    return text[:MAX_SAFE_ERROR_CHARS]


def classify_codex_failure(
    *,
    exit_code: int | None,
    stdout: str = "",
    stderr: str = "",
    structured_category: str = "",
) -> FailureClassification:
    structured = structured_category.strip().casefold()
    combined = "\n".join(part for part in (stderr, stdout) if part)
    if structured in {"usage_limit", "rate_limit", "credit_limit", "plan_limit"} or any(
        pattern.search(combined) for pattern in _USAGE_LIMIT_PATTERNS
    ):
        return FailureClassification(
            category="temporary_usage_limit",
            retryable=True,
            # Executor output may echo the implementation prompt. Persist a
            # stable operational summary rather than output-derived text.
            safe_error="Codex usage limit reached.",
            exit_code=exit_code,
        )
    if structured in {"implementation_failure", "tool_failure", "test_failure"}:
        return FailureClassification(
            category="implementation_failure",
            retryable=False,
            safe_error="Codex implementation failed.",
            exit_code=exit_code,
        )
    return FailureClassification(
        category="unknown_executor_failure",
        retryable=False,
        safe_error=f"Codex exited with code {exit_code}.",
        exit_code=exit_code,
    )


def resolve_codex_executable(
    *,
    configured: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
    home: Path | None = None,
) -> Path:
    configured_value = (configured if configured is not None else os.getenv("AI_BUILDER_OS_CODEX_PATH", "")).strip()
    candidates: list[Path] = []
    if configured_value:
        configured_path = Path(configured_value).expanduser()
        try:
            configured_path = configured_path.resolve()
        except OSError as exc:
            raise FileNotFoundError("Configured Codex executable could not be resolved.") from exc
        if not configured_path.is_file() or not os.access(configured_path, os.X_OK):
            raise FileNotFoundError("Configured Codex executable is unavailable or not executable.")
        return configured_path
    resolved = which("codex")
    if resolved and ".app/Contents/" not in resolved:
        candidates.append(Path(resolved))
    root = home or Path.home()
    candidates.extend(
        (
            root / ".codex" / "packages" / "standalone" / "current" / "codex",
            root / ".local" / "bin" / "codex",
            root / ".codex" / "bin" / "codex",
        )
    )
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            real = candidate.expanduser().resolve()
        except OSError:
            continue
        if real in seen:
            continue
        seen.add(real)
        if real.is_file() and os.access(real, os.X_OK):
            return real
    raise FileNotFoundError("Could not find an executable standalone Codex CLI.")


Runner = Callable[..., subprocess.CompletedProcess[str]]


class CodexAppServerClient:
    def __init__(
        self,
        executable: Path | None = None,
        *,
        runner: Runner = subprocess.run,
        timeout_seconds: float = 10,
    ) -> None:
        self.executable = executable or resolve_codex_executable()
        self.runner = runner
        self.timeout_seconds = timeout_seconds
        self.cli_version = ""

    def _run(self, args: Sequence[str], *, input_text: str = "") -> subprocess.CompletedProcess[str]:
        return self.runner(
            [str(self.executable), *args],
            input=input_text or None,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )

    def health(self) -> bool:
        result = self._run(("app-server", "daemon", "version"))
        if result.returncode == 0:
            try:
                report = json.loads(result.stdout or result.stderr)
            except json.JSONDecodeError:
                return False
            if not isinstance(report, Mapping) or report.get("status", "running") != "running":
                return False
            cli_version = str(report.get("managedCodexVersion", report.get("cliVersion", "")))
            if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", cli_version):
                return False
            self.cli_version = cli_version
            return True
        return False

    def ensure_healthy(self) -> None:
        if self.health():
            return
        started = self._run(("app-server", "daemon", "start"))
        if started.returncode == 0 and self.health():
            return
        restarted = self._run(("app-server", "daemon", "restart"))
        if restarted.returncode == 0 and self.health():
            return
        detail = safe_error(restarted.stderr or started.stderr or "Codex App Server did not become healthy.")
        raise CodexAppServerError(detail)

    def _proxy_payload(self) -> str:
        messages = (
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "ai-builder-os", "version": "1"},
                    "capabilities": {},
                },
            },
            {"method": "initialized"},
            {"id": 2, "method": "account/rateLimits/read"},
        )
        return "".join(json.dumps(message, separators=(",", ":")) + "\n" for message in messages)

    def read_rate_limits(self) -> Mapping[str, Any]:
        self.ensure_healthy()
        if self.runner is subprocess.run:
            stdout = self._read_rate_limits_live()
            stderr = ""
            returncode = 0
        else:
            result = self._run(("app-server", "proxy"), input_text=self._proxy_payload())
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
        if returncode != 0:
            raise CodexAppServerError(safe_error(stderr or "Codex App Server proxy failed."))
        encoded = stdout.encode("utf-8", errors="replace")
        if len(encoded) > MAX_PROTOCOL_BYTES:
            raise CodexAppServerError("Codex App Server response exceeded the safe size limit.")
        response: Mapping[str, Any] | None = None
        for line in stdout.splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, Mapping) and item.get("id") == 2:
                if isinstance(item.get("error"), Mapping):
                    raise CodexAppServerError(safe_error(str(item["error"].get("message", "Rate-limit read failed."))))
                candidate = item.get("result")
                if isinstance(candidate, Mapping):
                    response = candidate
        if response is None:
            raise CodexAppServerError("Codex App Server did not return a structured rate-limit result.")
        return response

    def _read_rate_limits_live(self) -> str:
        process = subprocess.Popen(
            [str(self.executable), "app-server", "proxy"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        if process.stdin is None or process.stdout is None:
            process.kill()
            raise CodexAppServerError("Codex App Server proxy streams were unavailable.")
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        captured: list[str] = []
        buffer = bytearray()

        def read_more(deadline: float) -> None:
            events = selector.select(timeout=max(0.01, deadline - time.monotonic()))
            if not events:
                return
            chunk = os.read(process.stdout.fileno(), 65_536)
            if not chunk:
                raise CodexAppServerError("Codex App Server proxy closed unexpectedly.")
            buffer.extend(chunk)
            if len(buffer) > MAX_PROTOCOL_BYTES:
                raise CodexAppServerError("Codex App Server response exceeded the safe size limit.")

        def send_frame(payload: bytes, opcode: int = 0x1) -> None:
            process.stdin.write(encode_websocket_client_frame(payload, opcode=opcode))
            process.stdin.flush()

        def send(message: Mapping[str, Any]) -> None:
            send_frame(json.dumps(message, separators=(",", ":")).encode("utf-8"))

        def receive_frame(deadline: float) -> tuple[int, bytes]:
            while time.monotonic() < deadline:
                frame = extract_websocket_frame(buffer)
                if frame is None:
                    read_more(deadline)
                    continue
                return frame
            raise CodexAppServerError("Codex App Server proxy response timed out.")

        def receive(response_id: int) -> None:
            deadline = time.monotonic() + self.timeout_seconds
            while time.monotonic() < deadline:
                opcode, body = receive_frame(deadline)
                if opcode == 0x9:
                    send_frame(body, opcode=0xA)
                    continue
                if opcode == 0x8:
                    raise CodexAppServerError("Codex App Server closed the proxy connection.")
                if opcode != 0x1:
                    continue
                try:
                    item = json.loads(body)
                except json.JSONDecodeError as exc:
                    raise CodexAppServerError("Codex App Server returned malformed JSON.") from exc
                captured.append(body.decode("utf-8", errors="replace"))
                if isinstance(item, Mapping) and item.get("id") == response_id:
                    if isinstance(item.get("error"), Mapping):
                        raise CodexAppServerError(safe_error(str(item["error"].get("message", "App Server request failed."))))
                    return
            raise CodexAppServerError("Codex App Server proxy response timed out.")

        try:
            websocket_key = base64.b64encode(os.urandom(16)).decode("ascii")
            request = (
                "GET / HTTP/1.1\r\n"
                "Host: localhost\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {websocket_key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            ).encode("ascii")
            process.stdin.write(request)
            process.stdin.flush()
            handshake_deadline = time.monotonic() + self.timeout_seconds
            while b"\r\n\r\n" not in buffer and time.monotonic() < handshake_deadline:
                read_more(handshake_deadline)
            header_end = buffer.find(b"\r\n\r\n")
            if header_end < 0:
                raise CodexAppServerError("Codex App Server websocket handshake timed out.")
            header = bytes(buffer[:header_end]).decode("ascii", errors="replace")
            del buffer[:header_end + 4]
            expected_accept = base64.b64encode(
                hashlib.sha1((websocket_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
            ).decode("ascii")
            if " 101 " not in header.splitlines()[0] or expected_accept.casefold() not in header.casefold():
                raise CodexAppServerError("Codex App Server rejected the websocket handshake.")
            send(
                {
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "clientInfo": {"name": "ai-builder-os", "version": "1"},
                        "capabilities": {},
                    },
                }
            )
            receive(1)
            send({"method": "initialized"})
            send({"id": 2, "method": "account/rateLimits/read"})
            receive(2)
            return "\n".join(captured)
        finally:
            selector.close()
            try:
                process.stdin.close()
            except OSError:
                pass
            try:
                process.terminate()
            except OSError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

    def availability(self, *, observed_at: datetime | None = None) -> CodexAvailability:
        try:
            return parse_rate_limit_snapshot(
                self.read_rate_limits(),
                observed_at=observed_at,
                cli_version=self.cli_version,
            )
        except ValueError as exc:
            raise CodexAppServerError(safe_error(str(exc))) from exc


def eligibility_due(retry_after: str, *, now: datetime | None = None) -> bool:
    parsed = parse_timestamp(retry_after)
    return parsed is None or parsed <= (now or utc_now()).astimezone(timezone.utc)


def next_event(events: Iterable[Mapping[str, Any]], event_type: str, **fields: Any) -> list[dict[str, Any]]:
    bounded = [dict(item) for item in events][-99:]
    bounded.append({"event": event_type, "occurred_at": isoformat(utc_now()), **fields})
    return bounded

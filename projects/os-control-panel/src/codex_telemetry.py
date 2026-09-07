from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from context_attribution import ContextContribution, numeric_contribution, unavailable_host_context
from control_plane.storage import atomic_write_json, control_data_dir, load_json, project_lock


OTEL_ADAPTER_VERSION = "2026-08-23.codex-otel.v1"
LOCAL_ADAPTER_VERSION = "2026-08-23.codex-local-session.experimental.v1"
OTEL_SCHEMA_VERSION = "codex-otel-logs.v1"
LOCAL_SCHEMA_VERSION = "codex-rollout-jsonl.v1"
OFFICIAL_OTEL_REFERENCE = "https://learn.chatgpt.com/docs/config-file/config-advanced#observability-and-telemetry"

EvidenceClass = Literal["attributable", "derived", "experimental", "unavailable"]
Availability = Literal["available", "unavailable", "disabled", "quarantined"]
Primitive = str | int | float | bool


class TelemetryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TelemetryCorrelation(TelemetryModel):
    status: Literal["correlated", "uncorrelated", "quarantined"]
    method: str = ""
    confidence: Literal["exact", "explicit", "none"] = "none"
    keys: list[str] = Field(default_factory=list)
    limitation: str = ""

    @model_validator(mode="after")
    def validate_correlation(self) -> "TelemetryCorrelation":
        self.keys = sorted(set(item.strip() for item in self.keys if item.strip()))
        if self.status == "correlated" and (not self.method.strip() or not self.keys):
            raise ValueError("Correlated telemetry requires a method and exact keys")
        if self.status != "correlated" and self.confidence != "none":
            raise ValueError("Only correlated telemetry may claim confidence")
        return self


class CodexTelemetryRecord(TelemetryModel):
    telemetry_id: str = Field(min_length=1)
    project_name: str = ""
    timestamp: str
    event_name: str = Field(min_length=1)
    source: Literal["codex_otel", "codex_local_session"]
    evidence_class: Literal["attributable", "experimental"]
    stability: Literal["supported", "versioned_experimental"]
    adapter_version: str = Field(min_length=1)
    source_schema_version: str = Field(min_length=1)
    schema_fingerprint: str = Field(min_length=1)
    privacy_classification: Literal["operational_metadata", "aggregate_usage"]
    original_event_id: str = ""
    sequence: int = Field(default=0, ge=0)
    session_id: str = ""
    turn_id: str = ""
    trace_id: str = ""
    work_request_id: str = ""
    requirement_id: str = ""
    proposal_id: str = ""
    proposal_revision: int = Field(default=0, ge=0)
    mcp_server: str = ""
    tool_name: str = ""
    outcome: str = ""
    duration_ms: float | None = Field(default=None, ge=0)
    metric_values: dict[str, Primitive] = Field(default_factory=dict)
    context_contributions: list[ContextContribution] = Field(default_factory=list)
    correlation: TelemetryCorrelation = Field(
        default_factory=lambda: TelemetryCorrelation(
            status="uncorrelated",
            limitation="No exact AI Builder OS workflow identity was supplied.",
        )
    )

    @model_validator(mode="after")
    def validate_evidence_boundary(self) -> "CodexTelemetryRecord":
        if self.source == "codex_local_session":
            if self.evidence_class != "experimental" or self.stability != "versioned_experimental":
                raise ValueError("Local-session evidence must remain versioned experimental")
        elif self.evidence_class != "attributable" or self.stability != "supported":
            raise ValueError("Supported Codex OTel evidence must remain attributable")
        forbidden = {
            "prompt", "user_prompt", "content", "message", "arguments", "output",
            "output_snippet", "reasoning", "summary", "base_instructions",
        }
        if forbidden.intersection(key.casefold() for key in self.metric_values):
            raise ValueError("Telemetry records cannot retain raw textual content")
        return self


class TelemetryQuarantineRecord(TelemetryModel):
    quarantine_id: str
    source: Literal["codex_otel", "codex_local_session"]
    reason: str
    event_name: str = "unknown"
    source_schema_version: str = "unknown"
    schema_fingerprint: str
    original_event_id: str = ""
    observed_at: str


class TelemetryIngestionResult(TelemetryModel):
    source: Literal["codex_otel", "codex_local_session"]
    accepted_ids: list[str] = Field(default_factory=list)
    duplicate_ids: list[str] = Field(default_factory=list)
    quarantined_ids: list[str] = Field(default_factory=list)
    ignored_count: int = Field(default=0, ge=0)
    adapter_version: str
    availability: Availability


class CodexTelemetryRunEvidence(TelemetryModel):
    project_name: str
    work_request_id: str = ""
    trace_id: str = ""
    session_id: str = ""
    source_record_ids: list[str] = Field(default_factory=list)
    metric_values: dict[str, Primitive] = Field(default_factory=dict)
    metric_classes: dict[str, EvidenceClass] = Field(default_factory=dict)
    context_contributions: list[ContextContribution] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


_SUPPORTED_OTEL_EVENTS = {
    "codex.conversation_starts",
    "codex.api_request",
    "codex.sse_event",
    "codex.websocket_request",
    "codex.websocket_event",
    "codex.user_prompt",
    "codex.tool_decision",
    "codex.tool_result",
    "codex.tool.call",
    "codex.tool.call.duration_ms",
    "codex.turn.e2e_duration_ms",
    "codex.turn.ttft.duration_ms",
    "codex.turn.ttfm.duration_ms",
    "codex.turn.tool.call",
    "codex.turn.token_usage",
}

_SAFE_IDENTITY_KEYS = {
    "project_name", "project", "ai_builder_os.project", "ai_builder_os.project_name",
    "work_request_id", "ai_builder_os.work_request_id", "requirement_id",
    "ai_builder_os.requirement_id", "proposal_id", "ai_builder_os.proposal_id",
    "proposal_revision", "ai_builder_os.proposal_revision", "trace_id", "session_id",
    "conversation_id", "turn_id", "thread_id", "request_id", "event_id",
}

_SAFE_OTEL_ATTRIBUTE_KEYS = _SAFE_IDENTITY_KEYS | {
    "app.version", "cli_version", "model", "reasoning_effort", "reasoning",
    "sandbox_policy", "approval_policy", "attempt", "status", "success", "duration_ms",
    "kind", "tool", "tool_name", "mcp_server", "mcp_tool", "decision",
    "decision_source", "prompt_length", "output_length", "output_size", "output_chars",
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
    "reasoning_output_tokens", "total_tokens", "token_type", "value", "count",
    "auth_mode", "originator", "session_source", "environment", "error_type",
    "network_proxy_active", "tmp_mem_enabled",
}

_METRIC_KEY_MAP = {
    "input_tokens": "input_tokens",
    "cached_input_tokens": "cached_input_tokens",
    "cache_write_input_tokens": "cache_write_tokens",
    "output_tokens": "output_tokens",
    "reasoning_output_tokens": "reasoning_tokens",
    "total_tokens": "total_tokens",
    "model": "model",
    "reasoning_effort": "reasoning_effort",
    "prompt_length": "prompt_length_characters",
    "output_length": "tool_result_observed_characters",
    "output_size": "tool_result_observed_characters",
    "output_chars": "tool_result_observed_characters",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: object) -> str:
    digest = sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _parse_time(value: object) -> datetime:
    normalized = str(value or "").strip().replace("Z", "+00:00")
    if not normalized:
        raise ValueError("Telemetry record is missing a timestamp")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _primitive(value: object) -> Primitive | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (str, int, float)) and not isinstance(value, complex):
        return value
    return None


def _schema_descriptor(value: object, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            result.extend(_schema_descriptor(value[key], path))
        return result
    if isinstance(value, list):
        return [f"{prefix}:list"]
    return [f"{prefix}:{type(value).__name__}"]


def schema_fingerprint(value: object) -> str:
    return sha256("\n".join(_schema_descriptor(value)).encode("utf-8")).hexdigest()


def _decode_otlp_value(value: object) -> object:
    if not isinstance(value, dict):
        return value
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in value:
            raw = value[key]
            if key == "intValue":
                try:
                    return int(raw)
                except (TypeError, ValueError):
                    return raw
            return raw
    return value


def _decode_otlp_attributes(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, list):
        return {}
    decoded: dict[str, object] = {}
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("key"), str):
            continue
        decoded[item["key"]] = _decode_otlp_value(item.get("value"))
    return decoded


def _iter_otel_events(payload: object) -> Iterable[dict[str, object]]:
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield from _iter_otel_events(item)
        return
    if not isinstance(payload, dict):
        return
    if any(key in payload for key in ("event_name", "name")) and "resourceLogs" not in payload:
        yield dict(payload)
        return
    for resource_log in payload.get("resourceLogs", []) if isinstance(payload.get("resourceLogs"), list) else []:
        if not isinstance(resource_log, dict):
            continue
        resource_attributes = _decode_otlp_attributes(
            resource_log.get("resource", {}).get("attributes", [])
            if isinstance(resource_log.get("resource"), dict) else []
        )
        for scope_log in resource_log.get("scopeLogs", []) if isinstance(resource_log.get("scopeLogs"), list) else []:
            if not isinstance(scope_log, dict):
                continue
            for log_record in scope_log.get("logRecords", []) if isinstance(scope_log.get("logRecords"), list) else []:
                if not isinstance(log_record, dict):
                    continue
                body = _decode_otlp_value(log_record.get("body"))
                attributes = {**resource_attributes, **_decode_otlp_attributes(log_record.get("attributes", []))}
                event_name = attributes.get("event.name") or attributes.get("name") or body
                yield {
                    "event_name": event_name,
                    "timestamp": log_record.get("timeUnixNano") or log_record.get("observedTimeUnixNano") or "",
                    "attributes": attributes,
                    "event_id": attributes.get("event_id") or attributes.get("request_id") or "",
                }


def _otel_timestamp(value: object) -> str:
    text = str(value or "").strip()
    if text.isdigit():
        return datetime.fromtimestamp(int(text) / 1_000_000_000, tz=timezone.utc).isoformat()
    return _parse_time(text).isoformat()


def _identity(attributes: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = attributes.get(key)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def _correlate(project_name: str, attributes: dict[str, object]) -> TelemetryCorrelation:
    source_project = _identity(attributes, "ai_builder_os.project", "ai_builder_os.project_name", "project_name", "project")
    if source_project and source_project != project_name:
        return TelemetryCorrelation(
            status="quarantined",
            limitation=f"Cross-project identity conflict for {source_project}.",
        )
    exact_keys: list[str] = []
    for normalized, candidates in (
        ("work_request_id", ("ai_builder_os.work_request_id", "work_request_id")),
        ("requirement_id", ("ai_builder_os.requirement_id", "requirement_id")),
        ("proposal_id", ("ai_builder_os.proposal_id", "proposal_id")),
        ("trace_id", ("trace_id",)),
        ("session_id", ("session_id", "conversation_id")),
        ("turn_id", ("turn_id",)),
    ):
        if _identity(attributes, *candidates):
            exact_keys.append(normalized)
    if source_project:
        exact_keys.append("project_name")
    if source_project and len(exact_keys) >= 2:
        return TelemetryCorrelation(
            status="correlated", method="exact_source_identity", confidence="exact", keys=exact_keys,
        )
    return TelemetryCorrelation(
        status="uncorrelated",
        limitation="No deterministic project plus workflow identity was supplied; timestamp proximity was not used.",
    )


class CodexTelemetryStore:
    def __init__(self, project_name: str) -> None:
        self.project_name = project_name
        self.root = control_data_dir(project_name) / "system_learning"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.json"

    def _read(self, name: str) -> list[dict[str, Any]]:
        value = load_json(self._path(name), [])
        return value if isinstance(value, list) else []

    def _upsert(self, name: str, identity: str, payload: dict[str, Any]) -> bool:
        with project_lock(self.project_name):
            values = self._read(name)
            for item in values:
                if item.get(identity) != payload[identity]:
                    continue
                if item != payload:
                    raise ValueError(f"Immutable {name} identity already exists with different content")
                return False
            values.append(payload)
            atomic_write_json(self._path(name), values)
        return True

    def record(self, record: CodexTelemetryRecord) -> bool:
        return self._upsert("codex_telemetry", "telemetry_id", record.model_dump(mode="json"))

    def quarantine(self, record: TelemetryQuarantineRecord) -> bool:
        payload = record.model_dump(mode="json")
        with project_lock(self.project_name):
            values = self._read("codex_telemetry_quarantine")
            if any(item.get("quarantine_id") == record.quarantine_id for item in values):
                # A duplicate malformed event retains its first-seen observation rather than
                # turning an optional telemetry retry into an immutable-record failure.
                return False
            values.append(payload)
            atomic_write_json(self._path("codex_telemetry_quarantine"), values)
        return True

    def records(self) -> list[CodexTelemetryRecord]:
        return [CodexTelemetryRecord.model_validate(item) for item in self._read("codex_telemetry")]

    def quarantined(self) -> list[TelemetryQuarantineRecord]:
        return [TelemetryQuarantineRecord.model_validate(item) for item in self._read("codex_telemetry_quarantine")]


def _quarantine(
    store: CodexTelemetryStore,
    *,
    source: Literal["codex_otel", "codex_local_session"],
    reason: str,
    event_name: str,
    source_schema_version: str,
    fingerprint: str,
    original_event_id: str = "",
) -> str:
    quarantine_id = _stable_id("codex-telemetry-quarantine", source, event_name, fingerprint, original_event_id, reason)
    store.quarantine(TelemetryQuarantineRecord(
        quarantine_id=quarantine_id,
        source=source,
        reason=reason,
        event_name=event_name or "unknown",
        source_schema_version=source_schema_version or "unknown",
        schema_fingerprint=fingerprint,
        original_event_id=original_event_id,
        observed_at=_now(),
    ))
    return quarantine_id


def _non_negative_int_identity(attributes: dict[str, object], *keys: str) -> int:
    value = _identity(attributes, *keys)
    if not value:
        return 0
    parsed = int(value)
    if parsed < 0:
        raise ValueError("Identity value must be non-negative")
    return parsed


def ingest_codex_otel(
    project_name: str,
    payload: object,
    *,
    enabled: bool = True,
    stale_after_days: int = 30,
    now: datetime | None = None,
) -> TelemetryIngestionResult:
    if not enabled:
        return TelemetryIngestionResult(
            source="codex_otel", adapter_version=OTEL_ADAPTER_VERSION, availability="disabled"
        )
    store = CodexTelemetryStore(project_name)
    accepted: list[str] = []
    duplicates: list[str] = []
    quarantined: list[str] = []
    ignored = 0
    reference_time = now or datetime.now(timezone.utc)
    for sequence, raw in enumerate(_iter_otel_events(payload), start=1):
        fingerprint = schema_fingerprint(raw)
        event_name = str(raw.get("event_name") or raw.get("name") or "").strip()
        original_event_id = str(raw.get("event_id") or "").strip()
        if event_name not in _SUPPORTED_OTEL_EVENTS:
            quarantined.append(_quarantine(
                store, source="codex_otel", reason="unsupported_event_type", event_name=event_name,
                source_schema_version=OTEL_SCHEMA_VERSION, fingerprint=fingerprint,
                original_event_id=original_event_id,
            ))
            continue
        try:
            timestamp = _otel_timestamp(raw.get("timestamp"))
        except (TypeError, ValueError, OverflowError):
            quarantined.append(_quarantine(
                store, source="codex_otel", reason="missing_or_malformed_timestamp", event_name=event_name,
                source_schema_version=OTEL_SCHEMA_VERSION, fingerprint=fingerprint,
                original_event_id=original_event_id,
            ))
            continue
        if reference_time - _parse_time(timestamp) > timedelta(days=stale_after_days):
            quarantined.append(_quarantine(
                store, source="codex_otel", reason="stale_event", event_name=event_name,
                source_schema_version=OTEL_SCHEMA_VERSION, fingerprint=fingerprint,
                original_event_id=original_event_id,
            ))
            continue
        attributes = _decode_otlp_attributes(raw.get("attributes", {}))
        correlation = _correlate(project_name, attributes)
        if correlation.status == "quarantined":
            quarantined.append(_quarantine(
                store, source="codex_otel", reason="cross_project_identity", event_name=event_name,
                source_schema_version=OTEL_SCHEMA_VERSION, fingerprint=fingerprint,
                original_event_id=original_event_id,
            ))
            continue
        safe = {
            key: primitive
            for key, value in attributes.items()
            if key in _SAFE_OTEL_ATTRIBUTE_KEYS and (primitive := _primitive(value)) is not None
        }
        metric_values = {
            _METRIC_KEY_MAP[key]: value
            for key, value in safe.items()
            if key in _METRIC_KEY_MAP
        }
        if event_name == "codex.api_request":
            metric_values["model_requests"] = 1
        if event_name in {"codex.tool_result", "codex.tool.call"}:
            metric_values["tool_calls"] = 1
        if event_name == "codex.turn.token_usage":
            token_type = str(safe.get("token_type", ""))
            token_value = safe.get("value", safe.get("count"))
            if token_type in {"total", "input", "cached_input", "output", "reasoning_output"} and isinstance(token_value, (int, float)):
                mapped = {
                    "total": "total_tokens", "input": "input_tokens",
                    "cached_input": "cached_input_tokens", "output": "output_tokens",
                    "reasoning_output": "reasoning_tokens",
                }[token_type]
                metric_values[mapped] = token_value
        source_schema_version = str(safe.get("app.version") or safe.get("cli_version") or OTEL_SCHEMA_VERSION)
        context_identity = {
            key: value for key, value in {
                "project_name": project_name if correlation.status == "correlated" else "",
                "work_request_id": _identity(attributes, "ai_builder_os.work_request_id", "work_request_id"),
                "trace_id": _identity(attributes, "trace_id"),
                "session_id": _identity(attributes, "session_id", "conversation_id"),
                "turn_id": _identity(attributes, "turn_id"),
                "tool_name": _identity(attributes, "mcp_tool", "tool_name", "tool"),
            }.items() if value
        }
        context_contributions: list[ContextContribution] = []
        observed_size = metric_values.get("tool_result_observed_characters")
        if isinstance(observed_size, (int, float)) and observed_size >= 0:
            context_contributions.append(numeric_contribution(
                "tool_results", int(observed_size), unit="characters",
                source="codex_otel_tool_result_size",
                workflow_identity=context_identity,
                adapter_version=OTEL_ADAPTER_VERSION,
                source_schema_version=source_schema_version,
                limitation="Codex OTel reported an observed tool-result size; model prompt retention remains unknown.",
            ))
        prompt_length = metric_values.get("prompt_length_characters")
        if isinstance(prompt_length, (int, float)) and prompt_length >= 0:
            context_contributions.append(numeric_contribution(
                "session_context", int(prompt_length), unit="characters",
                source="codex_otel_user_prompt_length",
                workflow_identity=context_identity,
                adapter_version=OTEL_ADAPTER_VERSION,
                source_schema_version=source_schema_version,
                limitation="Codex OTel reported user-prompt length only; the complete host-managed prompt remains unavailable.",
            ))
        telemetry_id = _stable_id(
            "codex-otel", original_event_id or event_name, timestamp, sequence,
            json.dumps(safe, sort_keys=True, separators=(",", ":")),
        )
        try:
            record = CodexTelemetryRecord(
                telemetry_id=telemetry_id,
                project_name=project_name if correlation.status == "correlated" else "",
                timestamp=timestamp,
                event_name=event_name,
                source="codex_otel",
                evidence_class="attributable",
                stability="supported",
                adapter_version=OTEL_ADAPTER_VERSION,
                source_schema_version=source_schema_version,
                schema_fingerprint=fingerprint,
                privacy_classification="aggregate_usage" if metric_values else "operational_metadata",
                original_event_id=original_event_id,
                sequence=sequence,
                session_id=_identity(attributes, "session_id", "conversation_id"),
                turn_id=_identity(attributes, "turn_id"),
                trace_id=_identity(attributes, "trace_id"),
                work_request_id=_identity(attributes, "ai_builder_os.work_request_id", "work_request_id"),
                requirement_id=_identity(attributes, "ai_builder_os.requirement_id", "requirement_id"),
                proposal_id=_identity(attributes, "ai_builder_os.proposal_id", "proposal_id"),
                proposal_revision=_non_negative_int_identity(
                    attributes, "ai_builder_os.proposal_revision", "proposal_revision"
                ),
                mcp_server=_identity(attributes, "mcp_server"),
                tool_name=_identity(attributes, "mcp_tool", "tool_name", "tool"),
                outcome=str(safe.get("success", safe.get("status", safe.get("decision", "")))).lower(),
                duration_ms=float(safe["duration_ms"]) if isinstance(safe.get("duration_ms"), (int, float)) else None,
                metric_values=metric_values,
                context_contributions=context_contributions,
                correlation=correlation,
            )
            recorded = store.record(record)
        except (TypeError, ValueError):
            quarantined.append(_quarantine(
                store, source="codex_otel", reason="normalization_error", event_name=event_name,
                source_schema_version=source_schema_version, fingerprint=fingerprint,
                original_event_id=original_event_id,
            ))
            continue
        if recorded:
            accepted.append(record.telemetry_id)
        else:
            duplicates.append(record.telemetry_id)
    availability: Availability = "quarantined" if quarantined and not accepted else "available"
    return TelemetryIngestionResult(
        source="codex_otel", accepted_ids=accepted, duplicate_ids=duplicates,
        quarantined_ids=quarantined, ignored_count=ignored,
        adapter_version=OTEL_ADAPTER_VERSION, availability=availability,
    )


_LOCAL_REQUIRED_PATHS = {
    "session_meta": {
        "payload.cli_version": str, "payload.session_id": str, "payload.model_provider": str,
    },
    "turn_context": {
        "payload.turn_id": str, "payload.model": str, "payload.effort": str,
    },
    "token_count": {
        "payload.info.model_context_window": (int, float),
        "payload.info.last_token_usage.input_tokens": (int, float),
        "payload.info.last_token_usage.cached_input_tokens": (int, float),
        "payload.info.last_token_usage.cache_write_input_tokens": (int, float),
        "payload.info.last_token_usage.output_tokens": (int, float),
        "payload.info.last_token_usage.reasoning_output_tokens": (int, float),
        "payload.info.last_token_usage.total_tokens": (int, float),
    },
    "task_started": {"payload.turn_id": str, "payload.started_at": str},
    "task_complete": {"payload.turn_id": str, "payload.completed_at": str, "payload.duration_ms": (int, float)},
}


def _path_value(value: object, path: str) -> object:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def _local_event_name(raw: dict[str, object]) -> str:
    if raw.get("type") in {"session_meta", "turn_context"}:
        return str(raw.get("type"))
    payload = raw.get("payload")
    return str(payload.get("type", "")) if isinstance(payload, dict) else ""


def _local_relevant_schema(raw: dict[str, object], event_name: str) -> dict[str, str]:
    descriptor: dict[str, str] = {}
    for path in sorted(_LOCAL_REQUIRED_PATHS[event_name]):
        value = _path_value(raw, path)
        descriptor[path] = type(value).__name__
    return descriptor


def ingest_codex_local_session(
    project_name: str,
    records: Iterable[dict[str, object] | str],
    *,
    enabled: bool = True,
    accepted_fingerprints: set[str] | None = None,
) -> TelemetryIngestionResult:
    if not enabled:
        return TelemetryIngestionResult(
            source="codex_local_session", adapter_version=LOCAL_ADAPTER_VERSION, availability="disabled"
        )
    store = CodexTelemetryStore(project_name)
    accepted: list[str] = []
    duplicates: list[str] = []
    quarantined: list[str] = []
    ignored = 0
    session_id = ""
    cli_version = "unknown"
    active_turn_id = ""
    active_model = ""
    active_effort = ""
    for sequence, item in enumerate(records, start=1):
        try:
            raw = json.loads(item) if isinstance(item, str) else dict(item)
        except (json.JSONDecodeError, TypeError, ValueError):
            fingerprint = schema_fingerprint({"malformed": type(item).__name__})
            quarantined.append(_quarantine(
                store, source="codex_local_session", reason="malformed_json_record",
                event_name="unknown", source_schema_version=LOCAL_SCHEMA_VERSION,
                fingerprint=fingerprint,
            ))
            continue
        event_name = _local_event_name(raw)
        if event_name not in _LOCAL_REQUIRED_PATHS:
            ignored += 1
            continue
        try:
            descriptor = _local_relevant_schema(raw, event_name)
            fingerprint = schema_fingerprint(descriptor)
            for path, expected in _LOCAL_REQUIRED_PATHS[event_name].items():
                if not isinstance(_path_value(raw, path), expected):
                    raise TypeError(path)
        except (KeyError, TypeError, ValueError):
            fingerprint = schema_fingerprint({"event_name": event_name, "shape": _schema_descriptor(raw)})
            quarantined.append(_quarantine(
                store, source="codex_local_session", reason="incompatible_schema",
                event_name=event_name, source_schema_version=LOCAL_SCHEMA_VERSION,
                fingerprint=fingerprint,
            ))
            continue
        if accepted_fingerprints is not None and fingerprint not in accepted_fingerprints:
            quarantined.append(_quarantine(
                store, source="codex_local_session", reason="unapproved_schema_fingerprint",
                event_name=event_name, source_schema_version=LOCAL_SCHEMA_VERSION,
                fingerprint=fingerprint,
            ))
            continue
        payload = raw["payload"]
        assert isinstance(payload, dict)
        if event_name == "session_meta":
            session_id = str(payload["session_id"])
            cli_version = str(payload["cli_version"])
        elif event_name == "turn_context":
            active_turn_id = str(payload["turn_id"])
            active_model = str(payload["model"])
            active_effort = str(payload["effort"])
        timestamp = str(raw.get("timestamp") or payload.get("started_at") or payload.get("completed_at") or "")
        try:
            normalized_time = _parse_time(timestamp).isoformat()
        except ValueError:
            quarantined.append(_quarantine(
                store, source="codex_local_session", reason="missing_or_malformed_timestamp",
                event_name=event_name, source_schema_version=f"{LOCAL_SCHEMA_VERSION}:{cli_version}",
                fingerprint=fingerprint,
            ))
            continue
        metric_values: dict[str, Primitive] = {}
        duration_ms: float | None = None
        turn_id = str(payload.get("turn_id") or active_turn_id)
        if event_name == "turn_context":
            metric_values = {"model": active_model, "reasoning_effort": active_effort}
        elif event_name == "token_count":
            info = payload["info"]
            assert isinstance(info, dict)
            usage = info["last_token_usage"]
            assert isinstance(usage, dict)
            metric_values = {
                "input_tokens": int(usage["input_tokens"]),
                "cached_input_tokens": int(usage["cached_input_tokens"]),
                "cache_write_tokens": int(usage["cache_write_input_tokens"]),
                "output_tokens": int(usage["output_tokens"]),
                "reasoning_tokens": int(usage["reasoning_output_tokens"]),
                "total_tokens": int(usage["total_tokens"]),
                "model_context_window": int(info["model_context_window"]),
            }
        elif event_name == "task_complete":
            duration_ms = float(payload["duration_ms"])
            metric_values["turn_duration_ms"] = duration_ms
        telemetry_id = _stable_id(
            "codex-local", session_id, turn_id, event_name, sequence, normalized_time, fingerprint
        )
        try:
            record = CodexTelemetryRecord(
                telemetry_id=telemetry_id,
                project_name="",
                timestamp=normalized_time,
                event_name=f"codex.local.{event_name}",
                source="codex_local_session",
                evidence_class="experimental",
                stability="versioned_experimental",
                adapter_version=LOCAL_ADAPTER_VERSION,
                source_schema_version=f"{LOCAL_SCHEMA_VERSION}:{cli_version}",
                schema_fingerprint=fingerprint,
                privacy_classification="aggregate_usage" if metric_values else "operational_metadata",
                sequence=sequence,
                session_id=session_id,
                turn_id=turn_id,
                duration_ms=duration_ms,
                metric_values=metric_values,
                correlation=TelemetryCorrelation(
                    status="uncorrelated",
                    limitation="Local session metadata has no exact AI Builder OS project/work-request identity; timestamp correlation is prohibited.",
                ),
            )
            recorded = store.record(record)
        except (TypeError, ValueError):
            quarantined.append(_quarantine(
                store, source="codex_local_session", reason="normalization_error",
                event_name=event_name, source_schema_version=f"{LOCAL_SCHEMA_VERSION}:{cli_version}",
                fingerprint=fingerprint,
            ))
            continue
        if recorded:
            accepted.append(record.telemetry_id)
        else:
            duplicates.append(record.telemetry_id)
    availability: Availability = "quarantined" if quarantined and not accepted else "available"
    return TelemetryIngestionResult(
        source="codex_local_session", accepted_ids=accepted, duplicate_ids=duplicates,
        quarantined_ids=quarantined, ignored_count=ignored,
        adapter_version=LOCAL_ADAPTER_VERSION, availability=availability,
    )


def summarize_correlated_telemetry(
    project_name: str,
    *,
    work_request_id: str = "",
    trace_id: str = "",
    session_id: str = "",
) -> CodexTelemetryRunEvidence:
    if not any((work_request_id, trace_id, session_id)):
        raise ValueError("Telemetry summary requires an exact workflow identity")
    records = [
        item for item in CodexTelemetryStore(project_name).records()
        if item.correlation.status == "correlated"
        and (not work_request_id or item.work_request_id == work_request_id)
        and (not trace_id or item.trace_id == trace_id)
        and (not session_id or item.session_id == session_id)
    ]
    values: dict[str, Primitive] = {}
    classes: dict[str, EvidenceClass] = {}
    contribution_index: dict[str, ContextContribution] = {}
    additive = {"model_requests", "tool_calls"}
    for record in records:
        for metric, value in record.metric_values.items():
            if metric in additive and isinstance(value, (int, float)):
                values[metric] = float(values.get(metric, 0)) + value
            else:
                values[metric] = value
            classes[metric] = record.evidence_class
        for contribution in record.context_contributions:
            contribution_index[contribution.contribution_id] = contribution
    limitations = [] if records else ["No deterministically correlated telemetry records matched the identity."]
    if records:
        host_unknown = unavailable_host_context(workflow_identity={
            key: value for key, value in {
                "project_name": project_name,
                "work_request_id": work_request_id,
                "trace_id": trace_id,
                "session_id": session_id,
            }.items() if value
        })
        contribution_index[host_unknown.contribution_id] = host_unknown
        limitations.append("Host-managed prompt composition remains unavailable outside measured contributions.")
    return CodexTelemetryRunEvidence(
        project_name=project_name,
        work_request_id=work_request_id,
        trace_id=trace_id,
        session_id=session_id,
        source_record_ids=sorted(item.telemetry_id for item in records),
        metric_values=values,
        metric_classes=classes,
        context_contributions=[contribution_index[key] for key in sorted(contribution_index)],
        limitations=limitations,
    )

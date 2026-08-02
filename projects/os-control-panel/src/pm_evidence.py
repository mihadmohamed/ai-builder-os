from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from pm_contract import PMFirstPartyEvidenceSource, PMMode, PMModeEvidencePacket, PMSourceState


OPTIONAL_SOURCE_KINDS = ("customer_feedback", "analytics", "experiment")
ALL_SOURCE_KINDS = (
    "product_history",
    "implementation",
    "qa",
    "release",
    *OPTIONAL_SOURCE_KINDS,
)
SAFE_REFERENCE_FIELDS = (
    "id",
    "title",
    "summary",
    "status",
    "occurred_at",
    "requirement_id",
    "metric",
    "value",
    "unit",
    "variant",
    "confidence",
    "provenance",
)
MAX_SOURCE_BYTES = 64_000
MAX_REFERENCES = 50
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
SECRET_RE = re.compile(r"(?i)\b(api[_ -]?key|token|password|secret)\s*[:=]\s*\S+")


def _redact(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return SECRET_RE.sub(r"\1=[REDACTED]", EMAIL_RE.sub("[REDACTED_EMAIL]", value))


def _safe_reference(payload: dict[str, Any]) -> dict[str, Any]:
    reference: dict[str, Any] = {}
    for field in SAFE_REFERENCE_FIELDS:
        value = payload.get(field)
        if isinstance(value, (str, int, float, bool)) and str(value).strip():
            reference[field] = _redact(value)
    return reference


def _history_reference(event: dict[str, Any]) -> dict[str, Any]:
    return _safe_reference(
        {
            "id": event.get("event_id", ""),
            "title": str(event.get("event_type", "workflow_event")).replace("_", " ").title(),
            "summary": event.get("summary") or event.get("intent") or event.get("approval_summary") or "",
            "status": event.get("status", ""),
            "occurred_at": event.get("recorded_at", ""),
            "requirement_id": event.get("requirement_id", ""),
        }
    )


def _load_optional_records(evidence_root: Path, relative_path: str) -> list[dict[str, Any]]:
    candidate = (evidence_root / relative_path).resolve()
    root = evidence_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Configured PM evidence path escapes product/evidence")
    if not candidate.is_file():
        raise FileNotFoundError(relative_path)
    if candidate.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Configured PM evidence source exceeds the 64KB bound")
    text = candidate.read_text(encoding="utf-8")
    if candidate.suffix == ".jsonl":
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    elif candidate.suffix == ".json":
        decoded = json.loads(text)
        values = decoded if isinstance(decoded, list) else [decoded]
    else:
        raise ValueError("Configured PM evidence sources must be JSON or JSONL")
    if not all(isinstance(item, dict) for item in values):
        raise ValueError("Configured PM evidence records must be objects")
    return [item for item in (_safe_reference(value) for value in values[:MAX_REFERENCES]) if item]


def _optional_sources(project_root: Path) -> dict[str, PMFirstPartyEvidenceSource]:
    evidence_root = project_root / "product" / "evidence"
    manifest_path = evidence_root / "sources.json"
    configured: dict[str, dict[str, Any]] = {}
    manifest_error = ""
    if manifest_path.is_file():
        try:
            if manifest_path.stat().st_size > MAX_SOURCE_BYTES:
                raise ValueError("Evidence manifest exceeds the 64KB bound")
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != "2026-07-21.pm-evidence-sources.v1":
                raise ValueError("Unsupported evidence manifest schema_version")
            entries = payload.get("sources", [])
            if not isinstance(entries, list):
                raise ValueError("Evidence manifest sources must be a list")
            for entry in entries:
                if not isinstance(entry, dict) or entry.get("kind") not in OPTIONAL_SOURCE_KINDS:
                    raise ValueError("Evidence manifest contains an unsupported source kind")
                kind = str(entry["kind"])
                if kind in configured:
                    raise ValueError(f"Duplicate configured evidence source: {kind}")
                configured[kind] = entry
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            manifest_error = str(exc)

    sources: dict[str, PMFirstPartyEvidenceSource] = {}
    for kind in OPTIONAL_SOURCE_KINDS:
        entry = configured.get(kind)
        if manifest_error:
            sources[kind] = PMFirstPartyEvidenceSource(
                kind=kind,
                configured=True,
                available=False,
                source_id=f"manifest:{kind}",
                unavailable_reason=f"Evidence manifest is invalid: {manifest_error}",
            )
            continue
        if entry is None:
            sources[kind] = PMFirstPartyEvidenceSource(
                kind=kind,
                configured=False,
                available=False,
                source_id=f"unconfigured:{kind}",
                unavailable_reason="No privacy-bounded first-party source is configured.",
            )
            continue
        owner = str(entry.get("owner", "")).strip()
        boundary = str(entry.get("privacy_boundary", "")).strip()
        relative_path = str(entry.get("path", "")).strip()
        source_id = str(entry.get("source_id", kind)).strip()
        if not owner or not boundary or not relative_path or not source_id:
            sources[kind] = PMFirstPartyEvidenceSource(
                kind=kind,
                configured=True,
                available=False,
                source_id=source_id or f"invalid:{kind}",
                owner=owner,
                privacy_boundary=boundary,
                unavailable_reason="Configured evidence requires source_id, owner, privacy_boundary, and path.",
            )
            continue
        try:
            references = _load_optional_records(evidence_root, relative_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            sources[kind] = PMFirstPartyEvidenceSource(
                kind=kind,
                configured=True,
                available=False,
                source_id=source_id,
                owner=owner,
                privacy_boundary=boundary,
                unavailable_reason=f"Configured evidence is unavailable: {exc}",
            )
        else:
            sources[kind] = PMFirstPartyEvidenceSource(
                kind=kind,
                configured=True,
                available=bool(references),
                source_id=source_id,
                owner=owner,
                privacy_boundary=boundary,
                references=references,
                unavailable_reason="" if references else "Configured evidence contains no safe records.",
            )
    return sources


def build_pm_mode_evidence(
    project_name: str,
    mode: PMMode,
    target_requirement_ids: list[str],
    source_state: PMSourceState,
) -> PMModeEvidencePacket:
    """Build a deterministic, bounded first-party evidence availability packet."""
    from control_plane.storage import project_path, read_history
    from workspace import list_approvals, list_implementation_runs

    history = read_history(project_name, limit=200)
    target_ids = {item.strip() for item in target_requirement_ids if item.strip()}
    filtered_history = []
    for event in history:
        if mode == "outcome_review" and event.get("event_type") in {
            "pm_proposal_submitted",
            "pm_proposal_rejected",
        }:
            continue
        if target_ids and mode == "outcome_review":
            if (
                event.get("requirement_id") not in target_ids
                and event.get("review_target_id") not in target_ids
            ):
                continue
        elif target_ids and event.get("requirement_id") not in {None, "", *target_ids}:
            continue
        filtered_history.append(event)
    history_refs = [item for item in (_history_reference(event) for event in filtered_history) if item]

    implementation_refs = []
    for run in list_implementation_runs(project_name):
        if target_ids and run.requirement_id not in target_ids:
            continue
        implementation_refs.append(
            _safe_reference(
                {
                    "id": run.run_id,
                    "title": f"{run.requirement_id} implementation",
                    "summary": run.summary or run.error,
                    "status": run.status,
                    "occurred_at": run.finished_at or run.started_at or run.created_at,
                    "requirement_id": run.requirement_id,
                }
            )
        )
    implementation_refs = [item for item in implementation_refs if item][:MAX_REFERENCES]

    qa_refs: list[dict[str, Any]] = []
    release_refs: list[dict[str, Any]] = []
    for approval in list_approvals(project_name):
        requirement_id = str(approval.payload.get("requirement_id", "")).strip()
        if target_ids and requirement_id not in target_ids:
            continue
        target = (
            release_refs
            if approval.approval_type == "release_delivery"
            else qa_refs
            if "qa" in approval.approval_type or "quality" in approval.approval_type
            else None
        )
        if target is not None:
            target.append(
                _safe_reference(
                    {
                        "id": approval.approval_id,
                        "title": approval.title,
                        "summary": approval.summary,
                        "status": approval.status,
                        "occurred_at": approval.resolved_at or approval.created_at,
                        "requirement_id": requirement_id,
                    }
                )
            )
    for event in filtered_history:
        event_type = str(event.get("event_type", "")).casefold()
        target = qa_refs if "qa" in event_type or "quality" in event_type else release_refs if "release" in event_type or "publication" in event_type else None
        if target is not None:
            reference = _history_reference(event)
            if reference:
                target.append(reference)

    def canonical(kind: str, refs: list[dict[str, Any]], empty: str) -> PMFirstPartyEvidenceSource:
        bounded = refs[:MAX_REFERENCES]
        return PMFirstPartyEvidenceSource(
            kind=kind,
            configured=True,
            available=bool(bounded),
            source_id=f"canonical:{kind}",
            owner="AI Builder OS canonical product state",
            privacy_boundary="Safe canonical fields only",
            references=bounded,
            unavailable_reason="" if bounded else empty,
        )

    optional_sources = _optional_sources(project_path(project_name))
    if target_ids and mode == "outcome_review":
        for kind, source in optional_sources.items():
            matching = [
                reference
                for reference in source.references
                if str(reference.get("requirement_id", "")).strip() in target_ids
            ]
            optional_sources[kind] = source.model_copy(
                update={
                    "available": bool(matching),
                    "references": matching,
                    "unavailable_reason": (
                        ""
                        if matching
                        else "Configured evidence contains no safe records for the requested requirement."
                    ),
                }
            )

    sources = {
        "product_history": canonical("product_history", history_refs, "No matching canonical history is available."),
        "implementation": canonical("implementation", implementation_refs, "Implementation evidence is unavailable."),
        "qa": canonical("qa", qa_refs, "QA evidence is unavailable."),
        "release": canonical("release", release_refs, "Release evidence is unavailable."),
        **optional_sources,
    }
    ordered = [sources[kind] for kind in ALL_SOURCE_KINDS]
    return PMModeEvidencePacket(
        project_name=project_name,
        mode=mode,
        target_requirement_ids=sorted(target_ids),
        sources=ordered,
        missing_sources=[item.kind for item in ordered if not item.available],
        source_state=source_state,
    )

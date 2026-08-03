from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from pm_contract import (
    PMEvidenceReference,
    PMModeEvidencePacket,
    PMReviewEvidencePacket,
    PMSourceState,
)


_WORD_RE = re.compile(r"[a-z0-9]{3,}")
_SAFE_HISTORY_FIELDS = (
    "summary",
    "intent",
    "status",
    "approval_summary",
    "requirement_id",
    "tests",
)


def _words(value: str) -> set[str]:
    return set(_WORD_RE.findall(value.casefold()))


def _history_summary(event: dict[str, Any]) -> str:
    parts: list[str] = []
    for field in _SAFE_HISTORY_FIELDS:
        value = event.get(field)
        if isinstance(value, list):
            text = "; ".join(str(item) for item in value if str(item).strip())
        elif isinstance(value, (str, int, float, bool)):
            text = str(value).strip()
        else:
            text = ""
        if text and text not in parts:
            parts.append(text)
    return " · ".join(parts)[:2_000] or "Recorded workflow evidence."


def _reference(
    evidence_type: str,
    source_id: str,
    title: str,
    summary: str,
    *,
    status: str = "",
    occurred_at: str = "",
    available: bool = True,
    provenance: str = "",
    confidence: str = "",
    stale: bool = False,
) -> PMEvidenceReference:
    return PMEvidenceReference(
        evidence_type=evidence_type,
        source_id=source_id,
        title=title[:300],
        status=status[:100],
        occurred_at=occurred_at,
        summary=summary[:2_000],
        available=available,
        provenance=provenance[:500],
        confidence=confidence if confidence in {"low", "medium", "high", "unknown"} else "",
        stale=stale,
    )


def _parse_time(value: str) -> datetime | None:
    normalized = value.strip()
    if not normalized:
        return None
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).astimezone(timezone.utc)


def _review_due_at(review_window: str, release_at: str) -> datetime | None:
    explicit = _parse_time(review_window)
    if explicit is not None:
        return explicit
    released = _parse_time(release_at)
    if released is None:
        return None
    match = re.search(
        r"\b(\d{1,4})\s*(day|days|week|weeks|month|months)\b",
        review_window,
        re.I,
    )
    if match is None:
        return None
    count = int(match.group(1))
    unit = match.group(2).casefold()
    days = count * (7 if unit.startswith("week") else 30 if unit.startswith("month") else 1)
    return released + timedelta(days=days)


def _learning_review_state(
    *,
    review_window: str,
    release_at: str,
    has_outcome_signal: bool,
    pending: bool,
    reviewed: bool,
) -> tuple[str, str]:
    due_at = _review_due_at(review_window, release_at)
    due_value = due_at.isoformat() if due_at is not None else ""
    if reviewed:
        return "reviewed", due_value
    if pending:
        return "decision_pending", due_value
    if due_at is not None and due_at > datetime.now(timezone.utc):
        return "not_yet_due", due_value
    if not review_window.strip() or not release_at.strip() or not has_outcome_signal:
        return "insufficient_evidence", due_value
    return "ready", due_value


def _deduplicate(
    references: list[PMEvidenceReference],
    *,
    target_identity: tuple[str, str],
) -> tuple[list[PMEvidenceReference], int]:
    unique: dict[tuple[str, str], PMEvidenceReference] = {}
    for item in references:
        unique.setdefault((item.evidence_type, item.source_id), item)
    ordered = sorted(
        unique.values(),
        key=lambda item: (
            item.evidence_type,
            item.occurred_at,
            item.source_id,
        ),
    )
    if len(ordered) <= 50:
        return ordered, 0

    # Preserve the review anchor and at least one representative from every
    # available evidence category before filling the bounded packet. Without
    # this reservation a large implementation history could evict the
    # requirement/artifact under review or every QA, release, or outcome item.
    selected: list[PMEvidenceReference] = []
    selected_identities: set[tuple[str, str]] = set()

    def reserve(item: PMEvidenceReference | None) -> None:
        if item is None:
            return
        identity = (item.evidence_type, item.source_id)
        if identity in selected_identities:
            return
        selected.append(item)
        selected_identities.add(identity)

    reserve(unique.get(target_identity))
    evidence_types = sorted({item.evidence_type for item in ordered})
    for evidence_type in evidence_types:
        candidates = [item for item in ordered if item.evidence_type == evidence_type]
        reserve(max(candidates, key=lambda item: (item.occurred_at, item.source_id)))
    for item in ordered:
        if len(selected) >= 50:
            break
        reserve(item)

    bounded = sorted(
        selected,
        key=lambda item: (
            item.evidence_type,
            item.occurred_at,
            item.source_id,
        ),
    )
    return bounded, len(ordered) - len(bounded)


def build_pm_review_evidence(
    project_name: str,
    review_mode: str,
    target_id: str,
    *,
    mode_evidence: PMModeEvidencePacket | None = None,
    source_state: PMSourceState | None = None,
) -> PMReviewEvidencePacket:
    """Build a stable, bounded PM packet without raw payloads or runtime secrets."""
    from control_plane.storage import read_history
    from workspace import (
        list_approvals,
        list_implementation_runs,
        load_requirement_document,
        load_task_document,
    )

    target_id = target_id.strip()
    if review_mode not in {"artifact_review", "outcome_review"}:
        raise ValueError("review_mode must be artifact_review or outcome_review")
    if not target_id:
        raise ValueError("target_id must not be empty")

    requirement_document = load_requirement_document(project_name)
    requirements = sorted(
        requirement_document.all_requirements,
        key=lambda item: int(item.id.removeprefix("R")),
    )
    tasks = sorted(load_task_document(project_name).tasks, key=lambda item: item.number)
    approvals = list_approvals(project_name)
    history = read_history(project_name, limit=500)
    references: list[PMEvidenceReference] = []
    missing: list[str] = []
    candidates: list[str] = []

    if review_mode == "artifact_review":
        artifact = next((item for item in approvals if item.approval_id == target_id), None)
        if artifact is None:
            missing.append("Approved artifact metadata is unavailable.")
        else:
            references.append(
                _reference(
                    "artifact",
                    artifact.approval_id,
                    artifact.title or artifact.approval_type.replace("_", " ").title(),
                    artifact.summary or "Approved workflow artifact.",
                    status=artifact.status,
                    occurred_at=artifact.resolved_at or artifact.created_at,
                    available=artifact.status == "APPROVED",
                )
            )
            artifact_words = _words(f"{artifact.title} {artifact.summary}")
            scored: list[tuple[int, str]] = []
            for requirement in requirements:
                if requirement.status == "DONE":
                    continue
                overlap = artifact_words & _words(f"{requirement.title} {requirement.description}")
                if overlap:
                    scored.append((len(overlap), requirement.id))
            candidates = [item[1] for item in sorted(scored, key=lambda item: (-item[0], item[1]))[:10]]

        for requirement in requirements:
            if requirement.id not in candidates:
                continue
            references.append(
                _reference(
                    "requirement_intent",
                    requirement.id,
                    requirement.title,
                    requirement.description,
                    status=requirement.status,
                )
            )
    else:
        from workspace import parse_requirement_outcome_profile

        requirement = next((item for item in requirements if item.id == target_id), None)
        if requirement is None:
            raise ValueError(f"Unknown outcome-review requirement: {target_id}")
        references.append(
            _reference(
                "requirement_intent",
                requirement.id,
                requirement.title,
                requirement.description,
                status=requirement.status,
            )
        )
        outcome_profile = parse_requirement_outcome_profile(requirement.description)
        for task in tasks:
            if target_id in task.requirements:
                references.append(
                    _reference(
                        "task",
                        f"task-{task.number}",
                        task.title,
                        task.body,
                        status=task.status,
                    )
                )
        implementation_found = False
        for run in list_implementation_runs(project_name):
            if run.requirement_id != target_id:
                continue
            implementation_found = True
            references.append(
                _reference(
                    "implementation",
                    run.run_id,
                    f"{target_id} implementation",
                    run.summary or run.error or "Implementation run recorded.",
                    status=run.status,
                    occurred_at=run.finished_at or run.started_at or run.created_at,
                )
            )
        qa_found = False
        release_found = False
        outcome_found = False
        for approval in approvals:
            safe_outcome_reference = approval.payload.get("outcome_reference_id", "").strip()
            safe_requirement_id = approval.payload.get("requirement_id", "").strip()
            if target_id not in {safe_outcome_reference, safe_requirement_id}:
                continue
            evidence_type = (
                "release"
                if approval.approval_type == "release_delivery"
                else "qa"
                if "qa" in approval.approval_type or "quality" in approval.approval_type
                else "outcome_signal"
            )
            qa_found |= evidence_type == "qa"
            release_found |= evidence_type == "release"
            outcome_found |= evidence_type == "outcome_signal"
            references.append(
                _reference(
                    evidence_type,
                    approval.approval_id,
                    approval.title,
                    approval.payload.get("outcome_detail", "").strip() or approval.summary,
                    status=approval.status,
                    occurred_at=approval.resolved_at or approval.created_at,
                )
            )

        if mode_evidence is not None:
            source_type = {
                "implementation": "implementation",
                "qa": "qa",
                "release": "release",
                "customer_feedback": "outcome_signal",
                "analytics": "outcome_signal",
                "experiment": "outcome_signal",
            }
            for source in mode_evidence.sources:
                evidence_type = source_type.get(source.kind)
                if evidence_type is None:
                    continue
                for index, safe in enumerate(source.references):
                    source_id = str(safe.get("id", "")).strip() or f"{source.source_id}:{index}"
                    summary = str(safe.get("summary", "")).strip() or "Safe first-party evidence reference."
                    references.append(
                        _reference(
                            evidence_type,
                            f"{source.kind}:{source_id}",
                            str(safe.get("title", "")).strip() or source.kind.replace("_", " ").title(),
                            summary,
                            status=str(safe.get("status", "")),
                            occurred_at=str(safe.get("occurred_at", "")),
                            provenance=str(safe.get("provenance", "")).strip() or source.source_id,
                            confidence=str(safe.get("confidence", "")).strip().casefold() or "unknown",
                        )
                    )
                    implementation_found |= evidence_type == "implementation"
                    qa_found |= evidence_type == "qa"
                    release_found |= evidence_type == "release"
                    outcome_found |= evidence_type == "outcome_signal"

        for event in history:
            if str(event.get("requirement_id", "")).strip() != target_id:
                continue
            event_type = str(event.get("event_type", "workflow_event"))
            if "implementation" in event_type:
                evidence_type = "implementation"
                implementation_found = True
            elif "qa" in event_type or "quality" in event_type:
                evidence_type = "qa"
                qa_found = True
            elif "release" in event_type or "publication" in event_type:
                evidence_type = "release"
                release_found = True
            elif "outcome" in event_type:
                evidence_type = "outcome_signal"
                outcome_found = True
            elif event_type.startswith("pm_proposal_"):
                evidence_type = "prior_decision"
            else:
                continue
            references.append(
                _reference(
                    evidence_type,
                    str(event.get("event_id", event_type)),
                    event_type.replace("_", " ").title(),
                    _history_summary(event),
                    status=str(event.get("status", "")),
                    occurred_at=str(
                        event.get(
                            "recorded_at",
                            event.get("created_at", event.get("occurred_at", "")),
                        )
                    ),
                )
            )

        if not implementation_found:
            missing.append("Implementation evidence is unavailable.")
        if not qa_found:
            missing.append("QA evidence is unavailable.")
        if not release_found:
            missing.append("Release evidence is unavailable.")
        if not outcome_found:
            missing.append("Outcome signals are unavailable.")

        reviewed = any(
            event.get("event_type") == "pm_proposal_approved"
            and event.get("review_target_id") == target_id
            and bool(event.get("review_action"))
            for event in history
        )
        release_times = [
            item.occurred_at
            for item in references
            if item.evidence_type == "release" and item.available and item.occurred_at
        ]
        release_at = max(release_times, key=lambda value: _parse_time(value) or datetime.min.replace(tzinfo=timezone.utc)) if release_times else ""
        release_time = _parse_time(release_at)
        if release_time is not None:
            references = [
                item.model_copy(
                    update={
                        "stale": bool(
                            item.evidence_type == "outcome_signal"
                            and _parse_time(item.occurred_at) is not None
                            and _parse_time(item.occurred_at) < release_time
                        )
                    }
                )
                for item in references
            ]
        usable_outcome_signal = any(
            item.evidence_type == "outcome_signal" and item.available and not item.stale
            for item in references
        )
        if outcome_found and not usable_outcome_signal:
            missing.append("Only stale outcome signals are available.")
        review_window = outcome_profile.post_release_review or outcome_profile.measurement_window
        review_state, review_due_at = _learning_review_state(
            review_window=review_window,
            release_at=release_at,
            has_outcome_signal=usable_outcome_signal,
            pending=False,
            reviewed=reviewed,
        )
        expected_evidence = list(
            outcome_profile.expected_outcome_evidence
            or outcome_profile.telemetry
            or outcome_profile.success_criteria
        )[:20]
        provenance = (
            sorted(
                {
                    source.source_id
                    for source in mode_evidence.sources
                    if source.available
                }
            )
            if mode_evidence is not None
            else []
        )
        configured_confidence = outcome_profile.evidence_confidence.strip().casefold()
        evidence_confidence = (
            configured_confidence
            if configured_confidence in {"low", "medium", "high", "unknown"}
            else "unknown"
        )
        missing_sources = list(mode_evidence.missing_sources) if mode_evidence is not None else []

    target_identity = (
        ("artifact", target_id)
        if review_mode == "artifact_review"
        else ("requirement_intent", target_id)
    )
    bounded_references, omitted_count = _deduplicate(
        references,
        target_identity=target_identity,
    )
    if omitted_count:
        missing.append(
            f"{omitted_count} additional evidence reference(s) were omitted by the 50-reference packet limit."
        )
    return PMReviewEvidencePacket(
        review_mode=review_mode,
        target_id=target_id,
        references=bounded_references,
        missing_evidence=missing,
        consolidation_candidate_ids=candidates,
        review_state=review_state if review_mode == "outcome_review" else None,
        review_window=review_window if review_mode == "outcome_review" else "",
        review_due_at=review_due_at if review_mode == "outcome_review" else "",
        expected_evidence=expected_evidence if review_mode == "outcome_review" else [],
        evidence_provenance=provenance if review_mode == "outcome_review" else [],
        evidence_confidence=evidence_confidence if review_mode == "outcome_review" else "",
        missing_sources=missing_sources if review_mode == "outcome_review" else [],
        source_state=source_state or PMSourceState(),
    )

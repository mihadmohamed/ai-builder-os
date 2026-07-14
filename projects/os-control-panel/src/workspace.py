from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import io
import json
import errno
import mimetypes
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from pydantic import BaseModel, Field
from PIL import Image, ImageOps

from agents_runtime.support import (
    AgentHandBackError,
    TOOL_REGISTRY,
    grade_agent_traces,
    load_agent_traces,
)
from operations_dashboard import (
    AGENT_ROLE_MODES,
    AgentRolePerformance,
    AgentRunSummary,
    ToolUsageSummary,
    summarize_agent_runs,
    summarize_role_performance,
    summarize_tool_usage,
)
from eval_framework import EVAL_COVERAGE, EvalCaseRecord, load_eval_case_catalog
from github_publication import (
    GitHubPublicationDraft,
    publish_github_publication,
    draft_eval_summary,
    draft_issue_from_requirement,
    draft_pr_description,
)
from runtime_capabilities import api_agents_enabled, web_app_frontend_bundle_installed, web_app_frontend_bundle_summary
from tenancy import active_user_id, active_user_label
from tools.project_registry import ProjectLocation, list_project_locations, load_project_manifest, register_project, resolve_project
from tools.project_repositories import (
    RepositoryActionPlan,
    attach_repository,
    plan_attached_repository,
    plan_standalone_repository,
    publish_standalone_repository,
    scaffold_standalone_repository,
)


@dataclass(frozen=True)
class LearningConceptRecommendation:
    concept: str
    why_now: str
    where_it_connects: str
    suggested_path: str
    current_gap: str
    why_for_you: str


@dataclass(frozen=True)
class LearningCompoundingSignal:
    score_bonus: int = 0
    why_now_addition: str = ""
    current_gap_addition: str = ""
    suggested_path_addition: str = ""
    resurfaced_from_learned: bool = False


@dataclass(frozen=True)
class BuildToLearnPathway:
    concept: str
    learning_goal: str
    experiment_slice: str
    project_anchor: str
    success_signal: str
    capture_prompt: str


@dataclass(frozen=True)
class LearningBuildToLearnLink:
    concept: str
    status: str
    learning_goal: str
    experiment_slice: str
    project_anchor: str
    success_signal: str
    capture_prompt: str
    captured_via: str
    last_updated: str
    outcome_summary: str
    unresolved_after_build: str
    learning_effect: str


@dataclass(frozen=True)
class LearningProgressItem:
    concept: str
    status: str
    latest_understanding: str
    recommended_next_move: str


@dataclass(frozen=True)
class LearningConceptRecord:
    concept: str
    status: str
    current_understanding: str
    open_questions: str
    recommended_next_move: str
    why_now: str
    current_gap: str
    history_count: int
    build_to_learn: LearningBuildToLearnLink | None


@dataclass(frozen=True)
class LearningConceptState:
    concept: str
    status: str
    current_understanding: str
    open_questions: str
    history_count: int


@dataclass(frozen=True)
class LearningConceptView:
    concept: str
    recommendation: LearningConceptRecommendation | None
    concept_state: LearningConceptState | None
    session_state: LearningAgentSession | None
    build_state: LearningBuildToLearnLink | None
    recommended_next_move: str


@dataclass(frozen=True)
class LearningConceptDetailView:
    concept: str
    state_label: str
    history_count: int
    primary_heading: str
    primary_text: str
    secondary_heading: str
    secondary_text: str
    tertiary_heading: str
    tertiary_text: str


@dataclass(frozen=True)
class LearningConceptKnowledge:
    concept: str
    why_now: str
    where_it_connects: str
    what_it_is: str
    why_it_exists: str
    nearby_distinction: str
    os_connection: str
    product_implication: str
    build_learning_goal: str
    build_experiment_slice: str
    build_project_anchor: str
    build_success_signal: str
    build_capture_prompt: str
    hierarchy_parent: str
    hierarchy_children: tuple[str, ...]
    relations: dict[str, tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class LearningConceptTruth:
    concept: str
    concept_facts: tuple[str, ...]
    concept_relationships: tuple[str, ...]
    important_distinctions: tuple[str, ...]
    implementation_anchors: tuple[str, ...]
    risks_and_misconceptions: tuple[str, ...]
    raw_markdown: str


@dataclass(frozen=True)
class LearningConceptFamily:
    name: str
    summary: str
    concepts: tuple[str, ...]
    gateway_concepts: tuple[str, ...]


@dataclass(frozen=True)
class LearningConceptFamilyPlacement:
    concept: str
    family_name: str
    family_summary: str
    concept_role: str
    gateway_concepts: tuple[str, ...]
    sibling_concepts: tuple[str, ...]
    natural_next_concepts: tuple[str, ...]


@dataclass(frozen=True)
class LearningConceptNavigationEntry:
    concept: str
    status: str
    depth: int


@dataclass(frozen=True)
class LearningConceptNavigationSection:
    family_name: str
    family_summary: str
    entries: tuple[LearningConceptNavigationEntry, ...]


@dataclass(frozen=True)
class LearningPlanStep:
    concept: str
    status: str
    depth: int
    is_current: bool
    is_completed: bool


@dataclass(frozen=True)
class LearningPlanFamily:
    family_name: str
    family_summary: str
    steps: tuple[LearningPlanStep, ...]


@dataclass(frozen=True)
class PersonalizedLearningPlan:
    current_concept: str
    current_family_name: str
    families: tuple[LearningPlanFamily, ...]


@dataclass(frozen=True)
class LearningTeachingStrategy:
    entry_point: str
    explanation_order: tuple[str, ...]
    os_context_depth: str
    technical_depth: str
    example_style: str
    coaching_style: str
    emphasis: tuple[str, ...]


@dataclass(frozen=True)
class LearningImplementationAnchor:
    concept: str
    label: str
    path: str
    kind: str
    why_it_matters: str
    excerpt: str


@dataclass(frozen=True)
class LearningConceptRelationship:
    relation: str
    target: str
    rationale: str


@dataclass(frozen=True)
class LearningAgentSession:
    concept: str
    session_status: str
    where_encountered: str
    current_understanding: str
    what_is_unclear: str
    what_it_is: str
    why_it_exists: str
    nearby_distinction: str
    os_connection: str
    product_implication: str
    latest_explanation_back: str
    clarification_response: str
    implementation_walkthrough: str
    implementation_relationships: str
    detected_gaps: tuple[str, ...]
    next_move: str
    coach_message: str
    turn_count: int
    updated_at: str
    proposed_concept_status: str = ""
    hand_back_reason: str = ""


@dataclass(frozen=True)
class LearningUsageStatus:
    user_email: str
    tier: str
    daily_limit: int
    turns_used_today: int
    turns_remaining_today: int


@dataclass(frozen=True)
class LearningOperatorUserSummary:
    user_email: str
    tier: str
    first_seen_at: str
    last_active_at: str
    live_turns_today: int
    turns_remaining_today: int
    concepts_learned: int
    current_concept: str


@dataclass(frozen=True)
class LearningOperatorDashboardSnapshot:
    total_users: int
    active_today: int
    active_last_7d: int
    live_turns_today: int
    logins_today: int
    rate_limit_hits_today: int
    users: tuple[LearningOperatorUserSummary, ...]


SOURCE_REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = SOURCE_REPO_ROOT
RUNTIME_ROOT_ENV = "AI_BUILDER_OS_RUNTIME_ROOT"
LEARNING_RELEASE_PROFILE_ENV = "AI_BUILDER_OS_LEARNING_RELEASE_PROFILE"
INTERNAL_V2_RELEASE_PROFILE = "internal_v2"
EXTERNAL_V2_RELEASE_PROFILE = "external_v2"
LEARNING_ALLOWED_EMAILS_ENV = "LEARNING_AGENT_ALLOWED_EMAILS"
LEARNING_STANDARD_DAILY_TURNS_ENV = "LEARNING_AGENT_STANDARD_DAILY_TURNS"
LEARNING_TRUSTED_DAILY_TURNS_ENV = "LEARNING_AGENT_TRUSTED_DAILY_TURNS"
DEFAULT_STANDARD_DAILY_TURNS = 10
DEFAULT_TRUSTED_DAILY_TURNS = 30


def _runtime_root() -> Path:
    raw = os.getenv(RUNTIME_ROOT_ENV, "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    home = os.getenv("AI_BUILDER_OS_HOME", "").strip()
    base = Path(home).expanduser().resolve() if home else REPO_ROOT / "private" / "ai-builder-os"
    return base / "runtime"


def learning_release_profile() -> str:
    raw = os.getenv(LEARNING_RELEASE_PROFILE_ENV, "").strip().lower()
    if raw == EXTERNAL_V2_RELEASE_PROFILE:
        return EXTERNAL_V2_RELEASE_PROFILE
    return INTERNAL_V2_RELEASE_PROFILE


def learning_reflection_enabled() -> bool:
    return learning_release_profile() == INTERNAL_V2_RELEASE_PROFILE


def learning_build_to_learn_enabled() -> bool:
    return learning_release_profile() == INTERNAL_V2_RELEASE_PROFILE


def learning_concept_incubation_enabled() -> bool:
    return learning_release_profile() == INTERNAL_V2_RELEASE_PROFILE


def _runtime_projects_root() -> Path:
    return _runtime_root() / "projects"


def _draft_projects_root() -> Path:
    return _runtime_root() / ".draft-projects"


def _candidate_project_paths(project_name: str) -> tuple[Path, ...]:
    try:
        return (resolve_project(project_name).workspace_path,)
    except ValueError:
        raw_name = project_name.strip()
        normalized_name = normalize_project_directory_name(project_name)
        names = tuple(dict.fromkeys(name for name in (raw_name, normalized_name) if name))
        return tuple(REPO_ROOT / "projects" / name for name in names)


def _scaffolded_project_path(project_name: str) -> Path | None:
    for candidate in _candidate_project_paths(project_name):
        if candidate.exists() and not validate_project_structure(candidate):
            return candidate
    return None


def _scaffolded_project_directory_name(project_name: str) -> str | None:
    scaffolded = _scaffolded_project_path(project_name)
    return scaffolded.name if scaffolded is not None else None


def _project_runtime_path(project_name: str) -> Path:
    try:
        location = resolve_project(project_name)
        stable_path = _runtime_projects_root() / location.project_id
        legacy_path = _runtime_projects_root() / location.name
        if not stable_path.exists() and legacy_path.exists() and legacy_path != stable_path:
            _merge_directory_without_overwrite(legacy_path, stable_path)
        legacy_project_data = location.workspace_path / "data"
        stable_data = stable_path / "data"
        if legacy_project_data.is_dir():
            for child in legacy_project_data.iterdir():
                if not child.is_file() or child.suffix not in {".json", ".jsonl"}:
                    continue
                stable_data.mkdir(parents=True, exist_ok=True)
                target = stable_data / child.name
                if not target.exists():
                    shutil.copy2(child, target)
        return stable_path
    except ValueError:
        for candidate in _candidate_project_paths(project_name):
            if candidate.exists():
                return candidate
    return _draft_projects_root() / normalize_project_directory_name(project_name)


def _project_runtime_data_path(project_name: str) -> Path:
    return _project_runtime_path(project_name) / "data"


def _project_runtime_user_data_path(project_name: str) -> Path | None:
    user_id = active_user_id()
    if not user_id:
        return None
    return _project_runtime_path(project_name) / "users" / user_id / "data"


def _project_display_name_from_slug(project_name: str) -> str:
    cleaned = re.sub(r"[-_]+", " ", project_name.strip())
    return " ".join(part.capitalize() for part in cleaned.split())


def _legacy_project_data_candidates(project_name: str) -> tuple[Path, ...]:
    normalized_name = normalize_project_directory_name(project_name)
    display_name = _project_display_name_from_slug(normalized_name)
    raw_name = project_name.strip()
    candidates: list[Path] = []
    for name in dict.fromkeys(value for value in (raw_name, display_name) if value and value != normalized_name):
        legacy_data = REPO_ROOT / "projects" / name / "data"
        if legacy_data.exists():
            candidates.append(legacy_data)
    return tuple(candidates)


def _runtime_data_migration_candidates(project_name: str) -> tuple[Path, ...]:
    normalized_name = normalize_project_directory_name(project_name)
    candidates: list[Path] = []
    legacy_runtime_data = _runtime_projects_root() / normalized_name / "data"
    if legacy_runtime_data.exists():
        candidates.append(legacy_runtime_data)
    draft_data = _draft_projects_root() / normalized_name / "data"
    if draft_data.exists():
        candidates.append(draft_data)
    legacy_draft_data = REPO_ROOT / ".draft-projects" / normalized_name / "data"
    if legacy_draft_data.exists():
        candidates.append(legacy_draft_data)
    candidates.extend(_legacy_project_data_candidates(project_name))
    deduped: list[Path] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)
    return tuple(deduped)


def _merge_directory_without_overwrite(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            _merge_directory_without_overwrite(child, target)
            continue
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(child, target)


def _rewrite_site_import_manifest_paths(site_imports_root: Path) -> None:
    for manifest_path in site_imports_root.glob("*/manifest.json"):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(payload, dict):
            continue
        changed = False
        import_root = manifest_path.parent

        saved_images = payload.get("saved_images", [])
        if isinstance(saved_images, list):
            for item in saved_images:
                if not isinstance(item, dict):
                    continue
                saved_path = str(item.get("saved_path", "")).strip()
                if not saved_path:
                    continue
                rewritten = import_root / Path(saved_path).name
                if str(rewritten) != saved_path and rewritten.exists():
                    item["saved_path"] = str(rewritten)
                    changed = True

        grouped_assets = payload.get("grouped_assets", {})
        if isinstance(grouped_assets, dict):
            for items in grouped_assets.values():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    saved_path = str(item.get("saved_path", "")).strip()
                    if not saved_path:
                        continue
                    rewritten = import_root / Path(saved_path).name
                    if str(rewritten) != saved_path and rewritten.exists():
                        item["saved_path"] = str(rewritten)
                        changed = True

        if changed:
            manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _migrate_legacy_project_runtime_data(project_name: str) -> None:
    destination_root = _project_runtime_data_path(project_name)
    migrated_any = False
    for source_root in _runtime_data_migration_candidates(project_name):
        if source_root.resolve() == destination_root.resolve():
            continue
        site_imports = source_root / "site-imports"
        if site_imports.exists():
            _merge_directory_without_overwrite(site_imports, destination_root / "site-imports")
            migrated_any = True
        for filename in ("agent_traces.jsonl", "pm_clarifications.json"):
            source_file = source_root / filename
            target_file = destination_root / filename
            if source_file.exists() and not target_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                migrated_any = True
    if migrated_any:
        destination_root.mkdir(parents=True, exist_ok=True)
        site_imports_root = destination_root / "site-imports"
        if site_imports_root.exists():
            _rewrite_site_import_manifest_paths(site_imports_root)


def _private_reflections_path() -> Path:
    return _private_user_root() / "thinking" / "reflections.md"


def _ensure_private_reflections_file() -> Path:
    path = _private_reflections_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Reflections\n\n"
            "This file is private and local-only.\n\n"
            "Use it for structured reflection entries that follow `reflection-model-v1.md`.\n"
        )
    return path


def _private_concept_notes_path() -> Path:
    return _private_user_root() / "learning" / "concept-notes.md"


def _ensure_private_concept_notes_file() -> Path:
    path = _private_concept_notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Concept Notes\n\n"
            "Use this file to capture concepts that need deeper understanding.\n"
        )
    return path


def _private_build_to_learn_path() -> Path:
    return _private_user_root() / "learning" / "build-to-learn.md"


def _private_learning_profile_path() -> Path:
    return _private_user_root() / "learning" / "learning-profile.json"


def _private_learning_agent_session_path() -> Path:
    return _private_user_root() / "learning" / "learning-agent-session.json"


def _private_user_root() -> Path:
    user_id = active_user_id()
    if user_id:
        return _runtime_root() / "private" / "users" / user_id
    return REPO_ROOT / "private"


def _learning_activity_log_path() -> Path:
    return _runtime_root() / "learning-agent-activity.jsonl"


def _ensure_learning_activity_log() -> Path:
    path = _learning_activity_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    return path


def _learning_allowed_emails() -> set[str]:
    raw = os.getenv(LEARNING_ALLOWED_EMAILS_ENV, "").strip()
    if not raw:
        return set()
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _learning_turn_limit_from_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, value)


def current_learning_access_tier() -> str:
    email = active_user_label().strip().lower()
    if email and email in _learning_allowed_emails():
        return "trusted"
    return "standard"


def _current_learning_daily_limit() -> int:
    if current_learning_access_tier() == "trusted":
        return _learning_turn_limit_from_env(LEARNING_TRUSTED_DAILY_TURNS_ENV, DEFAULT_TRUSTED_DAILY_TURNS)
    return _learning_turn_limit_from_env(LEARNING_STANDARD_DAILY_TURNS_ENV, DEFAULT_STANDARD_DAILY_TURNS)


def _activity_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_activity_timestamp(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _append_learning_activity_event(
    event_type: str,
    *,
    concept: str = "",
    metadata: dict[str, object] | None = None,
) -> Path:
    path = _ensure_learning_activity_log()
    payload = {
        "timestamp": _activity_timestamp(),
        "user_id": active_user_id(),
        "email": active_user_label().strip().lower(),
        "tier": current_learning_access_tier(),
        "event_type": event_type.strip(),
        "concept": concept.strip(),
        "metadata": metadata or {},
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return path


def _load_learning_activity_events() -> list[dict[str, object]]:
    path = _ensure_learning_activity_log()
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(raw, dict):
            records.append(raw)
    return records


LIVE_TURN_EVENT_TYPES = {
    "learning_session_started",
    "learning_clarification_requested",
    "learning_implementation_requested",
}


class LearningRateLimitExceededError(RuntimeError):
    """Raised when the current user has exhausted the daily live-turn limit."""


def record_learning_login() -> None:
    email = active_user_label().strip().lower()
    if not email:
        return
    _append_learning_activity_event("learning_login")


def current_learning_usage_status() -> LearningUsageStatus:
    email = active_user_label().strip().lower()
    tier = current_learning_access_tier()
    daily_limit = _current_learning_daily_limit()
    today = datetime.now(timezone.utc).date()
    turns_used = 0
    for event in _load_learning_activity_events():
        if str(event.get("email") or "").strip().lower() != email:
            continue
        if str(event.get("event_type") or "") not in LIVE_TURN_EVENT_TYPES:
            continue
        when = _parse_activity_timestamp(str(event.get("timestamp") or ""))
        if when is None or when.date() != today:
            continue
        turns_used += 1
    turns_remaining = max(0, daily_limit - turns_used)
    return LearningUsageStatus(
        user_email=email,
        tier=tier,
        daily_limit=daily_limit,
        turns_used_today=turns_used,
        turns_remaining_today=turns_remaining,
    )


def _record_learning_rate_limit_hit(concept: str = "") -> None:
    _append_learning_activity_event("learning_rate_limit_blocked", concept=concept)


def ensure_learning_turn_available(concept: str = "") -> LearningUsageStatus:
    status = current_learning_usage_status()
    if status.turns_remaining_today <= 0:
        _record_learning_rate_limit_hit(concept)
        tier_label = "Trusted access" if status.tier == "trusted" else "Open access"
        raise LearningRateLimitExceededError(
            f"{tier_label} includes {status.daily_limit} live turns per day. You’ve used them all for today. Please come back tomorrow."
        )
    return status


def log_learning_live_turn(event_type: str, *, concept: str = "") -> LearningUsageStatus:
    _append_learning_activity_event(event_type, concept=concept)
    return current_learning_usage_status()


def _user_learning_root(user_id: str) -> Path:
    return _runtime_root() / "private" / "users" / user_id / "learning"


def _load_learning_profile_for_user(user_id: str) -> dict[str, object]:
    path = _user_learning_root(user_id) / "learning-profile.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def _load_learning_concept_state_for_user(user_id: str) -> dict[str, object]:
    path = _user_learning_root(user_id) / "concept-state.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    concepts = raw.get("concepts") if isinstance(raw, dict) else None
    return concepts if isinstance(concepts, dict) else {}


def _load_learning_session_for_user(user_id: str) -> dict[str, object]:
    path = _user_learning_root(user_id) / "learning-agent-session.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def learning_operator_dashboard_snapshot() -> LearningOperatorDashboardSnapshot:
    events = _load_learning_activity_events()
    now = datetime.now(timezone.utc)
    today = now.date()
    last_7d = now - timedelta(days=7)
    by_email: dict[str, list[dict[str, object]]] = {}
    for event in events:
        email = str(event.get("email") or "").strip().lower()
        if not email:
            continue
        by_email.setdefault(email, []).append(event)

    user_rows: list[LearningOperatorUserSummary] = []
    for email, user_events in by_email.items():
        ordered = sorted(user_events, key=lambda item: str(item.get("timestamp") or ""))
        first_seen = str(ordered[0].get("timestamp") or "")
        last_seen = str(ordered[-1].get("timestamp") or "")
        tier = str(ordered[-1].get("tier") or "standard")
        live_turns_today = 0
        latest_user_id = ""
        current_concept = ""
        for event in ordered:
            latest_user_id = str(event.get("user_id") or latest_user_id)
            if str(event.get("event_type") or "") in LIVE_TURN_EVENT_TYPES:
                current_concept = str(event.get("concept") or current_concept)
            when = _parse_activity_timestamp(str(event.get("timestamp") or ""))
            if when is not None and when.date() == today and str(event.get("event_type") or "") in LIVE_TURN_EVENT_TYPES:
                live_turns_today += 1
        concepts_learned = 0
        if latest_user_id:
            concept_state = _load_learning_concept_state_for_user(latest_user_id)
            concepts_learned = sum(
                1
                for item in concept_state.values()
                if isinstance(item, dict) and str(item.get("status") or "").lower() == "learned"
            )
            if not current_concept:
                session_store = _load_learning_session_for_user(latest_user_id)
                active_session = session_store.get("active_session") if isinstance(session_store, dict) else None
                if isinstance(active_session, dict):
                    current_concept = str(active_session.get("concept") or "")
        daily_limit = (
            _learning_turn_limit_from_env(LEARNING_TRUSTED_DAILY_TURNS_ENV, DEFAULT_TRUSTED_DAILY_TURNS)
            if tier == "trusted"
            else _learning_turn_limit_from_env(LEARNING_STANDARD_DAILY_TURNS_ENV, DEFAULT_STANDARD_DAILY_TURNS)
        )
        user_rows.append(
            LearningOperatorUserSummary(
                user_email=email,
                tier=tier,
                first_seen_at=first_seen,
                last_active_at=last_seen,
                live_turns_today=live_turns_today,
                turns_remaining_today=max(0, daily_limit - live_turns_today),
                concepts_learned=concepts_learned,
                current_concept=current_concept,
            )
        )

    active_today = 0
    active_last_7d = 0
    seen_today: set[str] = set()
    seen_7d: set[str] = set()
    live_turns_today = 0
    logins_today = 0
    rate_limit_hits_today = 0
    for event in events:
        email = str(event.get("email") or "").strip().lower()
        if not email:
            continue
        when = _parse_activity_timestamp(str(event.get("timestamp") or ""))
        if when is None:
            continue
        if when.date() == today:
            seen_today.add(email)
            if str(event.get("event_type") or "") in LIVE_TURN_EVENT_TYPES:
                live_turns_today += 1
            elif str(event.get("event_type") or "") == "learning_login":
                logins_today += 1
            elif str(event.get("event_type") or "") == "learning_rate_limit_blocked":
                rate_limit_hits_today += 1
        if when >= last_7d:
            seen_7d.add(email)
    active_today = len(seen_today)
    active_last_7d = len(seen_7d)

    user_rows.sort(key=lambda item: item.last_active_at, reverse=True)
    return LearningOperatorDashboardSnapshot(
        total_users=len(user_rows),
        active_today=active_today,
        active_last_7d=active_last_7d,
        live_turns_today=live_turns_today,
        logins_today=logins_today,
        rate_limit_hits_today=rate_limit_hits_today,
        users=tuple(user_rows),
    )


def _concept_governing_truth_path() -> Path:
    return SOURCE_REPO_ROOT / "projects" / "os-control-panel" / "product" / "concept-governing-truth-R74.md"


def _concept_governing_truth_sections() -> dict[str, str]:
    path = _concept_governing_truth_path()
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n### ", text)
    sections: dict[str, str] = {}
    for index, chunk in enumerate(parts):
        if index == 0:
            continue
        heading, _, body = chunk.partition("\n")
        concept = heading.strip()
        if not concept:
            continue
        sections[_normalize_concept_key(concept)] = f"### {heading}\n{body}".strip()
    return sections


def learning_concept_governing_truth(concept: str) -> str:
    key = _normalize_concept_key(concept)
    if not key:
        return ""
    return _concept_governing_truth_sections().get(key, "")


def _concept_governing_truth_heading(section_text: str) -> str:
    first_line = section_text.splitlines()[0].strip() if section_text.strip() else ""
    return first_line.removeprefix("### ").strip()


def _concept_governing_truth_bullets(section_text: str, heading: str) -> tuple[str, ...]:
    lines = section_text.splitlines()
    target = f"{heading}:"
    capture = False
    bullets: list[str] = []
    current: str | None = None
    for raw_line in lines:
        stripped = raw_line.rstrip()
        if not capture:
            if stripped == target:
                capture = True
            continue
        if re.match(r"^[A-Z][^:]+:$", stripped):
            break
        if not stripped:
            continue
        if stripped.startswith("- ") or stripped.startswith("  - "):
            if current:
                bullets.append(current.strip())
            current = stripped.split("- ", 1)[1].strip()
            continue
        if current is not None:
            current = f"{current} {stripped.strip()}".strip()
    if current:
        bullets.append(current.strip())
    return tuple(bullet for bullet in bullets if bullet)


def _learning_concept_truth_catalog() -> dict[str, LearningConceptTruth]:
    catalog: dict[str, LearningConceptTruth] = {}
    for key, section_text in _concept_governing_truth_sections().items():
        concept = _concept_governing_truth_heading(section_text) or key
        catalog[key] = LearningConceptTruth(
            concept=concept,
            concept_facts=_concept_governing_truth_bullets(section_text, "Concept facts"),
            concept_relationships=_concept_governing_truth_bullets(section_text, "Concept relationships"),
            important_distinctions=_concept_governing_truth_bullets(section_text, "Important distinctions"),
            implementation_anchors=_concept_governing_truth_bullets(section_text, "Implementation anchors"),
            risks_and_misconceptions=_concept_governing_truth_bullets(section_text, "Risks / misconceptions"),
            raw_markdown=section_text,
        )
    return catalog


def _learning_truth_paragraph(bullets: tuple[str, ...], *, fallback: str) -> str:
    cleaned = tuple(item.strip() for item in bullets if item.strip())
    if not cleaned:
        return fallback
    return " ".join(cleaned)


def _learning_truth_phrase_overrides(concept: str, text: str) -> str:
    if concept.strip().lower() == "rag":
        return text.replace("Retrieval-augmented generation", "Retrieval-Augmented Generation", 1)
    return text


def _learning_truth_exists_reason(
    truth: LearningConceptTruth,
    *,
    concept: str,
    where_it_connects: str,
) -> str:
    if truth.risks_and_misconceptions:
        return (
            f"This concept matters because without it, AI Builder OS can drift into problems like "
            f"{truth.risks_and_misconceptions[0].lower()}."
        )
    if truth.implementation_anchors:
        return (
            f"This concept matters in AI Builder OS because it shows up through "
            f"{truth.implementation_anchors[0]}."
        )
    return (
        f"This concept matters because it changes how AI Builder OS handles "
        f"{where_it_connects.strip() or concept}."
    )


def _learning_truth_os_connection(truth: LearningConceptTruth, *, concept: str) -> str:
    anchor_summary = _learning_truth_paragraph(
        truth.implementation_anchors,
        fallback=f"{concept} currently has no curated implementation walkthrough anchors.",
    )
    return f"In AI Builder OS, {anchor_summary}"


def _learning_truth_product_implication(
    truth: LearningConceptTruth,
    *,
    concept: str,
    where_it_connects: str,
) -> str:
    if truth.risks_and_misconceptions:
        return (
            f"For a product leader, {concept} changes how to reason about trust and tradeoffs because "
            f"{truth.risks_and_misconceptions[0].lower()}."
        )
    if where_it_connects.strip():
        return (
            f"For a product leader, {concept} changes how to reason about "
            f"{where_it_connects.strip()} in AI Builder OS."
        )
    return (
        f"For a product leader, {concept} matters when AI Builder OS needs clear judgment about "
        f"workflow quality, context, or capability boundaries."
    )


def _learning_truth_where_it_connects(truth: LearningConceptTruth, *, concept: str) -> str:
    anchors = tuple(item.strip() for item in truth.implementation_anchors if item.strip())
    if anchors:
        return " ".join(anchors[:2])
    relationships = tuple(item.strip() for item in truth.concept_relationships if item.strip())
    if relationships:
        return " ".join(relationships[:2])
    return f"{concept} appears in the curated learning catalog but does not yet have richer OS-local connection text."


def _learning_truth_why_now(concept: str, family_name: str | None) -> str:
    if family_name:
        return (
            f"{concept} is part of the curated {family_name.lower()} learning path and matters to how "
            "AI Builder OS works in practice."
        )
    return f"{concept} is part of the curated learning catalog and matters to current AI Builder OS work."


def _learning_truth_build_fields(
    concept: str,
    where_it_connects: str,
    *,
    truth: LearningConceptTruth,
) -> BuildToLearnPathway:
    anchor = where_it_connects.strip() or f"{concept} in current OS work"
    core_fact = truth.concept_facts[0] if truth.concept_facts else concept
    return BuildToLearnPathway(
        concept=concept,
        learning_goal=(
            f"Learn {concept} through one bounded OS walkthrough. Core idea: {core_fact}"
        ),
        experiment_slice=(
            f"Choose one bounded OS walkthrough where {concept} is clearly in play and pressure-test what it changes."
        ),
        project_anchor=anchor,
        success_signal=(
            f"You can explain {concept} simply, place it in the OS flow, and name the practical tradeoff it affects."
        ),
        capture_prompt=(
            f"After the walkthrough, capture what {concept} changed, what still feels weak, and which nearby concept remains easiest to confuse it with."
        ),
    )


def _learning_truth_relationship_structure(
    truth: LearningConceptTruth,
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    raw = truth.raw_markdown.splitlines()
    parent = ""
    children: list[str] = []
    related: list[str] = []
    capture = False
    mode = ""
    for line in raw:
        stripped = line.rstrip()
        if not capture:
            if stripped == "Concept relationships:":
                capture = True
            continue
        if re.match(r"^[A-Z][^:]+:$", stripped):
            break
        if not stripped:
            continue
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            child_match = re.search(r"Child of `([^`]+)`", item)
            if child_match:
                parent = child_match.group(1).strip()
                mode = ""
                continue
            parent_of_match = re.search(r"Parent(?: concept)? of `([^`]+)`", item)
            if parent_of_match:
                children.append(parent_of_match.group(1).strip())
                mode = ""
                continue
            gateway_match = item.startswith("Gateway concept for:")
            parent_list_match = item.startswith("Parent concept for:") or item.startswith("Parent of:")
            related_list_match = (
                item.startswith("Sibling to:")
                or item.startswith("Adjacent to:")
                or item.startswith("Closely linked to:")
                or item.startswith("Supports:")
                or item.startswith("Especially useful for:")
            )
            supporting_match = re.search(r"Supporting technique for `([^`]+)`", item)
            if supporting_match:
                related.append(supporting_match.group(1).strip())
                mode = ""
                continue
            if gateway_match or parent_list_match:
                mode = "children"
                continue
            if related_list_match:
                mode = "related"
                continue
            mode = ""
            continue
        if stripped.startswith("  - "):
            item = stripped[4:].strip().strip("`")
            if mode == "children":
                children.append(item)
            elif mode == "related":
                related.append(item)
    return (
        parent,
        tuple(dict.fromkeys(item for item in children if item)),
        tuple(dict.fromkeys(item for item in related if item)),
    )


def _learning_truth_confusions(
    truth: LearningConceptTruth,
    *,
    concept: str,
    all_concepts: tuple[str, ...],
) -> tuple[str, ...]:
    distinction_text = " ".join(truth.important_distinctions).lower()
    matches: list[str] = []
    for candidate in all_concepts:
        if candidate == concept:
            continue
        if candidate.lower() in distinction_text:
            matches.append(candidate)
    return tuple(dict.fromkeys(matches))


def _default_learning_profile() -> dict[str, str]:
    return {
        "product_background": "Product leader with some AI experience",
        "technical_comfort": "Comfortable reading architecture and tooling",
        "os_understanding_level": "New to AI Builder OS",
        "current_trajectory": "Design stronger agent workflows and evals",
        "credibility_goal": "Explain concepts simply to others",
        "preferred_learning_style": "Implementation walkthroughs",
        "current_learning_posture": "Applying in real work",
    }


def _ensure_private_learning_profile_file() -> Path:
    path = _private_learning_profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(_default_learning_profile(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _ensure_private_learning_agent_session_file() -> Path:
    path = _private_learning_agent_session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"active_session": None}, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_learning_profile() -> dict[str, str]:
    path = _ensure_private_learning_profile_file()
    defaults = _default_learning_profile()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raw = {}
    profile: dict[str, str] = {}
    for field, fallback in defaults.items():
        value = raw.get(field, fallback) if isinstance(raw, dict) else fallback
        profile[field] = str(value).strip() or fallback
    return profile


def save_learning_profile(
    *,
    product_background: str,
    technical_comfort: str,
    os_understanding_level: str,
    current_trajectory: str,
    credibility_goal: str,
    preferred_learning_style: str,
    current_learning_posture: str,
) -> Path:
    profile = {
        "product_background": product_background.strip() or _default_learning_profile()["product_background"],
        "technical_comfort": technical_comfort.strip() or _default_learning_profile()["technical_comfort"],
        "os_understanding_level": os_understanding_level.strip() or _default_learning_profile()["os_understanding_level"],
        "current_trajectory": current_trajectory.strip() or _default_learning_profile()["current_trajectory"],
        "credibility_goal": credibility_goal.strip() or _default_learning_profile()["credibility_goal"],
        "preferred_learning_style": preferred_learning_style.strip() or _default_learning_profile()["preferred_learning_style"],
        "current_learning_posture": current_learning_posture.strip() or _default_learning_profile()["current_learning_posture"],
    }
    path = _ensure_private_learning_profile_file()
    path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")
    _append_learning_activity_event("learning_profile_saved")
    return path


def learning_teaching_strategy(profile: dict[str, str] | None = None) -> LearningTeachingStrategy:
    current_profile = profile if profile is not None else load_learning_profile()
    background = current_profile.get("product_background", "").strip().lower()
    technical_comfort = current_profile.get("technical_comfort", "").strip().lower()
    os_level = current_profile.get("os_understanding_level", "").strip().lower()
    trajectory = current_profile.get("current_trajectory", "").strip().lower()
    credibility_goal = current_profile.get("credibility_goal", "").strip().lower()
    learning_style = current_profile.get("preferred_learning_style", "").strip().lower()
    posture = current_profile.get("current_learning_posture", "").strip().lower()

    if "technical builder" in background:
        entry_point = "Start from system behavior first, then translate it into product meaning."
    elif "already building ai-assisted workflows" in background:
        entry_point = "Start from workflow use and operating decisions before naming the abstract concept."
    elif "new to ai product systems" in background:
        entry_point = "Start from the basic problem the concept solves before adding structure or jargon."
    else:
        entry_point = "Start from product judgment and practical usefulness before getting more technical."

    if "implementation walkthroughs" in learning_style:
        explanation_order = ("what_it_is", "os_connection", "why_it_exists", "nearby_distinction", "product_implication")
        example_style = "Use implementation-grounded examples and concrete OS surfaces early."
    elif "concrete examples first" in learning_style:
        explanation_order = ("what_it_is", "nearby_distinction", "why_it_exists", "os_connection", "product_implication")
        example_style = "Lead with a simple practical example before abstracting upward."
    elif "step-by-step coaching" in learning_style:
        explanation_order = ("why_it_exists", "what_it_is", "nearby_distinction", "os_connection", "product_implication")
        example_style = "Use one bounded step at a time and keep the next move extremely explicit."
    else:
        explanation_order = ("why_it_exists", "what_it_is", "product_implication", "nearby_distinction", "os_connection")
        example_style = "Lead with broad framing, then narrow into distinctions and implementation."

    if os_level.startswith("new"):
        os_context_depth = "Assume little AI Builder OS familiarity and explain local surfaces explicitly."
    elif "comfortable" in os_level or "advanced" in os_level:
        os_context_depth = "Assume the learner can place OS-local surfaces in the wider flow without re-explaining each one."
    else:
        os_context_depth = "Assume some AI Builder OS familiarity, but still name local surfaces and why they matter."

    if "implementing" in technical_comfort or "debugging" in technical_comfort:
        technical_depth = "Use direct architecture language when it helps, but keep each turn concise."
    elif "architecture" in technical_comfort or "tooling" in technical_comfort:
        technical_depth = "Use moderate technical depth and make tradeoffs explicit without overloading the learner."
    else:
        technical_depth = "Prefer plain language and translate every necessary technical term immediately."

    emphasis: list[str] = []
    if "foundations" in trajectory:
        emphasis.append("Prioritize gateway concepts, parent concepts, and broad mental models before specialized edges.")
    if "workflows and evals" in trajectory:
        emphasis.append("Favor workflow, eval, and operating-model consequences when choosing what to stress.")
    if "fluently in real product work" in trajectory:
        emphasis.append("Keep the explanation practical and tied to real OS use rather than abstract theory.")
    if "explain concepts simply" in credibility_goal:
        emphasis.append("Favor plain-language distinctions that the learner could repeat to someone else.")
    elif "architecture decisions" in credibility_goal or "product and architecture decisions" in credibility_goal:
        emphasis.append("Favor decision-making tradeoffs and consequences over glossary-style definition alone.")
    else:
        emphasis.append("Favor confidence-building explanations that help the learner operate and speak credibly.")

    if "exploring" in posture:
        coaching_style = "Use gentle orientation and low pressure while keeping the concept boundaries crisp."
    elif "refreshing" in posture or "refining" in posture:
        coaching_style = "Assume partial familiarity and focus on sharpening distinctions rather than re-teaching everything."
    elif "applying" in posture or "real work" in posture:
        coaching_style = "Coach toward practical use, durable language, and clear operating judgment."
    else:
        coaching_style = "Stay supportive, direct, and focused on turning partial understanding into usable fluency."

    return LearningTeachingStrategy(
        entry_point=entry_point,
        explanation_order=explanation_order,
        os_context_depth=os_context_depth,
        technical_depth=technical_depth,
        example_style=example_style,
        coaching_style=coaching_style,
        emphasis=tuple(emphasis),
    )


def _teaching_strategy_payload(profile: dict[str, str] | None = None) -> dict[str, object]:
    strategy = learning_teaching_strategy(profile)
    return {
        "entry_point": strategy.entry_point,
        "explanation_order": list(strategy.explanation_order),
        "os_context_depth": strategy.os_context_depth,
        "technical_depth": strategy.technical_depth,
        "example_style": strategy.example_style,
        "coaching_style": strategy.coaching_style,
        "emphasis": list(strategy.emphasis),
    }


def _learning_concept_catalog() -> dict[str, LearningConceptKnowledge]:
    truth_catalog = _learning_concept_truth_catalog()
    if not truth_catalog:
        return {}

    family_map = _learning_concept_families()
    concept_to_family: dict[str, LearningConceptFamily] = {}
    for family in family_map.values():
        for concept in family.concepts:
            concept_to_family[_normalize_concept_key(concept)] = family

    all_concepts = tuple(truth.concept for truth in truth_catalog.values())
    raw_relationships = {
        key: _learning_truth_relationship_structure(truth)
        for key, truth in truth_catalog.items()
    }
    parent_map = {
        "workflows": "Agents",
        "orchestration": "Agents",
        "handoffs": "Agents",
        "results and state": "Agents",
        "traces / observability": "Agents",
        "human hand-back": "Agents",
        "agent-output quality evals": "Evals",
        "tool selection evals": "Evals",
        "workflow evals": "Evals",
        "trace grading": "Workflow Evals",
        "memory evals": "Evals",
        "safety evals": "Evals",
        "cost evals": "Evals",
        "latency evals": "Evals",
        "reliability evals": "Evals",
        "replays": "Evals",
        "retrieval": "Memory systems",
        "file search": "Retrieval",
        "rag": "Retrieval",
        "function calling": "Tool use",
        "connectors": "Tool use",
        "mcp": "Connectors",
        "tool selection": "Tool use",
    }
    for key, (parent, _, _) in raw_relationships.items():
        if parent and key not in parent_map:
            parent_map[key] = parent

    relation_overrides: dict[str, dict[str, tuple[tuple[str, str], ...]]] = {
        "evals": {
            "next_after": (
                ("Workflow Evals", "Workflow Evals are a natural next concept after Evals in the curated learning path."),
                ("Agent-output quality evals", "Agent-output quality evals are a natural next concept after Evals in the curated learning path."),
                ("Trace grading", "Trace grading is a useful deeper layer once the basic eval frame is already in view."),
            ),
            "related": (
                ("Replays", "Replays are a supporting evaluation technique used inside the broader eval system."),
                ("Trace grading", "Trace grading judges the path of a run rather than only the visible result."),
            ),
        },
        "trace grading": {
            "prerequisite": (("Evals", "Trace grading makes the most sense once the broader eval layer is already clear."),),
            "next_after": (("Agent-output quality evals", "Agent-output quality evals are a helpful adjacent concept after Trace grading."),),
        },
        "rag": {
            "often_confused_with": (("Memory systems", "RAG is not the same as long-term memory. Retrieval can support RAG, but not all retrieval patterns are full RAG systems."),),
            "related": (
                ("MCP", "MCP is about structured capability and context access, while RAG is one way of grounding a model with retrieved information."),
                ("Memory systems", "RAG sits inside the broader memory and retrieval family in AI Builder OS."),
            ),
            "next_after": (("Memory systems", "Memory systems are a natural next concept after RAG in the curated learning path."),),
        },
        "memory systems": {
            "next_after": (("Retrieval", "Retrieval is a natural next concept after Memory systems in the curated learning path."),),
        },
        "retrieval": {
            "next_after": (
                ("File search", "File search is a natural next concept after Retrieval in the curated learning path."),
                ("RAG", "RAG is a natural next concept after Retrieval in the curated learning path."),
            ),
        },
        "tool selection": {
            "related": (
                ("Tool Selection Evals", "Tool Selection Evals judge whether tool selection behavior was actually good."),
                ("Function calling", "Function calling shapes invocation, while tool selection decides whether invocation should happen at all."),
            ),
            "next_after": (("Tool Selection Evals", "Tool Selection Evals are a natural next concept after Tool selection in the curated learning path."),),
        },
        "mcp": {
            "related": (
                ("RAG", "MCP and RAG can both affect how context reaches a model, even though one is a protocol layer and the other is a retrieval pattern."),
                ("Connectors", "Connectors are the broader integration surface that make MCP easier to place in practice."),
            ),
        },
    }

    children_by_parent: dict[str, list[str]] = {}
    for key, parent in parent_map.items():
        children_by_parent.setdefault(_normalize_concept_key(parent), []).append(truth_catalog[key].concept)
    for key, (_, children, _) in raw_relationships.items():
        if children:
            bucket = children_by_parent.setdefault(key, [])
            for child in children:
                child_key = _normalize_concept_key(child)
                if child_key in parent_map and _normalize_concept_key(parent_map[child_key]) != key:
                    continue
                if child not in bucket:
                    bucket.append(child)

    catalog: dict[str, LearningConceptKnowledge] = {}
    for key, truth in truth_catalog.items():
        family = concept_to_family.get(key)
        where_it_connects = _learning_truth_where_it_connects(truth, concept=truth.concept)
        build_fields = _learning_truth_build_fields(truth.concept, where_it_connects, truth=truth)
        parent = parent_map.get(key, '')
        children = tuple(children_by_parent.get(key, ()))
        related_names = list(raw_relationships[key][2])
        if parent and parent not in related_names:
            related_names.insert(0, parent)
        confusion_names = _learning_truth_confusions(truth, concept=truth.concept, all_concepts=all_concepts)
        next_after_targets = children[:2] if children else tuple(name for name in related_names[:1] if name != truth.concept)
        override_relations = relation_overrides.get(key, {})

        catalog[key] = LearningConceptKnowledge(
            concept=truth.concept,
            why_now=_learning_truth_why_now(truth.concept, family.name if family is not None else None),
            where_it_connects=where_it_connects,
            what_it_is=_learning_truth_phrase_overrides(
                truth.concept,
                _learning_truth_paragraph(
                    truth.concept_facts,
                    fallback=f"{truth.concept} is part of the curated learning catalog but still needs clearer concept facts.",
                ),
            ),
            why_it_exists=_learning_truth_exists_reason(
                truth,
                concept=truth.concept,
                where_it_connects=where_it_connects,
            ),
            nearby_distinction=_learning_truth_paragraph(
                truth.important_distinctions,
                fallback=f"{truth.concept} still needs a sharper nearby distinction in the curated concept truth.",
            ),
            os_connection=_learning_truth_os_connection(truth, concept=truth.concept),
            product_implication=_learning_truth_product_implication(
                truth,
                concept=truth.concept,
                where_it_connects=where_it_connects,
            ),
            build_learning_goal=build_fields.learning_goal,
            build_experiment_slice=build_fields.experiment_slice,
            build_project_anchor=build_fields.project_anchor,
            build_success_signal=build_fields.success_signal,
            build_capture_prompt=build_fields.capture_prompt,
            hierarchy_parent=parent,
            hierarchy_children=children,
            relations={
                'often_confused_with': override_relations.get("often_confused_with", tuple(
                    (name, truth.important_distinctions[0])
                    for name in confusion_names
                )),
                'related': override_relations.get("related", tuple(
                    (name, f"{name} is structurally related to {truth.concept} in the curated concept truth.")
                    for name in dict.fromkeys(name for name in related_names if name != truth.concept)
                )),
                'next_after': override_relations.get("next_after", tuple(
                    (name, f"{name} is a natural next concept after {truth.concept} in the curated learning path.")
                    for name in next_after_targets
                )),
                'prerequisite': override_relations.get("prerequisite", ()),
            },
        )
    return catalog

def _fallback_learning_knowledge(
    concept: str,
    *,
    current_understanding: str = "",
    what_is_unclear: str = "",
    where_encountered: str = "",
) -> LearningConceptKnowledge:
    concept_label = concept.strip()
    confusion_clause = f" What feels unclear right now: {what_is_unclear.strip()}." if what_is_unclear.strip() else ""
    encountered_clause = f" It showed up in: {where_encountered.strip()}." if where_encountered.strip() else ""
    current_clause = f" Your current read is: {current_understanding.strip()}." if current_understanding.strip() else ""
    return LearningConceptKnowledge(
        concept=concept_label,
        why_now=f"{concept_label} is relevant enough to current OS work that the learning layer should help clarify it instead of leaving it as vague familiarity.",
        where_it_connects=where_encountered.strip() or "Current OS work and concept development.",
        what_it_is=f"{concept_label} appears to be an idea, pattern, or system term that matters enough to current work to warrant deliberate clarification.{current_clause}",
        why_it_exists=f"This concept likely exists because AI-assisted systems keep introducing layers that solve specific reliability, context, workflow, or integration problems.{confusion_clause}",
        nearby_distinction=f"A useful next move is to separate {concept_label} from whatever nearby concept or buzzword it is easiest to confuse it with.{encountered_clause}",
        os_connection=f"The main learning question for AI Builder OS is where {concept_label} affects implementation, workflow quality, or product judgment rather than just vocabulary familiarity.",
        product_implication=f"A product leader should care about {concept_label} only if it changes decisions, tradeoffs, or trust in the system. The goal is not to know the term, but to know when it matters.",
        build_learning_goal=f"Learn {concept_label} by turning it into one bounded experiment or concrete walkthrough tied to current OS work.",
        build_experiment_slice=f"Choose one narrow OS situation where {concept_label} seems relevant and pressure-test what the concept is supposed to change.",
        build_project_anchor=where_encountered.strip() or "Current OS work.",
        build_success_signal=f"You can explain {concept_label} in plain language, point to one real OS situation where it matters, and name one nearby concept it should not be confused with.",
        build_capture_prompt=f"After the experiment, capture what {concept_label} actually changed, what still feels vague, and whether the concept earned a real place in the OS vocabulary.",
        hierarchy_parent="",
        hierarchy_children=(),
        relations={},
    )


def _learning_knowledge_for(
    concept: str,
    *,
    current_understanding: str = "",
    what_is_unclear: str = "",
    where_encountered: str = "",
) -> LearningConceptKnowledge:
    key = concept.strip().lower()
    knowledge = _learning_concept_catalog().get(key)
    if knowledge is not None:
        return knowledge
    return _fallback_learning_knowledge(
        concept,
        current_understanding=current_understanding,
        what_is_unclear=what_is_unclear,
        where_encountered=where_encountered,
    )


def _learning_concept_families() -> dict[str, LearningConceptFamily]:
    return {
        "agent workflow systems": LearningConceptFamily(
            name="Agent workflow systems",
            summary="Core concepts for how agents, workflows, state, and hand-offs work together in structured AI systems.",
            concepts=(
                "Agents",
                "Workflows",
                "Orchestration",
                "Handoffs",
                "Results and state",
                "Traces / observability",
                "Human hand-back",
            ),
            gateway_concepts=("Agents",),
        ),
        "evals and reliability": LearningConceptFamily(
            name="Evals and reliability",
            summary="Core concepts for judging quality, correctness, safety, cost, latency, and reliability in AI systems.",
            concepts=(
                "Evals",
                "Agent-output quality evals",
                "Tool Selection Evals",
                "Workflow Evals",
                "Trace grading",
                "Memory Evals",
                "Safety Evals",
                "Cost Evals",
                "Latency Evals",
                "Reliability Evals",
                "Replays",
            ),
            gateway_concepts=("Evals",),
        ),
        "context and knowledge systems": LearningConceptFamily(
            name="Context and knowledge systems",
            summary="Core concepts for memory, retrieval, and how grounded information reaches the model when it is needed.",
            concepts=(
                "Memory systems",
                "Retrieval",
                "File search",
                "RAG",
            ),
            gateway_concepts=("Memory systems",),
        ),
        "tool and capability access": LearningConceptFamily(
            name="Tool and capability access",
            summary="Core concepts for how models use tools, functions, and external capabilities to reach data and actions.",
            concepts=(
                "Tool use",
                "Function calling",
                "Connectors",
                "MCP",
                "Tool selection",
            ),
            gateway_concepts=("Tool use",),
        ),
    }


def learning_concept_family(concept: str) -> LearningConceptFamily | None:
    normalized = _normalize_concept_key(concept)
    if not normalized:
        return None
    for family in _learning_concept_families().values():
        if any(_normalize_concept_key(item) == normalized for item in family.concepts):
            return family
    return None


def learning_concept_family_placement(concept: str) -> LearningConceptFamilyPlacement | None:
    knowledge = _learning_knowledge_for(concept)
    family = learning_concept_family(concept)
    if family is None:
        return None

    normalized = _normalize_concept_key(knowledge.concept)
    sibling_concepts = tuple(
        item for item in family.concepts if _normalize_concept_key(item) != normalized
    )
    natural_next_concepts = tuple(target for target, _ in knowledge.relations.get("next_after", ()))

    if any(_normalize_concept_key(item) == normalized for item in family.gateway_concepts):
        concept_role = "gateway"
    elif knowledge.hierarchy_parent.strip():
        concept_role = "specialized"
    else:
        concept_role = "member"

    return LearningConceptFamilyPlacement(
        concept=knowledge.concept,
        family_name=family.name,
        family_summary=family.summary,
        concept_role=concept_role,
        gateway_concepts=family.gateway_concepts,
        sibling_concepts=sibling_concepts,
        natural_next_concepts=natural_next_concepts,
    )


def _learning_family_children_map(family: LearningConceptFamily) -> dict[str, tuple[str, ...]]:
    catalog = _learning_concept_catalog()
    family_members = {_normalize_concept_key(item): item for item in family.concepts}
    child_map: dict[str, list[str]] = {
        _normalize_concept_key(gateway): [] for gateway in family.gateway_concepts
    }

    for concept in family.concepts:
        knowledge = catalog.get(_normalize_concept_key(concept))
        if knowledge is None:
            continue
        if knowledge.hierarchy_children:
            child_map[_normalize_concept_key(concept)] = list(knowledge.hierarchy_children)

    assigned_children: set[str] = set()
    for concept in family.concepts:
        knowledge = catalog.get(_normalize_concept_key(concept))
        if knowledge is None or not knowledge.hierarchy_parent.strip():
            continue
        parent_key = _normalize_concept_key(knowledge.hierarchy_parent)
        if parent_key in family_members:
            child_map.setdefault(parent_key, [])
            child_map[parent_key].append(knowledge.concept)
            assigned_children.add(_normalize_concept_key(knowledge.concept))

    gateway_members = {_normalize_concept_key(item) for item in family.gateway_concepts}
    for gateway in family.gateway_concepts:
        gateway_key = _normalize_concept_key(gateway)
        if child_map.get(gateway_key):
            continue
        fallback_children = [
            concept
            for concept in family.concepts
            if _normalize_concept_key(concept) not in gateway_members
            and _normalize_concept_key(concept) not in assigned_children
        ]
        if fallback_children:
            child_map[gateway_key] = fallback_children

    normalized_map: dict[str, tuple[str, ...]] = {}
    for parent_key, children in child_map.items():
        seen: set[str] = set()
        ordered: list[str] = []
        for child in children:
            child_key = _normalize_concept_key(child)
            if child_key in seen or child_key not in family_members:
                continue
            seen.add(child_key)
            ordered.append(family_members[child_key])
        normalized_map[parent_key] = tuple(ordered)
    return normalized_map


def _learning_family_tree_lines(
    family: LearningConceptFamily,
    *,
    current_concept: str = "",
) -> list[str]:
    normalized_current = _normalize_concept_key(current_concept)
    children_map = _learning_family_children_map(family)

    def format_label(concept: str) -> str:
        return f"{concept} (current)" if _normalize_concept_key(concept) == normalized_current else concept

    def append_children(lines: list[str], parent: str, prefix: str = "") -> None:
        children = children_map.get(_normalize_concept_key(parent), ())
        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{prefix}{branch}{format_label(child)}")
            child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
            append_children(lines, child, child_prefix)

    roots = family.gateway_concepts or family.concepts
    if not roots:
        return []

    lines: list[str] = []
    if len(roots) == 1:
        root = roots[0]
        lines.append(format_label(root))
        append_children(lines, root)
        return lines

    lines.append(family.name)
    for index, root in enumerate(roots):
        is_last = index == len(roots) - 1
        branch = "└── " if is_last else "├── "
        lines.append(f"{branch}{format_label(root)}")
        append_children(lines, root, "    " if is_last else "│   ")
    return lines


def learning_concept_navigation_sections() -> list[LearningConceptNavigationSection]:
    views_by_key = {
        _normalize_concept_key(view.concept): view for view in list_learning_concept_views()
    }
    sections: list[LearningConceptNavigationSection] = []

    for family in _learning_concept_families().values():
        children_map = _learning_family_children_map(family)
        seen: set[str] = set()
        entries: list[LearningConceptNavigationEntry] = []

        def append_entry(concept: str, depth: int) -> None:
            key = _normalize_concept_key(concept)
            if key in seen:
                return
            seen.add(key)
            view = views_by_key.get(key)
            status = (
                view.concept_state.status
                if view is not None and view.concept_state is not None
                else "upcoming"
            )
            entries.append(
                LearningConceptNavigationEntry(
                    concept=view.concept if view is not None else concept,
                    status=status,
                    depth=depth,
                )
            )
            for child in children_map.get(key, ()):
                append_entry(child, depth + 1)

        for gateway in family.gateway_concepts or family.concepts:
            append_entry(gateway, 0)
        for concept in family.concepts:
            append_entry(concept, 0)

        sections.append(
            LearningConceptNavigationSection(
                family_name=family.name,
                family_summary=family.summary,
                entries=tuple(entries),
            )
        )

    return sections


def _learning_plan_ordered_steps() -> list[tuple[str, str, int]]:
    ordered: list[tuple[str, str, int]] = []
    for section in learning_concept_navigation_sections():
        for entry in section.entries:
            ordered.append((section.family_name, entry.concept, entry.depth))
    return ordered


def _learning_plan_current_concept(
    ordered_steps: list[tuple[str, str, int]],
    *,
    views_by_key: dict[str, LearningConceptView],
) -> str:
    active_session = load_learning_agent_session()
    if active_session is not None:
        return active_session.concept

    for _, concept, _ in ordered_steps:
        view = views_by_key.get(_normalize_concept_key(concept))
        status = view.concept_state.status if view is not None and view.concept_state is not None else "upcoming"
        if status in {"in_progress", "reopened"}:
            return concept

    # Once there is no active or reopened concept, the learning plan should
    # advance through the curated ordered sequence rather than switching to a
    # separately ranked recommendation. This keeps the visible "next" step in
    # the plan aligned with the concept the OS actually moves to after a
    # learner marks the current concept learned.
    for _, concept, _ in ordered_steps:
        view = views_by_key.get(_normalize_concept_key(concept))
        status = view.concept_state.status if view is not None and view.concept_state is not None else "upcoming"
        if status != "learned":
            return concept

    recommendations = list_learning_concept_recommendations(limit=1)
    if recommendations:
        recommended = recommendations[0].concept
        by_key = {(_normalize_concept_key(concept)): (family_name, concept, depth) for family_name, concept, depth in ordered_steps}
        key = _normalize_concept_key(recommended)
        while key in by_key:
            _, concept, _ = by_key[key]
            view = views_by_key.get(key)
            status = view.concept_state.status if view is not None and view.concept_state is not None else "upcoming"
            knowledge = _learning_concept_catalog().get(key)
            parent = knowledge.hierarchy_parent.strip() if knowledge is not None else ""
            if status == "learned" or not parent:
                return concept
            parent_key = _normalize_concept_key(parent)
            parent_view = views_by_key.get(parent_key)
            parent_status = (
                parent_view.concept_state.status
                if parent_view is not None and parent_view.concept_state is not None
                else "upcoming"
            )
            if parent_status != "learned":
                key = parent_key
                continue
            return concept

    return ordered_steps[0][1] if ordered_steps else ""


def personalized_learning_plan() -> PersonalizedLearningPlan | None:
    sections = learning_concept_navigation_sections()
    if not sections:
        return None

    views_by_key = {
        _normalize_concept_key(view.concept): view for view in list_learning_concept_views()
    }
    ordered_steps = _learning_plan_ordered_steps()
    current_concept = _learning_plan_current_concept(ordered_steps, views_by_key=views_by_key)
    if not current_concept:
        return None

    current_family_name = sections[0].family_name
    families: list[LearningPlanFamily] = []
    current_concept_key = _normalize_concept_key(current_concept)
    current_found = False

    for section in sections:
        steps: list[LearningPlanStep] = []
        for entry in section.entries:
            key = _normalize_concept_key(entry.concept)
            view = views_by_key.get(key)
            status = view.concept_state.status if view is not None and view.concept_state is not None else entry.status
            is_current = key == current_concept_key
            if is_current:
                current_family_name = section.family_name
                current_found = True
            steps.append(
                LearningPlanStep(
                    concept=entry.concept,
                    status=status,
                    depth=entry.depth,
                    is_current=is_current,
                    is_completed=status == "learned",
                )
            )
        families.append(
            LearningPlanFamily(
                family_name=section.family_name,
                family_summary=section.family_summary,
                steps=tuple(steps),
            )
        )

    if not current_found:
        return None

    return PersonalizedLearningPlan(
        current_concept=current_concept,
        current_family_name=current_family_name,
        families=tuple(families),
    )


def _implementation_anchor_excerpt(path: str, search_text: str, *, radius: int = 3) -> str:
    target = REPO_ROOT / path
    if not target.exists():
        return ""
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return ""
    index = 0
    lowered_search = search_text.lower().strip()
    if lowered_search:
        for idx, line in enumerate(lines):
            if lowered_search in line.lower():
                index = idx
                break
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    excerpt_lines = lines[start:end]
    while excerpt_lines and not excerpt_lines[0].strip():
        excerpt_lines.pop(0)
    while excerpt_lines and not excerpt_lines[-1].strip():
        excerpt_lines.pop()
    return "\n".join(excerpt_lines[:8]).strip()


def learning_implementation_anchors(concept: str) -> list[LearningImplementationAnchor]:
    key = _normalize_concept_key(concept)
    specs: dict[str, tuple[tuple[str, str, str, str, str], ...]] = {
        "agents": (
            (
                "Codex-native workflow",
                ".agents/skills/ai-builder-os-workflow/SKILL.md",
                "workflow",
                "Keep model work in the current Codex chat by default",
                "This skill keeps interactive agent work in Codex while the deterministic controller owns routing, queues, claims, approvals, and history.",
            ),
            (
                "Agent runtime",
                "projects/os-control-panel/src/agents_runtime/runner.py",
                "code",
                "class AgentsWorkflowRuntime",
                "This optional API-backed deployment runtime owns SDK agent runs, sessions, approvals, and traces.",
            ),
            (
                "Available role tools",
                "projects/os-control-panel/src/agents_runtime/tools.py",
                "code",
                "def tools_for_role",
                "This shows explicit least-privilege capability boundaries for each SDK agent.",
            ),
            (
                "Shared Agents workspace",
                "projects/os-control-panel/src/app.py",
                "code",
                "Agents",
                "This is the user-facing surface where multiple OS roles are exposed as real agent work lanes.",
            ),
        ),
        "workflows": (
            (
                "Workflow scenario fixture",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"pm_chat_discovery_produces_draft\"",
                "This is a concrete workflow artifact: it names a real multi-step behavior the OS expects to complete correctly, so workflow stops feeling like vague process language.",
            ),
            (
                "Orchestrator recommendation",
                "projects/os-control-panel/src/workspace.py",
                "code",
                "def orchestrator_recommendation",
                "This is one place the OS explicitly decides what should happen next in a workflow.",
            ),
            (
                "Task registry",
                "projects/os-control-panel/product/tasks.md",
                "doc",
                "Status:",
                "The task registry is one durable workflow surface: work moves through named states instead of staying implicit.",
            ),
            (
                "Active agent threads",
                "projects/os-control-panel/data/agent_threads.json",
                "state",
                "\"status\"",
                "This runtime artifact shows workflows in motion: active, archived, saved, and pending-approval states make the current position of multi-step agent work inspectable.",
            ),
        ),
        "evals": (
            (
                "OS control-panel eval runner",
                "projects/os-control-panel/tools/eval_runner.py",
                "tool",
                "def main()",
                "This is the deterministic validation entrypoint for the control panel, so it shows how the OS turns expected behavior into a repeatable check.",
            ),
            (
                "Scenario definitions",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"scenario_id\"",
                "These scenario cases make the evals concrete by naming the situations the OS should handle correctly.",
            ),
            (
                "Capability eval case catalog",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"output_quality_grounded\"",
                "This is where the OS stores concrete eval contracts such as output quality, workflow traces, memory, safety, cost, latency, and reliability, so the eval categories become real artifacts instead of abstract labels.",
            ),
            (
                "Eval coverage map",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "EvalCoverageRecord(\"os-control-panel\", \"Learning Agent\", \"Output Quality\"",
                "This shows which eval dimensions are already applied to real OS agents, making evals feel like an operating habit rather than a theoretical testing concept.",
            ),
        ),
        "replays": (
            (
                "Replay-backed eval runner",
                "projects/parentmate/tools/eval_runner.py",
                "tool",
                "replay",
                "This runner shows how replay files get fed back into the system so downstream behavior can be checked deterministically.",
            ),
            (
                "Replay fixtures",
                "projects/parentmate/evals/replays/email_1_response.json",
                "fixture",
                "\"response\"",
                "This is a concrete replay artifact: a saved model-shaped output used to stabilize an eval run.",
            ),
            (
                "Replay capture tool",
                "projects/parentmate/tools/capture_replays.py",
                "tool",
                "def main()",
                "This tool shows how replays are intentionally captured and refreshed rather than appearing magically.",
            ),
        ),
        "trace grading": (
            (
                "Agent runtime trace grader tests",
                "projects/os-control-panel/tests/unit/test_agent_runtime.py",
                "test",
                "trace_grader",
                "These tests make trace grading concrete by checking whether a workflow trace is clean, incomplete, or risky even when outputs look plausible.",
            ),
            (
                "Agent runtime",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "trace",
                "The runtime is where traces are persisted and reviewed, which is the operational side of trace grading inside the OS.",
            ),
            (
                "Operations dashboard",
                "projects/os-control-panel/src/operations_dashboard.py",
                "code",
                "trace",
                "The dashboard turns trace evidence into something the operator can inspect instead of leaving it buried in raw execution state.",
            ),
            (
                "Terminal trace eval case",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"workflow_terminal_trace\"",
                "This is a concrete trace-shaped eval artifact: a tiny example run with start, model, and completion events that shows what a gradeable workflow trace actually looks like in practice.",
            ),
        ),
        "agent-output quality evals": (
            (
                "Output-quality eval case",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"output_quality_grounded\"",
                "This is a concrete output-quality contract: it checks whether an agent response includes the grounded terms the OS expects and avoids unsupported claims.",
            ),
            (
                "Agent runtime tests",
                "projects/os-control-panel/tests/unit/test_agent_runtime.py",
                "test",
                "output_guardrail",
                "These tests show that the OS is not only checking whether agents run, but whether their outputs stay inside grounded, trustworthy boundaries.",
            ),
            (
                "Eval coverage for Learning Agent quality",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "EvalCoverageRecord(\"os-control-panel\", \"Learning Agent\", \"Output Quality\"",
                "This coverage record shows that output quality is already treated as a named evaluation dimension for the Learning Agent, not just a subjective product judgment after the fact.",
            ),
            (
                "Agent runtime guardrails",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "guardrail",
                "This is where live-agent quality moves from vibes into explicit runtime constraints and reviewable trace behavior.",
            ),
        ),
        "tool selection evals": (
            (
                "Tool-selection eval case",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"tool_selection_exact\"",
                "This is a concrete tool-selection contract showing the exact tools, allowed tools, and order expectations the OS can grade against.",
            ),
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Tool Selection\"",
                "This shows that tool selection is already a named eval dimension in the OS rather than an accidental side concern.",
            ),
            (
                "Learning and live-role tool coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "Tool Selection",
                "These coverage records show that PM, Experience Designer, UI Designer, Learning Agent, and Orchestrator are already being judged on tool choice.",
            ),
            (
                "Agent runtime tests",
                "projects/os-control-panel/tests/unit/test_agent_runtime.py",
                "test",
                "tool",
                "The runtime tests make tool-use behavior inspectable enough to support tool-selection reasoning.",
            ),
        ),
        "workflow evals": (
            (
                "Workflow scenario fixture",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"requirement_deletion_cleans_linked_state\"",
                "This is a concrete workflow eval artifact: it names a real OS behavior the system must preserve, so workflow evals look like executable situations rather than generic prose about process quality.",
            ),
            (
                "Scenario eval runner",
                "projects/os-control-panel/tools/scenario_eval_runner.py",
                "tool",
                "def main()",
                "This runner is the operational entrypoint for workflow scenario validation in the control panel.",
            ),
            (
                "Learning workflow scenario",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"tutoring_progression_and_build_routing_are_sensible\"",
                "This shows that workflow evals also cover the Learning Agent itself: progression, routing, and build-to-learn behavior are treated as workflow contracts, not just UI behavior.",
            ),
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Workflow\"",
                "The eval framework already treats workflow as a first-class evaluation type across multiple agent surfaces.",
            ),
        ),
        "memory evals": (
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Memory\"",
                "This shows that memory is already treated as its own evaluation layer in the OS.",
            ),
            (
                "Concept state store",
                "private/learning/concept-state.json",
                "state",
                "\"concepts\"",
                "This durable state makes memory behavior concrete: the OS is already storing and reusing structured learning memory.",
            ),
            (
                "Learning profile",
                "private/learning/learning-profile.json",
                "state",
                "\"current_trajectory\"",
                "This is another concrete memory layer: persistent operator learning context that can be used or misused by the system.",
            ),
        ),
        "safety evals": (
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Safety\"",
                "The eval framework already treats safety as a first-class dimension covering bounded behavior and hand-back logic.",
            ),
            (
                "SDK input and output guardrails",
                "projects/os-control-panel/src/agents_runtime/guardrails.py",
                "code",
                "@input_guardrail",
                "This is where SDK tripwires turn safety policy into explicit input and output enforcement.",
            ),
            (
                "Learning-agent hand-back tests",
                "projects/os-control-panel/tests/unit/test_workspace.py",
                "test",
                "hand_back",
                "These tests make one concrete safety move visible: the system pausing and handing control back when it should not bluff forward.",
            ),
        ),
        "cost evals": (
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Cost\"",
                "This shows that cost is already treated as an explicit eval dimension in the OS.",
            ),
            (
                "Cost budget evaluator",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "def evaluate_cost",
                "This evaluates captured SDK token usage and estimated spend against an explicit budget.",
            ),
            (
                "Cost threshold tests",
                "projects/os-control-panel/tests/unit/test_eval_framework.py",
                "test",
                "evaluate_cost",
                "These tests make the cost budget logic concrete enough to teach as a real evaluation concept.",
            ),
        ),
        "latency evals": (
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Latency\"",
                "This shows that latency is already treated as an explicit eval dimension in the OS.",
            ),
            (
                "SDK run duration summary",
                "projects/os-control-panel/src/operations_dashboard.py",
                "code",
                "def _duration_seconds",
                "This derives response time from correlated SDK lifecycle events so latency becomes measurable.",
            ),
            (
                "Latency threshold tests",
                "projects/os-control-panel/tests/unit/test_eval_framework.py",
                "test",
                "evaluate_latency",
                "These tests make the latency budget logic concrete enough to teach as a real evaluation concept.",
            ),
        ),
        "reliability evals": (
            (
                "Eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Reliability\"",
                "This shows that reliability is already treated as its own eval dimension across evaluated projects.",
            ),
            (
                "Reliability threshold tests",
                "projects/os-control-panel/tests/unit/test_eval_framework.py",
                "test",
                "evaluate_reliability",
                "These tests make repeat-run and consistency checks concrete enough to teach as a real reliability concept.",
            ),
            (
                "Agent runtime trace integrity checks",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "missing_model_call",
                "This is where the OS checks terminal trace integrity, which is one concrete part of operational reliability.",
            ),
        ),
        "orchestration": (
            (
                "Orchestrator recommendation",
                "projects/os-control-panel/src/workspace.py",
                "code",
                "def orchestrator_recommendation",
                "This is the clearest explicit orchestration surface in the OS: it recommends what role or action should happen next.",
            ),
            (
                "Live orchestrator review",
                "projects/os-control-panel/src/workspace.py",
                "code",
                "def run_live_orchestrator_review",
                "This shows orchestration as a reviewable, advisory system behavior rather than hidden control flow.",
            ),
            (
                "Workflow scenarios",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"result\"",
                "These scenarios make orchestration visible by encoding expected routing and cleanup behavior.",
            ),
        ),
        "handoffs": (
            (
                "Approval inbox artifacts",
                "projects/os-control-panel/data/approvals.json",
                "state",
                "\"approval_type\"",
                "These approval records are concrete handoff artifacts: one role produces work, then the Product Director receives an explicit item to review, approve, or reject.",
            ),
            (
                "Agent thread handoff state",
                "projects/os-control-panel/data/agent_threads.json",
                "state",
                "\"pending_approval\"",
                "These thread records show that agent conversations do not just disappear; they move into explicit handoff states such as pending approval, archived, or saved.",
            ),
            (
                "Workflow handoff scenario",
                "projects/os-control-panel/evals/scenarios.json",
                "fixture",
                "\"routed_experience_finding_routes_to_pm\"",
                "This scenario shows a handoff as an executable expectation: a routed experience finding should land with PM instead of disappearing into vague routing language.",
            ),
        ),
        "results and state": (
            (
                "Requirements registry",
                "projects/os-control-panel/product/requirements.md",
                "doc",
                "Status:",
                "This is a canonical results-and-state artifact: product intent becomes durable only when it is captured as named requirements with explicit status.",
            ),
            (
                "Task registry",
                "projects/os-control-panel/product/tasks.md",
                "doc",
                "Status:",
                "This is another durable state surface: work moves through explicit task states rather than living only inside chat or memory.",
            ),
            (
                "Implementation run records",
                "projects/os-control-panel/data/implementation_runs.json",
                "state",
                "\"project_name\"",
                "These run records make results-and-state operational: the OS remembers which implementation attempts started, where they wrote output, and whether they are still active.",
            ),
        ),
        "traces / observability": (
            (
                "Trace log artifacts",
                "projects/os-control-panel/data/agent_traces.jsonl",
                "state",
                "\"event\": \"run_started\"",
                "This is the raw observability artifact: a real stream of run_started and run_completed events that shows how the OS records what happened over time.",
            ),
            (
                "Operations dashboard",
                "projects/os-control-panel/src/operations_dashboard.py",
                "code",
                "summarize_agent_runs",
                "This turns raw trace events into an inspectable observability surface for operators.",
            ),
            (
                "Trace integrity eval cases",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"trace\"",
                "These cases make traces concrete as structured evidence rather than loose debug text.",
            ),
        ),
        "human hand-back": (
            (
                "Learning-agent hand-back logic",
                "projects/os-control-panel/src/workspace.py",
                "code",
                "\"hand_back\"",
                "This is where the tutoring agent explicitly decides to pause and return control instead of bluffing through ambiguity.",
            ),
            (
                "Trace-level hand-back event",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "human_hand_back",
                "This makes hand-back visible as an explicit runtime event rather than an invisible failure mode.",
            ),
            (
                "Operations dashboard hand-back view",
                "projects/os-control-panel/tests/unit/test_operations_dashboard.py",
                "test",
                "hand_back",
                "These tests show that hand-backs are counted and surfaced as a meaningful operating signal.",
            ),
        ),
        "tool use": (
            (
                "Role tool definitions",
                "projects/os-control-panel/src/agents_runtime/tools.py",
                "code",
                "@function_tool",
                "This is the clearest surface where typed SDK tools and their approval boundaries are defined.",
            ),
            (
                "Available tools per role",
                "projects/os-control-panel/src/agents_runtime/tools.py",
                "code",
                "def tools_for_role",
                "This shows that tool use is role-shaped and bounded rather than unlimited.",
            ),
            (
                "Tool-completed trace events",
                "projects/os-control-panel/data/agent_traces.jsonl",
                "state",
                "\"tool_completed\"",
                "This is the concrete runtime artifact for tool use: the trace log records when a tool was actually invoked, so tool use becomes inspectable instead of implicit.",
            ),
        ),
        "function calling": (
            (
                "Role tool definitions",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "AgentToolDefinition",
                "These typed tool definitions are the closest current OS equivalent to structured function-calling surfaces.",
            ),
            (
                "Read-only capability execution",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "if tool_name == \"read_requirements\"",
                "This shows structured, named capability execution instead of vague free-form tool instructions.",
            ),
            (
                "Tool-call trace artifact",
                "projects/os-control-panel/data/agent_traces.jsonl",
                "state",
                "\"tool_name\"",
                "This trace artifact makes function-calling-style behavior concrete: a named tool is requested, executed, and recorded with structured metadata.",
            ),
        ),
        "connectors": (
            (
                "Gmail plugin skill",
                ".codex/plugins/cache/openai-curated/gmail/2cb26e7b/skills/gmail/SKILL.md",
                "doc",
                "connected Gmail data",
                "This is one concrete connected capability surface the OS environment can access through a bounded integration.",
            ),
            (
                "Google Calendar plugin skill",
                ".codex/plugins/cache/openai-curated/google-calendar/2cb26e7b/skills/google-calendar/SKILL.md",
                "doc",
                "connected Google Calendar data",
                "This is another concrete connector-style capability surface available to the OS environment.",
            ),
            (
                "Plugin/connector instructions",
                "agent/system.md",
                "doc",
                "Apps (Connectors)",
                "This is where the broader OS explicitly names apps and connectors as structured capability surfaces.",
            ),
        ),
        "tool selection": (
            (
                "Tool-selection eval case",
                "projects/os-control-panel/evals/eval_cases.json",
                "fixture",
                "\"tool_selection_exact\"",
                "This is a concrete tool-selection artifact showing the actual, expected, and allowed tools the OS can grade against.",
            ),
            (
                "Tool-selection eval coverage",
                "projects/os-control-panel/src/eval_framework.py",
                "code",
                "\"Tool Selection\"",
                "This is where the OS treats capability choice as a distinct quality concern rather than an invisible implementation detail.",
            ),
            (
                "Tool-use runtime tests",
                "projects/os-control-panel/tests/unit/test_agents_sdk_runtime.py",
                "test",
                "registry_has_real_handoffs",
                "These tests verify the real SDK tool, handoff, approval, and agents-as-tools contracts.",
            ),
        ),
        "retrieval": (
            (
                "Read-only role tools",
                "projects/os-control-panel/src/agents_runtime/tools.py",
                "code",
                "\"read_requirements\"",
                "These tools show the OS selectively fetching context when needed instead of stuffing everything into every run.",
            ),
            (
                "Available tools guidance",
                "projects/os-control-panel/src/agents_runtime/registry.py",
                "code",
                "tools_for_role",
                "This binds retrieval tools directly to each SDK specialist with a least-privilege contract.",
            ),
            (
                "RAG concept grounding",
                "projects/os-control-panel/src/workspace.py",
                "code",
                "\"rag\": LearningConceptKnowledge",
                "The learning model already treats RAG as one specific retrieval-grounding pattern, which helps make retrieval teachable in context.",
            ),
        ),
        "file search": (
            (
                "Requirements reader tool",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "\"read_requirements\"",
                "This is one concrete local file-search-like path: fetch the specific requirements context instead of carrying the whole project blindly.",
            ),
            (
                "Tasks reader tool",
                "projects/os-control-panel/src/agents_runtime/support.py",
                "code",
                "\"read_tasks\"",
                "This is another concrete local-context retrieval path grounded in project files.",
            ),
            (
                "Read-only runtime tests",
                "projects/os-control-panel/tests/unit/test_agent_runtime.py",
                "test",
                "read_only",
                "These tests make the local file-context access path concrete enough to teach honestly.",
            ),
        ),
        "memory systems": (
            (
                "Private memory",
                "private/memory.md",
                "memory",
                "memory",
                "This file is one of the OS's durable memory layers, so it shows what gets preserved as operating context over time.",
            ),
            (
                "Concept state store",
                "private/learning/concept-state.json",
                "state",
                "\"concepts\"",
                "This state file shows that learning memory is not just prose; it is structured, durable concept progression.",
            ),
            (
                "Reflections store",
                "private/thinking/reflections.md",
                "memory",
                "##",
                "This shows another memory layer: reflective signals preserved for later reuse instead of disappearing after one conversation.",
            ),
        ),
    }
    anchors: list[LearningImplementationAnchor] = []
    for label, path, kind, search_text, why in specs.get(key, ())[:3]:
        anchors.append(
            LearningImplementationAnchor(
                concept=concept.strip() or key,
                label=label,
                path=path,
                kind=kind,
                why_it_matters=why,
                excerpt=_implementation_anchor_excerpt(path, search_text),
            )
        )
    return anchors


def _personalized_learning_reason(concept: str, profile: dict[str, str]) -> str:
    key = concept.strip().lower()
    trajectory = profile.get("current_trajectory", "")
    credibility = profile.get("credibility_goal", "")
    technical = profile.get("technical_comfort", "")
    style = profile.get("preferred_learning_style", "")

    reasons = {
        "trace grading": f"For your current trajectory in agent orchestration and product-system reliability, trace grading helps you judge workflow quality rather than stopping at polished outputs. It directly supports your credibility goal of explaining how agent systems should be evaluated in plain language.",
        "rag": f"Given your trajectory around memory, retrieval, and grounded context, RAG matters because it is one of the first concepts where capability can outrun understanding. Learning it well helps you speak credibly about when retrieval is actually needed instead of repeating architecture jargon.",
        "mcp": f"Because you are operating in a tool- and connector-rich environment, MCP matters less as protocol trivia and more as a way to reason clearly about structured capability access. That fits your need for conceptual fluency rather than deep implementation specialization.",
        "connectors": f"Because the OS already reaches into external capability surfaces, connectors matter for you as the practical layer that turns AI systems from isolated demos into workflow participants.",
        "tool selection": f"You are already building in a tool-rich environment, so tool selection matters because it sharpens your ability to judge whether an agent used capability well instead of just producing a decent-looking answer.",
        "memory systems": f"Your work is already turning reflection, learning, and durable context into OS capabilities. Memory systems matter for you because they connect directly to the kind of AI product operating model you are trying to build and explain credibly.",
        "agent-output quality evals": f"You have already noticed the gap between deterministic workflow correctness and live agent usefulness. This concept matters for you because it sharpens your ability to explain what trustworthy agent quality actually means at a product-system level.",
        "evals": f"Evals matter for your trajectory because they give you the quality language beneath orchestration, reliability, and trustworthy AI-assisted workflows. They are part of the conceptual foundation you want to explain simply and credibly.",
        "replays": f"Replays matter for you because they reveal the difference between stable system validation and live model behavior. That distinction supports the kind of grounded product judgment your credibility goal requires.",
    }
    reason = reasons.get(key)
    if reason:
        return reason
    return (
        f"This concept matters for your trajectory in {trajectory} because it can strengthen the way you reason about AI-assisted product systems. "
        f"It also fits your credibility goal of {credibility.lower() if credibility else 'building jargon-free conceptual fluency'}. "
        f"Given your learning style ({style}) and current technical comfort ({technical}), the OS should teach it in context rather than assume surface familiarity is enough."
    )


def _personalized_learning_path(concept: str, profile: dict[str, str], fallback: str) -> str:
    style = profile.get("preferred_learning_style", "").lower()
    posture = profile.get("current_learning_posture", "").lower()
    if "build" in style or "build" in posture:
        return f"{fallback} If the explanation still feels thin, route it quickly into a bounded build-to-learn experiment."
    if "example" in style or "context" in style:
        return f"{fallback} Keep the explanation tied to current OS work and use concrete examples before adding more abstraction."
    return fallback


def _personalized_gap(current_gap: str, profile: dict[str, str]) -> str:
    credibility = profile.get("credibility_goal", "")
    if credibility:
        return f"{current_gap} This is especially relevant because your credibility goal is: {credibility}"
    return current_gap


def _learning_text_tokens(*parts: str) -> set[str]:
    tokens: set[str] = set()
    for part in parts:
        for token in re.findall(r"[a-zA-Z0-9']+", part.lower()):
            if len(token) >= 4:
                tokens.add(token)
    return tokens


def _latest_learning_history_event(state: dict[str, object]) -> dict[str, object]:
    history = state.get("history")
    if not isinstance(history, list) or not history:
        return {}
    latest = history[-1]
    return latest if isinstance(latest, dict) else {}


def _concept_is_learned_or_strengthened(
    state: dict[str, object],
    build_link: LearningBuildToLearnLink | None,
) -> bool:
    if str(state.get("status") or "").lower() == "learned":
        return True
    return build_link is not None and build_link.status == "captured" and build_link.learning_effect == "strengthened"


def _concept_has_active_uncertainty(
    state: dict[str, object],
    build_link: LearningBuildToLearnLink | None,
) -> bool:
    status = str(state.get("status") or "").lower()
    if status in {"in_progress", "reopened", "build_to_learn"}:
        return True
    return build_link is not None and (
        build_link.status in {"planned", "active"}
        or bool(build_link.unresolved_after_build.strip())
        or build_link.learning_effect == "reopened"
    )


def _learning_compounding_signal(
    knowledge: LearningConceptKnowledge,
    *,
    catalog: dict[str, LearningConceptKnowledge],
    concept_states: dict[str, object],
    active_session: LearningAgentSession | None,
) -> LearningCompoundingSignal:
    key = knowledge.concept.lower()
    own_state = concept_states.get(key)
    if not isinstance(own_state, dict):
        own_state = {}
    own_build = _extract_build_to_learn_link(own_state, knowledge.concept)
    own_status = str(own_state.get("status") or "").lower()

    score_bonus = 0
    why_lines: list[str] = []
    gap_lines: list[str] = []
    path_lines: list[str] = []
    resurfaced_from_learned = False

    latest_event = _latest_learning_history_event(own_state)
    if latest_event and own_status in {"reopened", "in_progress"}:
        note = str(latest_event.get("note") or "").strip()
        if note:
            gap_lines.append(f"Recent learning state: {note}")

    for target, rationale in knowledge.relations.get("prerequisite", ()):
        target_key = target.strip().lower()
        target_state = concept_states.get(target_key)
        if not isinstance(target_state, dict):
            continue
        target_build = _extract_build_to_learn_link(target_state, target)
        if _concept_is_learned_or_strengthened(target_state, target_build):
            score_bonus += 24
            why_lines.append(f"Your recent progress on {target} unlocks this next layer. {rationale}")
            path_lines.append(f"Use {target} as the anchor when you explain or compare this concept.")
            break

    for source_key, source_knowledge in catalog.items():
        source_state = concept_states.get(source_key)
        if not isinstance(source_state, dict):
            source_state = {}
        source_build = _extract_build_to_learn_link(source_state, source_knowledge.concept)
        source_active = active_session is not None and active_session.concept.strip().lower() == source_key

        for target, rationale in source_knowledge.relations.get("next_after", ()):
            if target.strip().lower() != key:
                continue
            if _concept_is_learned_or_strengthened(source_state, source_build):
                score_bonus += 32
                why_lines.append(f"This is the natural next concept after {source_knowledge.concept}. {rationale}")
                path_lines.append(f"Ask the tutor to connect {source_knowledge.concept} to {knowledge.concept} explicitly.")
                break
            if source_active and str(source_state.get("status") or "").lower() in {"in_progress", "reopened"}:
                score_bonus += 12
                why_lines.append(f"{source_knowledge.concept} is active right now, so this follow-on concept is becoming relevant already.")
                break

        for relation in ("often_confused_with", "related", "prerequisite"):
            for target, rationale in source_knowledge.relations.get(relation, ()):
                if target.strip().lower() != key:
                    continue
                source_uncertain = _concept_has_active_uncertainty(source_state, source_build) or source_active
                if not source_uncertain:
                    continue
                if relation == "often_confused_with":
                    score_bonus += 26
                    resurfaced_from_learned = resurfaced_from_learned or own_status == "learned"
                    why_lines.append(
                        f"Recent uncertainty in {source_knowledge.concept} makes this distinction relevant again. {rationale}"
                    )
                    gap_lines.append(
                        f"It may be worth reopening this concept briefly so the distinction with {source_knowledge.concept} becomes crisp again."
                    )
                    path_lines.append(
                        f"Ask the tutor to compare {knowledge.concept} and {source_knowledge.concept} in plain language before treating either as fully settled."
                    )
                    break
                if relation == "prerequisite":
                    score_bonus += 18
                    resurfaced_from_learned = resurfaced_from_learned or own_status == "learned"
                    why_lines.append(
                        f"{source_knowledge.concept} is still carrying uncertainty, and this concept supports it as a foundation. {rationale}"
                    )
                    gap_lines.append(
                        f"A quick revisit here may prevent shallow understanding from leaking into {source_knowledge.concept}."
                    )
                    break
                score_bonus += 10
                why_lines.append(
                    f"{source_knowledge.concept} is active enough that this adjacent concept now matters more. {rationale}"
                )
                break

    if own_build is not None and own_build.status == "captured":
        if own_build.learning_effect == "strengthened":
            path_lines.append("Use what the build just taught you to choose the next adjacent concept deliberately, not generically.")
        elif own_build.learning_effect == "reopened":
            gap_lines.append("The last build surfaced fresh uncertainty, so a comparison or distinction step is more important than pushing forward too quickly.")

    why_now_addition = " ".join(dict.fromkeys(line.strip() for line in why_lines if line.strip()))
    current_gap_addition = " ".join(dict.fromkeys(line.strip() for line in gap_lines if line.strip()))
    suggested_path_addition = " ".join(dict.fromkeys(line.strip() for line in path_lines if line.strip()))
    return LearningCompoundingSignal(
        score_bonus=score_bonus,
        why_now_addition=why_now_addition,
        current_gap_addition=current_gap_addition,
        suggested_path_addition=suggested_path_addition,
        resurfaced_from_learned=resurfaced_from_learned,
    )


def _follow_on_learning_move(knowledge: LearningConceptKnowledge) -> str:
    for relation in ("next_after", "related"):
        targets = knowledge.relations.get(relation, ())
        if not targets:
            continue
        target, rationale = targets[0]
        if relation == "next_after":
            return f"Once this feels stable, {target} is the natural next concept. {rationale}"
        return f"A useful adjacent concept after this is {target}. {rationale}"
    return ""


def _learning_recommendation_relevance_score(
    knowledge: LearningConceptKnowledge,
    profile: dict[str, str],
    *,
    active_session: LearningAgentSession | None,
    state_status: str,
    current_gap: str,
    build_link: LearningBuildToLearnLink | None,
    concept_notes_present: bool,
    concept_states: dict[str, object],
    note_unresolved_concepts: set[str],
) -> int:
    score = 0
    key = knowledge.concept.lower()
    profile_text = " ".join(
        (
            profile.get("product_background", ""),
            profile.get("technical_comfort", ""),
            profile.get("current_trajectory", ""),
            profile.get("credibility_goal", ""),
            profile.get("preferred_learning_style", ""),
            profile.get("current_learning_posture", ""),
        )
    )
    profile_tokens = _learning_text_tokens(profile_text)
    knowledge_tokens = _learning_text_tokens(
        knowledge.concept,
        knowledge.why_now,
        knowledge.where_it_connects,
        knowledge.what_it_is,
        knowledge.os_connection,
        knowledge.product_implication,
    )
    score += len(profile_tokens & knowledge_tokens) * 4

    if "retrieval" in profile_tokens and key == "rag":
        score += 28
    if key == "rag" and profile_tokens.intersection({"memory", "grounded", "context"}):
        score += 10
    if "memory" in profile_tokens and key == "memory systems":
        score += 18
    if "eval" in profile_tokens and key in {"evals", "trace grading", "agent-output quality evals"}:
        score += 14
    if "orchestration" in profile_tokens and key in {"trace grading", "agent-output quality evals", "mcp"}:
        score += 12
    if key == "mcp" and profile_tokens.intersection({"systems", "workflow", "tool", "tools", "capability", "capabilities"}):
        score += 10
    if "connector" in profile_tokens and key == "mcp":
        score += 10
    if key == "mcp" and note_unresolved_concepts.intersection({"memory systems", "rag", "retrieval"}):
        score += 18
    if "credibility" in profile_tokens and key in {"rag", "evals", "trace grading", "memory systems"}:
        score += 6
    if key in {"cost evals", "latency evals", "reliability evals"}:
        score -= 8
    if key == "replays":
        score -= 10
    if key == "trace grading" and "evals" in note_unresolved_concepts:
        score += 12

    if active_session is not None and active_session.concept.strip().lower() == key:
        score += 60
    if state_status.lower() == "reopened":
        score += 50
    elif state_status.lower() == "in_progress":
        score += 40
    if build_link is not None and build_link.status == "captured" and build_link.unresolved_after_build:
        score += 35
    elif build_link is not None and build_link.status in {"planned", "active"}:
        score += 20
    if concept_notes_present:
        score += 15
        if knowledge.hierarchy_parent.strip():
            score += 18
    if "Open questions remain" in current_gap:
        score += 10

    unresolved_concepts = {
        concept_key
        for concept_key, raw_state in concept_states.items()
        if isinstance(raw_state, dict)
        and str(raw_state.get("status") or "").lower() in {"in_progress", "reopened"}
    }
    unresolved_concepts.update(note_unresolved_concepts)
    if concept_notes_present:
        unresolved_concepts.add(key)
    if build_link is not None and build_link.unresolved_after_build:
        unresolved_concepts.add(key)
    if active_session is not None:
        unresolved_concepts.add(active_session.concept.strip().lower())

    for relation in ("prerequisite", "next_after", "related"):
        for target, _rationale in knowledge.relations.get(relation, ()):
            if target.strip().lower() in unresolved_concepts:
                if relation == "prerequisite":
                    score += 12
                elif relation == "next_after":
                    score += 16
                else:
                    score += 6
    return score


def _concept_needs_frontdoor_recommendation(
    *,
    concept_body: str,
    state: dict[str, object],
    build_link: LearningBuildToLearnLink | None,
) -> bool:
    status = str(state.get("status") or "").lower()
    if status == "reopened":
        return True
    if build_link is not None and build_link.unresolved_after_build:
        return True

    understanding = str(
        state.get("current_understanding")
        or (_concept_note_field(concept_body, "My current understanding") or _concept_note_field(concept_body, "What it is"))
    ).lower()
    uncertainty = str(
        state.get("open_questions")
        or _concept_note_field(concept_body, "What is unclear")
        or _concept_note_field(concept_body, "Open questions")
    ).lower()
    early_markers = (
        "very early",
        "early",
        "not enough to explain",
        "cannot explain",
        "can't explain",
        "too vague",
        "still vague",
        "surface familiarity",
        "partial",
        "fuzzy",
        "just know the term",
    )
    if any(marker in understanding for marker in early_markers):
        return True
    if any(marker in uncertainty for marker in ("really necessary", "truly needed", "still unclear", "still fuzzy")):
        return True
    return False


def _ensure_private_build_to_learn_file() -> Path:
    path = _private_build_to_learn_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Build To Learn\n\n"
            "Use this file to capture bounded concept-learning experiments that should be learned partly by building.\n"
        )
    return path


def _private_concept_state_path() -> Path:
    return _private_user_root() / "learning" / "concept-state.json"


def _ensure_private_concept_state_file() -> Path:
    path = _private_concept_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps({"concepts": {}}, indent=2))
    return path


def _load_private_concept_state_store() -> dict[str, object]:
    path = _ensure_private_concept_state_file()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raw = {"concepts": {}}
    concepts = raw.get("concepts")
    if not isinstance(concepts, dict):
        concepts = {}
    return {"concepts": concepts}


def _save_private_concept_state_store(store: dict[str, object]) -> Path:
    path = _ensure_private_concept_state_file()
    path.write_text(json.dumps(store, indent=2, sort_keys=True))
    return path


def _normalize_concept_key(concept: str) -> str:
    return concept.strip().lower()


def _concept_state_entry(concept_key: str) -> dict[str, object]:
    store = _load_private_concept_state_store()
    concepts = store.get("concepts")
    if not isinstance(concepts, dict):
        return {}
    entry = concepts.get(concept_key)
    return entry if isinstance(entry, dict) else {}


def _upsert_learning_concept_state(
    concept: str,
    *,
    status: str | None = None,
    current_understanding: str | None = None,
    open_questions: str | None = None,
    note: str = "",
    source: str = "manual",
) -> Path:
    key = _normalize_concept_key(concept)
    if not key:
        raise ValueError("Concept is required to update learning concept state.")
    store = _load_private_concept_state_store()
    concepts = store["concepts"]
    assert isinstance(concepts, dict)
    existing = concepts.get(key)
    if not isinstance(existing, dict):
        existing = {"concept": concept.strip(), "history": []}
    history = existing.get("history")
    if not isinstance(history, list):
        history = []
    if status is not None:
        existing["status"] = status
    if current_understanding is not None:
        existing["current_understanding"] = current_understanding
    if open_questions is not None:
        existing["open_questions"] = open_questions
    existing["concept"] = concept.strip() or existing.get("concept", key)
    existing["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    history.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": source,
            "status": str(existing.get("status", "in_progress")),
            "note": note.strip(),
        }
    )
    existing["history"] = history[-20:]
    concepts[key] = existing
    return _save_private_concept_state_store(store)


def _normalize_build_to_learn_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"planned", "active", "captured"}:
        return normalized
    return "planned"


def _extract_build_to_learn_link(entry: dict[str, object], concept_name: str) -> LearningBuildToLearnLink | None:
    raw = entry.get("build_to_learn")
    if not isinstance(raw, dict):
        return None
    return LearningBuildToLearnLink(
        concept=str(raw.get("concept") or concept_name),
        status=_normalize_build_to_learn_status(str(raw.get("status") or "planned")),
        learning_goal=str(raw.get("learning_goal") or ""),
        experiment_slice=str(raw.get("experiment_slice") or ""),
        project_anchor=str(raw.get("project_anchor") or ""),
        success_signal=str(raw.get("success_signal") or ""),
        capture_prompt=str(raw.get("capture_prompt") or ""),
        captured_via=str(raw.get("captured_via") or "build-to-learn helper"),
        last_updated=str(raw.get("last_updated") or str(entry.get("updated_at") or "")),
        outcome_summary=str(raw.get("outcome_summary") or ""),
        unresolved_after_build=str(raw.get("unresolved_after_build") or ""),
        learning_effect=str(raw.get("learning_effect") or ""),
    )


def _normalize_reflection_field(value: str, fallback: str) -> str:
    cleaned = value.strip()
    return cleaned or fallback


def _looks_like_reflection_conclusion(raw_signal: str) -> bool:
    lowered = raw_signal.lower().strip()
    if not lowered:
        return False
    markers = (
        " i think ",
        " i believe ",
        " means ",
        " suggests ",
        " matters ",
        " increases ",
        " reduces ",
        " leads to ",
        " creates ",
        " amplifies ",
        " without ",
        " with ai",
        "ai ",
    )
    padded = f" {lowered} "
    return any(marker in padded for marker in markers)


def _looks_like_reflection_tension(raw_signal: str) -> bool:
    lowered = raw_signal.lower()
    markers = (
        "feel",
        "felt",
        "surprised",
        "uncomfortable",
        "worried",
        "concerned",
        "doubt",
        "cold feet",
        "tension",
        "frustrated",
        "energized",
        "excited",
    )
    return any(marker in lowered for marker in markers)


def build_dynamic_reflection_plan(raw_signal: str) -> dict[str, object]:
    normalized = raw_signal.strip()
    if not normalized:
        raise ValueError("Raw signal is required to build a reflection plan.")

    defaults: dict[str, str] = {}
    questions: list[dict[str, str]] = []
    conclusion_like = _looks_like_reflection_conclusion(normalized)
    tension_like = _looks_like_reflection_tension(normalized)

    if conclusion_like:
        defaults["current_conclusion"] = normalized
        questions.append(
            {
                "field": "what_happened",
                "prompt": "What concrete moment, example, or experience brought you to this view?",
            }
        )
        questions.append(
            {
                "field": "why_it_stood_out",
                "prompt": (
                    "Why does this feel important right now?"
                    if not tension_like
                    else "What about that moment felt sharp or important enough to capture?"
                ),
            }
        )
    elif tension_like:
        questions.extend(
            [
                {
                    "field": "what_happened",
                    "prompt": "What specifically triggered that reaction or tension?",
                },
                {
                    "field": "why_it_stood_out",
                    "prompt": "Why did that feel important enough to capture?",
                },
                {
                    "field": "current_conclusion",
                    "prompt": "What are you concluding from that right now?",
                },
            ]
        )
    else:
        questions.extend(
            [
                {
                    "field": "what_happened",
                    "prompt": "What concrete situation are you reacting to here?",
                },
                {
                    "field": "why_it_stood_out",
                    "prompt": "Why did this stand out to you?",
                },
                {
                    "field": "current_conclusion",
                    "prompt": "What are you concluding right now?",
                },
            ]
        )

    return {
        "questions": questions[:3],
        "defaults": defaults,
    }


def save_private_reflection_draft(
    raw_signal: str,
    *,
    scope: str = "",
    source: str = "",
    what_happened: str,
    why_it_stood_out: str,
    current_conclusion: str,
    confidence: str,
    possible_route: str,
    captured_via: str = "interactive reflection helper",
) -> Path:
    path = _ensure_private_reflections_file()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    scope_value = _normalize_reflection_field(scope, "unspecified")
    source_value = _normalize_reflection_field(source, "manual-capture")
    confidence_value = _normalize_reflection_field(confidence, "medium")
    route_value = _normalize_reflection_field(possible_route, "keep-private")
    entry = (
        f"\n\n## {timestamp} — reflection helper draft — {scope_value}\n\n"
        f"- Scope: {scope_value}\n"
        f"- Type: reflection-draft\n"
        f"- Source: {source_value}\n"
        f"- Confidence: {confidence_value}\n"
        f"- Route: {route_value}\n"
        f"- Captured via: {captured_via.strip() or 'interactive reflection helper'}\n\n"
        f"Signal:\n- {raw_signal.strip()}\n\n"
        f"What happened:\n- {what_happened.strip()}\n\n"
        f"Why it stood out:\n- {why_it_stood_out.strip()}\n\n"
        f"Current conclusion:\n- {current_conclusion.strip()}\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return path




def build_concept_teaching_brief(
    concept: str,
    *,
    current_understanding: str = "",
    what_is_unclear: str = "",
    where_encountered: str = "",
) -> dict[str, str]:
    normalized = concept.strip()
    if not normalized:
        raise ValueError("Concept is required to build a teaching brief.")
    knowledge = _learning_knowledge_for(
        normalized,
        current_understanding=current_understanding,
        what_is_unclear=what_is_unclear,
        where_encountered=where_encountered,
    )
    current_clause = f" Your current read is: {current_understanding.strip()}." if current_understanding.strip() else ""
    unclear_clause = f" The specific uncertainty right now is: {what_is_unclear.strip()}." if what_is_unclear.strip() else ""
    encountered_clause = f" It showed up in: {where_encountered.strip()}." if where_encountered.strip() else ""
    return {
        "what_it_is": f"{knowledge.what_it_is}{current_clause}".strip(),
        "why_it_exists": f"{knowledge.why_it_exists}{unclear_clause}".strip(),
        "nearby_distinction": f"{knowledge.nearby_distinction}{encountered_clause}".strip(),
        "os_connection": knowledge.os_connection,
        "product_implication": knowledge.product_implication,
    }


def _learning_agent_similarity_score(text: str, reference: str) -> float:
    text_words = {word for word in re.findall(r"[a-zA-Z0-9']+", text.lower()) if len(word) > 3}
    reference_words = {word for word in re.findall(r"[a-zA-Z0-9']+", reference.lower()) if len(word) > 3}
    if not text_words or not reference_words:
        return 0.0
    return len(text_words & reference_words) / max(1, len(reference_words))


def _learning_agent_example_sentence(knowledge: LearningConceptKnowledge) -> str:
    os_sentence = knowledge.os_connection.strip()
    if os_sentence:
        normalized = os_sentence[0].lower() + os_sentence[1:] if len(os_sentence) > 1 else os_sentence.lower()
        return f"For example, {normalized}"
    return f"For example, {knowledge.concept} matters when a system needs a more trustworthy decision than a polished-sounding answer alone can provide."


def _learning_agent_clarification_focus(session: LearningAgentSession, detail: str) -> str:
    detail_value = detail.strip()
    if detail_value:
        return detail_value
    if session.detected_gaps:
        return session.detected_gaps[0]
    if session.what_is_unclear.strip():
        return session.what_is_unclear.strip()
    return "the part that still feels fuzzy"


def _requested_learning_comparison_target(current_concept: str, detail: str) -> str:
    detail_value = detail.strip().lower()
    if not detail_value:
        return ""
    current_key = _normalize_concept_key(current_concept)
    candidates = sorted(
        (knowledge.concept for key, knowledge in _learning_concept_catalog().items() if key != current_key),
        key=len,
        reverse=True,
    )
    for candidate in candidates:
        if candidate.lower() in detail_value:
            return candidate
    return ""


def _learning_comparison_relationship_summary(source: LearningConceptKnowledge, target: LearningConceptKnowledge) -> str:
    source_key = _normalize_concept_key(source.concept)
    target_key = _normalize_concept_key(target.concept)

    def _has_relation(knowledge: LearningConceptKnowledge, relation: str, concept_key: str) -> bool:
        return any(_normalize_concept_key(name) == concept_key for name, _ in knowledge.relations.get(relation, ()))

    if _has_relation(source, "next_after", target_key) or _has_relation(target, "prerequisite", source_key):
        return (
            f"{source.concept} is the broader foundation here, and {target.concept} is a narrower follow-on or specialized layer inside that broader learning path."
        )
    if _has_relation(source, "prerequisite", target_key) or _has_relation(target, "next_after", source_key):
        return (
            f"{target.concept} is the broader or more foundational concept here, and {source.concept} builds on top of it as a narrower follow-on."
        )
    if _has_relation(source, "often_confused_with", target_key) or _has_relation(target, "often_confused_with", source_key):
        return (
            f"{source.concept} and {target.concept} are sibling concepts that are easy to confuse, but neither is simply a subset of the other."
        )
    if _has_relation(source, "related", target_key) or _has_relation(target, "related", source_key):
        return (
            f"{source.concept} and {target.concept} are adjacent concepts. They are related, but there is no strong parent-child hierarchy captured in the current learning model."
        )
    return (
        f"There is no strong stored hierarchy between {source.concept} and {target.concept} in the current learning model, so the comparison should stay conservative and focus on scope and purpose."
    )


def _load_private_learning_agent_session_store() -> dict[str, object]:
    path = _ensure_private_learning_agent_session_file()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raw = {"active_session": None}
    if not isinstance(raw, dict):
        raw = {"active_session": None}
    return raw


def _save_private_learning_agent_session_store(store: dict[str, object]) -> Path:
    path = _ensure_private_learning_agent_session_file()
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _learning_session_from_dict(raw: dict[str, object]) -> LearningAgentSession | None:
    if not isinstance(raw, dict):
        return None
    concept = str(raw.get("concept", "")).strip()
    if not concept:
        return None
    gaps = raw.get("detected_gaps", [])
    if not isinstance(gaps, list):
        gaps = []
    return LearningAgentSession(
        concept=concept,
        session_status=str(raw.get("session_status", "active") or "active"),
        where_encountered=str(raw.get("where_encountered", "") or ""),
        current_understanding=str(raw.get("current_understanding", "") or ""),
        what_is_unclear=str(raw.get("what_is_unclear", "") or ""),
        what_it_is=str(raw.get("what_it_is", "") or ""),
        why_it_exists=str(raw.get("why_it_exists", "") or ""),
        nearby_distinction=str(raw.get("nearby_distinction", "") or ""),
        os_connection=str(raw.get("os_connection", "") or ""),
        product_implication=str(raw.get("product_implication", "") or ""),
        latest_explanation_back=str(raw.get("latest_explanation_back", "") or ""),
        clarification_response=str(raw.get("clarification_response", "") or ""),
        implementation_walkthrough=str(raw.get("implementation_walkthrough", "") or ""),
        implementation_relationships=str(raw.get("implementation_relationships", "") or ""),
        detected_gaps=tuple(str(item) for item in gaps),
        next_move=str(raw.get("next_move", "explain_back") or "explain_back"),
        proposed_concept_status=str(raw.get("proposed_concept_status", "") or ""),
        hand_back_reason=str(raw.get("hand_back_reason", "") or ""),
        coach_message=str(raw.get("coach_message", "") or ""),
        turn_count=int(raw.get("turn_count", 0) or 0),
        updated_at=str(raw.get("updated_at", "") or ""),
    )


def _build_learning_clarification_response(
    session: LearningAgentSession,
    action: Literal["simpler", "specific_confusion", "another_example", "nearby_comparison"],
    detail: str = "",
) -> str:
    knowledge = _learning_knowledge_for(
        session.concept,
        current_understanding=session.current_understanding,
        what_is_unclear=session.what_is_unclear,
        where_encountered=session.where_encountered,
    )
    focus = _learning_agent_clarification_focus(session, detail)
    focus_lower = focus.lower()
    latest = session.latest_explanation_back.strip()

    if action == "simpler":
        response = (
            f"In plainer language, {knowledge.concept} is this: {knowledge.what_it_is} "
            f"It matters because {knowledge.why_it_exists[0].lower() + knowledge.why_it_exists[1:] if len(knowledge.why_it_exists) > 1 else knowledge.why_it_exists.lower()} "
            f"{_learning_agent_example_sentence(knowledge)}."
        )
        if latest:
            response += " In your next explanation, keep that mechanism and reason, and drop any extra system words that are not doing real work."
        return response.strip()

    if action == "specific_confusion":
        if any(marker in focus_lower for marker in ("when", "threshold", "necessary", "needed", "overkill", "enough")):
            return (
                f"The confusion here is really about {focus}. "
                f"The anchor is this: {knowledge.why_it_exists} "
                f"{_learning_agent_example_sentence(knowledge)}. "
                "What usually clears this up is asking: what specific problem exists that a simpler path would not solve?"
            ).strip()
        if any(marker in focus_lower for marker in ("difference", "different", "vs", "versus", "compare", "same")):
            return (
                f"The key distinction is this: {knowledge.nearby_distinction} "
                "If you can explain that difference cleanly, the concept usually stops feeling fuzzy."
            ).strip()
        if any(marker in focus_lower for marker in ("where", "implemented", "os", "workflow", "appear", "used")):
            return (
                f"The best anchor for that confusion is where it shows up in the OS: {knowledge.os_connection} "
                "That tells you what practical job the concept is doing instead of leaving it as vocabulary."
            ).strip()
        return (
            f"Let’s focus on {focus}. The core mechanism is: {knowledge.what_it_is} "
            f"The sharpest distinction to keep in mind is: {knowledge.nearby_distinction} "
            f"{_learning_agent_example_sentence(knowledge)}."
        ).strip()

    if action == "another_example":
        return (
            f"Here is another concrete anchor: {_learning_agent_example_sentence(knowledge)} "
            f"What makes that example useful is the product implication: {knowledge.product_implication}"
        ).strip()

    requested_target = _requested_learning_comparison_target(session.concept, detail)
    if requested_target:
        target_knowledge = _learning_knowledge_for(requested_target)
        relationship_summary = _learning_comparison_relationship_summary(knowledge, target_knowledge)
        hierarchy_prompt = " The hierarchy question you asked about should be answered directly."
        if "hierarch" not in detail.lower():
            hierarchy_prompt = ""
        return (
            f"Compare them this way: {knowledge.concept} is about {knowledge.what_it_is.lower()} "
            f"{target_knowledge.concept} is about {target_knowledge.what_it_is.lower()} "
            f"The structural relationship is: {relationship_summary}{hierarchy_prompt} "
            f"In the OS, {knowledge.concept} connects here: {knowledge.os_connection} "
            f"while {target_knowledge.concept} connects here: {target_knowledge.os_connection} "
            "If you remember one thing, remember which concept is broader and which one is the narrower or more specialized layer."
        ).strip()

    comparison_target = knowledge.nearby_distinction
    if detail.strip():
        comparison_target = f"{comparison_target} The comparison you asked about was: {detail.strip()}."
    return (
        f"A useful comparison is this: {comparison_target} "
        f"If you remember one thing, remember the core mechanism: {knowledge.what_it_is}"
    ).strip()


def _build_learning_gap_feedback(
    concept: str,
    explanation_back: str,
    *,
    nearby_distinction: str,
    os_connection: str,
    current_understanding: str,
) -> dict[str, object]:
    knowledge = _learning_knowledge_for(
        concept,
        current_understanding=current_understanding,
        what_is_unclear="",
        where_encountered=os_connection,
    )
    store = _load_private_concept_state_store()
    concepts_store = store.get("concepts")
    if not isinstance(concepts_store, dict):
        concepts_store = {}
    compounding_signal = _learning_compounding_signal(
        knowledge,
        catalog=_learning_concept_catalog(),
        concept_states=concepts_store,
        active_session=load_learning_agent_session(),
    )
    text = explanation_back.strip()
    lowered = text.lower()
    words = re.findall(r"[a-zA-Z0-9']+", text)
    concept_label = concept.strip()
    gaps: list[str] = []
    sentence_count = len([part for part in re.split(r"[.!?]+", text) if part.strip()])
    has_reason_marker = any(
        marker in lowered
        for marker in (
            "because",
            "so that",
            "in order",
            "exists to",
            "used to",
            "helps",
            "the aim is",
            "the goal is",
            "matters because",
            "when ",
        )
    )
    has_example_marker = any(
        marker in lowered
        for marker in (
            "for example",
            "for an example",
            "example",
            "for instance",
            "in the os",
            "in an agent workflow",
            "in this workflow",
        )
    )
    has_distinction_marker = any(
        marker in lowered for marker in ("not the same", "different", "rather than", "instead of", "versus", "vs")
    ) or _learning_agent_similarity_score(text, nearby_distinction) >= 0.15
    has_mechanism_overlap = _learning_agent_similarity_score(text, knowledge.what_it_is) >= 0.18
    has_os_anchor = _learning_agent_similarity_score(text, os_connection) >= 0.16

    if len(words) < 14:
        gaps.append("The explanation is still thin. It needs a clearer mechanism, not just a headline.")
    if concept_label and concept_label.lower() in lowered and sentence_count <= 2 and not has_reason_marker and not has_example_marker:
        gaps.append("The explanation still leans on the term itself instead of explaining the idea underneath it.")
    if not has_mechanism_overlap:
        gaps.append("The mechanism is still vague. It is not yet clear what the concept actually does.")
    if not has_reason_marker:
        gaps.append("It is still not clear why the concept exists or when it matters.")
    if not has_example_marker and not has_os_anchor:
        gaps.append("It would be stronger with one concrete example or situation where the concept matters.")
    if nearby_distinction.strip() and not has_distinction_marker:
        gaps.append("The explanation would be stronger if it separated this concept from the nearby thing it is easiest to confuse it with.")
    abstract_terms = ("system", "workflow", "context", "architecture", "orchestration", "capability", "integration", "process")
    if sum(1 for term in abstract_terms if term in lowered) >= 3 and len(words) < 45 and not has_mechanism_overlap:
        gaps.append("The explanation still depends on broad system words more than a plain mechanism.")

    distinction_only_gap = [
        "The explanation would be stronger if it separated this concept from the nearby thing it is easiest to confuse it with."
    ]
    if (
        gaps == distinction_only_gap
        and has_mechanism_overlap
        and has_reason_marker
        and (has_example_marker or has_os_anchor)
    ):
        gaps = []

    key = concept_label.strip().lower()
    build_first_concepts = {"rag", "trace grading", "agent-output quality evals", "memory systems", "mcp"}
    broad_uncertainty_markers = (
        "not sure",
        "i'm not sure",
        "dont know",
        "don't know",
        "unclear",
        "confused",
        "lost",
        "everything",
        "whole thing",
        "all of it",
        "overall system",
        "overall workflow",
    )
    severe_ambiguity = (
        sum(1 for marker in broad_uncertainty_markers if marker in lowered) >= 1
        and sum(1 for term in abstract_terms if term in lowered) >= 2
    ) or (
        sentence_count <= 2
        and sum(1 for term in abstract_terms if term in lowered) >= 4
        and not has_mechanism_overlap
        and "example" not in lowered
    )
    if gaps:
        if severe_ambiguity and len(gaps) >= 3:
            return {
                "detected_gaps": gaps,
                "next_move": "hand_back",
                "hand_back_reason": (
                    "The explanation is still too broad to improve responsibly through another normal clarification turn."
                ),
                "coach_message": (
                    "Let's narrow this down before we continue. "
                    "Pick one specific part of the concept, one concrete example, or one exact question to anchor the next turn."
                ),
            }
        next_move = "clarify"
        top_gap = gaps[0].lower()
        if "nearby thing" in top_gap and nearby_distinction.strip():
            coach_message = (
                "You are getting closer. Tighten the distinction next: "
                f"{nearby_distinction.strip()}"
            )
        elif "example" in top_gap and os_connection.strip():
            coach_message = (
                "You are close, but the explanation still needs a concrete anchor. "
                f"Use this OS example: {os_connection.strip()}"
            )
        elif "why the concept exists" in top_gap:
            coach_message = (
                "You are close, but the explanation still needs the reason for the concept, not just the label. "
                "Use this question: what problem does it solve that a simpler path would not?"
            )
        else:
            coach_message = (
                "You are close, but the understanding still feels partial. "
                "Try again in plain language and make the mechanism more concrete."
            )
    else:
        if key in build_first_concepts and learning_build_to_learn_enabled():
            next_move = "build_to_learn"
            coach_message = (
                "This explanation is now strong enough to move beyond vocabulary. "
                "The next best move is to pressure-test it through one bounded build-to-learn step."
            )
        else:
            next_move = "save_understanding"
            coach_message = (
                "This explanation is in good shape. The next move is to save the understanding back into concept state and decide whether any doubts remain."
            )
        if compounding_signal.why_now_addition:
            coach_message = f"{coach_message} {compounding_signal.why_now_addition}".strip()
        elif compounding_signal.suggested_path_addition:
            coach_message = f"{coach_message} {compounding_signal.suggested_path_addition}".strip()
        else:
            follow_on = _follow_on_learning_move(knowledge)
            if follow_on:
                coach_message = f"{coach_message} {follow_on}".strip()
    return {
        "detected_gaps": gaps,
        "next_move": next_move,
        "hand_back_reason": "",
        "coach_message": coach_message,
    }


def _agent_proposed_concept_status(concept: str, *, next_move: str) -> str:
    existing = _concept_state_entry(_normalize_concept_key(concept))
    current_status = str(existing.get("status") or "").lower()
    if next_move == "build_to_learn":
        return "build_to_learn"
    if next_move == "save_understanding":
        return "learned"
    if current_status == "learned":
        return "reopened"
    if current_status == "build_to_learn":
        return "build_to_learn"
    if current_status in {"in_progress", "reopened"}:
        return current_status
    return "in_progress"


def _apply_learning_agent_low_risk_transition(
    concept: str,
    *,
    proposed_status: str,
    current_understanding: str,
    open_questions: str,
    note: str,
) -> None:
    if proposed_status not in {"in_progress", "reopened"}:
        return
    existing = _concept_state_entry(_normalize_concept_key(concept))
    current_status = str(existing.get("status") or "").lower()
    if current_status == proposed_status:
        return
    save_learning_concept_management_update(
        concept,
        status=proposed_status,
        current_understanding=current_understanding,
        open_questions=open_questions,
        note=note,
        source="learning agent session",
    )


def load_learning_agent_session() -> LearningAgentSession | None:
    store = _load_private_learning_agent_session_store()
    return _learning_session_from_dict(store.get("active_session", {}))


def start_learning_agent_session(
    concept: str,
    *,
    where_encountered: str = "",
    current_understanding: str = "",
    what_is_unclear: str = "",
) -> LearningAgentSession:
    concept_value = concept.strip()
    if not concept_value:
        raise ValueError("Concept is required to start a learning-agent session.")
    ensure_learning_turn_available(concept_value)
    proposed_status = _agent_proposed_concept_status(
        concept_value,
        next_move="clarify",
    )
    _apply_learning_agent_low_risk_transition(
        concept_value,
        proposed_status=proposed_status,
        current_understanding=current_understanding.strip(),
        open_questions=what_is_unclear.strip(),
        note="Learning session started.",
    )
    try:
        teaching_turn = _run_live_learning_teaching_turn(
            concept_value,
            where_encountered=where_encountered,
            current_understanding=current_understanding,
            what_is_unclear=what_is_unclear,
        )
        brief = {
            "what_it_is": teaching_turn.what_it_is,
            "why_it_exists": teaching_turn.why_it_exists,
            "nearby_distinction": teaching_turn.nearby_distinction,
            "os_connection": teaching_turn.os_connection,
            "product_implication": teaching_turn.product_implication,
            "coach_message": teaching_turn.coach_message,
        }
    except LivePMDiscoveryError:
        brief = build_concept_teaching_brief(
            concept_value,
            current_understanding=current_understanding,
            what_is_unclear=what_is_unclear,
            where_encountered=where_encountered,
        )
    raw_session = {
        "concept": concept_value,
        "session_status": "active",
        "where_encountered": where_encountered.strip(),
        "current_understanding": current_understanding.strip(),
        "what_is_unclear": what_is_unclear.strip(),
        "what_it_is": brief.get("what_it_is", ""),
        "why_it_exists": brief.get("why_it_exists", ""),
        "nearby_distinction": brief.get("nearby_distinction", ""),
        "os_connection": brief.get("os_connection", ""),
        "product_implication": brief.get("product_implication", ""),
        "latest_explanation_back": "",
        "clarification_response": "",
        "implementation_walkthrough": "",
        "implementation_relationships": "",
        "detected_gaps": [],
        "next_move": "clarify",
        "proposed_concept_status": proposed_status,
        "hand_back_reason": "",
        "coach_message": brief.get(
            "coach_message",
            "Use the teaching brief, ask for clarification where needed, and capture what is clearer once the concept feels more grounded.",
        ),
        "turn_count": 0,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save_private_learning_agent_session_store({"active_session": raw_session})
    log_learning_live_turn("learning_session_started", concept=concept_value)
    session = _learning_session_from_dict(raw_session)
    assert session is not None
    return session


def continue_learning_agent_session(explanation_back: str) -> LearningAgentSession:
    session = load_learning_agent_session()
    if session is None:
        raise ValueError("No active learning-agent session exists.")
    feedback = _build_learning_gap_feedback(
        session.concept,
        explanation_back,
        nearby_distinction=session.nearby_distinction,
        os_connection=session.os_connection,
        current_understanding=session.current_understanding,
    )
    proposed_status = _agent_proposed_concept_status(
        session.concept,
        next_move=str(feedback["next_move"]),
    )
    _apply_learning_agent_low_risk_transition(
        session.concept,
        proposed_status=proposed_status,
        current_understanding=explanation_back.strip() or session.current_understanding,
        open_questions=" ".join(feedback["detected_gaps"]) or session.what_is_unclear,
        note="Concept progression updated from learning-agent session.",
    )
    raw_session = {
        "concept": session.concept,
        "session_status": "active",
        "where_encountered": session.where_encountered,
        "current_understanding": session.current_understanding,
        "what_is_unclear": session.what_is_unclear,
        "what_it_is": session.what_it_is,
        "why_it_exists": session.why_it_exists,
        "nearby_distinction": session.nearby_distinction,
        "os_connection": session.os_connection,
        "product_implication": session.product_implication,
        "latest_explanation_back": explanation_back.strip(),
        "clarification_response": "",
        "implementation_walkthrough": session.implementation_walkthrough,
        "implementation_relationships": session.implementation_relationships,
        "detected_gaps": list(feedback["detected_gaps"]),
        "next_move": str(feedback["next_move"]),
        "proposed_concept_status": proposed_status,
        "hand_back_reason": str(feedback.get("hand_back_reason", "")),
        "coach_message": str(feedback["coach_message"]),
        "turn_count": session.turn_count + 1,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save_private_learning_agent_session_store({"active_session": raw_session})
    updated = _learning_session_from_dict(raw_session)
    assert updated is not None
    return updated


def pause_learning_agent_session() -> Path:
    session = load_learning_agent_session()
    if session is None:
        raise ValueError("No active learning-agent session exists.")
    raw_session = {
        "concept": session.concept,
        "session_status": "paused",
        "where_encountered": session.where_encountered,
        "current_understanding": session.current_understanding,
        "what_is_unclear": session.what_is_unclear,
        "what_it_is": session.what_it_is,
        "why_it_exists": session.why_it_exists,
        "nearby_distinction": session.nearby_distinction,
        "os_connection": session.os_connection,
        "product_implication": session.product_implication,
        "latest_explanation_back": session.latest_explanation_back,
        "clarification_response": session.clarification_response,
        "implementation_walkthrough": session.implementation_walkthrough,
        "implementation_relationships": session.implementation_relationships,
        "detected_gaps": list(session.detected_gaps),
        "next_move": session.next_move,
        "proposed_concept_status": session.proposed_concept_status,
        "hand_back_reason": session.hand_back_reason,
        "coach_message": session.coach_message,
        "turn_count": session.turn_count,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    return _save_private_learning_agent_session_store({"active_session": raw_session})


def request_learning_agent_clarification(
    action: Literal["simpler", "specific_confusion", "another_example", "nearby_comparison"],
    *,
    detail: str = "",
) -> LearningAgentSession:
    session = load_learning_agent_session()
    if session is None:
        raise ValueError("No active learning-agent session exists.")
    ensure_learning_turn_available(session.concept)
    try:
        clarification_turn = _run_live_learning_clarification_turn(session, action, detail=detail)
        clarification_response = clarification_turn.clarification_response
        coach_message = clarification_turn.coach_message
    except LivePMDiscoveryError:
        clarification_response = _build_learning_clarification_response(session, action, detail=detail)
        coach_message = "Use the clarification above, then capture what is clearer now or ask one more focused follow-up."
    raw_session = {
        "concept": session.concept,
        "session_status": "active",
        "where_encountered": session.where_encountered,
        "current_understanding": session.current_understanding,
        "what_is_unclear": detail.strip() or session.what_is_unclear,
        "what_it_is": session.what_it_is,
        "why_it_exists": session.why_it_exists,
        "nearby_distinction": session.nearby_distinction,
        "os_connection": session.os_connection,
        "product_implication": session.product_implication,
        "latest_explanation_back": session.latest_explanation_back,
        "clarification_response": clarification_response,
        "implementation_walkthrough": session.implementation_walkthrough,
        "implementation_relationships": session.implementation_relationships,
        "detected_gaps": list(session.detected_gaps),
        "next_move": "clarify",
        "proposed_concept_status": _agent_proposed_concept_status(
            session.concept,
            next_move="clarify",
        ),
        "hand_back_reason": "",
        "coach_message": coach_message,
        "turn_count": session.turn_count,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save_private_learning_agent_session_store({"active_session": raw_session})
    log_learning_live_turn("learning_clarification_requested", concept=session.concept)
    updated = _learning_session_from_dict(raw_session)
    assert updated is not None
    return updated


def request_learning_agent_implementation_walkthrough() -> LearningAgentSession:
    session = load_learning_agent_session()
    if session is None:
        raise ValueError("No active learning-agent session exists.")
    anchors = learning_implementation_anchors(session.concept)
    if not anchors:
        raw_session = {
            "concept": session.concept,
            "session_status": "active",
            "where_encountered": session.where_encountered,
            "current_understanding": session.current_understanding,
            "what_is_unclear": session.what_is_unclear,
            "what_it_is": session.what_it_is,
            "why_it_exists": session.why_it_exists,
            "nearby_distinction": session.nearby_distinction,
            "os_connection": session.os_connection,
            "product_implication": session.product_implication,
            "latest_explanation_back": session.latest_explanation_back,
            "clarification_response": session.clarification_response,
            "implementation_walkthrough": "",
            "implementation_relationships": "",
            "detected_gaps": list(session.detected_gaps),
            "next_move": "hand_back",
            "proposed_concept_status": session.proposed_concept_status,
            "hand_back_reason": f"The OS does not yet have clear implementation anchors for {session.concept}.",
            "coach_message": "Keep learning the concept through explanation or build-to-learn for now, and only ask for implementation walkthroughs when the OS truly implements the concept.",
            "turn_count": session.turn_count,
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
        }
        _save_private_learning_agent_session_store({"active_session": raw_session})
        updated = _learning_session_from_dict(raw_session)
        assert updated is not None
        return updated
    ensure_learning_turn_available(session.concept)
    try:
        turn = _run_live_learning_implementation_turn(session, anchors)
        walkthrough_intro = turn.walkthrough_intro
        relationships = turn.how_the_pieces_fit
        coach_message = turn.coach_message
    except LivePMDiscoveryError:
        fallback = _build_learning_implementation_walkthrough_response(session, anchors)
        walkthrough_intro = fallback["walkthrough_intro"]
        relationships = fallback["how_the_pieces_fit"]
        coach_message = fallback["coach_message"]
    raw_session = {
        "concept": session.concept,
        "session_status": "active",
        "where_encountered": session.where_encountered,
        "current_understanding": session.current_understanding,
        "what_is_unclear": session.what_is_unclear,
        "what_it_is": session.what_it_is,
        "why_it_exists": session.why_it_exists,
        "nearby_distinction": session.nearby_distinction,
        "os_connection": session.os_connection,
        "product_implication": session.product_implication,
        "latest_explanation_back": session.latest_explanation_back,
        "clarification_response": session.clarification_response,
        "implementation_walkthrough": walkthrough_intro,
        "implementation_relationships": relationships,
        "detected_gaps": list(session.detected_gaps),
        "next_move": "clarify",
        "proposed_concept_status": session.proposed_concept_status,
        "hand_back_reason": "",
        "coach_message": coach_message,
        "turn_count": session.turn_count,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _save_private_learning_agent_session_store({"active_session": raw_session})
    log_learning_live_turn("learning_implementation_requested", concept=session.concept)
    updated = _learning_session_from_dict(raw_session)
    assert updated is not None
    return updated


def clear_learning_agent_session() -> Path:
    return _save_private_learning_agent_session_store({"active_session": None})


def _concept_note_sections() -> dict[str, str]:
    path = _ensure_private_concept_notes_file()
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"\n### Concept: ", text)
    results: dict[str, str] = {}
    for index, chunk in enumerate(sections):
        if index == 0:
            continue
        title, _, body = chunk.partition("\n")
        concept = title.strip()
        if concept:
            results[concept.lower()] = body
    return results


def _concept_note_needs_more_learning(body: str) -> bool:
    lowered = body.lower()
    markers = (
        "to be learned",
        "very early",
        "i don't know",
        "do not know",
        "need to understand",
        "potentially relevant",
    )
    return any(marker in lowered for marker in markers)


def _concept_note_field(body: str, heading: str) -> str:
    pattern = rf"#### {re.escape(heading)}\n(.*?)(?=\n#### |\Z)"
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _display_concept_name(concept_key: str) -> str:
    normalized = concept_key.strip().lower()
    special = {
        "mcp": "MCP",
        "rag": "RAG",
    }
    return special.get(normalized, normalized.title())


def list_learning_concept_recommendations(limit: int = 4) -> list[LearningConceptRecommendation]:
    sections = _concept_note_sections()
    profile = load_learning_profile()
    store = _load_private_concept_state_store()
    concepts_store = store.get("concepts")
    if not isinstance(concepts_store, dict):
        concepts_store = {}

    active_session = load_learning_agent_session()
    catalog_map = _learning_concept_catalog()
    catalog = list(catalog_map.values())
    scored: list[tuple[int, LearningConceptRecommendation]] = []
    note_unresolved_concepts = {
        concept_key
        for concept_key, body in sections.items()
        if _concept_note_needs_more_learning(body)
        or (
            (_concept_note_field(body, "Open questions") or "").strip()
            and (_concept_note_field(body, "Open questions") or "").strip().lower() != "no open questions captured yet."
        )
    }

    for knowledge in catalog:
        key = knowledge.concept.lower()
        body = sections.get(key, "")
        state = concepts_store.get(key)
        if not isinstance(state, dict):
            state = {}
        build_link = _extract_build_to_learn_link(state, knowledge.concept)
        compounding_signal = _learning_compounding_signal(
            knowledge,
            catalog=catalog_map,
            concept_states=concepts_store,
            active_session=active_session,
        )
        has_durable_learning_state = bool(body.strip() or state or build_link is not None)
        if has_durable_learning_state and not (
            active_session is not None and active_session.concept.strip().lower() == key
        ) and not _concept_needs_frontdoor_recommendation(
            concept_body=body,
            state=state,
            build_link=build_link,
        ) and not compounding_signal.resurfaced_from_learned:
            continue

        state_status = str(state.get("status") or "")
        is_learned = state_status.lower() == "learned" and not build_link and not body
        if body and not _concept_note_needs_more_learning(body) and state_status.lower() == "learned" and not build_link and not compounding_signal.resurfaced_from_learned:
            continue
        if is_learned and not compounding_signal.resurfaced_from_learned:
            continue

        current_gap = "Not yet captured as a full learning state."
        if body:
            understanding = _concept_note_field(body, "My current understanding") or _concept_note_field(body, "What it is")
            open_questions = _concept_note_field(body, "Open questions")
            if understanding:
                current_gap = f"Current note is still partial: {understanding}"
            if open_questions and open_questions.lower() != "no open questions captured yet.":
                current_gap = f"Open questions remain: {open_questions}"
        if state.get("open_questions"):
            current_gap = f"Open questions remain: {str(state.get('open_questions')).strip()}"
        elif state.get("current_understanding") and state_status.lower() in {"in_progress", "reopened"}:
            current_gap = f"Current understanding is still developing: {str(state.get('current_understanding')).strip()}"
        if build_link is not None and build_link.status == "captured" and build_link.unresolved_after_build:
            if learning_build_to_learn_enabled():
                current_gap = f"Build-to-learn still left this unresolved: {build_link.unresolved_after_build}"
            else:
                current_gap = f"A previous deeper exploration still left this unresolved: {build_link.unresolved_after_build}"

        suggested_path = (
            "Start a learning session and let the learning agent decide whether this needs clarification, a distinction, or an implementation walkthrough."
            if not learning_build_to_learn_enabled()
            else "Start a learning session and let the learning agent decide whether this needs clarification, a distinction, or a build step."
        )
        if active_session is not None and active_session.concept.strip().lower() == key:
            suggested_path = "Resume the active learning session and keep building understanding from the current thread."
        elif learning_build_to_learn_enabled() and build_link is not None and build_link.status in {"planned", "active"}:
            suggested_path = "Open the linked build pathway, then bring what it teaches back into the learning session."
        elif state_status.lower() in {"reopened", "in_progress"}:
            suggested_path = "Resume the learning session with the current state and work through the remaining uncertainty."
        elif learning_build_to_learn_enabled() and build_link is not None and build_link.status == "captured":
            suggested_path = "Resume the learning session with the build outcome and decide whether the concept is now settled or still needs sharpening."

        if compounding_signal.current_gap_addition:
            current_gap = f"{current_gap} {compounding_signal.current_gap_addition}".strip()
        if compounding_signal.why_now_addition:
            why_now = f"{knowledge.why_now} {compounding_signal.why_now_addition}".strip()
        else:
            why_now = knowledge.why_now
        if compounding_signal.suggested_path_addition:
            suggested_path = f"{suggested_path} {compounding_signal.suggested_path_addition}".strip()

        recommendation = LearningConceptRecommendation(
            concept=knowledge.concept,
            why_now=why_now,
            where_it_connects=knowledge.where_it_connects,
            suggested_path=_personalized_learning_path(knowledge.concept, profile, suggested_path),
            current_gap=_personalized_gap(current_gap, profile),
            why_for_you=_personalized_learning_reason(knowledge.concept, profile),
        )
        score = _learning_recommendation_relevance_score(
            knowledge,
            profile,
            active_session=active_session,
            state_status=state_status,
            current_gap=current_gap,
            build_link=build_link,
            concept_notes_present=bool(body and _concept_note_needs_more_learning(body)),
            concept_states=concepts_store,
            note_unresolved_concepts=note_unresolved_concepts,
        )
        score += compounding_signal.score_bonus
        scored.append((score, recommendation))

    scored.sort(key=lambda item: (-item[0], item[1].concept.lower()))
    return [item for _, item in scored[:limit]]


def _build_to_learn_sections() -> dict[str, str]:
    path = _ensure_private_build_to_learn_file()
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"\n## \d{4}-\d{2}-\d{2} — ", text)
    results: dict[str, str] = {}
    for index, chunk in enumerate(sections):
        if index == 0:
            continue
        title, _, body = chunk.partition("\n")
        concept = title.strip()
        if concept:
            results[concept.lower()] = body
    return results


def _learning_recommendation_map(limit: int = 10) -> dict[str, LearningConceptRecommendation]:
    return {item.concept.lower(): item for item in list_learning_concept_recommendations(limit=limit)}


def _build_learning_concept_view(
    concept_key: str,
    *,
    concept_sections: dict[str, str],
    build_sections: dict[str, str],
    recommendation_map: dict[str, LearningConceptRecommendation],
    concepts_store: dict[str, object],
    active_session: LearningAgentSession | None,
) -> LearningConceptView:
    body = concept_sections.get(concept_key, "")
    build_body = build_sections.get(concept_key, "")
    recommendation = recommendation_map.get(concept_key)
    state = concepts_store.get(concept_key)
    if not isinstance(state, dict):
        state = {}

    concept_name = str(state.get("concept") or _display_concept_name(concept_key))
    understanding = str(
        state.get("current_understanding")
        or (_concept_note_field(body, "My current understanding") or _concept_note_field(body, "What it is"))
    )
    open_questions = str(state.get("open_questions") or _concept_note_field(body, "Open questions"))
    build_link = _extract_build_to_learn_link(state, concept_name)
    inferred_status = "upcoming"
    recommended_next_move = (
        recommendation.suggested_path
        if recommendation
        else "Review and decide whether to continue learning, create a build pathway, or reopen this concept."
    )
    if body:
        if _concept_note_needs_more_learning(body) or (open_questions and open_questions.lower() != "no open questions captured yet."):
            inferred_status = "in_progress"
            recommended_next_move = (
                f"Resolve open questions: {open_questions}"
                if open_questions and open_questions.lower() != "no open questions captured yet."
                else "Continue with the learning agent to tighten the current understanding."
            )
        else:
            inferred_status = "learned"
            recommended_next_move = "Reuse this concept confidently and deepen only if a new edge case appears."
    elif build_body:
        inferred_status = "in_progress"
        success_signal = re.search(r"### Success signal\n(.*?)(?=\n### |\Z)", build_body, re.DOTALL)
        recommended_next_move = success_signal.group(1).strip() if success_signal else "Run the bounded experiment and capture what changed."
    if build_link is not None:
        if build_link.status == "captured":
            recommended_next_move = (
                f"Remaining uncertainty: {build_link.unresolved_after_build}"
                if build_link.unresolved_after_build
                else "Resume the learning session with the build outcome and decide whether the concept is now settled or still needs sharpening."
            )
        elif build_link.status in {"planned", "active"}:
            recommended_next_move = build_link.success_signal or recommended_next_move

    status = str(state.get("status") or inferred_status)
    history = state.get("history")
    history_count = len(history) if isinstance(history, list) else 0

    concept_state: LearningConceptState | None = None
    if body or build_body or state:
        concept_state = LearningConceptState(
            concept=concept_name,
            status=status,
            current_understanding=understanding,
            open_questions=open_questions,
            history_count=history_count,
        )

    session_state = None
    if active_session is not None and active_session.concept.strip().lower() == concept_key:
        session_state = active_session

    return LearningConceptView(
        concept=concept_name,
        recommendation=recommendation,
        concept_state=concept_state,
        session_state=session_state,
        build_state=build_link,
        recommended_next_move=recommended_next_move,
    )


def list_learning_concept_views() -> list[LearningConceptView]:
    concept_sections = _concept_note_sections()
    build_sections = _build_to_learn_sections()
    catalog_keys = set(_learning_concept_catalog())
    recommendation_map = _learning_recommendation_map(limit=max(10, len(catalog_keys)))
    store = _load_private_concept_state_store()
    concepts_store = store.get("concepts")
    if not isinstance(concepts_store, dict):
        concepts_store = {}

    all_keys = catalog_keys | set(concept_sections) | set(build_sections) | set(recommendation_map) | set(concepts_store)
    views: list[LearningConceptView] = []
    active_session = load_learning_agent_session()
    for concept_key in all_keys:
        views.append(
            _build_learning_concept_view(
                concept_key,
                concept_sections=concept_sections,
                build_sections=build_sections,
                recommendation_map=recommendation_map,
                concepts_store=concepts_store,
                active_session=active_session,
            )
        )

    views.sort(key=lambda item: item.concept.lower())
    return views


def learning_concept_records() -> list[LearningConceptRecord]:
    records: list[LearningConceptRecord] = []
    for view in list_learning_concept_views():
        concept_state = view.concept_state
        records.append(
            LearningConceptRecord(
                concept=view.concept,
                status=concept_state.status if concept_state is not None else "upcoming",
                current_understanding=concept_state.current_understanding if concept_state is not None else "",
                open_questions=concept_state.open_questions if concept_state is not None else "",
                recommended_next_move=view.recommended_next_move,
                why_now=view.recommendation.why_now if view.recommendation is not None else "Concept is present in the learning layer.",
                current_gap=view.recommendation.current_gap if view.recommendation is not None else "No current gap captured yet.",
                history_count=concept_state.history_count if concept_state is not None else 0,
                build_to_learn=view.build_state,
            )
        )

    records.sort(key=lambda item: item.concept.lower())
    return records


def learning_concept_record(concept: str) -> LearningConceptRecord | None:
    key = _normalize_concept_key(concept)
    for record in learning_concept_records():
        if record.concept.lower() == key:
            return record
    return None


def learning_concept_view(concept: str) -> LearningConceptView | None:
    key = _normalize_concept_key(concept)
    if not key:
        return None
    for view in list_learning_concept_views():
        if view.concept.lower() == key:
            return view
    return None


def learning_concept_detail_view(concept: str) -> LearningConceptDetailView | None:
    view = learning_concept_view(concept)
    if view is None:
        return None

    session = view.session_state
    concept_state = view.concept_state
    recommendation = view.recommendation
    build_state = view.build_state
    has_persisted_learning_state = concept_state is not None and bool(
        concept_state.current_understanding.strip() or concept_state.open_questions.strip()
    )

    primary_heading = "Latest understanding"
    primary_text = concept_state.current_understanding.strip() if concept_state is not None else "No understanding captured yet."
    secondary_heading = "Open questions"
    secondary_text = concept_state.open_questions.strip() if concept_state is not None else ""
    tertiary_heading = "Agent-recommended next move"
    tertiary_text = view.recommended_next_move.strip()

    if not has_persisted_learning_state and session is None:
        primary_heading = "Why learn this now"
        primary_text = recommendation.why_now.strip() if recommendation is not None else "No learning rationale captured yet."
        secondary_heading = "Current gap"
        secondary_text = recommendation.current_gap.strip() if recommendation is not None else "No current gap captured yet."
        tertiary_heading = "Suggested first move"
        tertiary_text = view.recommended_next_move.strip() or "Start a learning session for this concept."

    if session is not None:
        primary_heading = "Latest understanding"
        primary_text = (
            session.latest_explanation_back.strip()
            or session.current_understanding.strip()
            or primary_text
        )
        secondary_heading = "Open questions"
        if session.detected_gaps:
            secondary_text = "\n".join(f"- {gap}" for gap in session.detected_gaps if gap.strip())
        elif session.what_is_unclear.strip():
            secondary_text = session.what_is_unclear.strip()
        tertiary_heading = "Agent-recommended next move"
        tertiary_text = session.coach_message.strip()

    if (
        not primary_text.strip()
        and concept_state is not None
        and concept_state.status.lower() in {"in_progress", "reopened"}
    ):
        primary_text = "Learning session started. Your latest understanding will appear here as you work through the current concept with the agent."

    if secondary_heading == "Open questions" and not secondary_text:
        if concept_state is not None and concept_state.status.lower() == "learned":
            secondary_text = "No open questions are active right now."
        else:
            secondary_text = "No open questions have been captured yet."

    if not tertiary_text:
        if secondary_heading == "Open questions" and secondary_text and secondary_text not in {
            "No open questions are active right now.",
            "No open questions have been captured yet.",
        }:
            tertiary_text = "Continue with the learning agent and work through the open questions before marking this concept as settled."
        elif build_state is not None and build_state.status in {"planned", "active"}:
            tertiary_text = "Open the linked build pathway and use it to pressure-test the concept through one bounded experiment."
        elif concept_state is not None and concept_state.status.lower() in {"reopened", "in_progress"}:
            tertiary_text = "Resume the learning session and let the agent decide whether this concept needs clarification, a distinction, or a build step."
        else:
            tertiary_text = "Reuse this concept in context and reopen it if a new edge case or doubt shows up."

    return LearningConceptDetailView(
        concept=view.concept,
        state_label=(concept_state.status if concept_state is not None else "upcoming").replace("_", " ").title(),
        history_count=concept_state.history_count if concept_state is not None else 0,
        primary_heading=primary_heading,
        primary_text=primary_text,
        secondary_heading=secondary_heading,
        secondary_text=secondary_text,
        tertiary_heading=tertiary_heading,
        tertiary_text=tertiary_text,
    )


def learning_concept_history(concept: str) -> list[dict[str, str]]:
    entry = _concept_state_entry(_normalize_concept_key(concept))
    history = entry.get("history")
    if not isinstance(history, list):
        return []
    cleaned: list[dict[str, str]] = []
    for item in history:
        if isinstance(item, dict):
            cleaned.append({str(k): str(v) for k, v in item.items()})
    return cleaned


def learning_concept_build_to_learn(concept: str) -> LearningBuildToLearnLink | None:
    entry = _concept_state_entry(_normalize_concept_key(concept))
    return _extract_build_to_learn_link(entry, concept.strip() or concept)


def learning_concept_relationships(concept: str) -> list[LearningConceptRelationship]:
    key = _normalize_concept_key(concept)
    knowledge = _learning_concept_catalog().get(key)
    concept_map = knowledge.relations if knowledge is not None else {}
    relationships: list[LearningConceptRelationship] = []
    for relation, items in concept_map.items():
        for target, rationale in items:
            relationships.append(
                LearningConceptRelationship(
                    relation=relation,
                    target=target,
                    rationale=rationale,
                )
            )
    return relationships


def learning_concept_hierarchy(concept: str) -> str:
    family = learning_concept_family(concept)
    if family is None:
        return ""
    lines = _learning_family_tree_lines(family, current_concept=concept)
    return "\n".join(lines)


def save_learning_concept_management_update(
    concept: str,
    *,
    status: str,
    current_understanding: str,
    open_questions: str,
    note: str = "",
    source: str = "concept manager",
) -> Path:
    path = _upsert_learning_concept_state(
        concept,
        status=status,
        current_understanding=current_understanding,
        open_questions=open_questions,
        note=note or "Concept lifecycle updated.",
        source=source,
    )
    if status.strip().lower() == "learned":
        _append_learning_activity_event("learning_concept_learned", concept=concept)
    return path


def learning_progress_items() -> dict[str, list[LearningProgressItem]]:
    learned: list[LearningProgressItem] = []
    in_progress: list[LearningProgressItem] = []
    upcoming: list[LearningProgressItem] = []

    for view in list_learning_concept_views():
        concept_state = view.concept_state
        status = concept_state.status if concept_state is not None else "upcoming"
        item = LearningProgressItem(
            concept=view.concept,
            status=status,
            latest_understanding=concept_state.current_understanding if concept_state is not None else "",
            recommended_next_move=view.recommended_next_move,
        )
        normalized_status = status.lower()
        if normalized_status == "learned":
            learned.append(item)
        elif normalized_status in {"in_progress", "reopened", "build_to_learn"}:
            in_progress.append(item)
        else:
            upcoming.append(item)

    return {
        "learned": learned,
        "in_progress": in_progress,
        "upcoming": upcoming,
    }


def build_build_to_learn_pathway(
    concept: str,
    *,
    where_it_connects: str = "",
    current_gap: str = "",
) -> BuildToLearnPathway:
    normalized = concept.strip()
    if not normalized:
        raise ValueError("Concept is required to build a build-to-learn pathway.")
    knowledge = _learning_knowledge_for(
        normalized,
        current_understanding="",
        what_is_unclear=current_gap,
        where_encountered=where_it_connects,
    )
    anchor = where_it_connects.strip() or knowledge.build_project_anchor
    gap_clause = current_gap.strip()
    learning_goal = knowledge.build_learning_goal
    experiment_slice = knowledge.build_experiment_slice
    success_signal = knowledge.build_success_signal
    capture_prompt = knowledge.build_capture_prompt

    if gap_clause:
        learning_goal = f"{learning_goal} Current pressure to resolve: {gap_clause}"
        capture_prompt = f"{capture_prompt} Pay special attention to whether it resolves this: {gap_clause}"
    if anchor and anchor != knowledge.build_project_anchor:
        experiment_slice = f"{experiment_slice} Keep it tied to this current anchor: {anchor}"

    return BuildToLearnPathway(
        concept=knowledge.concept,
        learning_goal=learning_goal,
        experiment_slice=experiment_slice,
        project_anchor=anchor,
        success_signal=success_signal,
        capture_prompt=capture_prompt,
    )


def save_private_build_to_learn_pathway(
    concept: str,
    *,
    learning_goal: str,
    experiment_slice: str,
    project_anchor: str,
    success_signal: str,
    capture_prompt: str,
    captured_via: str = "build-to-learn helper",
) -> Path:
    path = _ensure_private_build_to_learn_file()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    concept_value = concept.strip() or "Unspecified concept"
    entry = (
        f"\n\n## {timestamp} — {concept_value}\n\n"
        f"_Captured via: {captured_via.strip() or 'build-to-learn helper'}_\n\n"
        f"### Learning goal\n{learning_goal.strip() or 'Needs follow-up refinement.'}\n\n"
        f"### Bounded experiment slice\n{experiment_slice.strip() or 'Needs follow-up refinement.'}\n\n"
        f"### Project anchor\n{project_anchor.strip() or 'Needs follow-up refinement.'}\n\n"
        f"### Success signal\n{success_signal.strip() or 'Needs follow-up refinement.'}\n\n"
        f"### Capture prompt\n{capture_prompt.strip() or 'Needs follow-up refinement.'}\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    key = _normalize_concept_key(concept_value)
    store = _load_private_concept_state_store()
    concepts = store.get("concepts")
    assert isinstance(concepts, dict)
    existing = concepts.get(key)
    if not isinstance(existing, dict):
        existing = {"concept": concept_value, "history": []}
    existing_status = str(existing.get("status") or "")
    existing["status"] = "reopened" if existing_status == "learned" else (existing_status or "in_progress")
    existing["concept"] = concept_value
    existing["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    history = existing.get("history")
    if not isinstance(history, list):
        history = []
    history.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": captured_via,
            "status": str(existing.get("status", "in_progress")),
            "note": "Build-to-learn pathway saved.",
        }
    )
    existing["history"] = history[-20:]
    existing["build_to_learn"] = {
        "concept": concept_value,
        "status": "planned",
        "learning_goal": learning_goal.strip(),
        "experiment_slice": experiment_slice.strip(),
        "project_anchor": project_anchor.strip(),
        "success_signal": success_signal.strip(),
        "capture_prompt": capture_prompt.strip(),
        "captured_via": captured_via.strip() or "build-to-learn helper",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "outcome_summary": "",
        "unresolved_after_build": "",
        "learning_effect": "",
    }
    concepts[key] = existing
    _save_private_concept_state_store(store)
    return path


def save_build_to_learn_outcome(
    concept: str,
    *,
    outcome_summary: str,
    unresolved_after_build: str,
    learning_effect: Literal["strengthened", "reopened"],
    current_understanding: str = "",
    source: str = "build-to-learn concept capture",
) -> Path:
    concept_value = concept.strip()
    if not concept_value:
        raise ValueError("Concept is required to capture build-to-learn outcome.")
    key = _normalize_concept_key(concept_value)
    store = _load_private_concept_state_store()
    concepts = store.get("concepts")
    assert isinstance(concepts, dict)
    existing = concepts.get(key)
    if not isinstance(existing, dict):
        existing = {"concept": concept_value, "history": []}
    history = existing.get("history")
    if not isinstance(history, list):
        history = []
    raw_link = existing.get("build_to_learn")
    if not isinstance(raw_link, dict):
        raw_link = {"concept": concept_value}

    existing["concept"] = concept_value
    existing["status"] = "reopened" if learning_effect == "reopened" else str(existing.get("status") or "in_progress")
    if current_understanding.strip():
        existing["current_understanding"] = current_understanding.strip()
    if unresolved_after_build.strip():
        existing["open_questions"] = unresolved_after_build.strip()
    elif learning_effect == "strengthened":
        existing["open_questions"] = ""
    existing["updated_at"] = datetime.now().strftime("%Y-%m-%d")

    raw_link.update(
        {
            "concept": concept_value,
            "status": "captured",
            "outcome_summary": outcome_summary.strip(),
            "unresolved_after_build": unresolved_after_build.strip(),
            "learning_effect": learning_effect,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }
    )
    existing["build_to_learn"] = raw_link

    note = "Build-to-learn outcome captured."
    if learning_effect == "reopened":
        note += " The concept was reopened because building surfaced fresh uncertainty."
    else:
        note += " Building strengthened understanding, but human confirmation still decides when it is learned."
    history.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": source,
            "status": str(existing.get("status", "in_progress")),
            "note": note,
        }
    )
    existing["history"] = history[-20:]
    concepts[key] = existing
    return _save_private_concept_state_store(store)


def save_private_concept_note_draft(
    concept: str,
    *,
    where_encountered: str,
    current_understanding: str,
    what_is_unclear: str,
    what_it_is: str = "",
    why_it_exists: str,
    nearby_distinction: str = "",
    where_it_appears: str,
    product_implication: str,
    current_working_opinion: str,
    open_questions: str,
    captured_via: str = "interactive concept-learning helper",
) -> Path:
    path = _ensure_private_concept_notes_file()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    concept_value = concept.strip() or "Unspecified concept"
    encountered_value = where_encountered.strip() or "Needs follow-up context."
    understanding_value = current_understanding.strip() or "Needs follow-up refinement."
    unclear_value = what_is_unclear.strip() or "Needs follow-up refinement."
    what_it_is_value = what_it_is.strip() or "Needs follow-up refinement."
    why_exists_value = why_it_exists.strip() or "Needs follow-up refinement."
    nearby_distinction_value = nearby_distinction.strip() or "Needs follow-up refinement."
    appears_value = where_it_appears.strip() or "Needs follow-up refinement."
    implication_value = product_implication.strip() or "Needs follow-up refinement."
    opinion_value = current_working_opinion.strip() or "Needs follow-up refinement."
    questions_value = open_questions.strip() or "No open questions captured yet."
    entry = (
        f"\n\n### Concept: {concept_value}\n\n"
        f"_Captured on {timestamp} via: {captured_via.strip() or 'interactive concept-learning helper'}_\n\n"
        f"#### Where I encountered it\n{encountered_value}\n\n"
        f"#### My current understanding\n{understanding_value}\n\n"
        f"#### What is unclear\n{unclear_value}\n\n"
        f"#### What it is\n{what_it_is_value}\n\n"
        f"#### Why it exists\n{why_exists_value}\n\n"
        f"#### Nearby distinction\n{nearby_distinction_value}\n\n"
        f"#### Where it appears in the OS\n{appears_value}\n\n"
        f"#### Product implication\n{implication_value}\n\n"
        f"#### My current working opinion\n{opinion_value}\n\n"
        f"#### Open questions\n{questions_value}\n"
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    existing_status = str(_concept_state_entry(_normalize_concept_key(concept_value)).get("status") or "")
    has_open_questions = questions_value.lower() != "no open questions captured yet."
    if existing_status == "learned" and has_open_questions:
        status = "reopened"
    else:
        status = existing_status or "in_progress"
        if status == "upcoming":
            status = "in_progress"
    _upsert_learning_concept_state(
        concept_value,
        status=status,
        current_understanding=understanding_value,
        open_questions=questions_value,
        note="Concept note draft saved.",
        source=captured_via,
    )
    return path

TOOLS_ROOT = REPO_ROOT / "tools"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from create_project import scaffold_project  # type: ignore  # noqa: E402
from qa_report import (  # type: ignore  # noqa: E402
    parse_report as parse_qa_report,
    reliability_statement as qa_reliability_statement,
    resolve_runner as resolve_qa_runner,
    run_runner as run_qa_runner,
)
from tools.common import (  # noqa: E402
    active_agent_threads as load_active_agent_threads,
    active_experience_findings as load_active_experience_findings,
    active_pm_clarifications as load_active_pm_clarifications,
    create_pm_clarification,
    iter_projects,
    load_pm_clarification_store,
    normalize_project_directory_name,
    parse_requirements,
    parse_tasks,
    requirement_has_experience_trigger,
    requirement_has_structural_trigger,
    requirement_has_ui_trigger,
    resolve_pm_clarification_in_store,
    save_pm_clarification_store,
    validate_project_structure,
)


REQUIREMENT_BLOCK_PATTERN = re.compile(
    r"###\s+(R\d+)\s+—\s+(.+?)\n\n"
    r"Status:\s+(.+?)\n"
    r"(?:Priority:\s+(.+?)\n)?"
    r"(?:Effort:\s+(.+?)\n)?"
    r"(?:UI Runtime:\s+(.+?)\n)?"
    r"Description:\n"
    r"(.*?)(?=\n###\s+R\d+\s+—|\n---|\Z)",
    re.DOTALL,
)
TASK_BLOCK_PATTERN = re.compile(
    r"^##\s+Task\s+(\d+):\s+(.+?)\n\n"
    r"Type:\s+(.+?)\n"
    r"Status:\s+(.+?)\n"
    r"Requirement(?:s)?:\s+(.+?)\n\n"
    r"(.*?)(?=^##\s+Task\s+\d+:|\Z)",
    re.DOTALL | re.MULTILINE,
)

ACTIVE_HEADER = "## Active Requirements"
BACKLOG_HEADER = "## Backlog (Not yet prioritised)"
RULES_HEADER = "## Rules"
REQUIREMENT_RULES_HEADER = "## Requirement Rules"
PRODUCT_REQUIREMENTS_HEADER = "# Product Requirements"
RUNTIME_DATA_DIR = _project_runtime_data_path("os-control-panel")
EXPERIENCE_FILE = RUNTIME_DATA_DIR / "experience_findings.json"
IMPLEMENTATION_FILE = RUNTIME_DATA_DIR / "implementation_runs.json"
AGENT_THREAD_FILE = RUNTIME_DATA_DIR / "agent_threads.json"
APPROVAL_FILE = RUNTIME_DATA_DIR / "approvals.json"
SPRINT_FILE = RUNTIME_DATA_DIR / "sprint.json"
QUALITY_FILE = RUNTIME_DATA_DIR / "quality_reviews.json"
MANUAL_VERIFICATION_FILE = RUNTIME_DATA_DIR / "manual_verifications.json"
AGENT_UPLOAD_DIR = RUNTIME_DATA_DIR / "agent_uploads"
IMPLEMENTATION_LOG_DIR = RUNTIME_DATA_DIR / "implementation_logs"
IMPLEMENTATION_ACTIVE_STATES = {"QUEUED", "RUNNING"}
SPRINT_ACTIVE_STATES = {"PLANNING", "ACTIVE", "BLOCKED", "READY_TO_CLOSE"}
IMPLEMENTATION_STALE_MINUTES = 5
PREVIEW_PORT_BASE = 8600
PREVIEW_PORT_SPAN = 300
UI_RUNTIME_OPTIONS = ("streamlit", "web_app")
DEFAULT_UI_RUNTIME = "streamlit"
EXPERIENCE_HANDOFF_STATES = {
    "ready_for_pm_review",
    "ready_for_product_director",
    "handoff_prepared",
    "routed",
    "accepted",
    "resolved",
    "superseded",
}


@dataclass(frozen=True)
class RequirementSummary:
    id: str
    title: str
    status: str


@dataclass(frozen=True)
class TaskSummary:
    id: str
    title: str
    status: str


@dataclass(frozen=True)
class RequirementRecord:
    id: str
    title: str
    status: str
    priority: str
    effort: str
    description: str
    ui_runtime: str = ""


@dataclass(frozen=True)
class OpenAIRuntimeDecision:
    requirement_id: str
    required: bool
    surface: str
    capabilities: tuple[str, ...]
    credentials: tuple[str, ...]
    rationale: str
    confidence: str
    review_reasons: tuple[str, ...]
    requirement_fingerprint: str
    updated_at: str


@dataclass(frozen=True)
class RequirementDocument:
    intro: str
    active_requirements: tuple[RequirementRecord, ...]
    backlog_requirements: tuple[RequirementRecord, ...]
    rules_text: str


@dataclass(frozen=True)
class TaskBlock:
    number: int
    title: str
    task_type: str
    status: str
    requirements: tuple[str, ...]
    body: str


@dataclass(frozen=True)
class TaskDocument:
    intro: str
    tasks: tuple[TaskBlock, ...]


@dataclass(frozen=True)
class ProjectSummary:
    name: str
    path: Path
    structure_ok: bool
    missing_paths: tuple[str, ...]
    default_ui_runtime: str
    requirement_counts: dict[str, int]
    new_requirements: tuple[RequirementSummary, ...]
    task_counts: dict[str, int]
    pending_tasks: tuple[TaskSummary, ...]
    project_id: str = ""
    mode: str = "embedded_showcase"
    visibility: str = "public"
    ownership: str = "self"
    repository: str = ""
    default_branch: str = "main"


@dataclass(frozen=True)
class RequirementRecommendation:
    requirement_id: str
    title: str
    rationale: str


@dataclass(frozen=True)
class DiscoveryQuestion:
    id: str
    prompt: str


@dataclass(frozen=True)
class DiscoveryPlan:
    mode: str
    framing: str
    questions: tuple[DiscoveryQuestion, ...]


@dataclass(frozen=True)
class AgentMessage:
    role: str
    content: str
    created_at: str
    attachments: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentThread:
    thread_id: str
    project_name: str
    agent_name: str
    mode: str
    status: str
    idea: str
    planner_type: str
    plan_mode: str
    current_question_index: int
    current_field_id: str
    answers: dict[str, str]
    draft_title: str
    draft: str
    draft_data: dict[str, str]
    messages: tuple[AgentMessage, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ExperienceFinding:
    finding_id: str
    project_name: str
    user_problem: str
    affected_workflow: str
    evidence: str
    confidence: str
    severity: str
    frequency: str
    recommendation_type: str
    rationale: str
    recommended_next_role: str
    handoff_state: str
    created_at: str


@dataclass(frozen=True)
class ExperienceIntakePlan:
    affected_workflow_prompt: str
    evidence_prompt: str
    rationale_prompt: str
    recommendation_type: str


@dataclass(frozen=True)
class ImplementationRun:
    run_id: str
    project_name: str
    requirement_id: str
    requirement_title: str
    status: str
    summary: str
    error: str
    created_at: str
    started_at: str
    finished_at: str
    output_path: str
    log_path: str
    worker_pid: int | None


@dataclass(frozen=True)
class ImplementationRunInspection:
    run: ImplementationRun
    display_status: str
    tone: Literal["active", "completed", "failed", "stale"]
    output_available: bool
    log_available: bool
    output_excerpt: str
    log_excerpt: str


@dataclass(frozen=True)
class ProjectPreview:
    project_name: str
    available: bool
    runtime: str
    entry_path: Path | None
    url: str
    command: tuple[str, ...]
    status_text: str


@dataclass(frozen=True)
class ProjectRuntimeProfile:
    runtime: str
    project_type: str
    label: str
    implementation_guidance: str
    default_deployment_provider: str
    preview_kind: str
    release_expectation: str
    capability_pack: tuple[str, ...] = ()
    architecture_guidance: tuple[str, ...] = ()
    qa_release_checks: tuple[str, ...] = ()


FIGMA_DESIGN_MODES = ("code_first", "figma_referenced", "figma_managed")


@dataclass(frozen=True)
class FigmaDesignReference:
    requirement_id: str
    frame_url: str
    frame_name: str
    approval_status: str


@dataclass(frozen=True)
class ProjectFigmaConfig:
    mode: str
    file_url: str
    file_name: str
    references: tuple[FigmaDesignReference, ...]


PROJECT_RUNTIME_PROFILES = {
    "streamlit": ProjectRuntimeProfile(
        runtime="streamlit",
        project_type="streamlit",
        label="Streamlit app",
        implementation_guidance=(
            "Build this as a Python Streamlit app. Prefer simple file-backed state, Streamlit-native controls, "
            "rerun-safe interaction loops, clear workflow orientation after actions, local preview through `streamlit run`, "
            "and Railway as the default hosted-service deployment target."
        ),
        default_deployment_provider="railway",
        preview_kind="streamlit",
        release_expectation=(
            "Release should preserve Streamlit runtime packaging and Railway-compatible hosted Python service behavior."
        ),
        capability_pack=(
            "Streamlit-native UI composition",
            "rerun-safe interaction flow",
            "file-backed local workflow state",
            "Railway hosted Python service packaging",
        ),
        architecture_guidance=(
            "Keep the app server-oriented and simple.",
            "Prefer Streamlit-native controls before adding frontend complexity.",
            "Keep runtime data outside public product files.",
            "Use Railway as the default deployment capability for Streamlit and Python service work.",
        ),
        qa_release_checks=(
            "Streamlit app imports and renders",
            "Project eval runner passes",
            "Railway service packaging remains compatible",
        ),
    ),
    "web_app": ProjectRuntimeProfile(
        runtime="web_app",
        project_type="web_app",
        label="Web app",
        implementation_guidance=(
            "Build this as a Vercel-compatible Next.js/React web app. Prefer browser-native UX, reusable components, "
            "responsive behavior, explicit loading/empty/error states, npm scripts, and deployment through Vercel after GitHub release approval."
        ),
        default_deployment_provider="vercel",
        preview_kind="nextjs",
        release_expectation="Release should produce a Vercel-compatible branch with buildable Next.js assets.",
        capability_pack=(
            "Frontend app builder",
            "Frontend testing and debugging",
            "React best practices",
            "shadcn/ui best practices",
        ),
        architecture_guidance=(
            "Choose client components, server components, server actions, or API routes deliberately.",
            "Use shadcn/ui when the project needs polished common UI faster than hand-built primitives.",
            "Keep app-shell structure, route hierarchy, and component boundaries legible.",
            "Prefer Vercel preview deployment and browser verification as part of release readiness.",
        ),
        qa_release_checks=(
            "package.json has dev and build scripts",
            "Next.js app entry exists",
            "local dev server can be browser-smoked",
            "responsive behavior and interaction states are checked on the rendered surface",
            "release approval records preview/deployment expectations",
        ),
    ),
}


@dataclass(frozen=True)
class SprintPlan:
    project_name: str
    status: str
    requirement_ids: tuple[str, ...]
    created_at: str
    started_at: str
    completed_at: str
    current_requirement_id: str
    blocked_reason: str


IMPLEMENTATION_PROGRESS_BY_STATUS = {
    "QUEUED": 10,
    "RUNNING": 55,
    "COMPLETED": 100,
    "FAILED": 100,
}

IMPLEMENTATION_PROGRESS_MESSAGE_BY_STATUS = {
    "QUEUED": "Implementation is queued and waiting for the background worker to start.",
    "RUNNING": "Implementation is running; Codex is working through the OS workflow.",
    "COMPLETED": "Implementation finished; review the summary below.",
    "FAILED": "Implementation stopped with an error; review the error below.",
}

IMPLEMENTATION_STALE_ERROR_FRAGMENT = "marked failed during reconciliation"


@dataclass(frozen=True)
class PMClarification:
    clarification_id: str
    project_name: str
    requirement_id: str
    requirement_title: str
    source_thread_id: str
    summary: str
    questions: tuple[str, ...]
    status: str
    created_at: str
    resolved_at: str


@dataclass(frozen=True)
class RequirementDeletionResult:
    deleted_requirement: RequirementRecord
    removed_tasks: int
    updated_tasks: int
    removed_clarifications: int
    removed_implementation_runs: int


@dataclass(frozen=True)
class OrchestratorRecommendation:
    next_action: str
    next_role: str
    why: str


@dataclass(frozen=True)
class ArchitectReviewSnapshot:
    headline: str
    summary: str
    hotspots: tuple[str, ...]
    guardrails: tuple[str, ...]


@dataclass(frozen=True)
class QAReviewSnapshot:
    runner_path: str
    summary: str
    failures: tuple[str, ...]
    confidence: str
    raw_output: str


@dataclass(frozen=True)
class QualityReviewRecord:
    review_id: str
    project_name: str
    mode: str
    status: str
    runner_path: str
    summary: str
    failures: tuple[str, ...]
    confidence: str
    raw_output: str
    reviewed_at: str


@dataclass(frozen=True)
class ManualVerificationCheck:
    check_id: str
    title: str
    instructions: str
    status: str
    notes: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ManualVerificationPlan:
    project_name: str
    requirement_id: str
    checks: tuple[ManualVerificationCheck, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ManualVerificationSummary:
    requirement_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    not_run_checks: int
    signoff_state: str
    signoff_label: str


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    project_name: str
    approval_type: str
    source_thread_id: str
    source_agent_name: str
    title: str
    summary: str
    payload: dict[str, str]
    status: str
    created_at: str
    resolved_at: str


@dataclass(frozen=True)
class GitHubPublicationRequest:
    approval: ApprovalRequest
    target: str
    title: str
    body: str
    policy_status: str
    findings: tuple[str, ...]


@dataclass(frozen=True)
class GitChangePlan:
    included_paths: tuple[str, ...]
    excluded_paths: tuple[str, ...]
    branch: str


@dataclass(frozen=True)
class VercelDeploymentLookup:
    status: str
    url: str = ""
    deployment_id: str = ""
    ready_state: str = ""
    inspector_url: str = ""
    detail: str = ""


@dataclass(frozen=True)
class WorkflowTimelineEvent:
    event_id: str
    project_name: str
    occurred_at: str
    title: str
    summary: str
    actor: str
    artifact_kind: str
    artifact_id: str
    status_bucket: str
    detail: str


@dataclass(frozen=True)
class ProjectWorkflowHealth:
    project_name: str
    new_requirements: int
    in_progress_requirements: int
    backlog_requirements: int
    pending_tasks: int
    blocked_items: int
    open_approvals: int
    open_clarifications: int
    routed_items: int
    active_runs: int
    failed_runs: int
    quality_status: str


@dataclass(frozen=True)
class OperationsActivity:
    occurred_at: str
    project_name: str
    actor: str
    title: str
    status: str
    detail: str


@dataclass(frozen=True)
class OperationsDashboardSnapshot:
    agent_runs: tuple[AgentRunSummary, ...]
    role_performance: tuple[AgentRolePerformance, ...]
    tool_usage: tuple[ToolUsageSummary, ...]
    workflow_health: tuple[ProjectWorkflowHealth, ...]
    open_approvals: tuple[ApprovalRequest, ...]
    high_risk_tools: tuple[str, ...]
    trace_quality: dict[str, dict[str, object]]
    learning_progress: dict[str, tuple[LearningProgressItem, ...]]
    active_learning_session: LearningAgentSession | None
    activity: tuple[OperationsActivity, ...]
    eval_coverage: tuple[object, ...] = ()
    eval_cases: tuple[EvalCaseRecord, ...] = ()


@dataclass(frozen=True)
class InboxItem:
    kind: str
    title: str
    summary: str
    project_name: str
    status_bucket: str
    reference_id: str
    detail: str


@dataclass(frozen=True)
class AgentSummary:
    name: str
    title: str
    can_do: tuple[str, ...]
    memory_context: tuple[str, ...]
    workflow_position: tuple[str, ...]


@dataclass(frozen=True)
class LivePMProjectThread:
    thread_id: str
    project_name: str
    display_name: str
    ui_runtime: str
    planner_type: str
    status: str
    messages: tuple[AgentMessage, ...]
    draft_title: str
    draft_requirement: str
    created_at: str
    updated_at: str


class LivePMTurn(BaseModel):
    next_action: Literal["ask_question", "draft_requirements", "request_clarification"]
    assistant_message: str
    draft_title: str = ""
    draft_requirement: str = ""
    clarification_summary: str = ""
    clarification_questions: list[str] = Field(default_factory=list)


class LivePMDiscoveryError(RuntimeError):
    pass


def _ensure_live_pm_assistant_message(turn: LivePMTurn) -> LivePMTurn:
    if turn.assistant_message.strip():
        return turn
    if turn.next_action == "ask_question":
        message = "I need one more piece of context before I can continue."
    elif turn.next_action == "draft_requirements":
        title = turn.draft_title.strip()
        if title:
            message = f"I drafted the next requirement: {title}."
        else:
            message = "I drafted the next requirement from the context we have so far."
    else:
        summary = turn.clarification_summary.strip()
        if summary:
            message = f"I need clarification before I can continue: {summary}"
        elif turn.clarification_questions:
            message = f"I need clarification before I can continue: {turn.clarification_questions[0].strip()}"
        else:
            message = "I need clarification before I can continue."
    return turn.model_copy(update={"assistant_message": message})


class LiveExperienceTurn(BaseModel):
    next_action: Literal["ask_question", "draft_finding"]
    assistant_message: str
    finding_draft: str = ""
    user_problem: str = ""
    affected_workflow: str = ""
    evidence: str = ""
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    severity: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    frequency: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    recommendation_type: Literal["UX improvement in scope", "feature candidate", "scope escalation"] = "UX improvement in scope"
    rationale: str = ""


class LiveUIDesignTurn(BaseModel):
    next_action: Literal["ask_question", "draft_design_brief"]
    assistant_message: str
    draft_title: str = ""
    design_brief: str = ""


class LivePMReviewCompletionTurn(BaseModel):
    next_action: Literal["create_backlog_requirement", "confirm_out_of_scope"]
    assistant_message: str
    requirement_title: str = ""
    requirement_body: str = ""
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    effort: Literal["S", "M", "L"] = "M"
    scope_confirmation_title: str = ""
    scope_confirmation_summary: str = ""


class LiveLearningTeachingTurn(BaseModel):
    what_it_is: str
    why_it_exists: str
    nearby_distinction: str
    os_connection: str
    product_implication: str
    coach_message: str = "Use the teaching brief, ask a focused follow-up when needed, and capture what now feels clearer."


class LiveLearningClarificationTurn(BaseModel):
    clarification_response: str
    coach_message: str = "Use the clarification above, then explain the concept back again in simple language."


class LiveLearningImplementationTurn(BaseModel):
    walkthrough_intro: str
    how_the_pieces_fit: str
    coach_message: str = "Use the walkthrough above to explain how the concept appears in the OS in plain language."


class LiveOrchestratorReviewTurn(BaseModel):
    recommended_role: Literal[
        "Product Director",
        "PM",
        "Experience Designer",
        "UI Designer",
        "Architect",
        "Engineer",
        "QA",
        "None",
    ]
    recommended_action: str
    rationale: str
    agrees_with_deterministic: bool
    uncertainty: str = ""


REQUIREMENT_CONSOLIDATION_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "that",
    "this",
    "will",
    "have",
    "has",
    "are",
    "but",
    "not",
    "than",
    "then",
    "when",
    "where",
    "what",
    "which",
    "your",
    "their",
    "there",
    "about",
    "after",
    "before",
    "under",
    "while",
    "more",
    "less",
    "very",
    "over",
    "only",
    "just",
    "make",
    "need",
    "needs",
    "improve",
    "improved",
    "improvement",
    "enhance",
    "enhanced",
    "launch",
    "introduce",
    "broader",
    "initiative",
    "project",
    "product",
    "design",
    "review",
}


ROLE_CARDS = (
    {
        "name": "PM",
        "title": "Tom",
        "summary": "Clarifies ideas, drafts requirements, and turns approved work into structured tasks.",
    },
    {
        "name": "Experience Designer",
        "title": "Enzo",
        "summary": "Synthesises UX feedback into structured findings and routes them into the OS without taking over PM or engineering work.",
    },
    {
        "name": "UI Designer",
        "title": "Ricky",
        "summary": "Shapes visual direction, interaction design, layout decisions, and interface polish before and after implementation.",
    },
    {
        "name": "Architect",
        "title": "Andy",
        "summary": "Reviews structure, workflow design, and maintainability when the shape of the system is the real problem.",
    },
    {
        "name": "Orchestrator",
        "title": "Paul",
        "summary": "Inspects project state and recommends which role should run next without executing the work directly.",
    },
    {
        "name": "Engineer",
        "title": "Maciej",
        "summary": "Implements tasks, preserves behavior, and validates technical changes before closing work.",
    },
    {
        "name": "QA",
        "title": "Richard",
        "summary": "Runs validation, checks regressions, and flags obvious UX clarity issues on user-facing changes.",
    },
)

AGENT_SUMMARY_OVERRIDES: dict[str, dict[str, tuple[str, ...]]] = {
    "PM": {
        "can_do": (
            "Clarify ideas and turn them into structured requirements.",
            "Prioritise real `NEW` work before execution begins.",
            "Translate approved requirements into concrete, testable tasks.",
        ),
        "memory_context": (
            "Interrogate ambiguity before tasking downstream work.",
            "Prefer small, testable tasks over broad implementation asks.",
            "Keep PM focused on product definition rather than code changes.",
        ),
        "workflow_position": (
            "Usually the first formal OS role after an idea or approved finding enters the workflow.",
            "Runs after Experience Designer when raw UX feedback needs synthesis first.",
            "Hands structured tasks to downstream implementation once scope is clear.",
        ),
    },
    "Experience Designer": {
        "can_do": (
            "Gather and interpret user experience feedback.",
            "Synthesize usability issues and workflow friction into structured findings.",
            "Review an existing surface for clarity, hierarchy, scanability, and interaction quality.",
        ),
        "memory_context": (
            "Separate evidence from assumptions before suggesting product action.",
            "Keep findings inside current scope unless escalation is clearly justified.",
            "Route product work through PM or Product Director instead of implementing directly.",
        ),
        "workflow_position": (
            "Runs before PM when the main input is raw UX feedback, workflow friction, or user pain.",
            "Can also review a live surface before or after implementation when usability is the real question.",
            "Hands a structured finding into the workflow rather than taking over prioritisation or engineering.",
        ),
    },
    "UI Designer": {
        "can_do": (
            "Propose visual and interaction direction for user-facing surfaces.",
            "Shape layout, hierarchy, flow, and interface decisions before implementation settles.",
            "Review existing UI work and identify improvements in polish, consistency, or clarity.",
        ),
        "memory_context": (
            "Ground design recommendations in the actual workflow, not taste alone.",
            "Keep interface guidance implementable, concrete, and scoped.",
            "Route tracked design work through PM when it should become product work.",
        ),
        "workflow_position": (
            "Runs when interface direction, layout, interaction design, or visual polish is the real issue.",
            "Often shapes work before implementation, but can also critique a surface that already exists.",
            "Collaborates with PM and Experience Designer instead of bypassing the normal workflow.",
        ),
    },
    "Architect": {
        "can_do": (
            "Review system structure, role boundaries, validation design, and documentation shape.",
            "Identify structural risks, inconsistencies, and scaling problems.",
            "Recommend small, coherent changes that improve clarity and maintainability.",
        ),
        "memory_context": (
            "Start with diagnosis before proposing change.",
            "Prefer evolutionary improvements over grand redesigns.",
            "Keep guidance concrete and sequenceable so Engineer can act on it safely.",
        ),
        "workflow_position": (
            "Runs before Engineer when planned work introduces meaningful structural change.",
            "Helps when the shape of the system or workflow is the real problem.",
            "Narrows the implementation path before more engineering pressure is added.",
        ),
    },
    "Orchestrator": {
        "can_do": (
            "Inspect current project state and decide which role should run next.",
            "Route workflow based on requirements, tasks, and active workflow artifacts.",
            "Surface blocking clarifications, approvals, or handoffs before downstream work continues.",
        ),
        "memory_context": (
            "Route based on current file state rather than prior conversation context.",
            "Treat routed findings and clarifications as real workflow state when the project uses them.",
            "Recommend the simplest valid next step without doing the work yourself.",
        ),
        "workflow_position": (
            "Runs when the main question is what should happen next in the workflow.",
            "Can sit between any two roles as a routing layer, especially before engineering or QA.",
            "Keeps workflow movement inspectable without taking over PM, Engineer, or QA work directly.",
        ),
    },
    "Engineer": {
        "can_do": (
            "Implement approved tasks from `product/tasks.md`.",
            "Preserve behavior while changing code, prompts, or validation logic.",
            "Build the smallest viable implementation or validation mechanism needed next.",
        ),
        "memory_context": (
            "Proceed directly when the task is clear, but stop when requirements conflict or drift.",
            "Prefer simple, maintainable solutions over brittle or over-engineered ones.",
            "Move tasks to `DONE` only after successful validation.",
        ),
        "workflow_position": (
            "Runs after PM has created tasks and after Architect when structural triggers apply.",
            "Moves approved work through implementation and technical validation.",
            "Hands meaningful changes to QA rather than declaring the work complete on its own.",
        ),
    },
    "QA": {
        "can_do": (
            "Run the project validation path and summarize pass or fail status.",
            "Check regressions and mismatches against expected behavior.",
            "Flag obvious clarity issues on user-facing changes without redesigning the interface.",
        ),
        "memory_context": (
            "Treat eval and test results as the source of truth for validation work.",
            "Keep reporting precise, objective, and scoped to observed behavior.",
            "Report broken validation paths as system issues instead of papering over them.",
        ),
        "workflow_position": (
            "Usually runs after meaningful implementation changes.",
            "Confirms whether the system still behaves correctly before work is treated as done.",
            "Loops failures back into implementation or workflow review instead of changing code directly.",
        ),
    },
}


def list_agent_summaries() -> tuple[AgentSummary, ...]:
    return tuple(_build_agent_summary(role) for role in ROLE_CARDS)


def agent_summary_by_name(name: str) -> AgentSummary:
    for summary in list_agent_summaries():
        if summary.name == name:
            return summary
    raise ValueError(f"Agent summary not found: {name}")


def _requirements_path(project_name: str) -> Path:
    return _project_path(project_name) / "product" / "requirements.md"


def _role_doc_path(role_name: str) -> Path:
    file_map = {
        "PM": "pm.md",
        "Experience Designer": "experience-designer.md",
        "UI Designer": "ui-designer.md",
        "Engineer": "engineer.md",
        "QA": "qa.md",
        "Architect": "architect.md",
        "Orchestrator": "orchestrator.md",
    }
    return REPO_ROOT / "agent" / "roles" / file_map[role_name]


def architect_review_snapshot(project_name: str) -> ArchitectReviewSnapshot:
    project_dir = _project_path(project_name)
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    approvals = active_approvals(project_name)
    clarifications = active_pm_clarifications(project_name)
    sprint = load_sprint_plan(project_name)
    active_run = active_implementation_run(project_name)

    requirement_by_id = {item["id"]: item for item in requirements}
    hotspots: list[str] = []
    for task in tasks:
        if task["status"] not in {"TODO", "IN_PROGRESS"}:
            continue
        linked = [requirement_by_id[req_id] for req_id in task.get("requirements", []) if req_id in requirement_by_id]
        if any(requirement_has_structural_trigger(item) for item in linked):
            linked_ids = ", ".join(item["id"] for item in linked) or "linked requirement"
            hotspots.append(f"{task['id']} is pending with structural triggers on {linked_ids}.")

    if approvals:
        hotspots.append(f"{len(approvals)} open approval item(s) are still part of active workflow state.")
    if clarifications:
        hotspots.append(f"{len(clarifications)} open PM clarification(s) still block downstream work.")
    if sprint is not None and sprint.status == "BLOCKED":
        hotspots.append(f"Sprint is blocked on {sprint.current_requirement_id or 'the current requirement'}.")
    if active_run is not None:
        hotspots.append(f"Implementation run {active_run.run_id} is currently {active_run.status} for {active_run.requirement_id}.")

    if hotspots:
        headline = "Architect attention is warranted."
        summary = "The project has active structural or workflow-shaping conditions that should be reviewed before more implementation pressure is added."
    else:
        headline = "No active structural hotspot detected."
        summary = "The current project state does not show an immediate architecture trigger, though broader cleanup and consolidation decisions may still be valuable."

    guardrails = (
        "Prefer evolutionary fixes over broad redesign.",
        "Keep workflow state, product state, and runtime state clearly separated.",
        "Narrow broad UI or workflow initiatives before they become overlapping backlog items.",
    )
    return ArchitectReviewSnapshot(
        headline=headline,
        summary=summary,
        hotspots=tuple(hotspots),
        guardrails=guardrails,
    )


def run_project_qa_review(project_name: str, mode: str = "deterministic") -> QAReviewSnapshot:
    runner_path = resolve_qa_runner(project_name, mode)
    if runner_path is None:
        return QAReviewSnapshot(
            runner_path="",
            summary="No validation runner is available for this project and mode.",
            failures=(),
            confidence="Low confidence: no validation path is available.",
            raw_output="",
        )

    completed = run_qa_runner(runner_path)
    combined_output = completed.stdout.strip()
    if completed.stderr.strip():
        combined_output = f"{combined_output}\n{completed.stderr.strip()}".strip()
    summary, failures = parse_qa_report(combined_output)
    if summary is None:
        summary_text = "FAIL: no parseable pass/fail summary was found."
    else:
        passed, total = summary
        status = "PASS" if completed.returncode == 0 else "FAIL"
        summary_text = f"{status}: {passed}/{total} passing ({mode})"
    confidence = qa_reliability_statement(summary, completed.returncode)
    try:
        runner_label = str(runner_path.relative_to(_project_path(project_name)))
    except ValueError:
        runner_label = runner_path.name
    return QAReviewSnapshot(
        runner_path=runner_label,
        summary=summary_text,
        failures=tuple(failures),
        confidence=confidence,
        raw_output=combined_output,
    )


def _load_quality_reviews() -> list[dict[str, object]]:
    if not QUALITY_FILE.exists():
        return []
    try:
        payload = json.loads(QUALITY_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _save_quality_reviews(items: list[dict[str, object]]) -> None:
    QUALITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_FILE.write_text(json.dumps(items, indent=2))


def _quality_review_from_dict(raw_item: dict[str, object]) -> QualityReviewRecord:
    failures = raw_item.get("failures", [])
    if not isinstance(failures, list):
        failures = []
    return QualityReviewRecord(
        review_id=str(raw_item.get("review_id", "")),
        project_name=str(raw_item.get("project_name", "")),
        mode=str(raw_item.get("mode", "deterministic")),
        status=str(raw_item.get("status", "")),
        runner_path=str(raw_item.get("runner_path", "")),
        summary=str(raw_item.get("summary", "")),
        failures=tuple(str(item) for item in failures),
        confidence=str(raw_item.get("confidence", "")),
        raw_output=str(raw_item.get("raw_output", "")),
        reviewed_at=str(raw_item.get("reviewed_at", "")),
    )


def list_quality_reviews(project_name: str, *, mode: str | None = None) -> list[QualityReviewRecord]:
    items = [item for item in _load_quality_reviews() if str(item.get("project_name", "")) == project_name]
    if mode is not None:
        items = [item for item in items if str(item.get("mode", "")) == mode]
    return [
        _quality_review_from_dict(item)
        for item in sorted(items, key=lambda candidate: str(candidate.get("reviewed_at", "")), reverse=True)
    ]


def latest_quality_review(project_name: str, *, mode: str = "deterministic") -> QualityReviewRecord | None:
    reviews = list_quality_reviews(project_name, mode=mode)
    return reviews[0] if reviews else None


def record_project_qa_review(project_name: str, mode: str = "deterministic") -> QualityReviewRecord:
    snapshot = run_project_qa_review(project_name, mode=mode)
    status = "PASS" if snapshot.summary.startswith("PASS:") else "FAIL"
    review = {
        "review_id": str(uuid4()),
        "project_name": project_name,
        "mode": mode,
        "status": status,
        "runner_path": snapshot.runner_path,
        "summary": snapshot.summary,
        "failures": list(snapshot.failures),
        "confidence": snapshot.confidence,
        "raw_output": snapshot.raw_output,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    items = _load_quality_reviews()
    items.append(review)
    _save_quality_reviews(items)
    return _quality_review_from_dict(review)


def _load_manual_verifications() -> list[dict[str, object]]:
    if not MANUAL_VERIFICATION_FILE.exists():
        return []
    try:
        payload = json.loads(MANUAL_VERIFICATION_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _save_manual_verifications(items: list[dict[str, object]]) -> None:
    MANUAL_VERIFICATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANUAL_VERIFICATION_FILE.write_text(json.dumps(items, indent=2))


def _manual_verification_check_from_dict(raw_item: dict[str, object]) -> ManualVerificationCheck:
    return ManualVerificationCheck(
        check_id=str(raw_item.get("check_id", "")),
        title=str(raw_item.get("title", "")),
        instructions=str(raw_item.get("instructions", "")),
        status=str(raw_item.get("status", "NOT_RUN")),
        notes=str(raw_item.get("notes", "")),
        created_at=str(raw_item.get("created_at", "")),
        updated_at=str(raw_item.get("updated_at", "")),
    )


def _manual_verification_plan_from_dict(raw_item: dict[str, object]) -> ManualVerificationPlan:
    raw_checks = raw_item.get("checks", [])
    checks = tuple(
        _manual_verification_check_from_dict(check)
        for check in raw_checks
        if isinstance(check, dict)
    )
    return ManualVerificationPlan(
        project_name=str(raw_item.get("project_name", "")),
        requirement_id=str(raw_item.get("requirement_id", "")),
        checks=checks,
        created_at=str(raw_item.get("created_at", "")),
        updated_at=str(raw_item.get("updated_at", "")),
    )


def manual_verification_plan(project_name: str, requirement_id: str) -> ManualVerificationPlan | None:
    matching = next(
        (
            item
            for item in _load_manual_verifications()
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        return None
    return _manual_verification_plan_from_dict(matching)


def _signoff_state_for_counts(total_checks: int, passed_checks: int, failed_checks: int, not_run_checks: int) -> tuple[str, str]:
    if total_checks == 0:
        return ("NO_PLAN", "No verification plan")
    if failed_checks > 0:
        return ("BLOCKED", "Blocked by failing checks")
    if passed_checks == total_checks:
        return ("READY_FOR_SIGNOFF", "Ready for signoff")
    if not_run_checks == total_checks:
        return ("NOT_STARTED", "Verification not started")
    return ("IN_PROGRESS", "Verification in progress")


def manual_verification_summary(project_name: str, requirement_id: str) -> ManualVerificationSummary:
    plan = manual_verification_plan(project_name, requirement_id)
    checks = plan.checks if plan is not None else ()
    total_checks = len(checks)
    passed_checks = sum(1 for check in checks if check.status == "PASS")
    failed_checks = sum(1 for check in checks if check.status == "FAIL")
    not_run_checks = sum(1 for check in checks if check.status == "NOT_RUN")
    signoff_state, signoff_label = _signoff_state_for_counts(
        total_checks,
        passed_checks,
        failed_checks,
        not_run_checks,
    )
    return ManualVerificationSummary(
        requirement_id=requirement_id,
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        not_run_checks=not_run_checks,
        signoff_state=signoff_state,
        signoff_label=signoff_label,
    )


def add_manual_verification_check(
    project_name: str,
    requirement_id: str,
    *,
    title: str,
    instructions: str,
) -> ManualVerificationPlan:
    title_text = title.strip()
    if not title_text:
        raise ValueError("Verification check title is required.")

    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    now = datetime.now(timezone.utc).isoformat()
    if matching is None:
        matching = {
            "project_name": project_name,
            "requirement_id": requirement_id,
            "checks": [],
            "created_at": now,
            "updated_at": now,
        }
        items.append(matching)

    raw_checks = matching.setdefault("checks", [])
    if not isinstance(raw_checks, list):
        raw_checks = []
        matching["checks"] = raw_checks
    raw_checks.append(
        {
            "check_id": str(uuid4()),
            "title": title_text,
            "instructions": instructions.strip(),
            "status": "NOT_RUN",
            "notes": "",
            "created_at": now,
            "updated_at": now,
        }
    )
    matching["updated_at"] = now
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def update_manual_verification_check(
    project_name: str,
    requirement_id: str,
    check_id: str,
    *,
    status: str,
    notes: str,
) -> ManualVerificationPlan:
    normalized_status = status.strip().upper()
    if normalized_status not in {"NOT_RUN", "PASS", "FAIL"}:
        raise ValueError(f"Invalid verification status: {status}")

    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Manual verification plan not found: {project_name} {requirement_id}")

    raw_checks = matching.get("checks", [])
    if not isinstance(raw_checks, list):
        raise ValueError(f"Manual verification plan is malformed: {project_name} {requirement_id}")
    raw_check = next((check for check in raw_checks if str(check.get("check_id", "")) == check_id), None)
    if raw_check is None:
        raise ValueError(f"Manual verification check not found: {check_id}")

    now = datetime.now(timezone.utc).isoformat()
    raw_check["status"] = normalized_status
    raw_check["notes"] = notes.strip()
    raw_check["updated_at"] = now
    matching["updated_at"] = now
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def remove_manual_verification_check(project_name: str, requirement_id: str, check_id: str) -> ManualVerificationPlan | None:
    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        return None

    raw_checks = matching.get("checks", [])
    if not isinstance(raw_checks, list):
        return _manual_verification_plan_from_dict(matching)

    remaining_checks = [check for check in raw_checks if str(check.get("check_id", "")) != check_id]
    if len(remaining_checks) == len(raw_checks):
        return _manual_verification_plan_from_dict(matching)

    if not remaining_checks:
        items = [
            item
            for item in items
            if not (
                str(item.get("project_name", "")) == project_name
                and str(item.get("requirement_id", "")) == requirement_id
            )
        ]
        _save_manual_verifications(items)
        return None

    matching["checks"] = remaining_checks
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def _section_lines(path: Path, heading: str) -> list[str]:
    lines = path.read_text().splitlines()
    target = heading.strip().lower()
    start_index: int | None = None
    start_level = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        hashes = len(stripped) - len(stripped.lstrip("#"))
        title = stripped[hashes:].strip().lower()
        if title == target:
            start_index = index + 1
            start_level = hashes
            break
    if start_index is None:
        return []

    collected: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            if hashes <= start_level:
                break
        collected.append(line.rstrip())
    return collected


def _extract_bullets(lines: list[str]) -> tuple[str, ...]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("* ", "- ")):
            bullets.append(stripped[2:].strip())
    return tuple(bullets)


def _workflow_position_bullets(role_name: str) -> tuple[str, ...]:
    workflow_path = REPO_ROOT / "agent" / "workflow.md"
    lines = workflow_path.read_text().splitlines()
    start_pattern = f"{role_name.lower()} agent"
    start_index: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped[:1].isdigit() and start_pattern in stripped:
            start_index = index + 1
            break
    if start_index is None:
        return ()

    collected: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered[:1].isdigit() and lowered.endswith("agent") and "." in lowered:
            break
        collected.append(line.rstrip())
    return _extract_bullets(collected)


def _agent_memory_context(role_name: str) -> tuple[str, ...]:
    role_path = _role_doc_path(role_name)
    sections = ["Rules", "Behaviour Rules", "Memory Enforcement Rule"]
    bullets: list[str] = []
    for section in sections:
        bullets.extend(_extract_bullets(_section_lines(role_path, section)))
    seen: set[str] = set()
    deduped: list[str] = []
    for bullet in bullets:
        if bullet in seen:
            continue
        seen.add(bullet)
        deduped.append(bullet)
    return tuple(deduped[:3])


def _agent_can_do(role_name: str) -> tuple[str, ...]:
    role_path = _role_doc_path(role_name)
    bullets = _extract_bullets(_section_lines(role_path, "Responsibilities"))
    filtered = tuple(bullet for bullet in bullets if not bullet.startswith("Read "))
    return filtered[:3] or bullets[:3]


def _build_agent_summary(role: dict[str, str]) -> AgentSummary:
    name = role["name"]
    overrides = AGENT_SUMMARY_OVERRIDES.get(name, {})
    return AgentSummary(
        name=name,
        title=role["title"],
        can_do=overrides.get("can_do", _agent_can_do(name)),
        memory_context=overrides.get("memory_context", _agent_memory_context(name)),
        workflow_position=overrides.get("workflow_position", _workflow_position_bullets(name)),
    )


def _tasks_path(project_name: str) -> Path:
    return _project_path(project_name) / "product" / "tasks.md"


def _pm_clarifications_path(project_name: str) -> Path:
    return _project_runtime_data_path(project_name) / "pm_clarifications.json"


def _ensure_agent_thread_store() -> None:
    AGENT_THREAD_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AGENT_THREAD_FILE.exists():
        AGENT_THREAD_FILE.write_text("[]")


def _ensure_experience_store() -> None:
    EXPERIENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIENCE_FILE.exists():
        EXPERIENCE_FILE.write_text("[]")


def _ensure_implementation_store() -> None:
    IMPLEMENTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMPLEMENTATION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not IMPLEMENTATION_FILE.exists():
        IMPLEMENTATION_FILE.write_text("[]")


def _ensure_approval_store() -> None:
    APPROVAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not APPROVAL_FILE.exists():
        APPROVAL_FILE.write_text("[]")


def _ensure_pm_clarification_store(project_name: str) -> None:
    path = _pm_clarifications_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]")


def _normalize_priority(value: str) -> str:
    value = value.strip()
    return value.upper() if value else ""


def _normalize_effort(value: str) -> str:
    value = value.strip()
    return value.upper() if value else ""


def normalize_ui_runtime(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_")
    if normalized in UI_RUNTIME_OPTIONS:
        return normalized
    return DEFAULT_UI_RUNTIME


def project_runtime_profile(ui_runtime: str) -> ProjectRuntimeProfile:
    return PROJECT_RUNTIME_PROFILES[normalize_ui_runtime(ui_runtime)]


def project_runtime_label(ui_runtime: str) -> str:
    return project_runtime_profile(ui_runtime).label


def project_runtime_capability_summary(ui_runtime: str) -> str:
    profile = project_runtime_profile(ui_runtime)
    lines = [f"{profile.label} capability pack:"]
    lines.extend(f"- {item}" for item in profile.capability_pack)
    if profile.runtime == "web_app" and web_app_frontend_bundle_installed():
        lines.append(web_app_frontend_bundle_summary())
    if profile.architecture_guidance:
        lines.append("Architecture guidance:")
        lines.extend(f"- {item}" for item in profile.architecture_guidance)
    if profile.qa_release_checks:
        lines.append("Release checks:")
        lines.extend(f"- {item}" for item in profile.qa_release_checks)
    return "\n".join(lines)


def _ui_runtime_path(project_name: str) -> Path:
    return _project_path(project_name) / "product" / "ui-runtime.json"


def _openai_runtime_path(project_name: str) -> Path:
    return _requirements_path(project_name).with_name("openai-runtime.json")


OPENAI_RUNTIME_INFERENCE_VERSION = "4"


def _requirement_fingerprint(record: RequirementRecord) -> str:
    source = "\n".join((OPENAI_RUNTIME_INFERENCE_VERSION, record.title.strip(), record.description.strip()))
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def infer_openai_runtime_decision(record: RequirementRecord) -> OpenAIRuntimeDecision:
    text = f"{record.title}\n{record.description}".lower()
    ai_terms = (
        "openai", "artificial intelligence", " ai ", "ai-", "agent", "assistant", "chatbot",
        "language model", "llm", "model-generated", "model generated", "prompt", "chatgpt",
        "responses api", "agents sdk", "apps sdk", "realtime api",
    )
    padded_text = f" {text} "
    required = any(term in padded_text for term in ai_terms)
    capabilities: list[str] = []

    def mentions(*terms: str) -> bool:
        return any(term in text for term in terms)

    if required and mentions("current information", "latest information", "web search", "internet search", "market research", "competitor research", "external research"):
        capabilities.append("web_search")
    if required and mentions("knowledge base", "uploaded file", "uploaded document", "file search", "document search", "grounded in files", "search documents"):
        capabilities.append("file_search")
    if required and mentions("structured output", "extract", "classif", "score", "evaluate", "schema"):
        capabilities.append("structured_output")
    if required and mentions("function call", "tool call", "use tools", "external tool", "connector", "mcp"):
        capabilities.append("function_calling")
    if required and mentions("image generation", "generate image", "create image"):
        capabilities.append("image_generation")

    if required and mentions("inside chatgpt", "chatgpt app", "publish to chatgpt"):
        surface = "apps_sdk"
    elif required and mentions("real-time voice", "realtime voice", "live voice", "speech to speech", "audio conversation", "use realtime api", "with realtime api"):
        surface = "realtime_api"
        capabilities.append("realtime_audio")
    elif required and mentions("multi-agent", "multiple agents", "specialist agents", "handoff", "agent orchestration", "use the agents sdk", "with the agents sdk"):
        surface = "agents_sdk"
        capabilities.extend(("agent_handoffs", "tracing"))
    elif required:
        surface = "responses_api"
    else:
        surface = "none"

    review_reasons: list[str] = []
    if required:
        review_reasons.append("Introduces an external model dependency and API credential.")
    if required and mentions("personal data", "sensitive", "medical", "health", "financial", "children", "child data", "cv", "resume"):
        review_reasons.append("May process sensitive or personal data; confirm privacy and retention controls.")
    if required and mentions("write tool", "computer use", "send email", "make purchase", "publish automatically", "delete"):
        review_reasons.append("May perform consequential write actions; require explicit authorization boundaries.")
    if surface == "apps_sdk":
        review_reasons.append("Publishing a ChatGPT app introduces an external distribution and review surface.")

    if not required:
        rationale = "No model-driven behavior is implied by the current requirement."
        confidence = "high"
    else:
        named = ", ".join(dict.fromkeys(capabilities)) or "general model reasoning"
        rationale = f"The requirement implies model-driven behavior using {named}; {surface} is the smallest suitable OpenAI surface."
        confidence = "high" if mentions("openai", "agents sdk", "apps sdk", "web search", "realtime") else "medium"

    return OpenAIRuntimeDecision(
        requirement_id=record.id,
        required=required,
        surface=surface,
        capabilities=tuple(dict.fromkeys(capabilities)),
        credentials=("OPENAI_API_KEY",) if required else (),
        rationale=rationale,
        confidence=confidence,
        review_reasons=tuple(dict.fromkeys(review_reasons)),
        requirement_fingerprint=_requirement_fingerprint(record),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


def _openai_runtime_decision_to_dict(decision: OpenAIRuntimeDecision) -> dict[str, object]:
    return {
        "requirement_id": decision.requirement_id,
        "required": decision.required,
        "surface": decision.surface,
        "capabilities": list(decision.capabilities),
        "credentials": list(decision.credentials),
        "rationale": decision.rationale,
        "confidence": decision.confidence,
        "review_reasons": list(decision.review_reasons),
        "requirement_fingerprint": decision.requirement_fingerprint,
        "updated_at": decision.updated_at,
        "source": "automatic_requirement_inference",
    }


def _openai_runtime_decision_from_dict(raw: dict[str, object]) -> OpenAIRuntimeDecision:
    return OpenAIRuntimeDecision(
        requirement_id=str(raw.get("requirement_id", "")),
        required=bool(raw.get("required", False)),
        surface=str(raw.get("surface", "none")),
        capabilities=tuple(str(item) for item in raw.get("capabilities", []) if str(item)),
        credentials=tuple(str(item) for item in raw.get("credentials", []) if str(item)),
        rationale=str(raw.get("rationale", "")),
        confidence=str(raw.get("confidence", "medium")),
        review_reasons=tuple(str(item) for item in raw.get("review_reasons", []) if str(item)),
        requirement_fingerprint=str(raw.get("requirement_fingerprint", "")),
        updated_at=str(raw.get("updated_at", "")),
    )


def load_openai_runtime_decisions(project_name: str) -> dict[str, OpenAIRuntimeDecision]:
    path = _openai_runtime_path(project_name)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    raw_items = payload.get("requirements", {}) if isinstance(payload, dict) else {}
    if not isinstance(raw_items, dict):
        return {}
    return {
        str(requirement_id): _openai_runtime_decision_from_dict(raw)
        for requirement_id, raw in raw_items.items()
        if isinstance(raw, dict)
    }


def reconcile_openai_runtime_decisions(
    project_name: str,
    records: list[RequirementRecord] | tuple[RequirementRecord, ...] | None = None,
) -> dict[str, OpenAIRuntimeDecision]:
    if records is None:
        document = load_requirement_document(project_name)
        records = document.active_requirements + document.backlog_requirements
    existing = load_openai_runtime_decisions(project_name)
    decisions: dict[str, OpenAIRuntimeDecision] = {}
    for record in records:
        current = existing.get(record.id)
        if current is not None and current.requirement_fingerprint == _requirement_fingerprint(record):
            decisions[record.id] = current
        else:
            decisions[record.id] = infer_openai_runtime_decision(record)
    path = _openai_runtime_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "description": "Automatically inferred OpenAI runtime decisions. Product requirements remain provider-neutral unless product intent requires otherwise.",
        "requirements": {
            requirement_id: _openai_runtime_decision_to_dict(decision)
            for requirement_id, decision in decisions.items()
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return decisions


def requirement_openai_runtime_decision(project_name: str, record: RequirementRecord) -> OpenAIRuntimeDecision:
    current = load_openai_runtime_decisions(project_name).get(record.id)
    if current is not None and current.requirement_fingerprint == _requirement_fingerprint(record):
        return current
    return infer_openai_runtime_decision(record)


def _load_ui_runtime_payload(project_name: str) -> dict[str, object]:
    path = _ui_runtime_path(project_name)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def load_project_ui_runtime(project_name: str) -> str:
    payload = _load_ui_runtime_payload(project_name)
    return normalize_ui_runtime(str(payload.get("default_ui_runtime", DEFAULT_UI_RUNTIME)))


def save_project_ui_runtime(project_name: str, ui_runtime: str) -> None:
    path = _ui_runtime_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_ui_runtime_payload(project_name)
    payload["default_ui_runtime"] = normalize_ui_runtime(ui_runtime)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def _normalize_figma_mode(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_")
    return normalized if normalized in FIGMA_DESIGN_MODES else "code_first"


def load_project_figma_config(project_name: str) -> ProjectFigmaConfig:
    design = _load_ui_runtime_payload(project_name).get("design", {})
    if not isinstance(design, dict):
        design = {}
    raw_references = design.get("figma_references", [])
    references: list[FigmaDesignReference] = []
    if isinstance(raw_references, list):
        for raw in raw_references:
            if not isinstance(raw, dict) or not str(raw.get("requirement_id", "")).strip():
                continue
            references.append(
                FigmaDesignReference(
                    requirement_id=str(raw.get("requirement_id", "")).strip(),
                    frame_url=str(raw.get("frame_url", "")).strip(),
                    frame_name=str(raw.get("frame_name", "")).strip(),
                    approval_status=str(raw.get("approval_status", "draft")).strip().lower() or "draft",
                )
            )
    return ProjectFigmaConfig(
        mode=_normalize_figma_mode(str(design.get("mode", "code_first"))),
        file_url=str(design.get("figma_file_url", "")).strip(),
        file_name=str(design.get("figma_file_name", "")).strip(),
        references=tuple(references),
    )


def save_project_figma_config(
    project_name: str,
    *,
    mode: str,
    file_url: str,
    file_name: str,
) -> ProjectFigmaConfig:
    path = _ui_runtime_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_ui_runtime_payload(project_name)
    existing = payload.get("design", {})
    design = dict(existing) if isinstance(existing, dict) else {}
    design.update(
        {
            "mode": _normalize_figma_mode(mode),
            "figma_file_url": file_url.strip(),
            "figma_file_name": file_name.strip(),
        }
    )
    design.setdefault("figma_references", [])
    payload["design"] = design
    payload.setdefault("default_ui_runtime", DEFAULT_UI_RUNTIME)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return load_project_figma_config(project_name)


def save_requirement_figma_reference(
    project_name: str,
    *,
    requirement_id: str,
    frame_url: str,
    frame_name: str,
    approved: bool,
) -> ProjectFigmaConfig:
    config = load_project_figma_config(project_name)
    references = [item for item in config.references if item.requirement_id != requirement_id.strip()]
    if frame_url.strip():
        references.append(
            FigmaDesignReference(
                requirement_id=requirement_id.strip(),
                frame_url=frame_url.strip(),
                frame_name=frame_name.strip(),
                approval_status="approved" if approved else "draft",
            )
        )
    payload = _load_ui_runtime_payload(project_name)
    design = payload.get("design", {})
    design = dict(design) if isinstance(design, dict) else {}
    design["figma_references"] = [
        {
            "requirement_id": item.requirement_id,
            "frame_url": item.frame_url,
            "frame_name": item.frame_name,
            "approval_status": item.approval_status,
        }
        for item in references
    ]
    payload["design"] = design
    payload.setdefault("default_ui_runtime", DEFAULT_UI_RUNTIME)
    path = _ui_runtime_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return load_project_figma_config(project_name)


def requirement_figma_reference(project_name: str, requirement_id: str) -> FigmaDesignReference | None:
    return next(
        (item for item in load_project_figma_config(project_name).references if item.requirement_id == requirement_id),
        None,
    )


def figma_design_evidence_path(project_name: str, requirement_id: str) -> Path:
    safe_requirement_id = re.sub(r"[^A-Za-z0-9._-]+", "-", requirement_id.strip())
    return _project_path(project_name) / "product" / "figma-evidence" / f"{safe_requirement_id}.json"


def load_figma_design_evidence(project_name: str, requirement_id: str) -> dict[str, object]:
    path = figma_design_evidence_path(project_name, requirement_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _figma_reference_identity(value: str) -> tuple[str, str]:
    file_match = re.search(r"figma\.com/design/([^/?#]+)", value.strip())
    node_match = re.search(r"[?&]node-id=([^&#]+)", value.strip())
    file_key = file_match.group(1) if file_match else ""
    node_id = node_match.group(1).replace(":", "-") if node_match else ""
    return file_key, node_id


def figma_evidence_matches_reference(project_name: str, requirement_id: str) -> bool:
    reference = requirement_figma_reference(project_name, requirement_id)
    evidence = load_figma_design_evidence(project_name, requirement_id)
    if reference is None or reference.approval_status != "approved" or not evidence:
        return False
    source = evidence.get("source", {})
    if not isinstance(source, dict):
        return False
    evidence_url = str(source.get("frame_url", ""))
    screenshot = evidence.get("frame", {})
    screenshot_path = str(screenshot.get("screenshot_path", "")) if isinstance(screenshot, dict) else ""
    screenshot_exists = bool(screenshot_path and (_project_path(project_name) / screenshot_path).is_file())
    return (
        str(evidence.get("status", "")).upper() == "PASS"
        and _figma_reference_identity(evidence_url) == _figma_reference_identity(reference.frame_url)
        and screenshot_exists
    )


def effective_requirement_ui_runtime(project_name: str, record: RequirementRecord) -> str:
    if record.ui_runtime.strip():
        return normalize_ui_runtime(record.ui_runtime)
    return load_project_ui_runtime(project_name)


def _parse_requirement_section(section_text: str) -> tuple[RequirementRecord, ...]:
    records: list[RequirementRecord] = []
    for match in REQUIREMENT_BLOCK_PATTERN.finditer(section_text.strip()):
        description = match.group(7).strip()
        records.append(
            RequirementRecord(
                id=match.group(1).strip(),
                title=match.group(2).strip(),
                status=match.group(3).strip(),
                priority=_normalize_priority(match.group(4) or ""),
                effort=_normalize_effort(match.group(5) or ""),
                ui_runtime=(match.group(6) or "").strip(),
                description=description,
            )
        )
    return tuple(records)


def _parse_task_document(text: str) -> TaskDocument:
    matches = list(TASK_BLOCK_PATTERN.finditer(text))
    if not matches:
        return TaskDocument(intro=text.rstrip(), tasks=())

    intro = text[: matches[0].start()].rstrip()
    tasks: list[TaskBlock] = []
    for match in matches:
        tasks.append(
            TaskBlock(
                number=int(match.group(1)),
                title=match.group(2).strip(),
                task_type=match.group(3).strip(),
                status=match.group(4).strip(),
                requirements=tuple(re.findall(r"\bR\d+\b", match.group(5))),
                body=match.group(6).rstrip(),
            )
        )
    return TaskDocument(intro=intro, tasks=tuple(tasks))


def load_task_document(project_name: str) -> TaskDocument:
    path = _tasks_path(project_name)
    text = path.read_text()
    return _parse_task_document(text)


def _render_task_block(task: TaskBlock) -> str:
    requirement_label = "Requirements" if len(task.requirements) != 1 else "Requirement"
    requirements_text = ", ".join(task.requirements)
    parts = [
        f"## Task {task.number}: {task.title}",
        "",
        f"Type: {task.task_type}",
        f"Status: {task.status}",
        f"{requirement_label}: {requirements_text}",
        "",
        task.body.rstrip(),
    ]
    return "\n".join(parts).rstrip()


def save_task_document(project_name: str, document: TaskDocument) -> None:
    rendered_tasks = "\n\n".join(_render_task_block(task) for task in document.tasks)
    rendered = document.intro.rstrip()
    if rendered_tasks:
        rendered = f"{rendered}\n\n{rendered_tasks}\n"
    else:
        rendered = f"{rendered}\n"
    _tasks_path(project_name).write_text(rendered)


def load_requirement_document(project_name: str) -> RequirementDocument:
    path = _requirements_path(project_name)
    text = path.read_text()

    if PRODUCT_REQUIREMENTS_HEADER not in text:
        raise ValueError(f"Requirements file missing {PRODUCT_REQUIREMENTS_HEADER}: {path}")

    intro, product_section = text.split(PRODUCT_REQUIREMENTS_HEADER, 1)
    product_section = product_section.strip()

    rules_header = RULES_HEADER if RULES_HEADER in product_section else REQUIREMENT_RULES_HEADER
    if ACTIVE_HEADER not in product_section or BACKLOG_HEADER not in product_section or rules_header not in product_section:
        raise ValueError(f"Requirements file missing expected sections: {path}")

    _, after_active = product_section.split(ACTIVE_HEADER, 1)
    active_text, after_backlog_header = after_active.split(BACKLOG_HEADER, 1)
    backlog_text, rules_text = after_backlog_header.split(rules_header, 1)

    return RequirementDocument(
        intro=intro.rstrip(),
        active_requirements=_parse_requirement_section(active_text),
        backlog_requirements=_parse_requirement_section(backlog_text),
        rules_text=rules_text.strip(),
    )


def next_requirement_id(project_name: str) -> str:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    highest = 0
    for record in records:
        highest = max(highest, int(record.id.removeprefix("R")))
    return f"R{highest + 1}"


def _render_requirement_block(record: RequirementRecord) -> str:
    lines = [
        f"### {record.id} — {record.title}",
        "",
        f"Status: {record.status}",
    ]
    if record.priority:
        lines.append(f"Priority: {record.priority}")
    if record.effort:
        lines.append(f"Effort: {record.effort}")
    if record.ui_runtime.strip():
        lines.append(f"UI Runtime: {normalize_ui_runtime(record.ui_runtime)}")
    lines.extend(
        [
            "Description:",
            record.description.strip(),
        ]
    )
    return "\n".join(lines).rstrip()


def save_requirement_document(project_name: str, records: list[RequirementRecord], template: RequirementDocument) -> None:
    active_records = [record for record in records if record.status != "BACKLOG"]
    backlog_records = [record for record in records if record.status == "BACKLOG"]

    active_text = "\n\n".join(_render_requirement_block(record) for record in active_records) or "Add active requirements here."
    backlog_text = "\n\n".join(_render_requirement_block(record) for record in backlog_records) or "Add backlog requirements here when needed."

    rendered = "\n".join(
        [
            template.intro.rstrip(),
            "",
            PRODUCT_REQUIREMENTS_HEADER,
            "",
            ACTIVE_HEADER,
            "",
            active_text,
            "",
            "---",
            "",
            BACKLOG_HEADER,
            "",
            backlog_text,
            "",
            "---",
            "",
            RULES_HEADER,
            "",
            template.rules_text.strip(),
            "",
        ]
    )
    _requirements_path(project_name).write_text(rendered)
    reconcile_openai_runtime_decisions(project_name, records)


def recommend_requirement(records: list[RequirementRecord]) -> RequirementRecommendation | None:
    in_progress = [record for record in records if record.status == "IN_PROGRESS"]
    if in_progress:
        selected = in_progress[0]
        return RequirementRecommendation(
            requirement_id=selected.id,
            title=selected.title,
            rationale="Keep the currently active requirement moving before starting additional work.",
        )

    new_records = [record for record in records if record.status == "NEW"]
    if not new_records:
        return None

    priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "": 3}
    effort_rank = {"S": 0, "M": 1, "L": 2, "": 3}
    selected = sorted(
        new_records,
        key=lambda record: (
            priority_rank.get(record.priority, 3),
            effort_rank.get(record.effort, 3),
            record.id,
        ),
    )[0]
    return RequirementRecommendation(
        requirement_id=selected.id,
        title=selected.title,
        rationale="Prefer the highest-priority pending requirement, breaking ties toward lower effort.",
    )


def _replace_requirement_record(project_name: str, updated_record: RequirementRecord) -> None:
    document = load_requirement_document(project_name)
    all_records = list(document.active_requirements + document.backlog_requirements)
    replaced = False
    new_records: list[RequirementRecord] = []
    for record in all_records:
        if record.id == updated_record.id:
            new_records.append(updated_record)
            replaced = True
        else:
            new_records.append(record)
    if not replaced:
        raise ValueError(f"Requirement not found: {updated_record.id}")
    save_requirement_document(project_name, new_records, document)


def update_requirement(project_name: str, updated_record: RequirementRecord) -> None:
    document = load_requirement_document(project_name)
    all_records = list(document.active_requirements + document.backlog_requirements)
    existing = next((record for record in all_records if record.id == updated_record.id), None)
    if existing is None:
        raise ValueError(f"Requirement not found: {updated_record.id}")
    if updated_record.status == "DONE" and existing.status != "DONE":
        pending_record = RequirementRecord(
            id=updated_record.id,
            title=updated_record.title,
            status=existing.status,
            priority=updated_record.priority,
            effort=updated_record.effort,
            description=updated_record.description,
            ui_runtime=updated_record.ui_runtime,
        )
        _replace_requirement_record(project_name, pending_record)
        request_release_delivery_approval(project_name, updated_record)
        return
    _replace_requirement_record(project_name, updated_record)


def delete_requirement(project_name: str, requirement_id: str) -> RequirementDeletionResult:
    document = load_requirement_document(project_name)
    all_records = list(document.active_requirements + document.backlog_requirements)
    matching = next((record for record in all_records if record.id == requirement_id), None)
    if matching is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    if matching.status == "DONE":
        raise ValueError(f"Completed requirements cannot be deleted: {requirement_id}")
    active_run = active_implementation_run(project_name)
    if active_run is not None and active_run.requirement_id == requirement_id:
        raise ValueError(f"Requirement cannot be deleted while implementation is active: {requirement_id}")

    remaining_records = [record for record in all_records if record.id != requirement_id]
    save_requirement_document(project_name, remaining_records, document)
    existing_sprint = load_sprint_plan(project_name)
    if existing_sprint is not None and requirement_id in existing_sprint.requirement_ids:
        updated_ids = tuple(item for item in existing_sprint.requirement_ids if item != requirement_id)
        if updated_ids:
            _replace_sprint_plan(
                project_name,
                status="PLANNING" if existing_sprint.status == "PLANNING" else existing_sprint.status,
                requirement_ids=updated_ids,
                created_at=existing_sprint.created_at,
                started_at=existing_sprint.started_at,
                completed_at=existing_sprint.completed_at,
                current_requirement_id="" if existing_sprint.current_requirement_id == requirement_id else existing_sprint.current_requirement_id,
                blocked_reason=existing_sprint.blocked_reason if existing_sprint.current_requirement_id != requirement_id else "",
            )
        else:
            _save_sprint_plan_raw(project_name, None)

    task_document = load_task_document(project_name)
    remaining_tasks: list[TaskBlock] = []
    removed_tasks = 0
    updated_tasks = 0
    for task in task_document.tasks:
        if requirement_id not in task.requirements:
            remaining_tasks.append(task)
            continue

        remaining_requirements = tuple(req for req in task.requirements if req != requirement_id)
        if not remaining_requirements:
            removed_tasks += 1
            continue

        updated_tasks += 1
        remaining_tasks.append(
            TaskBlock(
                number=task.number,
                title=task.title,
                task_type=task.task_type,
                status=task.status,
                requirements=remaining_requirements,
                body=task.body,
            )
        )

    save_task_document(project_name, TaskDocument(intro=task_document.intro, tasks=tuple(remaining_tasks)))

    clarifications = _load_pm_clarifications(project_name)
    remaining_clarifications = [
        item for item in clarifications if str(item.get("requirement_id", "")) != requirement_id
    ]
    removed_clarifications = len(clarifications) - len(remaining_clarifications)
    _save_pm_clarifications(project_name, remaining_clarifications)

    raw_runs = _load_implementation_runs()
    remaining_runs: list[dict[str, object]] = []
    removed_implementation_runs = 0
    for run in raw_runs:
        if str(run.get("project_name", "")) != project_name or str(run.get("requirement_id", "")) != requirement_id:
            remaining_runs.append(run)
            continue
        removed_implementation_runs += 1
        for artifact_path in (run.get("output_path"), run.get("log_path")):
            if not artifact_path:
                continue
            path = Path(str(artifact_path))
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
    _save_implementation_runs(remaining_runs)

    return RequirementDeletionResult(
        deleted_requirement=matching,
        removed_tasks=removed_tasks,
        updated_tasks=updated_tasks,
        removed_clarifications=removed_clarifications,
        removed_implementation_runs=removed_implementation_runs,
    )


def append_requirement(
    project_name: str,
    title: str,
    description: str,
    *,
    status: str = "NEW",
    priority: str = "MEDIUM",
    effort: str = "M",
) -> RequirementRecord:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    new_record = RequirementRecord(
        id=next_requirement_id(project_name),
        title=title.strip(),
        status=status.strip(),
        priority=_normalize_priority(priority),
        effort=_normalize_effort(effort),
        description=description.strip(),
        ui_runtime="",
    )
    records.append(new_record)
    save_requirement_document(project_name, records, document)
    return new_record


def _priority_rank(value: str) -> int:
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(value.strip().upper(), 0)


def _effort_rank(value: str) -> int:
    return {"S": 1, "M": 2, "L": 3}.get(value.strip().upper(), 0)


def _requirement_similarity_tokens(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", text.lower())
    tokens = {
        token
        for token in cleaned.split()
        if len(token) > 2 and token not in REQUIREMENT_CONSOLIDATION_STOPWORDS
    }
    return tokens


def _find_requirement_consolidation_target(
    project_name: str,
    requirement_title: str,
    requirement_body: str,
) -> RequirementRecord | None:
    document = load_requirement_document(project_name)
    candidates = [
        record
        for record in (document.active_requirements + document.backlog_requirements)
        if record.status in {"NEW", "BACKLOG"}
    ]
    incoming_title_tokens = _requirement_similarity_tokens(requirement_title)
    incoming_body_tokens = _requirement_similarity_tokens(requirement_body)
    incoming_tokens = incoming_title_tokens | incoming_body_tokens
    if not incoming_tokens:
        return None

    best_match: RequirementRecord | None = None
    best_score = 0.0
    for candidate in candidates:
        candidate_title_tokens = _requirement_similarity_tokens(candidate.title)
        candidate_body_tokens = _requirement_similarity_tokens(candidate.description)
        candidate_tokens = candidate_title_tokens | candidate_body_tokens
        if not candidate_tokens:
            continue
        shared = incoming_tokens & candidate_tokens
        if len(shared) < 3:
            continue
        score = len(shared) / max(1, min(len(incoming_tokens), len(candidate_tokens)))
        title_overlap = len(incoming_title_tokens & candidate_title_tokens)
        if score < 0.45 and title_overlap < 2:
            continue
        if score > best_score:
            best_match = candidate
            best_score = score
    return best_match


def _merge_review_artifact_into_requirement(
    project_name: str,
    requirement: RequirementRecord,
    *,
    source_agent_name: str,
    artifact_title: str,
    artifact_body: str,
    priority: str,
    effort: str,
) -> RequirementRecord:
    note_header = "**Additional approved review input**"
    note_body = "\n".join(
        [
            note_header,
            f"Source: {source_agent_name}",
            f"Title: {artifact_title.strip() or 'Untitled review'}",
            "",
            artifact_body.strip(),
        ]
    ).strip()
    description = requirement.description.strip()
    if artifact_body.strip() not in description:
        description = f"{description}\n\n{note_body}".strip()

    merged = RequirementRecord(
        id=requirement.id,
        title=requirement.title,
        status=requirement.status,
        priority=priority if _priority_rank(priority) > _priority_rank(requirement.priority) else requirement.priority,
        effort=effort if _effort_rank(effort) > _effort_rank(requirement.effort) else requirement.effort,
        description=description,
        ui_runtime=requirement.ui_runtime,
    )
    update_requirement(project_name, merged)
    return merged


def move_requirement(project_name: str, requirement_id: str, direction: int) -> None:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    index = next((i for i, record in enumerate(records) if record.id == requirement_id), None)
    if index is None:
        raise ValueError(f"Requirement not found: {requirement_id}")

    target = index + direction
    if target < 0 or target >= len(records):
        return

    records[index], records[target] = records[target], records[index]
    save_requirement_document(project_name, records, document)


def create_project_from_ui(
    project_name: str,
    display_name: str,
    initial_idea: str,
    *,
    ui_runtime: str = DEFAULT_UI_RUNTIME,
) -> Path:
    normalized_ui_runtime = normalize_ui_runtime(ui_runtime)
    destination = scaffold_project(
        project_name=project_name.strip(),
        display_name=display_name.strip(),
        product_title=display_name.strip(),
        initial_requirement=initial_idea.strip(),
        ui_runtime=normalized_ui_runtime,
    )
    save_project_ui_runtime(destination.name, normalized_ui_runtime)
    return destination


def create_project_from_reviewed_draft(
    project_name: str,
    display_name: str,
    requirement_title: str,
    requirement_description: str,
    *,
    ui_runtime: str = DEFAULT_UI_RUNTIME,
) -> Path:
    normalized_project_name = project_name.strip()
    normalized_display_name = display_name.strip()
    normalized_requirement_title = requirement_title.strip()
    normalized_requirement_description = requirement_description.strip()
    normalized_ui_runtime = normalize_ui_runtime(ui_runtime)

    try:
        destination = scaffold_project(
            project_name=normalized_project_name,
            display_name=normalized_display_name,
            product_title=normalized_display_name,
            initial_requirement_title=normalized_requirement_title,
            initial_requirement=normalized_requirement_description,
            ui_runtime=normalized_ui_runtime,
        )
        save_project_ui_runtime(destination.name, normalized_ui_runtime)
        _migrate_legacy_project_runtime_data(destination.name)
        return destination
    except TypeError as exc:
        unsupported = str(exc)
        if "initial_requirement_title" not in unsupported and "ui_runtime" not in unsupported:
            raise

        destination = scaffold_project(
            project_name=normalized_project_name,
            display_name=normalized_display_name,
            product_title=normalized_display_name,
            initial_requirement=normalized_requirement_description,
        )
        created_project_name = destination.name
        save_project_ui_runtime(created_project_name, normalized_ui_runtime)
        _migrate_legacy_project_runtime_data(created_project_name)
        document = load_requirement_document(created_project_name)
        records = list(document.active_requirements + document.backlog_requirements)
        if records:
            first = records[0]
            records[0] = RequirementRecord(
                id=first.id,
                title=normalized_requirement_title or first.title,
                status=first.status,
                priority=first.priority,
                effort=first.effort,
                description=first.description,
                ui_runtime=first.ui_runtime,
            )
            save_requirement_document(created_project_name, records, document)
        return destination


def discovery_plan(idea: str) -> DiscoveryPlan:
    focus = idea.strip() or "this idea"
    lower_focus = focus.lower()
    if any(keyword in lower_focus for keyword in ("ui", "form", "flow", "workflow", "experience", "interaction")):
        return DiscoveryPlan(
            mode="interaction",
            framing="PM is treating this as an interaction and workflow discovery problem, so the next questions focus on where the current experience feels heavy or unclear.",
            questions=(
                DiscoveryQuestion("target_user", f"Who is the primary user for {focus}, and what makes them the right starting point?"),
                DiscoveryQuestion("problem", "What part of the current interaction feels most frustrating or low-value?"),
                DiscoveryQuestion("context", "Where in the current workflow does this friction show up most clearly?"),
                DiscoveryQuestion("constraints", "What should keep the first interaction simple, relevant, and uncluttered?"),
                DiscoveryQuestion("success", "What would make the first interaction feel more genuinely guided after a short period of use?"),
                DiscoveryQuestion("out_of_scope", "What should stay out of scope while we improve this interaction?"),
            ),
        )

    if any(keyword in lower_focus for keyword in ("integration", "sync", "calendar", "api", "import", "export")):
        return DiscoveryPlan(
            mode="integration",
            framing="PM is treating this as an integration-style requirement, so the next questions focus on system boundaries, dependencies, and value of the connection.",
            questions=(
                DiscoveryQuestion("target_user", f"Who most needs {focus}, and why are they the right first user?"),
                DiscoveryQuestion("problem", "What problem exists today because this system is not connected yet?"),
                DiscoveryQuestion("context", "What current workflow or dependency makes this integration worth doing now?"),
                DiscoveryQuestion("constraints", "What technical or operational constraints should shape the first slice?"),
                DiscoveryQuestion("success", "What outcome would prove the integration is useful without overbuilding it?"),
                DiscoveryQuestion("out_of_scope", "What related integration behavior should stay out of the first version?"),
            ),
        )

    return DiscoveryPlan(
        mode="general",
        framing="PM is treating this as a general product-discovery problem, so the next questions focus on user, problem, context, constraints, and success.",
        questions=(
            DiscoveryQuestion("target_user", f"Who is the primary user for {focus}, and what makes them the right starting point?"),
            DiscoveryQuestion("problem", "What user problem are we trying to solve first?"),
            DiscoveryQuestion("context", "What context or current workflow makes this problem worth solving now?"),
            DiscoveryQuestion("constraints", "What constraints or guardrails should shape the first version?"),
            DiscoveryQuestion("success", "What would make the first version feel successful after a short period of use?"),
            DiscoveryQuestion("out_of_scope", "What should stay out of scope for the first version?"),
        ),
    )


def discovery_questions(idea: str) -> tuple[DiscoveryQuestion, ...]:
    return discovery_plan(idea).questions


def experience_intake_plan(user_problem: str) -> ExperienceIntakePlan:
    problem = user_problem.strip().lower()
    recommendation_type = "UX improvement in scope"
    rationale_prompt = "Why should this finding be routed this way?"

    if any(keyword in problem for keyword in ("add", "should be able", "need to", "it will be better", "would be better")):
        recommendation_type = "feature candidate"
        rationale_prompt = "Why does this feel like a feature candidate rather than a small in-scope polish issue?"
    elif any(keyword in problem for keyword in ("scope", "permission", "share", "remote", "collaborator")):
        recommendation_type = "scope escalation"
        rationale_prompt = "Why does this seem to need a scope or strategy decision before PM acts?"

    affected_prompt = "Which user or workflow is feeling this problem most directly?"
    evidence_prompt = "What did you observe that supports this finding?"

    if any(keyword in problem for keyword in ("ui", "form", "layout", "card", "page", "screen")):
        affected_prompt = "Which screen or interaction path is being affected most?"
        evidence_prompt = "What about the current UI or interaction makes this issue visible?"
    elif any(keyword in problem for keyword in ("discovery", "question", "feedback", "intake")):
        affected_prompt = "Which feedback or discovery workflow is becoming heavy or unclear?"
        evidence_prompt = "What about the current intake flow is causing friction?"

    return ExperienceIntakePlan(
        affected_workflow_prompt=affected_prompt,
        evidence_prompt=evidence_prompt,
        rationale_prompt=rationale_prompt,
        recommendation_type=recommendation_type,
    )


def _load_agent_threads() -> list[dict[str, object]]:
    _ensure_agent_thread_store()
    return json.loads(AGENT_THREAD_FILE.read_text())


def _save_agent_threads(raw_threads: list[dict[str, object]]) -> None:
    _ensure_agent_thread_store()
    AGENT_THREAD_FILE.write_text(json.dumps(raw_threads, indent=2))


def _load_experience_findings() -> list[dict[str, object]]:
    _ensure_experience_store()
    return json.loads(EXPERIENCE_FILE.read_text())


def _save_experience_findings(raw_findings: list[dict[str, object]]) -> None:
    _ensure_experience_store()
    EXPERIENCE_FILE.write_text(json.dumps(raw_findings, indent=2))


def _load_implementation_runs() -> list[dict[str, object]]:
    _ensure_implementation_store()
    return json.loads(IMPLEMENTATION_FILE.read_text())


def _save_implementation_runs(raw_runs: list[dict[str, object]]) -> None:
    _ensure_implementation_store()
    IMPLEMENTATION_FILE.write_text(json.dumps(raw_runs, indent=2))


def _load_approvals() -> list[dict[str, object]]:
    _ensure_approval_store()
    return json.loads(APPROVAL_FILE.read_text())


def _save_approvals(raw_items: list[dict[str, object]]) -> None:
    _ensure_approval_store()
    APPROVAL_FILE.write_text(json.dumps(raw_items, indent=2))


def _load_pm_clarifications(project_name: str) -> list[dict[str, object]]:
    path = _pm_clarifications_path(project_name)
    _ensure_pm_clarification_store(project_name)
    return load_pm_clarification_store(path)


def _save_pm_clarifications(project_name: str, raw_items: list[dict[str, object]]) -> None:
    path = _pm_clarifications_path(project_name)
    _ensure_pm_clarification_store(project_name)
    save_pm_clarification_store(path, raw_items)


def _resolve_pm_clarification_raw(project_name: str, clarification_id: str) -> dict[str, object]:
    return resolve_pm_clarification_in_store(_pm_clarifications_path(project_name), clarification_id)


def _implementation_run_from_dict(raw_run: dict[str, object]) -> ImplementationRun:
    worker_pid = raw_run.get("worker_pid")
    return ImplementationRun(
        run_id=str(raw_run["run_id"]),
        project_name=str(raw_run["project_name"]),
        requirement_id=str(raw_run["requirement_id"]),
        requirement_title=str(raw_run.get("requirement_title", "")),
        status=str(raw_run["status"]),
        summary=str(raw_run.get("summary", "")),
        error=str(raw_run.get("error", "")),
        created_at=str(raw_run.get("created_at", "")),
        started_at=str(raw_run.get("started_at", "")),
        finished_at=str(raw_run.get("finished_at", "")),
        output_path=str(raw_run.get("output_path", "")),
        log_path=str(raw_run.get("log_path", "")),
        worker_pid=int(worker_pid) if worker_pid is not None else None,
    )


def _approval_from_dict(raw_item: dict[str, object]) -> ApprovalRequest:
    raw_payload = raw_item.get("payload", {})
    payload = {str(key): str(value) for key, value in dict(raw_payload).items()} if isinstance(raw_payload, dict) else {}
    return ApprovalRequest(
        approval_id=str(raw_item.get("approval_id", "")),
        project_name=str(raw_item.get("project_name", "")),
        approval_type=str(raw_item.get("approval_type", "")),
        source_thread_id=str(raw_item.get("source_thread_id", "")),
        source_agent_name=str(raw_item.get("source_agent_name", "")),
        title=str(raw_item.get("title", "")),
        summary=str(raw_item.get("summary", "")),
        payload=payload,
        status=str(raw_item.get("status", "")),
        created_at=str(raw_item.get("created_at", "")),
        resolved_at=str(raw_item.get("resolved_at", "")),
    )


def _clean_attachment_paths(paths: object) -> tuple[str, ...]:
    if not isinstance(paths, (list, tuple)):
        return ()
    return tuple(str(path) for path in paths if str(path).strip())


def _agent_message_from_dict(message: dict[str, object]) -> AgentMessage:
    return AgentMessage(
        role=str(message.get("role", "")),
        content=str(message.get("content", "")),
        created_at=str(message.get("created_at", "")),
        attachments=_clean_attachment_paths(message.get("attachments", [])),
    )


def _agent_message_payload(message: AgentMessage) -> dict[str, object]:
    return {
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
        "attachments": list(message.attachments),
    }


def _agent_message(role: str, content: str, *, attachments: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "role": role,
        "content": content.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "attachments": list(attachments),
    }


def _slugify_filename(name: str) -> str:
    stem = Path(name).stem or "image"
    suffix = Path(name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") or "image"
    safe_suffix = suffix if re.fullmatch(r"\.[A-Za-z0-9]+", suffix) else ".png"
    return f"{safe_stem}{safe_suffix}"


def save_agent_message_uploads(
    project_name: str,
    thread_id: str,
    image_files: tuple[tuple[str, bytes], ...],
) -> tuple[str, ...]:
    saved_paths: list[str] = []
    if not image_files:
        return ()

    upload_dir = AGENT_UPLOAD_DIR / project_name / thread_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    for original_name, raw_bytes in image_files:
        safe_name = _slugify_filename(original_name or "image.png")
        unique_name = f"{uuid4()}-{safe_name}"
        destination = upload_dir / unique_name
        destination.write_bytes(raw_bytes)
        saved_paths.append(str(destination))
    return tuple(saved_paths)


def _image_path_to_data_url(image_path: str) -> str | None:
    try:
        image_bytes = Path(image_path).read_bytes()
    except OSError:
        return None
    optimized = _optimize_live_input_image(image_bytes)
    if optimized is not None:
        mime, image_bytes = optimized
    else:
        mime_type, _ = mimetypes.guess_type(image_path)
        mime = mime_type or "image/png"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _optimize_live_input_image(image_bytes: bytes) -> tuple[str, bytes] | None:
    max_data_url_chars = 10_000
    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            prepared = ImageOps.exif_transpose(source)
            if prepared.mode not in {"RGB", "L"}:
                background = Image.new("RGB", prepared.size, (255, 255, 255))
                alpha_ready = prepared.convert("RGBA")
                background.paste(alpha_ready, mask=alpha_ready.getchannel("A"))
                prepared = background
            elif prepared.mode != "RGB":
                prepared = prepared.convert("RGB")

            for max_side, quality in (
                (768, 55),
                (512, 45),
                (384, 40),
                (256, 35),
            ):
                candidate = prepared.copy()
                candidate.thumbnail((max_side, max_side))
                buffer = io.BytesIO()
                candidate.save(buffer, format="JPEG", quality=quality, optimize=True)
                candidate_bytes = buffer.getvalue()
                encoded_len = len(base64.b64encode(candidate_bytes))
                if encoded_len <= max_data_url_chars:
                    return ("image/jpeg", candidate_bytes)

            buffer = io.BytesIO()
            tiny = prepared.copy()
            tiny.thumbnail((192, 192))
            tiny.save(buffer, format="JPEG", quality=30, optimize=True)
            return ("image/jpeg", buffer.getvalue())
    except Exception:
        return None


def _agent_thread_from_dict(raw_thread: dict[str, object]) -> AgentThread:
    raw_messages = raw_thread.get("messages", [])
    messages = tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )
    raw_answers = raw_thread.get("answers", {})
    answers = {str(key): str(value) for key, value in dict(raw_answers).items()} if isinstance(raw_answers, dict) else {}
    raw_draft_data = raw_thread.get("draft_data", {})
    draft_data = {str(key): str(value) for key, value in dict(raw_draft_data).items()} if isinstance(raw_draft_data, dict) else {}
    return AgentThread(
        thread_id=str(raw_thread["thread_id"]),
        project_name=str(raw_thread["project_name"]),
        agent_name=str(raw_thread["agent_name"]),
        mode=str(raw_thread["mode"]),
        status=str(raw_thread["status"]),
        idea=str(raw_thread.get("idea", "")),
        planner_type=str(raw_thread.get("planner_type", "hybrid")),
        plan_mode=str(raw_thread.get("plan_mode", "")),
        current_question_index=int(raw_thread.get("current_question_index", 0)),
        current_field_id=str(raw_thread.get("current_field_id", "")),
        answers=answers,
        draft_title=str(raw_thread.get("draft_title", "")),
        draft=str(raw_thread.get("draft", "")),
        draft_data=draft_data,
        messages=messages,
        created_at=str(raw_thread.get("created_at", "")),
        updated_at=str(raw_thread.get("updated_at", "")),
    )


def list_agent_threads(
    project_name: str,
    *,
    agent_name: str | None = None,
    mode: str | None = None,
) -> list[AgentThread]:
    raw_threads = _load_agent_threads()
    project_threads = [thread for thread in raw_threads if thread.get("project_name") == project_name]
    if agent_name is not None:
        project_threads = [thread for thread in project_threads if str(thread.get("agent_name", "")) == agent_name]
    if mode is not None:
        project_threads = [thread for thread in project_threads if str(thread.get("mode", "")) == mode]
    return [
        _agent_thread_from_dict(thread)
        for thread in sorted(project_threads, key=lambda item: str(item.get("updated_at", "")), reverse=True)
    ]


def active_agent_thread(project_name: str, *, agent_name: str, mode: str) -> AgentThread | None:
    return next(
        (
            thread
            for thread in list_agent_threads(project_name, agent_name=agent_name, mode=mode)
            if thread.status == "active"
        ),
        None,
    )


PM_DISCOVERY_OPTIONAL_FIELDS = {"out_of_scope"}
PM_DISCOVERY_MIN_WORDS = {
    "target_user": 2,
    "problem": 5,
    "context": 4,
    "constraints": 3,
    "success": 4,
    "out_of_scope": 2,
}
PM_DISCOVERY_GENERIC_PATTERNS = (
    "not sure",
    "tbd",
    "n/a",
    "no idea",
    "idk",
    "same as above",
    "unsure",
)


def _pm_discovery_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def _pm_clean_snippet(text: str) -> str:
    return text.strip().rstrip(".!?")


def _pm_answer_sufficient(field_id: str, answer: str) -> bool:
    value = answer.strip()
    if not value:
        return False

    lowered = value.lower()
    if any(pattern in lowered for pattern in PM_DISCOVERY_GENERIC_PATTERNS):
        return False

    words = _pm_discovery_words(value)
    min_words = PM_DISCOVERY_MIN_WORDS.get(field_id, 3)
    if len(words) < min_words:
        return False

    if field_id == "target_user":
        bland_tokens = {"user", "users", "people", "person", "team", "teams", "customer", "customers"}
        return any(token.lower() not in bland_tokens for token in words)

    return True


def _pm_field_prompt(plan: DiscoveryPlan, field_id: str) -> str:
    for question in plan.questions:
        if question.id == field_id:
            return question.prompt
    raise ValueError(f"PM discovery field not found: {field_id}")


def _pm_first_unsatisfied_field(plan: DiscoveryPlan, answers: dict[str, str]) -> str | None:
    for question in plan.questions:
        if not _pm_answer_sufficient(question.id, answers.get(question.id, "")):
            return question.id
    return None


def _pm_known_context_snippet(answers: dict[str, str], field_id: str) -> str:
    if field_id == "problem":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"For {target_user}, "
    if field_id == "context":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if target_user and problem:
            return f"For {target_user}, around `{problem}`, "
    if field_id == "constraints":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"To solve `{problem}` cleanly, "
    if field_id == "success":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"For {target_user}, "
    if field_id == "out_of_scope":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"While we improve `{problem}`, "
    return ""


def _pm_follow_up_prompt(plan: DiscoveryPlan, field_id: str, answers: dict[str, str]) -> str:
    prefix = _pm_known_context_snippet(answers, field_id)
    follow_ups = {
        "target_user": "I still need a clearer first user. Who exactly should we optimise for first, and why are they the right starting point?",
        "problem": "I need the sharper user pain here. What concrete frustration or failure are we solving first?",
        "context": "I still need the operating context. Where in the current workflow does this problem show up most clearly?",
        "constraints": "I need the guardrails for the first slice. What should we deliberately keep narrow, local, or simple?",
        "success": "I still need the success test. After a short period of use, what result would make you say this first version is working?",
        "out_of_scope": "I still need the boundary. What tempting adjacent work should stay out of the first version?",
    }
    return f"{prefix}{follow_ups.get(field_id, _pm_field_prompt(plan, field_id))}".strip()


def _pm_next_prompt(plan: DiscoveryPlan, idea: str, answers: dict[str, str], field_id: str) -> str:
    if field_id in answers and answers.get(field_id, "").strip() and not _pm_answer_sufficient(field_id, answers.get(field_id, "")):
        return _pm_follow_up_prompt(plan, field_id, answers)

    if field_id == "problem":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"Got it. For {target_user}, what user problem are we trying to solve first?"
    if field_id == "context":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"Thanks. Where does `{problem}` show up in the current workflow, and why is it worth solving now?"
    if field_id == "constraints":
        return "What constraints or guardrails should shape the first version so we learn without overbuilding it?"
    if field_id == "success":
        return "If we get the first slice right, what outcome would make this feel successful after a short period of use?"
    if field_id == "out_of_scope":
        return "Before I draft, what should stay clearly out of scope for the first version?"
    return _pm_field_prompt(plan, field_id)


def _build_pm_discovery_intro(idea: str, plan: DiscoveryPlan) -> str:
    focus = idea.strip() or "this idea"
    opening = (
        f"Got it. I’m treating `{focus}` as a {plan.mode} discovery problem. "
        "I’ll track what we already know, only ask the next question that matters, and draft requirements when I have enough context."
    )
    first_field = _pm_first_unsatisfied_field(plan, {})
    if not first_field:
        return opening
    return f"{opening}\n\n{_pm_next_prompt(plan, idea, {}, first_field)}"


def _pm_draft_ready(answers: dict[str, str], plan: DiscoveryPlan) -> bool:
    for question in plan.questions:
        if question.id in PM_DISCOVERY_OPTIONAL_FIELDS:
            continue
        if not _pm_answer_sufficient(question.id, answers.get(question.id, "")):
            return False
    return True


def _generate_pm_thread_draft(raw_thread: dict[str, object]) -> str:
    return build_discovery_draft(
        str(raw_thread.get("project_name", "")),
        str(raw_thread.get("idea", "")),
        {str(key): str(value) for key, value in dict(raw_thread.get("answers", {})).items()},
    )


def _agent_thread_messages(raw_thread: dict[str, object]) -> tuple[AgentMessage, ...]:
    raw_messages = raw_thread.get("messages", [])
    return tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )


def _pm_thread_label(raw_thread: dict[str, object]) -> str:
    idea = str(raw_thread.get("idea", "")).strip()
    if not idea:
        return "PM discovery thread"
    trimmed = idea[:72].rstrip()
    return trimmed if len(idea) <= 72 else f"{trimmed}..."


def _create_or_replace_pm_thread_clarification(
    project_name: str,
    raw_thread: dict[str, object],
    *,
    summary: str,
    questions: list[str],
) -> PMClarification:
    raw_items = _load_pm_clarifications(project_name)
    source_thread_id = str(raw_thread.get("thread_id", ""))
    remaining = [
        item
        for item in raw_items
        if not (
            str(item.get("source_thread_id", "")) == source_thread_id
            and str(item.get("status", "")) == "OPEN"
        )
    ]
    _save_pm_clarifications(project_name, remaining)
    return save_pm_clarification(
        project_name,
        requirement_id="",
        requirement_title=_pm_thread_label(raw_thread),
        source_thread_id=source_thread_id,
        summary=summary,
        questions=questions,
    )


def _apply_live_pm_turn_to_thread(
    project_name: str,
    matching: dict[str, object],
    turn: LivePMTurn,
) -> None:
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))

    if turn.next_action == "draft_requirements":
        matching["draft_title"] = turn.draft_title.strip()
        matching["draft"] = turn.draft_requirement.strip()
        matching["status"] = "active"
        return

    if turn.next_action == "request_clarification":
        summary = turn.clarification_summary.strip() or "PM needs clarification before it can draft responsibly."
        questions = [question.strip() for question in turn.clarification_questions if question.strip()]
        if not questions:
            raise LivePMDiscoveryError("PM requested a clarification without any clarification questions.")
        _create_or_replace_pm_thread_clarification(
            project_name,
            matching,
            summary=summary,
            questions=questions,
        )
        matching["status"] = "blocked_clarification"
        return

    matching["status"] = "active"


def start_pm_requirement_discovery_thread(
    project_name: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(
        project_name,
        raw_threads,
        agent_name="PM",
        mode="Requirement Discovery",
    )
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    thread_messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_pm_turn(project_name, project_name, thread_messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "PM",
        "mode": "Requirement Discovery",
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": turn.draft_title.strip() if turn.next_action == "draft_requirements" else "",
        "draft": turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else "",
        "draft_data": {},
        "messages": [_agent_message("user", idea.strip(), attachments=attachments)],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    _apply_live_pm_turn_to_thread(project_name, raw_thread, turn)
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_pm_requirement_discovery_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")

    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    matching["status"] = "active"
    turn = _run_live_pm_turn(
        project_name,
        project_name,
        _agent_thread_messages(matching),
    )
    _apply_live_pm_turn_to_thread(project_name, matching, turn)
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_pm_requirement_discovery_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")

    turn = _run_live_pm_turn(
        project_name,
        project_name,
        _agent_thread_messages(matching),
        force_draft=True,
    )
    _apply_live_pm_turn_to_thread(project_name, matching, turn)
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def save_pm_requirement_thread_to_requirements(
    project_name: str,
    thread_id: str,
    requirement_title: str,
    *,
    status: str,
    priority: str,
    effort: str,
) -> RequirementRecord:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")

    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no draft requirements yet: {thread_id}")

    record = append_requirement(
        project_name,
        requirement_title,
        draft,
        status=status,
        priority=priority,
        effort=effort,
    )
    matching["status"] = "saved"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return record


def request_pm_requirement_thread_approval(
    project_name: str,
    thread_id: str,
    *,
    requirement_title: str,
    status: str,
    priority: str,
    effort: str,
) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no draft requirements yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="requirement_draft",
        source_thread_id=thread_id,
        source_agent_name="PM",
        title=requirement_title.strip(),
        summary="Approve this PM draft to save it into product/requirements.md.",
        payload={
            "requirement_title": requirement_title.strip(),
            "status": status.strip(),
            "priority": priority.strip(),
            "effort": effort.strip(),
            "draft": draft,
        },
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def archive_agent_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name and thread.get("thread_id") == thread_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    matching["status"] = "archived"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def list_approvals(project_name: str | None = None) -> list[ApprovalRequest]:
    raw_items = _load_approvals()
    approvals = [_approval_from_dict(item) for item in raw_items if isinstance(item, dict)]
    if project_name is not None:
        approvals = [item for item in approvals if item.project_name == project_name]
    return sorted(approvals, key=lambda item: item.created_at, reverse=True)


def active_approvals(project_name: str | None = None) -> list[ApprovalRequest]:
    return [item for item in list_approvals(project_name) if item.status == "OPEN"]


def _create_or_replace_thread_approval(
    *,
    project_name: str,
    approval_type: str,
    source_thread_id: str,
    source_agent_name: str,
    title: str,
    summary: str,
    payload: dict[str, str],
) -> ApprovalRequest:
    raw_items = _load_approvals()
    remaining = [
        item
        for item in raw_items
        if not (
            str(item.get("project_name", "")) == project_name
            and str(item.get("source_thread_id", "")) == source_thread_id
            and str(item.get("status", "")) == "OPEN"
        )
    ]
    created_at = datetime.now(timezone.utc).isoformat()
    approval = {
        "approval_id": str(uuid4()),
        "project_name": project_name,
        "approval_type": approval_type,
        "source_thread_id": source_thread_id,
        "source_agent_name": source_agent_name,
        "title": title.strip(),
        "summary": summary.strip(),
        "payload": payload,
        "status": "OPEN",
        "created_at": created_at,
        "resolved_at": "",
    }
    remaining.append(approval)
    _save_approvals(remaining)
    return _approval_from_dict(approval)


def _create_github_publication_approval(
    *,
    project_name: str,
    source_id: str,
    source_agent_name: str,
    draft: GitHubPublicationDraft,
) -> ApprovalRequest:
    review = draft.review
    if review is None or not review.allowed:
        findings = review.findings if review is not None else ()
        details = "; ".join(finding.detail for finding in findings) or "GitHub publication policy did not allow this payload."
        raise ValueError(details)

    payload = {
        "github_target": draft.target,
        "github_title": draft.title,
        "github_body": draft.body,
        "policy_status": "PASS",
        "policy_findings": "",
        "publication_state": "draft_approved_required",
        **{f"metadata_{key}": value for key, value in draft.metadata.items()},
    }
    return _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="github_publication",
        source_thread_id=f"github-publication:{source_id}",
        source_agent_name=source_agent_name,
        title=f"Approve GitHub {draft.target.replace('_', ' ')}",
        summary=(
            "Review this policy-checked GitHub publication draft. Approval publishes it to GitHub "
            "when GitHub publishing credentials are configured."
        ),
        payload=payload,
    )


def github_publication_from_approval(approval: ApprovalRequest) -> GitHubPublicationRequest:
    findings = tuple(
        item.strip()
        for item in approval.payload.get("policy_findings", "").split("\n")
        if item.strip()
    )
    return GitHubPublicationRequest(
        approval=approval,
        target=approval.payload.get("github_target", ""),
        title=approval.payload.get("github_title", approval.title),
        body=approval.payload.get("github_body", ""),
        policy_status=approval.payload.get("policy_status", "UNKNOWN"),
        findings=findings,
    )


def _project_git_root(project_name: str) -> Path:
    location = resolve_project(project_name)
    return location.workspace_path if location.is_external else REPO_ROOT


def _current_git_branch(project_name: str) -> str:
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=_project_git_root(project_name),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _git_status_paths(project_name: str) -> tuple[str, ...]:
    try:
        output = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=_project_git_root(project_name),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return ()
    paths: list[str] = []
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if len(path) >= 2 and path[0] == path[-1] == '"':
            path = path[1:-1]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1].strip()
        if path:
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _git_deleted_paths(project_name: str) -> tuple[str, ...]:
    try:
        output = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=_project_git_root(project_name),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return ()
    paths: list[str] = []
    for line in output.splitlines():
        if len(line) < 4 or "D" not in line[:2]:
            continue
        path = line[3:].strip()
        if len(path) >= 2 and path[0] == path[-1] == '"':
            path = path[1:-1]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1].strip()
        if path:
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _release_path_is_public(path: str) -> bool:
    normalized = path.strip().strip('"').lstrip("./")
    if not normalized:
        return False
    blocked_prefixes = (
        "private/",
    )
    blocked_fragments = (
        "/private/",
        "/data/agent_uploads/",
        "/data/implementation_logs/",
        "/.next/",
        "/node_modules/",
    )
    blocked_suffixes = (".env", ".pem", ".key")
    if normalized.startswith(blocked_prefixes):
        return False
    if re.match(r"projects/[^/]+/data(?:/|$)", normalized):
        return False
    if any(fragment in normalized for fragment in blocked_fragments):
        return False
    if normalized.startswith(".next/") or normalized.startswith("node_modules/"):
        return False
    if normalized == "data" or normalized.startswith("data/"):
        return False
    if normalized.endswith(blocked_suffixes):
        return False
    if re.search(r"projects/[^/]+/data/(?:agent_traces|agent_threads|approvals|pm_clarifications|experience_findings|implementation_runs)\.jsonl?$", normalized):
        return False
    return True


def _release_git_change_plan(project_name: str) -> GitChangePlan:
    location = resolve_project(project_name)
    project_prefix = "" if location.is_external else f"projects/{location.name}/"
    required_path = f"{project_prefix}product/requirements.md"
    repo_wide_release = not location.is_external and location.name == "os-control-panel"
    candidates = [
        required_path,
        *(
            path
            for path in _git_status_paths(project_name)
            if repo_wide_release
            or not project_prefix
            or path.strip().strip('"').startswith(project_prefix)
        ),
    ]
    included: list[str] = []
    excluded: list[str] = []
    deleted_paths = set(_git_deleted_paths(project_name))
    for path in dict.fromkeys(candidates):
        if path in deleted_paths or _release_path_is_public(path):
            included.append(path)
        else:
            excluded.append(path)
    return GitChangePlan(
        included_paths=tuple(included),
        excluded_paths=tuple(excluded),
        branch=_current_git_branch(project_name),
    )


def _web_app_release_readiness(project_name: str) -> tuple[str, ...]:
    project_dir = _project_path(project_name)
    checks: list[str] = []
    package_path = project_dir / "package.json"
    if package_path.exists():
        checks.append("PASS package.json exists")
        try:
            package_payload = json.loads(package_path.read_text())
        except json.JSONDecodeError:
            checks.append("FAIL package.json is not valid JSON")
            package_payload = {}
        scripts = package_payload.get("scripts", {}) if isinstance(package_payload, dict) else {}
        if isinstance(scripts, dict) and scripts.get("dev"):
            checks.append("PASS package.json defines a dev script")
        else:
            checks.append("FAIL package.json should define a dev script for local preview")
        if isinstance(scripts, dict) and scripts.get("build"):
            checks.append("PASS package.json defines a build script")
        else:
            checks.append("FAIL package.json should define a build script for Vercel release readiness")
    else:
        checks.append("FAIL package.json is required for web app projects")

    if (project_dir / "app" / "page.tsx").exists() or (project_dir / "pages" / "index.tsx").exists():
        checks.append("PASS Next.js route entry exists")
    else:
        checks.append("FAIL add a Next.js route entry such as app/page.tsx")

    if (project_dir / "components.json").exists():
        checks.append("PASS shadcn/ui registry config is present")
    else:
        checks.append("INFO shadcn/ui is not configured yet; use it when common polished components would reduce UI risk")

    if (project_dir / "vercel.json").exists():
        checks.append("PASS vercel.json is present")
    else:
        checks.append("INFO vercel.json is optional; add it when routes, functions, cron, or build settings need explicit config")

    env_example = project_dir / ".env.example"
    if env_example.exists():
        checks.append("PASS .env.example documents runtime variables")
    else:
        checks.append("INFO add .env.example before relying on Vercel environment variables")

    evidence = web_app_browser_verification_evidence(project_name)
    if not evidence:
        checks.append("FAIL run `tools/verify_web_app.py` before approving Vercel release delivery")
    elif str(evidence.get("status", "")).upper() == "PASS":
        verified_at = str(evidence.get("verified_at", "") or "unknown time")
        checks.append(f"PASS Playwright browser verification passed at {verified_at}")
    else:
        failures = evidence.get("blocking_failures", [])
        detail = "; ".join(str(item) for item in failures) if isinstance(failures, list) else str(failures)
        checks.append(f"FAIL Playwright browser verification did not pass: {detail or 'no detail recorded'}")

    checks.append("ACTION verify Vercel preview deployment URL after GitHub push")
    return tuple(checks)


def _streamlit_release_readiness(project_name: str) -> tuple[str, ...]:
    project_dir = _project_path(project_name)
    checks: list[str] = []
    if (project_dir / "src" / "app.py").exists():
        checks.append("PASS Streamlit entrypoint exists at src/app.py")
    else:
        checks.append("FAIL Streamlit projects should keep src/app.py as the hosted entrypoint")

    if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
        checks.append("PASS Python dependency manifest exists")
    else:
        checks.append("INFO add requirements.txt or pyproject.toml before relying on Railway deploys")

    if (project_dir / "railway.toml").exists() or (project_dir / "Dockerfile").exists():
        checks.append("PASS Railway deployment config or Dockerfile is present")
    else:
        checks.append("INFO add railway.toml or Dockerfile when the Railway service needs explicit start/build settings")

    if (project_dir / ".env.example").exists():
        checks.append("PASS .env.example documents hosted runtime variables")
    else:
        checks.append("INFO add .env.example before relying on Railway environment variables")

    checks.append("ACTION verify Railway deployment or redeploy after GitHub push")
    return tuple(checks)


def project_release_readiness(
    project_name: str,
    ui_runtime: str,
    requirement_id: str = "",
) -> tuple[str, ...]:
    profile = project_runtime_profile(ui_runtime)
    if profile.runtime == "web_app":
        checks = list(_web_app_release_readiness(project_name))
        figma_config = load_project_figma_config(project_name)
        if figma_config.mode == "code_first":
            checks.append("INFO code-first design mode is active; no Figma reference is required")
        elif requirement_id:
            reference = requirement_figma_reference(project_name, requirement_id)
            if reference is None and figma_config.mode == "figma_referenced":
                checks.append(
                    f"INFO {requirement_id} has no Figma mapping and follows the code-first path within this Figma-capable project"
                )
            elif reference is None or not reference.frame_url:
                checks.append(f"FAIL {requirement_id} has no Figma frame reference")
            elif reference.approval_status != "approved":
                checks.append(f"FAIL {requirement_id} Figma frame reference is not approved")
            else:
                label = reference.frame_name or reference.frame_url
                checks.append(f"PASS {requirement_id} uses approved Figma frame: {label}")
                evidence = load_figma_design_evidence(project_name, requirement_id)
                if figma_evidence_matches_reference(project_name, requirement_id):
                    synced_at = str(evidence.get("synced_at", "") or "unknown time")
                    checks.append(f"PASS Figma connector evidence matches the approved frame; synced at {synced_at}")
                else:
                    checks.append(
                        f"FAIL sync Figma connector evidence for {requirement_id}; the approved frame must have matching metadata and a local screenshot"
                    )
        else:
            checks.append("INFO Figma design mode is active; requirement mapping is checked during release delivery")
        return tuple(checks)
    if profile.runtime == "streamlit":
        return _streamlit_release_readiness(project_name)
    return tuple(f"CHECK {item}" for item in profile.qa_release_checks)


def web_app_browser_verification_path(project_name: str) -> Path:
    return _project_path(project_name) / "product" / "browser-verification.json"


def web_app_browser_verification_evidence(project_name: str) -> dict[str, object]:
    evidence_path = web_app_browser_verification_path(project_name)
    if not evidence_path.exists():
        return {}
    try:
        parsed = json.loads(evidence_path.read_text())
    except json.JSONDecodeError:
        return {"status": "FAIL", "blocking_failures": ["browser verification evidence is not valid JSON"]}
    return parsed if isinstance(parsed, dict) else {"status": "FAIL", "blocking_failures": ["browser verification evidence is not an object"]}


def _web_app_browser_verification_passed(project_name: str) -> bool:
    evidence = web_app_browser_verification_evidence(project_name)
    return str(evidence.get("status", "")).upper() == "PASS"


def _task_is_web_app_release_validation_task(task: TaskBlock) -> bool:
    title = task.title.strip().lower()
    task_type = task.task_type.strip().lower()
    body = task.body.strip().lower()
    if "validation" not in task_type and not any(
        phrase in title for phrase in ("validate", "verification", "release readiness", "browser")
    ):
        return False
    verification_signals = (
        "playwright",
        "browser verification",
        "verify_web_app.py",
        "rendered",
        "release readiness",
        "responsive interaction states",
        "vercel release",
    )
    return any(signal in body or signal in title for signal in verification_signals)


def reconcile_web_app_requirement_after_verification(project_name: str, requirement_id: str) -> int:
    if not requirement_id.strip() or not _web_app_browser_verification_passed(project_name):
        return 0

    document = load_task_document(project_name)
    updated_tasks: list[TaskBlock] = []
    updated_count = 0
    for task in document.tasks:
        if (
            requirement_id in task.requirements
            and task.status != "DONE"
            and _task_is_web_app_release_validation_task(task)
        ):
            updated_tasks.append(
                TaskBlock(
                    number=task.number,
                    title=task.title,
                    task_type=task.task_type,
                    status="DONE",
                    requirements=task.requirements,
                    body=task.body,
                )
            )
            updated_count += 1
            continue
        updated_tasks.append(task)

    if updated_count:
        save_task_document(project_name, TaskDocument(intro=document.intro, tasks=tuple(updated_tasks)))
    return updated_count


def _site_import_manifest_candidates(project_name: str) -> tuple[Path, ...]:
    _migrate_legacy_project_runtime_data(project_name)
    candidates: list[Path] = []
    user_runtime = _project_runtime_user_data_path(project_name)
    if user_runtime is not None:
        candidates.append(user_runtime / "site-imports")
    candidates.append(_project_runtime_data_path(project_name) / "site-imports")
    return tuple(candidates)


def _latest_site_import_manifest(project_name: str) -> Path | None:
    manifests: list[Path] = []
    for root in _site_import_manifest_candidates(project_name):
        if not root.exists():
            continue
        manifests.extend(path for path in root.glob("*/manifest.json") if path.is_file())
    if not manifests:
        return None
    return max(manifests, key=lambda path: path.stat().st_mtime)


def _site_import_context_summary(project_name: str) -> str:
    manifest_path = _latest_site_import_manifest(project_name)
    if manifest_path is None:
        return ""
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    if not isinstance(payload, dict):
        return ""
    crawl_payload: dict[str, object] = {}
    crawl_path = manifest_path.parent / "crawl.json"
    if crawl_path.exists():
        try:
            parsed_crawl = json.loads(crawl_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            parsed_crawl = {}
        if isinstance(parsed_crawl, dict):
            crawl_payload = parsed_crawl

    requested_url = str(payload.get("requested_url", "")).strip()
    site_host = str(payload.get("site_host", "")).strip()
    saved_count = int(payload.get("saved_count", 0) or 0)
    counts = payload.get("counts", {})
    if not isinstance(counts, dict):
        counts = {}
    grouped_assets = payload.get("grouped_assets", {})
    if not isinstance(grouped_assets, dict):
        grouped_assets = {}

    summary_lines = [
        "Website import context is available from a prior bounded site extraction.",
        f"Manifest path: {manifest_path}",
    ]
    if requested_url:
        summary_lines.append(f"Source website: {requested_url}")
    if site_host:
        summary_lines.append(f"Site host: {site_host}")
    summary_lines.append(f"Downloaded assets: {saved_count}")
    if counts:
        counts_summary = ", ".join(f"{key}={int(value or 0)}" for key, value in counts.items())
        summary_lines.append(f"Classified asset counts: {counts_summary}")

    pages = crawl_payload.get("pages", [])
    if isinstance(pages, list) and pages:
        page = pages[0] if isinstance(pages[0], dict) else {}
        if isinstance(page, dict):
            title = str(page.get("title", "")).strip()
            if title:
                summary_lines.append(f"Primary page title: {title}")
            nav = page.get("navigation_labels", [])
            if isinstance(nav, list) and nav:
                summary_lines.append(
                    "Navigation labels: " + ", ".join(str(item).strip() for item in nav[:8] if str(item).strip())
                )
            blocks = page.get("content_blocks", [])
            if isinstance(blocks, list):
                snippets = [str(item).strip() for item in blocks[:3] if str(item).strip()]
                if snippets:
                    summary_lines.append("Representative source copy:")
                    summary_lines.extend(f"- {snippet}" for snippet in snippets)

    sample_lines: list[str] = []
    for role in ("logo", "hero", "gallery", "people", "icon"):
        items = grouped_assets.get(role, [])
        if not isinstance(items, list) or not items:
            continue
        first = items[0]
        if not isinstance(first, dict):
            continue
        source_url = str(first.get("source_url", "")).strip()
        saved_path = str(first.get("saved_path", "")).strip()
        if source_url or saved_path:
            sample_lines.append(f"- {role}: {saved_path or '<missing path>'} ({source_url or 'no source url'})")
    if not sample_lines:
        saved_images = payload.get("saved_images", [])
        if isinstance(saved_images, list):
            fallback_items = [item for item in saved_images[:5] if isinstance(item, dict)]
            for item in fallback_items:
                source_url = str(item.get("source_url", "")).strip()
                saved_path = str(item.get("saved_path", "")).strip()
                if source_url or saved_path:
                    sample_lines.append(f"- asset: {saved_path or '<missing path>'} ({source_url or 'no source url'})")
    if sample_lines:
        summary_lines.append("Representative local assets:")
        summary_lines.extend(sample_lines[:5])

    summary_lines.append(
        "When implementing website replication or improvement work, prefer these downloaded local assets over hotlinking the source site, and keep any transformed or reused assets traceable."
    )
    summary_lines.append(
        "If the user asked to replicate or improve the referenced site, do not substitute placeholder copy or abstract illustrations when grounded source copy and assets are available locally."
    )
    return "\n".join(summary_lines)


def latest_site_import_summary(project_name: str) -> dict[str, object]:
    manifest_path = _latest_site_import_manifest(project_name)
    if manifest_path is None:
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, dict):
        return {}
    payload = dict(payload)
    payload["manifest_path"] = str(manifest_path)
    crawl_path = manifest_path.parent / "crawl.json"
    if crawl_path.exists():
        try:
            crawl_payload = json.loads(crawl_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            crawl_payload = {}
        if isinstance(crawl_payload, dict):
            payload["crawl_path"] = str(crawl_path)
            payload["pages"] = crawl_payload.get("pages", [])
            payload["crawl_failures"] = crawl_payload.get("failures", [])
    return payload


def _release_commit_message(record: RequirementRecord) -> str:
    return f"Complete {record.id}: {record.title}".strip()


def _draft_with_project_repository(project_name: str, draft: GitHubPublicationDraft) -> GitHubPublicationDraft:
    location = resolve_project(project_name)
    metadata = dict(draft.metadata)
    if location.repository:
        metadata["repository"] = location.repository
    metadata["branch"] = _current_git_branch(project_name)
    return replace(draft, metadata=metadata)


def request_release_delivery_approval(project_name: str, record: RequirementRecord) -> ApprovalRequest:
    delivery_record = RequirementRecord(
        id=record.id,
        title=record.title,
        status="DONE",
        priority=record.priority,
        effort=record.effort,
        description=record.description,
        ui_runtime=record.ui_runtime,
    )
    issue_draft = _draft_with_project_repository(project_name, draft_issue_from_requirement(
        project_name=project_name,
        requirement_id=delivery_record.id,
        title=delivery_record.title,
        status=delivery_record.status,
        priority=delivery_record.priority,
        effort=delivery_record.effort,
        description=delivery_record.description,
    ))
    review = issue_draft.review
    if review is None or not review.allowed:
        findings = review.findings if review is not None else ()
        details = "; ".join(finding.detail for finding in findings) or "Release delivery policy did not allow this payload."
        raise ValueError(details)

    latest_run = latest_requirement_implementation(project_name, delivery_record.id)
    latest_review = latest_quality_review(project_name, mode="deterministic")
    change_plan = _release_git_change_plan(project_name)
    release_runtime = effective_requirement_ui_runtime(project_name, delivery_record)
    release_profile = project_runtime_profile(release_runtime)
    if release_profile.runtime == "web_app" and not _web_app_browser_verification_passed(project_name):
        raise ValueError(
            "Web app release delivery requires passing Playwright browser verification before Vercel approval. "
            f"Run `.venv/bin/python tools/verify_web_app.py {project_name}` and try again."
        )
    figma_config = load_project_figma_config(project_name)
    figma_reference = requirement_figma_reference(project_name, delivery_record.id)
    figma_required = figma_config.mode == "figma_managed" or figma_reference is not None
    if release_profile.runtime == "web_app" and figma_required:
        if figma_reference is None or not figma_reference.frame_url:
            raise ValueError(
                f"{delivery_record.id} requires a Figma frame mapping before release delivery because "
                f"the project design mode is {figma_config.mode}."
            )
        if figma_reference.approval_status != "approved":
            raise ValueError(f"Approve the Figma design reference for {delivery_record.id} before release delivery.")
        if not figma_evidence_matches_reference(project_name, delivery_record.id):
            raise ValueError(
                f"Sync matching Figma connector evidence for {delivery_record.id} before release delivery."
            )
    figma_evidence = load_figma_design_evidence(project_name, delivery_record.id)
    openai_decision = requirement_openai_runtime_decision(project_name, delivery_record)
    payload = {
        "requirement_id": delivery_record.id,
        "requirement_title": delivery_record.title,
        "requirement_status": delivery_record.status,
        "requirement_priority": delivery_record.priority,
        "requirement_effort": delivery_record.effort,
        "requirement_ui_runtime": release_runtime,
        "project_type": release_profile.project_type,
        "deployment_provider": release_profile.default_deployment_provider,
        "release_expectation": release_profile.release_expectation,
        "capability_pack": "\n".join(release_profile.capability_pack),
        "architecture_guidance": "\n".join(release_profile.architecture_guidance),
        "openai_runtime_required": "YES" if openai_decision.required else "NO",
        "openai_surface": openai_decision.surface,
        "openai_capabilities": "\n".join(openai_decision.capabilities),
        "openai_credentials": "\n".join(openai_decision.credentials),
        "openai_rationale": openai_decision.rationale,
        "openai_confidence": openai_decision.confidence,
        "openai_review_reasons": "\n".join(openai_decision.review_reasons),
        "release_readiness": "\n".join(
            project_release_readiness(project_name, release_runtime, delivery_record.id)
        ),
        "design_mode": figma_config.mode,
        "figma_file_url": figma_config.file_url,
        "figma_file_name": figma_config.file_name,
        "figma_frame_url": figma_reference.frame_url if figma_reference is not None else "",
        "figma_frame_name": figma_reference.frame_name if figma_reference is not None else "",
        "figma_approval_status": figma_reference.approval_status if figma_reference is not None else "",
        "figma_evidence_status": str(figma_evidence.get("status", "")),
        "figma_evidence_synced_at": str(figma_evidence.get("synced_at", "")),
        "figma_design_summary": str(figma_evidence.get("design_summary", "")),
        "requirement_description": delivery_record.description,
        "github_target": issue_draft.target,
        "github_repository": resolve_project(project_name).repository,
        "github_title": issue_draft.title,
        "github_body": issue_draft.body,
        "policy_status": "PASS",
        "policy_findings": "",
        "implementation_run_id": latest_run.run_id if latest_run is not None else "",
        "implementation_status": latest_run.status if latest_run is not None else "NOT_RECORDED",
        "implementation_summary": latest_run.summary if latest_run is not None else "",
        "quality_status": latest_review.status if latest_review is not None else "NOT_RECORDED",
        "quality_summary": latest_review.summary if latest_review is not None else "",
        "git_branch": change_plan.branch,
        "git_commit_message": _release_commit_message(delivery_record),
        "git_included_paths": "\n".join(change_plan.included_paths),
        "git_excluded_paths": "\n".join(change_plan.excluded_paths),
        "release_state": "approval_required",
    }
    return _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="release_delivery",
        source_thread_id=f"release-delivery:{delivery_record.id}",
        source_agent_name="Delivery",
        title=f"Approve release delivery for {delivery_record.id}",
        summary=(
            "Review this release bundle before marking the requirement DONE, publishing the GitHub issue, "
            "committing approved files, and pushing the branch."
        ),
        payload=payload,
    )


def request_github_issue_publication(project_name: str, requirement_id: str) -> ApprovalRequest:
    document = load_requirement_document(project_name)
    records = [*document.active_requirements, *document.backlog_requirements]
    record = next((item for item in records if item.id == requirement_id), None)
    if record is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    draft = _draft_with_project_repository(project_name, draft_issue_from_requirement(
        project_name=project_name,
        requirement_id=record.id,
        title=record.title,
        status=record.status,
        priority=record.priority,
        effort=record.effort,
        description=record.description,
    ))
    return _create_github_publication_approval(
        project_name=project_name,
        source_id=f"issue:{record.id}",
        source_agent_name="Orchestrator",
        draft=draft,
    )


def request_github_pr_publication(project_name: str, run_id: str) -> ApprovalRequest:
    run = next((item for item in list_implementation_runs(project_name) if item.run_id == run_id), None)
    if run is None:
        raise ValueError(f"Implementation run not found: {run_id}")
    draft = _draft_with_project_repository(project_name, draft_pr_description(
        project_name=project_name,
        requirement_id=run.requirement_id,
        requirement_title=run.requirement_title,
        run_id=run.run_id,
        run_status=run.status,
        summary=run.summary,
    ))
    return _create_github_publication_approval(
        project_name=project_name,
        source_id=f"pr:{run.run_id}",
        source_agent_name="Engineer",
        draft=draft,
    )


def request_github_eval_publication(project_name: str) -> ApprovalRequest:
    review = latest_quality_review(project_name, mode="deterministic")
    if review is None:
        raise ValueError("No deterministic quality review is available for GitHub publication.")
    draft = _draft_with_project_repository(project_name, draft_eval_summary(
        project_name=project_name,
        status=review.status,
        summary=review.summary,
        failures=review.failures,
        runner_path=review.runner_path,
    ))
    return _create_github_publication_approval(
        project_name=project_name,
        source_id=f"eval:{review.review_id}",
        source_agent_name="QA",
        draft=draft,
    )


def standalone_workspaces_root() -> Path:
    configured = os.getenv("AI_BUILDER_OS_WORKSPACES_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "Projects" / "ai-builder-os").resolve()


def request_standalone_repository_creation(
    *,
    project_name: str,
    display_name: str,
    initial_requirement_title: str,
    initial_requirement: str,
    ui_runtime: str,
    repository: str,
    visibility: str = "private",
    ownership: str = "self",
    workspace_parent: Path | None = None,
) -> ApprovalRequest:
    plan = plan_standalone_repository(
        project_name=project_name,
        workspace_parent=workspace_parent or standalone_workspaces_root(),
        repository=repository,
        visibility=visibility,
        ownership=ownership,
    )
    payload = {
        **{key: str(value) for key, value in plan.to_dict().items() if key != "external_side_effects"},
        "external_side_effects": "\n".join(plan.external_side_effects),
        "display_name": display_name.strip(),
        "initial_requirement_title": initial_requirement_title.strip(),
        "initial_requirement": initial_requirement.strip(),
        "ui_runtime": normalize_ui_runtime(ui_runtime),
        "repository_action_state": "approval_required",
    }
    return _create_or_replace_thread_approval(
        project_name="os-control-panel",
        approval_type="repository_action",
        source_thread_id=f"repository-action:create:{plan.project_id}",
        source_agent_name="Project Registry",
        title=f"Create {plan.visibility} repository for {display_name.strip() or plan.project_name}",
        summary=(
            "Review the standalone workspace, GitHub owner, visibility, ownership and external side effects. "
            "Approval scaffolds the project, creates the GitHub repository, pushes main and registers it locally."
        ),
        payload=payload,
    )


def request_repository_attachment(
    *,
    workspace_path: Path,
    repository: str,
    display_name: str,
    visibility: str = "private",
    ownership: str = "self",
) -> ApprovalRequest:
    plan = plan_attached_repository(
        workspace_path=workspace_path,
        repository=repository,
        visibility=visibility,
        ownership=ownership,
    )
    payload = {
        **{key: str(value) for key, value in plan.to_dict().items() if key != "external_side_effects"},
        "external_side_effects": "\n".join(plan.external_side_effects),
        "display_name": display_name.strip(),
        "repository_action_state": "approval_required",
    }
    return _create_or_replace_thread_approval(
        project_name="os-control-panel",
        approval_type="repository_action",
        source_thread_id=f"repository-action:attach:{plan.project_id}",
        source_agent_name="Project Registry",
        title=f"Attach repository for {display_name.strip() or plan.project_name}",
        summary="Review the repository identity, privacy, ownership and local workspace before registering it.",
        payload=payload,
    )


def _repository_plan_from_payload(payload: dict[str, str]) -> RepositoryActionPlan:
    return RepositoryActionPlan(
        action=payload.get("action", ""),
        project_id=payload.get("project_id", ""),
        project_name=payload.get("project_name", ""),
        workspace_path=payload.get("workspace_path", ""),
        repository=payload.get("repository", ""),
        visibility=payload.get("visibility", "private"),
        ownership=payload.get("ownership", "self"),
        default_branch=payload.get("default_branch", "main"),
        external_side_effects=tuple(
            item for item in payload.get("external_side_effects", "").splitlines() if item.strip()
        ),
    )


def _approve_repository_action(approval: ApprovalRequest) -> dict[str, str]:
    plan = _repository_plan_from_payload(approval.payload)
    if plan.action == "create_standalone_repository":
        root = Path(plan.workspace_path)
        location = load_project_manifest(root) if root.exists() else None
        if location is None:
            location = scaffold_standalone_repository(
                plan,
                display_name=approval.payload.get("display_name", plan.project_name),
                initial_requirement_title=approval.payload.get("initial_requirement_title", "Initial requirement"),
                initial_requirement=approval.payload.get("initial_requirement", ""),
                ui_runtime=approval.payload.get("ui_runtime", DEFAULT_UI_RUNTIME),
            )
        else:
            register_project(location, write_manifest=False)
        published = publish_standalone_repository(plan, approved=True)
        return {
            "outcome_kind": "standalone_repository_created",
            "outcome_title": location.display_name,
            "outcome_reference_id": location.project_id,
            "outcome_detail": f"Created and registered {published['repository']} as a {published['visibility']} repository.",
            "repository_action_state": "published",
            "repository_url": published["url"],
        }
    if plan.action == "attach_repository":
        location = attach_repository(
            plan,
            display_name=approval.payload.get("display_name", plan.project_name),
        )
        return {
            "outcome_kind": "repository_attached",
            "outcome_title": location.display_name,
            "outcome_reference_id": location.project_id,
            "outcome_detail": "Validated and registered the existing repository workspace.",
            "repository_action_state": "registered",
        }
    raise ValueError(f"Unsupported repository action: {plan.action}")


def _run_git_command(project_name: str, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=_project_git_root(project_name),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(detail or f"git {' '.join(args)} failed") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not run git: {exc}") from exc
    return result.stdout.strip()


def _staged_git_paths(project_name: str) -> tuple[str, ...]:
    output = _run_git_command(project_name, ["diff", "--cached", "--name-only"])
    paths = []
    for line in output.splitlines():
        path = line.strip().strip('"')
        if path:
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _commit_and_push_release(project_name: str, payload: dict[str, str]) -> dict[str, str]:
    deleted_paths = set(_git_deleted_paths(project_name))
    included_paths = tuple(
        path.strip()
        for path in payload.get("git_included_paths", "").splitlines()
        if path.strip() and (path.strip() in deleted_paths or _release_path_is_public(path.strip()))
    )
    if not included_paths:
        return {
            "git_commit_sha": "",
            "git_push_target": "",
            "git_delivery_detail": "No public files were selected for commit.",
        }

    staged_paths = _staged_git_paths(project_name)
    preexisting_staged = tuple(path for path in staged_paths if path not in included_paths)
    if preexisting_staged:
        preview = "\n".join(preexisting_staged[:12])
        remainder = len(preexisting_staged) - min(len(preexisting_staged), 12)
        if remainder > 0:
            preview += f"\n... and {remainder} more"
        raise RuntimeError(
            "Release delivery only works from a clean staged index right now. "
            "Unstage unrelated files before approving release delivery again.\n\n"
            f"Currently staged outside the approved bundle:\n{preview}"
        )

    git_root = _project_git_root(project_name)
    deleted_included = tuple(
        path
        for path in included_paths
        if path in deleted_paths and path not in staged_paths
    )
    existing_included = tuple(
        path for path in included_paths if (git_root / path).exists()
    )
    if existing_included:
        _run_git_command(project_name, ["add", "--", *existing_included])
    if deleted_included:
        _run_git_command(project_name, ["add", "-u", "--", *deleted_included])
    try:
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=_project_git_root(project_name),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return {
            "git_commit_sha": "",
            "git_push_target": "",
            "git_delivery_detail": "No staged changes were available after applying the approved file list.",
        }
    except subprocess.CalledProcessError as exc:
        if exc.returncode != 1:
            detail = (exc.stderr or exc.stdout or "").strip()
            raise RuntimeError(detail or "Could not inspect staged git changes.") from exc

    message = payload.get("git_commit_message", "").strip() or "Complete approved requirement delivery"
    _run_git_command(project_name, ["commit", "-m", message])
    commit_sha = _run_git_command(project_name, ["rev-parse", "HEAD"])
    branch = payload.get("git_branch", "").strip() or _current_git_branch(project_name)
    if not branch:
        raise RuntimeError("Could not determine the current git branch for release delivery.")
    _run_git_command(project_name, ["push", "origin", branch])
    return {
        "git_commit_sha": commit_sha,
        "git_push_target": f"origin/{branch}",
        "git_delivery_detail": f"Committed and pushed approved files to origin/{branch}.",
    }


def _vercel_project_env_key(project_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", project_name).strip("_").upper()
    return f"AI_BUILDER_OS_VERCEL_PROJECT_{normalized}"


def _configured_vercel_token() -> str:
    return (
        os.environ.get("AI_BUILDER_OS_VERCEL_TOKEN")
        or os.environ.get("VERCEL_TOKEN")
        or ""
    ).strip()


def _configured_vercel_team_id() -> str:
    return (
        os.environ.get("AI_BUILDER_OS_VERCEL_TEAM_ID")
        or os.environ.get("VERCEL_TEAM_ID")
        or ""
    ).strip()


def _configured_vercel_project(project_name: str) -> str:
    return (
        os.environ.get(_vercel_project_env_key(project_name))
        or os.environ.get("AI_BUILDER_OS_VERCEL_PROJECT_ID")
        or os.environ.get("VERCEL_PROJECT_ID")
        or project_name
    ).strip()


def _vercel_api_get(path: str, *, token: str, params: dict[str, str]) -> dict[str, object]:
    query = urlencode({key: value for key, value in params.items() if value})
    request = Request(
        f"https://api.vercel.com{path}?{query}" if query else f"https://api.vercel.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ai-builder-os",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Vercel API returned {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Vercel API request failed: {exc.reason}") from exc
    parsed = json.loads(raw) if raw else {}
    if not isinstance(parsed, dict):
        raise RuntimeError("Vercel API returned an unexpected response.")
    return parsed


def lookup_vercel_preview_deployment(
    project_name: str,
    *,
    commit_sha: str,
    branch: str,
) -> VercelDeploymentLookup:
    if not commit_sha:
        return VercelDeploymentLookup(status="skipped", detail="No commit SHA was available for Vercel lookup.")
    token = _configured_vercel_token()
    if not token:
        return VercelDeploymentLookup(
            status="not_configured",
            detail="Set AI_BUILDER_OS_VERCEL_TOKEN or VERCEL_TOKEN to look up Vercel preview deployments.",
        )

    params = {
        "projectId": _configured_vercel_project(project_name),
        "sha": commit_sha,
        "branch": branch,
        "limit": "5",
        "teamId": _configured_vercel_team_id(),
    }
    try:
        payload = _vercel_api_get("/v7/deployments", token=token, params=params)
    except RuntimeError as exc:
        return VercelDeploymentLookup(status="error", detail=str(exc))

    raw_deployments = payload.get("deployments", [])
    deployments = raw_deployments if isinstance(raw_deployments, list) else []
    if not deployments:
        return VercelDeploymentLookup(
            status="not_found",
            detail=(
                "No Vercel deployment matched the pushed commit yet. "
                "The GitHub integration may still be queued or the Vercel project mapping may need configuration."
            ),
        )

    deployment = next((item for item in deployments if isinstance(item, dict) and item.get("url")), None)
    if deployment is None:
        deployment = next((item for item in deployments if isinstance(item, dict)), {})
    if not isinstance(deployment, dict):
        return VercelDeploymentLookup(status="error", detail="Vercel returned an unreadable deployment record.")

    raw_url = str(deployment.get("url", "") or "")
    url = raw_url if raw_url.startswith("http") else (f"https://{raw_url}" if raw_url else "")
    ready_state = str(deployment.get("readyState", "") or deployment.get("state", "") or "")
    return VercelDeploymentLookup(
        status="found" if url else "found_without_url",
        url=url,
        deployment_id=str(deployment.get("uid", "") or deployment.get("id", "") or ""),
        ready_state=ready_state,
        inspector_url=str(deployment.get("inspectorUrl", "") or ""),
        detail=f"Matched Vercel deployment for branch `{branch}` and commit `{commit_sha[:12]}`.",
    )


def _vercel_release_payload(project_name: str, payload: dict[str, str], git_result: dict[str, str]) -> dict[str, str]:
    if payload.get("project_type") != "web_app":
        return {}
    lookup = lookup_vercel_preview_deployment(
        project_name,
        commit_sha=git_result.get("git_commit_sha", ""),
        branch=payload.get("git_branch", ""),
    )
    return {
        "vercel_lookup_status": lookup.status,
        "vercel_preview_url": lookup.url,
        "vercel_deployment_id": lookup.deployment_id,
        "vercel_ready_state": lookup.ready_state,
        "vercel_inspector_url": lookup.inspector_url,
        "vercel_lookup_detail": lookup.detail,
    }


def _approve_release_delivery(project_name: str, approval: ApprovalRequest) -> dict[str, str]:
    if approval.payload.get("project_type") == "web_app" and not _web_app_browser_verification_passed(project_name):
        raise RuntimeError(
            "Web app release delivery requires passing Playwright browser verification before Vercel approval. "
            f"Run `.venv/bin/python tools/verify_web_app.py {project_name}` and approve again."
        )
    record = RequirementRecord(
        id=approval.payload.get("requirement_id", ""),
        title=approval.payload.get("requirement_title", approval.title),
        status="DONE",
        priority=approval.payload.get("requirement_priority", ""),
        effort=approval.payload.get("requirement_effort", ""),
        description=approval.payload.get("requirement_description", ""),
        ui_runtime=approval.payload.get("requirement_ui_runtime", ""),
    )
    if not record.id:
        raise RuntimeError("Release approval is missing a requirement id.")
    _replace_requirement_record(project_name, record)
    git_result = _commit_and_push_release(project_name, approval.payload)
    vercel_result = _vercel_release_payload(project_name, approval.payload, git_result)
    publish_result = publish_github_publication(
        {
            "github_target": approval.payload.get("github_target", "issue"),
            "github_title": approval.payload.get("github_title", approval.title),
            "github_body": approval.payload.get("github_body", ""),
            "policy_status": approval.payload.get("policy_status", "UNKNOWN"),
        }
    )
    return {
        "outcome_kind": "release_delivery_published",
        "outcome_title": record.title,
        "outcome_reference_id": record.id,
        "outcome_detail": (
            f"Marked {record.id} DONE, published the GitHub issue, and completed approved code delivery."
        ),
        "release_state": "published",
        "github_published_kind": publish_result.kind,
        "github_published_url": publish_result.url,
        "github_published_reference_id": publish_result.reference_id,
        **git_result,
        **vercel_result,
    }


def _approval_outcome_payload(result: RequirementRecord | ApprovalRequest) -> dict[str, str]:
    if isinstance(result, RequirementRecord):
        return {
            "outcome_kind": "requirement",
            "outcome_title": result.title,
            "outcome_reference_id": result.id,
            "outcome_detail": f"Continued into backlog requirement {result.id}.",
        }
    return {
        "outcome_kind": "approval",
        "outcome_title": result.title,
        "outcome_reference_id": result.approval_id,
        "outcome_detail": "Continued into an explicit scope confirmation.",
    }


LIVE_PM_DEFAULT_MODEL = os.getenv("OPENAI_PM_LIVE_MODEL", "gpt-4o-mini")
LIVE_AGENT_DEFAULT_MODEL = os.getenv("OPENAI_AGENT_LIVE_MODEL", LIVE_PM_DEFAULT_MODEL)


def _live_pm_system_prompt(
    project_name: str,
    display_name: str,
    *,
    ui_runtime: str = DEFAULT_UI_RUNTIME,
    force_draft: bool,
) -> str:
    runtime = normalize_ui_runtime(ui_runtime)
    profile = project_runtime_profile(runtime)
    site_import_context = _site_import_context_summary(project_name) if runtime == "web_app" else ""
    force_line = (
        "You must now draft the initial requirement, even if some uncertainty remains. Put any uncertainty into the draft's open questions."
        if force_draft
        else "Ask exactly one next clarifying question when you still need meaningful context. Draft only when you genuinely have enough."
    )
    runtime_line = (
        f"Planned project capability profile: {profile.label}. {profile.implementation_guidance}\n"
        f"{project_runtime_capability_summary(runtime)}\n"
        "Use this planned runtime context directly while shaping the initial requirement. Do not request `read_project_capability_profile` during brand-new project discovery, because the project does not exist yet."
        if runtime == "web_app"
        else f"Planned project capability profile: {profile.label}. Keep the default Streamlit implementation shape unless the user explicitly asks for something else."
    )
    site_import_line = (
        "Imported website context is already available for this project.\n"
        f"{site_import_context}\n"
        "When the user asks to replicate, extract, refresh, or improve an existing website using imported source material, the drafted requirement must make that explicit.\n"
        "Translate imported context into product truth by naming when source copy should be reused or adapted, when downloaded local site assets should be the primary visual source set, and when generic placeholder copy or abstract substitute visuals are not acceptable."
        if site_import_context
        else ""
    )
    return (
        "You are the Product Manager for AI Builder OS in Requirement Discovery Mode.\n"
        f"You are helping shape a brand-new project called `{display_name}` (`{project_name}`).\n"
        "Work like a real PM: understand the user, problem, context, constraints, and success before drafting.\n"
        f"{runtime_line}\n"
        f"{site_import_line}\n"
        "Be concise, specific, and genuinely responsive to the prior messages.\n"
        "When the user shares images, use them as real context for the conversation instead of ignoring them.\n"
        "If the user shares a public website URL and wants analysis, replication, extraction, or redesign, request the relevant website tool instead of claiming you cannot access websites:\n"
        "- `fetch_webpage` for one-page text, headings, links, and image extraction\n"
        "- `crawl_website` for bounded same-site structure and content extraction across multiple pages\n"
        "- `render_webpage` when the site may depend on JavaScript rendering or browser-visible content\n"
        "- `download_site_images` when the user explicitly wants image binaries saved locally for reference or replication\n"
        "- `classify_downloaded_site_assets` after image download when the team needs a reuse map for logo, hero, gallery, people, or icon assets\n"
        "Do not ask a fixed questionnaire. Ask only the next most relevant question.\n"
        "If the user has already answered something implicitly, do not ask for it again.\n"
        "If a materially blocking ambiguity remains around scope boundary, concurrency, ownership, system boundary, failure handling, or success criteria, "
        "you may choose `request_clarification` instead of `ask_question`. Use that only when the ambiguity should become a durable inbox item rather than a normal next-turn question.\n"
        f"{force_line}\n"
        "When you draft, produce exactly one strong initial requirement for the new project.\n"
        "If imported website context exists and the request is to replicate or improve that site, make source-copy reuse, downloaded local asset reuse, and no-placeholder expectations explicit in the requirement body.\n"
        "The draft requirement body should use these headings exactly:\n"
        "Problem statement\nTarget user\nCore job-to-be-done\nSuccess criteria\nConstraints\nOut of scope\nAssumptions\nOpen questions"
    )


def _message_to_live_pm_input(message: AgentMessage) -> dict[str, object]:
    role = message.role if message.role in {"user", "assistant", "developer", "system"} else "user"
    if message.attachments and role == "user":
        content: list[dict[str, str]] = [{"type": "input_text", "text": message.content}]
        for image_path in message.attachments:
            data_url = _image_path_to_data_url(image_path)
            if data_url is None:
                continue
            content.append({"type": "input_image", "image_url": data_url})
        return {"role": role, "content": content}
    return {"role": role, "content": message.content}


def _friendly_live_agent_error_message(detail: str) -> str:
    lowered = detail.lower()
    if "insufficient_quota" in lowered or "you exceeded your current quota" in lowered:
        return (
            "The live agent could not start because the OpenAI API project has run out of quota. "
            "Check billing and usage limits for the API key configured in `OPENAI_API_KEY`."
        )
    if "invalid_api_key" in lowered or "incorrect api key provided" in lowered:
        return (
            "The live agent could not start because OPENAI_API_KEY is invalid. "
            "Update the environment variable to a valid OpenAI API key and try again."
        )
    if "rate_limit" in lowered:
        return "The live agent is being rate limited by the model provider right now. Please wait a moment and try again."
    return detail


def _run_bounded_structured_turn(
    *,
    role: str,
    project_name: str,
    model: str,
    developer_prompt: str,
    input_messages: list[dict[str, object]],
    output_type: type[BaseModel],
) -> BaseModel:
    if not api_agents_enabled():
        raise LivePMDiscoveryError(
            "API-backed live agents are disabled. Prepare this work for Codex from the Workflow Inbox, "
            "or explicitly enable OpenAI API mode with AI_BUILDER_OS_ENABLE_API_AGENTS=1."
        )
    from agents_runtime import AgentsWorkflowRuntime

    try:
        return AgentsWorkflowRuntime(model=model).run_structured(
            project_name,
            role=role,
            instructions=developer_prompt,
            input_messages=input_messages,
            output_type=output_type,
            actor=active_user_label() or "streamlit-user",
            source="streamlit",
        )
    except AgentHandBackError as exc:
        raise LivePMDiscoveryError(_friendly_live_agent_error_message(str(exc))) from exc


def _live_learning_system_prompt(intent: Literal["teach_concept", "clarify_concept", "explain_implementation"]) -> str:
    intent_block = (
        "For this turn, teach the concept from first principles and prepare the learner for clarification, implementation grounding, or saved understanding."
        if intent == "teach_concept"
        else (
            "For this turn, resolve the learner's exact confusion and then route them back into clarification, implementation grounding, or saved understanding."
            if intent == "clarify_concept"
            else "For this turn, explain how the concept is implemented in the OS using only the provided anchors and then route the learner back into clarification or saved understanding."
        )
    )
    build_guardrail = (
        "- Do not recommend build-to-learn in this release profile. Keep the next move inside clarification, implementation, hierarchy, comparison, or saved understanding.\n"
        if not learning_build_to_learn_enabled()
        else "- Do not recommend build-to-learn unless you can justify a bounded experiment tied to the concept.\n"
    )
    return (
        "You are the Learning Agent for AI Builder OS.\n"
        "You are the single tutoring agent inside a bounded, local-first learning session.\n"
        "Your job is to help one learner understand one concept at a time in plain, jargon-light language.\n"
        f"{intent_block}\n"
        "\n"
        "Core tutoring behavior:\n"
        "- Explain simply before sounding clever.\n"
        "- Treat the learner's exact confusion as the center of the turn.\n"
        "- Use jargon only when necessary and immediately translate it.\n"
        "- Prefer one clear next move over a long, sprawling answer.\n"
        "- Stay calm, supportive, and practical.\n"
        "- Use the supplied teaching strategy explicitly; it is the current personalization contract for this learner.\n"
        "- Use the learner's AI Builder OS understanding level to decide how much OS-local context to assume.\n"
        "\n"
        "Grounding guardrails:\n"
        "- Stay anchored to the selected concept and the supplied OS context.\n"
        "- Do not drift into generic AI advice detached from the current concept.\n"
        "- Do not invent implementation details, files, evals, or workflows that are not supported by the provided context.\n"
        "- If the context is thin or uncertain, say so plainly and stay conservative.\n"
        "\n"
        "Learning-quality guardrails:\n"
        "- Do not mistake surface familiarity for understanding.\n"
        "- Do not imply a concept is fully learned just because the learner uses the right vocabulary.\n"
        f"{build_guardrail}"
        "- Keep the learner on the current concept instead of silently switching topics.\n"
        "- If you mention a nearby concept, use it only to sharpen the current concept.\n"
        "- When comparing concepts, say explicitly whether the relationship is broader/narrower, prerequisite/follow-on, sibling, or simply adjacent.\n"
        "- If the learner asks about hierarchy, answer that directly instead of leaving it implicit.\n"
        "- In implementation walkthroughs, name both the main OS surface and one concrete artifact or example that shows what the concept looks like in practice.\n"
        "- Explain what that example artifact proves, checks, or records inside the OS instead of only naming files.\n"
        "\n"
        "Session boundaries:\n"
        "- This is not an open-ended chat assistant.\n"
        "- Keep the response bounded enough that the next move remains obvious.\n"
        "- Use the supplied structured fields faithfully."
    )


def _live_learning_agent_contract() -> dict[str, object]:
    return {
        "teaching_style": [
            "Explain concepts in simple, plain language first.",
            "Use supportive coaching without sounding vague or overly enthusiastic.",
            "Prefer one concrete example or distinction over a long list.",
            "Apply the supplied teaching strategy instead of defaulting to one generic explanation shape.",
        ],
        "grounding_rules": [
            "Stay anchored to the selected concept and provided OS context.",
            "Do not invent files, evals, workflows, or implementation details.",
            "If the context is uncertain or incomplete, say so clearly instead of bluffing.",
        ],
        "learning_guardrails": [
            "Do not treat keyword familiarity as real understanding.",
            "Do not mark or imply that a concept is learned prematurely.",
            "Keep the tutoring bounded and on the current concept.",
            "Use nearby concepts only to clarify the current concept, not to drift away from it.",
            "When comparing concepts, name the structural relationship explicitly: broader/narrower, prerequisite/follow-on, sibling, or adjacent only.",
        ],
        "progression_rules": [
            "Default to deepening understanding before implying concept completion.",
            (
                "Do not recommend build-to-learn in this release profile; keep the next move inside explanation, implementation, hierarchy, comparison, or saved understanding."
                if not learning_build_to_learn_enabled()
                else "Recommend build-to-learn only when a bounded experiment is clearly justified."
            ),
            "When in doubt, choose the narrower next move.",
        ],
        "implementation_rules": [
            "Use only the provided anchors and excerpts to explain implementation.",
            "Explain how the anchors relate instead of dumping them as an unconnected list.",
            "If the provided anchors are not enough to support a confident walkthrough, say so plainly.",
            "Name both the main OS surface and one concrete artifact or example that shows what the concept looks like in practice.",
            "Explain what the example artifact proves, checks, or records instead of only naming where it lives.",
        ],
    }


def _run_live_learning_teaching_turn(
    concept: str,
    *,
    where_encountered: str,
    current_understanding: str,
    what_is_unclear: str,
) -> LiveLearningTeachingTurn:
    knowledge = _learning_knowledge_for(
        concept,
        current_understanding=current_understanding,
        what_is_unclear=what_is_unclear,
        where_encountered=where_encountered,
    )
    profile = load_learning_profile()
    teaching_strategy = _teaching_strategy_payload(profile)
    governing_truth = learning_concept_governing_truth(concept)
    parsed = _run_bounded_structured_turn(
        role="Learning Agent",
        project_name="os-control-panel",
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=_live_learning_system_prompt("teach_concept"),
        input_messages=[
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "intent": "teach_concept",
                        "concept": knowledge.concept,
                        "where_encountered": where_encountered.strip(),
                        "current_understanding": current_understanding.strip(),
                        "what_is_unclear": what_is_unclear.strip(),
                        "learning_profile": profile,
                        "teaching_strategy": teaching_strategy,
                        "concept_context": {
                            "why_now": knowledge.why_now,
                            "where_it_connects": knowledge.where_it_connects,
                            "what_it_is": knowledge.what_it_is,
                            "why_it_exists": knowledge.why_it_exists,
                            "nearby_distinction": knowledge.nearby_distinction,
                            "os_connection": knowledge.os_connection,
                            "product_implication": knowledge.product_implication,
                        },
                        "governing_truth": governing_truth,
                        "agent_contract": _live_learning_agent_contract(),
                        "output_guidance": {
                            "what_it_is": "2-4 concise sentences explaining the concept simply.",
                            "why_it_exists": "1-3 concise sentences naming the problem this concept solves.",
                            "nearby_distinction": "1-3 concise sentences comparing the nearest easy-to-confuse concept.",
                            "os_connection": "1-3 concise sentences tying the concept to AI Builder OS.",
                            "product_implication": "1-3 concise sentences on why a product leader should care.",
                            "coach_message": "One short supportive sentence asking the learner to explain it back simply.",
                        },
                    },
                    indent=2,
                ),
            },
        ],
        output_type=LiveLearningTeachingTurn,
    )
    assert isinstance(parsed, LiveLearningTeachingTurn)
    return parsed


def _run_live_learning_clarification_turn(
    session: LearningAgentSession,
    action: Literal["simpler", "specific_confusion", "another_example", "nearby_comparison"],
    *,
    detail: str = "",
) -> LiveLearningClarificationTurn:
    knowledge = _learning_knowledge_for(
        session.concept,
        current_understanding=session.current_understanding,
        what_is_unclear=session.what_is_unclear,
        where_encountered=session.where_encountered,
    )
    governing_truth = learning_concept_governing_truth(session.concept)
    comparison_target = _requested_learning_comparison_target(session.concept, detail) if action == "nearby_comparison" else ""
    comparison_target_knowledge = _learning_knowledge_for(comparison_target) if comparison_target else None
    comparison_relationship = (
        _learning_comparison_relationship_summary(knowledge, comparison_target_knowledge)
        if comparison_target_knowledge is not None
        else ""
    )
    profile = load_learning_profile()
    teaching_strategy = _teaching_strategy_payload(profile)
    parsed = _run_bounded_structured_turn(
        role="Learning Agent",
        project_name="os-control-panel",
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=_live_learning_system_prompt("clarify_concept"),
        input_messages=[
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "intent": "clarify_concept",
                        "clarification_mode": action,
                        "concept": knowledge.concept,
                        "specific_confusion": detail.strip(),
                        "learning_profile": profile,
                        "teaching_strategy": teaching_strategy,
                        "session_state": {
                            "where_encountered": session.where_encountered,
                            "current_understanding": session.current_understanding,
                            "what_is_unclear": session.what_is_unclear,
                            "latest_explanation_back": session.latest_explanation_back,
                            "detected_gaps": list(session.detected_gaps),
                            "turn_count": session.turn_count,
                        },
                        "concept_context": {
                            "what_it_is": knowledge.what_it_is,
                            "why_it_exists": knowledge.why_it_exists,
                            "nearby_distinction": knowledge.nearby_distinction,
                            "os_connection": knowledge.os_connection,
                            "product_implication": knowledge.product_implication,
                        },
                        "governing_truth": governing_truth,
                        "comparison_context": {
                            "requested_target": comparison_target,
                            "target_context": (
                                {
                                    "concept": comparison_target_knowledge.concept,
                                    "what_it_is": comparison_target_knowledge.what_it_is,
                                    "why_it_exists": comparison_target_knowledge.why_it_exists,
                                    "nearby_distinction": comparison_target_knowledge.nearby_distinction,
                                    "os_connection": comparison_target_knowledge.os_connection,
                                    "product_implication": comparison_target_knowledge.product_implication,
                                }
                                if comparison_target_knowledge is not None
                                else {}
                            ),
                            "relationship_hint": comparison_relationship,
                            "asks_for_hierarchy": "hierarch" in detail.lower(),
                        },
                        "agent_contract": _live_learning_agent_contract(),
                        "response_rules": {
                            "simpler": "Re-explain more plainly without just repeating the same wording.",
                            "specific_confusion": "Answer the exact confusion directly and concretely.",
                            "another_example": "Give a different concrete example from the concept context.",
                            "nearby_comparison": (
                                "Compare the selected concept to the requested nearby concept. "
                                "State clearly what each concept measures or is responsible for, "
                                "say whether one is broader/narrower or whether they are sibling/adjacent concepts, "
                                "and answer any hierarchy question directly."
                            ),
                        },
                        "output_guidance": {
                            "clarification_response": (
                                "2-7 concise sentences that directly resolve the requested confusion. "
                                "For nearby comparison, explicitly include scope, structural relationship, and one practical anchor."
                            ),
                            "coach_message": "One short supportive sentence inviting the learner to explain it back again.",
                        },
                    },
                    indent=2,
                ),
            },
        ],
        output_type=LiveLearningClarificationTurn,
    )
    assert isinstance(parsed, LiveLearningClarificationTurn)
    return parsed


def _build_learning_implementation_walkthrough_response(
    session: LearningAgentSession,
    anchors: list[LearningImplementationAnchor],
) -> dict[str, str]:
    profile = load_learning_profile()
    strategy = learning_teaching_strategy(profile)
    anchor_labels = ", ".join(anchor.label for anchor in anchors[:3])
    intro = (
        f"Here is where {session.concept} becomes concrete in the OS: {anchor_labels}. "
        "These anchors show the concept in action instead of leaving it as abstract vocabulary."
    )
    if anchors:
        system_anchor = anchors[0]
        artifact_anchor = next(
            (anchor for anchor in anchors if anchor.kind in {"fixture", "state", "doc", "test"}),
            system_anchor,
        )
        fit = " ".join(
            [
                f"System surface: {system_anchor.label} shows where {session.concept} lives operationally in the OS.",
                f"Concrete example: {artifact_anchor.label} shows what {session.concept} looks like as a real artifact or check in practice.",
                f"Why that matters: {artifact_anchor.why_it_matters}",
            ]
        )
    else:
        fit = "Use the supplied anchors to explain both the main OS surface and one concrete example artifact for the concept."
    if "Assume little AI Builder OS familiarity" in strategy.os_context_depth:
        intro += " I will stay explicit about what each OS surface is before assuming any local workflow familiarity."
    elif "Assume the learner can place OS-local surfaces" in strategy.os_context_depth:
        intro += " I will assume you can place these anchors in the wider OS flow without re-explaining every surface."
    coach_message = (
        f"{strategy.coaching_style} Use the walkthrough above to capture what each anchor does and how the pieces relate."
    )
    return {
        "walkthrough_intro": intro,
        "how_the_pieces_fit": fit,
        "coach_message": coach_message,
    }


def _run_live_learning_implementation_turn(
    session: LearningAgentSession,
    anchors: list[LearningImplementationAnchor],
) -> LiveLearningImplementationTurn:
    profile = load_learning_profile()
    teaching_strategy = _teaching_strategy_payload(profile)
    governing_truth = learning_concept_governing_truth(session.concept)
    parsed = _run_bounded_structured_turn(
        role="Learning Agent",
        project_name="os-control-panel",
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=_live_learning_system_prompt("explain_implementation"),
        input_messages=[
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "intent": "explain_implementation",
                        "concept": session.concept,
                        "learning_profile": profile,
                        "teaching_strategy": teaching_strategy,
                        "session_state": {
                            "where_encountered": session.where_encountered,
                            "current_understanding": session.current_understanding,
                            "what_is_unclear": session.what_is_unclear,
                            "latest_explanation_back": session.latest_explanation_back,
                            "detected_gaps": list(session.detected_gaps),
                            "turn_count": session.turn_count,
                        },
                        "governing_truth": governing_truth,
                        "agent_contract": _live_learning_agent_contract(),
                        "implementation_anchors": [
                            {
                                "label": anchor.label,
                                "path": anchor.path,
                                "kind": anchor.kind,
                                "why_it_matters": anchor.why_it_matters,
                                "excerpt": anchor.excerpt,
                            }
                            for anchor in anchors
                        ],
                        "output_guidance": {
                            "walkthrough_intro": (
                                "2-4 concise sentences explaining where the concept appears in the OS and naming the main system surface the learner should orient around first."
                            ),
                            "how_the_pieces_fit": (
                                "3-6 concise sentences that explicitly cover: "
                                "(1) one main system surface, "
                                "(2) one concrete artifact or example anchor, "
                                "(3) what that artifact proves/checks/records in practice, and "
                                "(4) how the system surface and artifact relate to the concept."
                            ),
                            "coach_message": "One short supportive sentence inviting the learner to explain the concept back using the implementation anchors.",
                        },
                    },
                    indent=2,
                ),
            },
        ],
        output_type=LiveLearningImplementationTurn,
    )
    assert isinstance(parsed, LiveLearningImplementationTurn)
    return parsed


def _run_live_pm_turn(
    project_name: str,
    display_name: str,
    messages: tuple[AgentMessage, ...],
    *,
    ui_runtime: str = DEFAULT_UI_RUNTIME,
    force_draft: bool = False,
) -> LivePMTurn:
    parsed = _run_bounded_structured_turn(
        role="PM",
        project_name=project_name,
        model=LIVE_PM_DEFAULT_MODEL,
        developer_prompt=_live_pm_system_prompt(
            project_name,
            display_name,
            ui_runtime=ui_runtime,
            force_draft=force_draft,
        ),
        input_messages=[_message_to_live_pm_input(message) for message in messages],
        output_type=LivePMTurn,
    )
    assert isinstance(parsed, LivePMTurn)
    return _ensure_live_pm_assistant_message(parsed)


def _live_experience_system_prompt(project_name: str, mode: str, *, force_draft: bool) -> str:
    runtime = load_project_ui_runtime(project_name)
    profile = project_runtime_profile(runtime)
    mode_guidance = {
        "Feedback Synthesis": (
            "Your job is to turn UX feedback, workflow friction, or user pain into one structured finding that can be routed into the OS."
        ),
        "Usability Review": (
            "Your job is to review a UI or flow for usability, clarity, hierarchy, scanability, and workflow friction, then turn that into one structured finding."
        ),
    }
    runtime_focus = (
        "When reviewing a Streamlit surface, pay extra attention to rerun orientation, repeated stacked sections, explicit workflow state, and whether the primary action stays obvious."
        if profile.runtime == "streamlit"
        else "When reviewing a web app surface, pay extra attention to responsive behavior, browser-native navigation expectations, form completion friction, and loading, empty, error, or success states."
    )
    force_line = (
        "You must now draft the strongest finding you can from the current context, and put any remaining uncertainty into the rationale."
        if force_draft
        else "Ask exactly one next clarifying question when meaningful uncertainty remains. Draft only when you have enough to write one strong finding."
    )
    return (
        "You are the Experience Designer for AI Builder OS.\n"
        f"You are working inside project `{project_name}` in mode `{mode}`.\n"
        f"Project capability profile: {profile.label}. {profile.implementation_guidance}\n"
        f"{project_runtime_capability_summary(runtime)}\n"
        f"{mode_guidance.get(mode, mode_guidance['Feedback Synthesis'])}\n"
        "If the active runtime is `web_app` and the frontend implementation shape matters, request `read_project_capability_profile` before drafting so your finding stays aligned with the bounded local frontend bundle.\n"
        "If the user shares a public website URL and wants critique, comparison, or extraction, request `fetch_webpage`, `crawl_website`, or `render_webpage` before drafting instead of treating the website as inaccessible. If local image references would materially help, request `download_site_images` too, and request `classify_downloaded_site_assets` when an asset reuse map would improve the critique.\n"
        "Be concise, genuinely responsive to prior messages, and do not ask a fixed questionnaire.\n"
        "When the user shares images, use them as real evidence for the usability or experience discussion.\n"
        "Prioritise usability problems, comprehension gaps, and workflow friction over purely aesthetic commentary.\n"
        f"{runtime_focus}\n"
        "When you draft, produce exactly one structured finding and classify it as one of:\n"
        "- UX improvement in scope\n"
        "- feature candidate\n"
        "- scope escalation\n"
        f"{force_line}\n"
        "The finding draft should use these headings exactly:\n"
        "User problem\nAffected workflow\nEvidence\nConfidence\nSeverity / frequency\nRecommendation type\nRationale\nRecommended next role"
    )


def _run_live_experience_turn(
    project_name: str,
    mode: str,
    messages: tuple[AgentMessage, ...],
    *,
    force_draft: bool = False,
) -> LiveExperienceTurn:
    parsed = _run_bounded_structured_turn(
        role="Experience Designer",
        project_name=project_name,
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=_live_experience_system_prompt(project_name, mode, force_draft=force_draft),
        input_messages=[_message_to_live_pm_input(message) for message in messages],
        output_type=LiveExperienceTurn,
    )
    assert isinstance(parsed, LiveExperienceTurn)
    return parsed


def _live_ui_designer_system_prompt(project_name: str, mode: str, *, force_draft: bool) -> str:
    runtime = load_project_ui_runtime(project_name)
    profile = project_runtime_profile(runtime)
    mode_guidance = {
        "Design Direction": (
            "Your job is to help shape the intended visual system, aesthetics, interaction design, layout approach, and look-and-feel of a user-facing surface before implementation is settled."
        ),
        "UI Review": (
            "Your job is to critique an existing UI that already exists and identify concrete improvements in hierarchy, spacing, composition, visual consistency, and polish."
        ),
    }
    force_line = (
        "You must now draft one concise design brief from the current context, even if some uncertainty remains."
        if force_draft
        else "Ask exactly one next clarifying question when meaningful design uncertainty remains. Draft only when you have enough to propose one strong design brief."
    )
    runtime_line = (
        f"Project capability profile: {profile.label}. {profile.implementation_guidance}"
    )
    runtime_constraint = (
        "Do not assume Next.js, React, or browser-native routing unless the user explicitly asks to explore a different runtime shape."
        if profile.runtime == "streamlit"
        else "Do not assume Streamlit patterns, Streamlit widgets, or Streamlit layout constraints unless the user explicitly asks to explore a different runtime shape."
    )
    return (
        "You are the UI Designer for AI Builder OS.\n"
        f"You are working inside project `{project_name}` in mode `{mode}`.\n"
        f"{runtime_line}\n"
        f"{project_runtime_capability_summary(runtime)}\n"
        f"{mode_guidance.get(mode, mode_guidance['Design Direction'])}\n"
        "If the active runtime is `web_app` and the frontend implementation shape matters, request `read_project_capability_profile` before drafting so your design brief stays aligned with the bounded local frontend bundle.\n"
        "If the user shares a public website URL and wants replication, reference capture, or visual analysis, request `fetch_webpage`, `crawl_website`, or `render_webpage` before drafting instead of treating the website as inaccessible. If the user wants local visual references or asset pull-through, request `download_site_images` too, and request `classify_downloaded_site_assets` when a structured asset reuse map would help implementation.\n"
        "Focus on usable visual direction, layout, and interface quality rather than vague taste commentary.\n"
        "When the user shares images, use them as real visual context for your critique or design direction.\n"
        "Keep the mode boundary crisp: Design Direction is forward-looking target-state guidance, while UI Review is critique of an existing surface.\n"
        f"{runtime_constraint}\n"
        "Do not ask a fixed questionnaire.\n"
        f"{force_line}\n"
        "When you draft, produce exactly one design brief.\n"
        "The design brief should use these headings exactly:\n"
        "Design goal\nUser and context\nVisual direction\nLayout and interaction guidance\nSurface changes\nConstraints\nOpen questions"
    )


def _run_live_ui_designer_turn(
    project_name: str,
    mode: str,
    messages: tuple[AgentMessage, ...],
    *,
    force_draft: bool = False,
) -> LiveUIDesignTurn:
    parsed = _run_bounded_structured_turn(
        role="UI Designer",
        project_name=project_name,
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=_live_ui_designer_system_prompt(project_name, mode, force_draft=force_draft),
        input_messages=[_message_to_live_pm_input(message) for message in messages],
        output_type=LiveUIDesignTurn,
    )
    assert isinstance(parsed, LiveUIDesignTurn)
    return parsed


def _live_pm_review_completion_system_prompt(project_name: str, artifact_type: str) -> str:
    artifact_label = "approved workflow artifact"
    if artifact_type == "experience_finding":
        artifact_label = "approved Experience Designer finding"
    elif artifact_type == "design_brief":
        artifact_label = "approved UI Designer design brief"

    return (
        "You are the Product Manager for AI Builder OS.\n"
        f"You are reviewing one {artifact_label} inside project `{project_name}`.\n"
        "Your job is to finish the workflow so approved review output becomes actionable.\n"
        "Decide between exactly two outcomes:\n"
        "- `create_backlog_requirement` when the approved artifact should become a real backlog requirement inside this project.\n"
        "- `confirm_out_of_scope` when the approved artifact should not enter backlog without explicit Product Director confirmation.\n"
        "Choose `confirm_out_of_scope` only when the work is truly outside the product scope, too broad, or misaligned with the current product direction.\n"
        "When you choose `create_backlog_requirement`, draft exactly one strong backlog requirement using these headings exactly:\n"
        "Problem statement\nTarget user\nCore job-to-be-done\nSuccess criteria\nConstraints\nOut of scope\nAssumptions\nOpen questions\n"
        "When you choose `confirm_out_of_scope`, provide a concise title and summary that explains why Product Director confirmation is needed.\n"
        "Be concise, specific, and results-oriented."
    )


def _run_live_pm_review_completion_turn(
    project_name: str,
    artifact_type: str,
    artifact_title: str,
    artifact_body: str,
) -> LivePMReviewCompletionTurn:
    parsed = _run_bounded_structured_turn(
        role="PM",
        project_name=project_name,
        model=LIVE_PM_DEFAULT_MODEL,
        developer_prompt=_live_pm_review_completion_system_prompt(project_name, artifact_type),
        input_messages=[
            {"role": "user", "content": f"Artifact title: {artifact_title.strip() or 'Untitled artifact'}"},
            {"role": "user", "content": artifact_body.strip()},
        ],
        output_type=LivePMReviewCompletionTurn,
    )
    assert isinstance(parsed, LivePMReviewCompletionTurn)
    return parsed


def _live_pm_thread_from_dict(raw_thread: dict[str, object]) -> LivePMProjectThread:
    raw_messages = raw_thread.get("messages", [])
    messages = tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )
    return LivePMProjectThread(
        thread_id=str(raw_thread["thread_id"]),
        project_name=str(raw_thread["project_name"]),
        display_name=str(raw_thread["display_name"]),
        planner_type=str(raw_thread.get("planner_type", "live")),
        status=str(raw_thread["status"]),
        messages=messages,
        draft_title=str(raw_thread.get("draft_title", "")),
        draft_requirement=str(raw_thread.get("draft_requirement", "")),
        created_at=str(raw_thread.get("created_at", "")),
        updated_at=str(raw_thread.get("updated_at", "")),
    )


def start_live_pm_project_thread(
    project_name: str,
    display_name: str,
    idea: str,
    *,
    ui_runtime: str = DEFAULT_UI_RUNTIME,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> LivePMProjectThread:
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    normalized_project_name = normalize_project_directory_name(project_name)
    attachments = save_agent_message_uploads(normalized_project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_pm_turn(normalized_project_name, display_name, messages, ui_runtime=ui_runtime)
    updated_at = datetime.now(timezone.utc).isoformat()
    draft_title = turn.draft_title.strip() if turn.next_action == "draft_requirements" else ""
    draft_requirement = turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else ""
    return LivePMProjectThread(
        thread_id=thread_id,
        project_name=normalized_project_name,
        display_name=display_name.strip(),
        ui_runtime=normalize_ui_runtime(ui_runtime),
        planner_type="live",
        status="drafted" if draft_requirement else "active",
        messages=(
            *messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=draft_title,
        draft_requirement=draft_requirement,
        created_at=created_at,
        updated_at=updated_at,
    )


def continue_live_pm_project_thread(
    thread: LivePMProjectThread,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> LivePMProjectThread:
    user_message = AgentMessage(
        role="user",
        content=reply.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
        attachments=save_agent_message_uploads(thread.project_name, thread.thread_id, image_files),
    )
    messages = (*thread.messages, user_message)
    turn = _run_live_pm_turn(thread.project_name, thread.display_name, messages, ui_runtime=thread.ui_runtime)
    updated_at = datetime.now(timezone.utc).isoformat()
    draft_title = turn.draft_title.strip() if turn.next_action == "draft_requirements" else thread.draft_title
    draft_requirement = turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else thread.draft_requirement
    return LivePMProjectThread(
        thread_id=thread.thread_id,
        project_name=thread.project_name,
        display_name=thread.display_name,
        ui_runtime=thread.ui_runtime,
        planner_type=thread.planner_type,
        status="drafted" if draft_requirement else "active",
        messages=(
            *messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=draft_title,
        draft_requirement=draft_requirement,
        created_at=thread.created_at,
        updated_at=updated_at,
    )


def draft_live_pm_project_thread(thread: LivePMProjectThread) -> LivePMProjectThread:
    turn = _run_live_pm_turn(
        thread.project_name,
        thread.display_name,
        thread.messages,
        ui_runtime=thread.ui_runtime,
        force_draft=True,
    )
    updated_at = datetime.now(timezone.utc).isoformat()
    return LivePMProjectThread(
        thread_id=thread.thread_id,
        project_name=thread.project_name,
        display_name=thread.display_name,
        ui_runtime=thread.ui_runtime,
        planner_type=thread.planner_type,
        status="drafted",
        messages=(
            *thread.messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=turn.draft_title.strip(),
        draft_requirement=turn.draft_requirement.strip(),
        created_at=thread.created_at,
        updated_at=updated_at,
    )


def start_experience_designer_thread(
    project_name: str,
    mode: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(project_name, raw_threads, agent_name="Experience Designer", mode=mode)
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_experience_turn(project_name, mode, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "Experience Designer",
        "mode": mode,
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": "Experience finding draft" if turn.next_action == "draft_finding" else "",
        "draft": turn.finding_draft.strip() if turn.next_action == "draft_finding" else "",
        "draft_data": {
            "user_problem": turn.user_problem.strip(),
            "affected_workflow": turn.affected_workflow.strip(),
            "evidence": turn.evidence.strip(),
            "confidence": turn.confidence.strip(),
            "severity": turn.severity.strip(),
            "frequency": turn.frequency.strip(),
            "recommendation_type": turn.recommendation_type.strip(),
            "rationale": turn.rationale.strip(),
        }
        if turn.next_action == "draft_finding"
        else {},
        "messages": [
            _agent_message("user", idea.strip(), attachments=attachments),
            _agent_message("assistant", turn.assistant_message.strip()),
        ],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_experience_designer_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")
    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    turn = _run_live_experience_turn(project_name, str(matching.get("mode", "")), _agent_thread_messages(matching))
    if turn.next_action == "draft_finding":
        matching["draft_title"] = "Experience finding draft"
        matching["draft"] = turn.finding_draft.strip()
        matching["draft_data"] = {
            "user_problem": turn.user_problem.strip(),
            "affected_workflow": turn.affected_workflow.strip(),
            "evidence": turn.evidence.strip(),
            "confidence": turn.confidence.strip(),
            "severity": turn.severity.strip(),
            "frequency": turn.frequency.strip(),
            "recommendation_type": turn.recommendation_type.strip(),
            "rationale": turn.rationale.strip(),
        }
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_experience_designer_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    turn = _run_live_experience_turn(
        project_name,
        str(matching.get("mode", "")),
        _agent_thread_messages(matching),
        force_draft=True,
    )
    matching["draft_title"] = "Experience finding draft"
    matching["draft"] = turn.finding_draft.strip()
    matching["draft_data"] = {
        "user_problem": turn.user_problem.strip(),
        "affected_workflow": turn.affected_workflow.strip(),
        "evidence": turn.evidence.strip(),
        "confidence": turn.confidence.strip(),
        "severity": turn.severity.strip(),
        "frequency": turn.frequency.strip(),
        "recommendation_type": turn.recommendation_type.strip(),
        "rationale": turn.rationale.strip(),
    }
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def save_experience_thread_to_finding(project_name: str, thread_id: str) -> ExperienceFinding:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft_data = matching.get("draft_data", {})
    if not isinstance(draft_data, dict) or not draft_data:
        raise ValueError(f"Thread has no experience finding draft yet: {thread_id}")
    finding = save_experience_finding(
        project_name,
        user_problem=str(draft_data.get("user_problem", "")),
        affected_workflow=str(draft_data.get("affected_workflow", "")),
        evidence=str(draft_data.get("evidence", "")),
        confidence=str(draft_data.get("confidence", "MEDIUM")),
        severity=str(draft_data.get("severity", "MEDIUM")),
        frequency=str(draft_data.get("frequency", "MEDIUM")),
        recommendation_type=str(draft_data.get("recommendation_type", "UX improvement in scope")),
        rationale=str(draft_data.get("rationale", "")),
    )
    matching["status"] = "saved"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return finding


def _experience_finding_pm_review_body(finding: ExperienceFinding) -> str:
    return "\n".join(
        [
            "Approved Experience Designer finding:",
            f"User problem: {finding.user_problem}",
            f"Affected workflow: {finding.affected_workflow}",
            f"Evidence: {finding.evidence}",
            f"Confidence: {finding.confidence}",
            f"Severity: {finding.severity}",
            f"Frequency: {finding.frequency}",
            f"Recommendation type: {finding.recommendation_type}",
            f"Rationale: {finding.rationale}",
            f"Recommended next role: {finding.recommended_next_role}",
        ]
    )


def _design_brief_pm_review_body(title: str, draft: str) -> str:
    return "\n".join(
        [
            f"Approved UI Designer brief: {title.strip() or 'Untitled design brief'}",
            "",
            draft.strip(),
        ]
    ).strip()


def _request_scope_confirmation(
    project_name: str,
    *,
    source_thread_id: str,
    source_agent_name: str,
    title: str,
    summary: str,
    payload: dict[str, str],
) -> ApprovalRequest:
    return _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="scope_confirmation",
        source_thread_id=source_thread_id,
        source_agent_name=source_agent_name,
        title=title.strip(),
        summary=summary.strip(),
        payload=payload,
    )


def _complete_review_artifact_with_pm(
    project_name: str,
    *,
    artifact_type: str,
    source_thread_id: str,
    source_agent_name: str,
    artifact_title: str,
    artifact_body: str,
    finding_id: str = "",
) -> RequirementRecord | ApprovalRequest:
    turn = _run_live_pm_review_completion_turn(
        project_name,
        artifact_type,
        artifact_title,
        artifact_body,
    )
    if turn.next_action == "create_backlog_requirement":
        requirement_title = turn.requirement_title.strip() or artifact_title.strip() or "Follow-up requirement"
        requirement_body = turn.requirement_body.strip() or artifact_body.strip()
        target = _find_requirement_consolidation_target(project_name, requirement_title, requirement_body)
        if target is None:
            requirement = append_requirement(
                project_name,
                requirement_title,
                requirement_body,
                status="BACKLOG",
                priority=turn.priority,
                effort=turn.effort,
            )
        else:
            requirement = _merge_review_artifact_into_requirement(
                project_name,
                target,
                source_agent_name=source_agent_name,
                artifact_title=requirement_title,
                artifact_body=requirement_body,
                priority=turn.priority,
                effort=turn.effort,
            )
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        return requirement

    confirmation_payload = {
        "requirement_title": turn.requirement_title.strip(),
        "requirement_body": turn.requirement_body.strip(),
        "priority": turn.priority,
        "effort": turn.effort,
        "artifact_type": artifact_type,
        "finding_id": finding_id.strip(),
    }
    return _request_scope_confirmation(
        project_name,
        source_thread_id=source_thread_id,
        source_agent_name="PM",
        title=turn.scope_confirmation_title.strip() or f"Confirm out-of-scope outcome for {artifact_title.strip() or source_agent_name}",
        summary=turn.scope_confirmation_summary.strip()
        or "PM believes this approved review should stay out of the current project scope unless Product Director says otherwise.",
        payload=confirmation_payload,
    )


def request_experience_thread_approval(project_name: str, thread_id: str) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft_data = matching.get("draft_data", {})
    if not isinstance(draft_data, dict) or not draft_data:
        raise ValueError(f"Thread has no experience finding draft yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="experience_finding",
        source_thread_id=thread_id,
        source_agent_name="Experience Designer",
        title="Approve Experience Designer finding",
        summary="Approve this reviewed finding to save it and continue it through PM completion.",
        payload={str(key): str(value) for key, value in draft_data.items()},
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def start_ui_designer_thread(
    project_name: str,
    mode: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(project_name, raw_threads, agent_name="UI Designer", mode=mode)
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_ui_designer_turn(project_name, mode, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "UI Designer",
        "mode": mode,
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": turn.draft_title.strip() if turn.next_action == "draft_design_brief" else "",
        "draft": turn.design_brief.strip() if turn.next_action == "draft_design_brief" else "",
        "draft_data": {},
        "messages": [
            _agent_message("user", idea.strip(), attachments=attachments),
            _agent_message("assistant", turn.assistant_message.strip()),
        ],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_ui_designer_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")
    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    turn = _run_live_ui_designer_turn(project_name, str(matching.get("mode", "")), _agent_thread_messages(matching))
    if turn.next_action == "draft_design_brief":
        matching["draft_title"] = turn.draft_title.strip()
        matching["draft"] = turn.design_brief.strip()
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_ui_designer_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    turn = _run_live_ui_designer_turn(
        project_name,
        str(matching.get("mode", "")),
        _agent_thread_messages(matching),
        force_draft=True,
    )
    matching["draft_title"] = turn.draft_title.strip()
    matching["draft"] = turn.design_brief.strip()
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def request_ui_design_brief_approval(project_name: str, thread_id: str) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no design brief draft yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="design_brief",
        source_thread_id=thread_id,
        source_agent_name="UI Designer",
        title=str(matching.get("draft_title", "")).strip() or "Approve UI design brief",
        summary="Approve this design brief to continue it through PM completion into backlog or scope confirmation.",
        payload={"draft": draft},
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def approve_request(project_name: str, approval_id: str) -> ApprovalRequest:
    raw_items = _load_approvals()
    matching = next(
        (
            item
            for item in raw_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Approval not found: {approval_id}")
    if str(matching.get("status", "")) != "OPEN":
        raise ValueError(f"Approval is not open: {approval_id}")

    approval = _approval_from_dict(matching)
    outcome_payload: dict[str, str] = {}
    if approval.approval_type == "requirement_draft":
        record = save_pm_requirement_thread_to_requirements(
            project_name,
            approval.source_thread_id,
            approval.payload.get("requirement_title", approval.title),
            status=approval.payload.get("status", "NEW"),
            priority=approval.payload.get("priority", "MEDIUM"),
            effort=approval.payload.get("effort", "M"),
        )
        outcome_payload = {
            "outcome_kind": "requirement",
            "outcome_title": record.title,
            "outcome_reference_id": record.id,
            "outcome_detail": f"Saved into requirements.md as {record.id} ({record.status}).",
        }
    elif approval.approval_type == "experience_finding":
        finding = save_experience_thread_to_finding(project_name, approval.source_thread_id)
        result = _complete_review_artifact_with_pm(
            project_name,
            artifact_type="experience_finding",
            source_thread_id=approval.source_thread_id,
            source_agent_name=approval.source_agent_name,
            artifact_title="Approved Experience Designer finding",
            artifact_body=_experience_finding_pm_review_body(finding),
            finding_id=finding.finding_id,
        )
        outcome_payload = _approval_outcome_payload(result)
    elif approval.approval_type == "design_brief":
        draft = approval.payload.get("draft", "").strip()
        result = _complete_review_artifact_with_pm(
            project_name,
            artifact_type="design_brief",
            source_thread_id=approval.source_thread_id,
            source_agent_name=approval.source_agent_name,
            artifact_title=approval.title,
            artifact_body=_design_brief_pm_review_body(approval.title, draft),
        )
        outcome_payload = _approval_outcome_payload(result)
        archive_agent_thread(project_name, approval.source_thread_id)
    elif approval.approval_type == "scope_confirmation":
        finding_id = approval.payload.get("finding_id", "").strip()
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        archive_agent_thread(project_name, approval.source_thread_id)
        outcome_payload = {
            "outcome_kind": "scope_confirmed",
            "outcome_title": approval.title,
            "outcome_reference_id": approval.approval_id,
            "outcome_detail": "Confirmed out of scope and resolved without creating new backlog work.",
        }
    elif approval.approval_type == "github_publication":
        target = approval.payload.get("github_target", "publication").replace("_", " ")
        publish_result = publish_github_publication({str(key): str(value) for key, value in approval.payload.items()})
        outcome_payload = {
            "outcome_kind": "github_publication_published",
            "outcome_title": approval.payload.get("github_title", approval.title),
            "outcome_reference_id": publish_result.reference_id,
            "outcome_detail": (
                f"Published approved {target} draft to GitHub. {publish_result.detail}"
            ),
            "publication_state": "published",
            "github_published_kind": publish_result.kind,
            "github_published_url": publish_result.url,
            "github_published_reference_id": publish_result.reference_id,
        }
    elif approval.approval_type == "release_delivery":
        outcome_payload = _approve_release_delivery(project_name, approval)
    elif approval.approval_type == "repository_action":
        outcome_payload = _approve_repository_action(approval)
    else:
        raise ValueError(f"Unsupported approval type: {approval.approval_type}")

    updated_items = _load_approvals()
    updated_matching = next(
        (
            item
            for item in updated_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if updated_matching is None:
        updated_matching = matching
        updated_items.append(updated_matching)
    updated_matching["status"] = "APPROVED"
    updated_matching["resolved_at"] = datetime.now(timezone.utc).isoformat()
    updated_matching["payload"] = {
        **{str(key): str(value) for key, value in approval.payload.items()},
        **outcome_payload,
    }
    _save_approvals(updated_items)
    return _approval_from_dict(updated_matching)


def reject_request(project_name: str, approval_id: str) -> ApprovalRequest:
    raw_items = _load_approvals()
    matching = next(
        (
            item
            for item in raw_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Approval not found: {approval_id}")
    if str(matching.get("status", "")) != "OPEN":
        raise ValueError(f"Approval is not open: {approval_id}")
    approval = _approval_from_dict(matching)
    outcome_payload: dict[str, str] = {}
    if approval.approval_type == "scope_confirmation":
        title = approval.payload.get("requirement_title", "").strip() or approval.title.strip()
        body = approval.payload.get("requirement_body", "").strip() or approval.summary.strip()
        record = append_requirement(
            project_name,
            title,
            body,
            status="BACKLOG",
            priority=approval.payload.get("priority", "MEDIUM"),
            effort=approval.payload.get("effort", "M"),
        )
        finding_id = approval.payload.get("finding_id", "").strip()
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        archive_agent_thread(project_name, approval.source_thread_id)
        outcome_payload = {
            "outcome_kind": "requirement",
            "outcome_title": record.title,
            "outcome_reference_id": record.id,
            "outcome_detail": f"Sent to backlog as {record.id} after rejecting the out-of-scope recommendation.",
        }
    matching["status"] = "REJECTED"
    matching["resolved_at"] = datetime.now(timezone.utc).isoformat()
    matching["payload"] = {
        **{str(key): str(value) for key, value in approval.payload.items()},
        **outcome_payload,
    }
    _save_approvals(raw_items)
    return _approval_from_dict(matching)


def workflow_inbox_items(project_name: str | None = None) -> list[InboxItem]:
    project_names: list[str]
    if project_name is not None:
        project_names = [project_name]
    else:
        project_names = [project.name for project in summarize_projects()]

    items: list[InboxItem] = []
    for current_project in project_names:
        for approval in active_approvals(current_project):
            items.append(
                InboxItem(
                    kind="approval",
                    title=approval.title,
                    summary=approval.summary,
                    project_name=current_project,
                    status_bucket="waiting",
                    reference_id=approval.approval_id,
                    detail=f"{approval.source_agent_name} approval request",
                )
            )

        for clarification in active_pm_clarifications(current_project):
            title = (
                f"{clarification.requirement_id} needs clarification"
                if clarification.requirement_id
                else f"{clarification.requirement_title or 'PM discovery'} needs clarification"
            )
            items.append(
                InboxItem(
                    kind="pm_clarification",
                    title=title,
                    summary=clarification.summary,
                    project_name=current_project,
                    status_bucket="blocked",
                    reference_id=clarification.clarification_id,
                    detail="Open PM clarification",
                )
            )

        for thread in list_agent_threads(current_project):
            if thread.status != "active":
                continue
            last_role = thread.messages[-1].role if thread.messages else ""
            if last_role == "assistant":
                items.append(
                    InboxItem(
                        kind="agent_thread",
                        title=f"{thread.agent_name} — {thread.mode}",
                        summary="Waiting on your reply in the live agent thread.",
                        project_name=current_project,
                        status_bucket="waiting",
                        reference_id=thread.thread_id,
                        detail=thread.messages[-1].content if thread.messages else "",
                    )
                )

        for finding in list_experience_findings(current_project):
            if finding.handoff_state in {"routed", "ready_for_pm_review", "ready_for_product_director", "handoff_prepared"}:
                items.append(
                    InboxItem(
                        kind="experience_finding",
                        title=f"Experience finding {finding.finding_id}",
                        summary=finding.user_problem,
                        project_name=current_project,
                        status_bucket="routed",
                        reference_id=finding.finding_id,
                        detail=f"{finding.handoff_state} -> {finding.recommended_next_role}",
                    )
                )

        for run in list_implementation_runs(current_project):
            if run.status in IMPLEMENTATION_ACTIVE_STATES:
                items.append(
                    InboxItem(
                        kind="implementation_run",
                        title=f"{run.requirement_id} implementation",
                        summary=run.summary or implementation_progress_message(run.status),
                        project_name=current_project,
                        status_bucket="running",
                        reference_id=run.run_id,
                        detail=run.status,
                    )
                )

    return items


def orchestrator_recommendation(project_name: str) -> OrchestratorRecommendation:
    project_dir = _project_path(project_name)
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    findings = load_active_experience_findings(project_dir / "data" / "experience_findings.json")
    clarifications = load_active_pm_clarifications(project_dir / "data" / "pm_clarifications.json")
    agent_threads = load_active_agent_threads(project_dir / "data" / "agent_threads.json")
    approvals = active_approvals(project_name)

    if approvals:
        first = approvals[0]
        return OrchestratorRecommendation(
            next_action=f"Review approval request: {first.title}.",
            next_role="Product Director",
            why=f"{first.source_agent_name} created an open approval request that should be resolved before the workflow progresses.",
        )

    if clarifications:
        first = clarifications[0]
        target = first.get("requirement_id") or first.get("requirement_title") or "PM discovery"
        return OrchestratorRecommendation(
            next_action=f"Answer PM clarification for {target}.",
            next_role="Product Director",
            why=f"{target} has an open PM clarification request that should be resolved before further tasking or implementation.",
        )

    if agent_threads:
        thread = agent_threads[0]
        agent_name = str(thread.get("agent_name", "Agent"))
        mode = str(thread.get("mode", ""))
        last_role = str(thread.get("last_role", ""))
        if last_role == "assistant":
            return OrchestratorRecommendation(
                next_action=f"Continue the active {agent_name} {mode} thread in the project UI.",
                next_role="Product Director",
                why=f"Thread {thread['thread_id']} is still active and currently waiting on a human reply before the workflow can progress.",
            )
        return OrchestratorRecommendation(
            next_action=f"Continue the active {agent_name} {mode} thread.",
            next_role=agent_name or "PM",
            why=f"Thread {thread['thread_id']} is still active and should complete before the project is treated as idle.",
        )

    new_requirements = [item for item in requirements if item["status"] == "NEW"]
    if new_requirements:
        item = new_requirements[0]
        return OrchestratorRecommendation(
            next_action=f"Run PM on {item['id']}.",
            next_role="PM",
            why=f"{item['id']} is marked NEW in product/requirements.md and has not yet been turned into tasks.",
        )

    if findings:
        routed = next((item for item in findings if item["handoff_state"] == "routed"), None)
        if routed is not None:
            role = str(routed.get("recommended_next_role", "")) or "PM"
            return OrchestratorRecommendation(
                next_action=f"Run {role} on the routed workflow artifact.",
                next_role=role,
                why=f"Finding {routed['finding_id']} is routed and points to {role}.",
            )

        ready_pm = next((item for item in findings if item["handoff_state"] == "ready_for_pm_review"), None)
        if ready_pm is not None:
            return OrchestratorRecommendation(
                next_action="Run PM on the ready-for-review experience finding.",
                next_role="PM",
                why=f"Finding {ready_pm['finding_id']} is waiting on PM review.",
            )

        ready_pd = next((item for item in findings if item["handoff_state"] == "ready_for_product_director"), None)
        if ready_pd is not None:
            return OrchestratorRecommendation(
                next_action="Review the scope-escalation finding with the Product Director.",
                next_role="Product Director",
                why=f"Finding {ready_pd['finding_id']} is waiting on Product Director review.",
            )

    pending_tasks = [item for item in tasks if item["status"] in {"TODO", "IN_PROGRESS"}]
    if pending_tasks:
        first = pending_tasks[0]
        requirement_by_id = {item["id"]: item for item in requirements}
        linked_requirements = [requirement_by_id[req_id] for req_id in first.get("requirements", []) if req_id in requirement_by_id]
        if any(requirement_has_structural_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run Architect review before implementation on {linked_ids}.",
                next_role="Architect",
                why=f"{first['id']} is pending, but its linked requirement introduces a structural trigger that should be reviewed before Engineer starts.",
            )
        if any(requirement_has_experience_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run Experience Designer before implementation on {linked_ids}.",
                next_role="Experience Designer",
                why=f"{first['id']} is pending, and its linked requirement is experience-heavy enough that usability/workflow review should happen before Engineer starts.",
            )
        if any(requirement_has_ui_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run UI Designer before implementation on {linked_ids}.",
                next_role="UI Designer",
                why=f"{first['id']} is pending, and its linked requirement is UI-heavy enough that design direction or UI review should happen before Engineer starts.",
            )
        return OrchestratorRecommendation(
            next_action=f"Run Engineer on {first['id']}.",
            next_role="Engineer",
            why=f"{first['id']} is still {first['status']} in product/tasks.md.",
        )

    backlog = [item for item in requirements if item["status"] == "BACKLOG"]
    if backlog:
        return OrchestratorRecommendation(
            next_action="No agent needs to run automatically.",
            next_role="None",
            why="There are no NEW requirements, no active workflow artifacts, and no pending tasks. Remaining work is backlog only.",
        )

    return OrchestratorRecommendation(
        next_action="No agent needs to run automatically.",
        next_role="None",
        why="There are no NEW requirements, no active workflow artifacts, and no pending tasks.",
    )


def run_live_orchestrator_review(project_name: str) -> LiveOrchestratorReviewTurn:
    deterministic = orchestrator_recommendation(project_name)
    parsed = _run_bounded_structured_turn(
        role="Orchestrator",
        project_name=project_name,
        model=LIVE_AGENT_DEFAULT_MODEL,
        developer_prompt=(
            "You are the bounded live review layer for the AI Builder OS Orchestrator. "
            "Review the deterministic recommendation against current project context. "
            "You may recommend a different role or action, but you cannot route work, mutate state, "
            "or overrule the deterministic control layer. State uncertainty plainly."
        ),
        input_messages=[
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "deterministic_recommendation": {
                            "next_role": deterministic.next_role,
                            "next_action": deterministic.next_action,
                            "why": deterministic.why,
                        },
                        "review_request": (
                            "Check whether this is the best next workflow step. Request read-only context tools "
                            "only if the supplied recommendation is insufficient."
                        ),
                    },
                    indent=2,
                ),
            }
        ],
        output_type=LiveOrchestratorReviewTurn,
    )
    assert isinstance(parsed, LiveOrchestratorReviewTurn)
    return parsed


def agent_trace_quality(project_name: str) -> dict[str, object]:
    return grade_agent_traces(load_agent_traces(project_name))


def sprint_preimplementation_gate(project_name: str, requirement_id: str) -> tuple[str, str] | None:
    requirements = parse_requirements(_requirements_path(project_name))
    tasks = parse_tasks(_tasks_path(project_name))
    requirement_by_id = {item["id"]: item for item in requirements}
    requirement = requirement_by_id.get(requirement_id)
    if requirement is None:
        return None

    linked_pending_tasks = [
        task
        for task in tasks
        if task["status"] in {"TODO", "IN_PROGRESS"} and requirement_id in task.get("requirements", [])
    ]
    if not linked_pending_tasks:
        return None

    if requirement_has_structural_trigger(requirement):
        return (
            "Architect",
            f"{requirement_id} has pending task work and introduces structural change, so Architect should review it before implementation continues.",
        )
    if requirement_has_experience_trigger(requirement):
        return (
            "Experience Designer",
            f"{requirement_id} has pending task work and is experience-heavy enough that usability/workflow review should happen before implementation continues.",
        )
    if requirement_has_ui_trigger(requirement):
        return (
            "UI Designer",
            f"{requirement_id} has pending task work and is UI-heavy enough that design review should happen before implementation continues.",
        )
    return None


def list_pm_clarifications(project_name: str) -> list[PMClarification]:
    raw_items = _load_pm_clarifications(project_name)
    return [
        PMClarification(
            clarification_id=str(item["clarification_id"]),
            project_name=str(item["project_name"]),
            requirement_id=str(item["requirement_id"]),
            requirement_title=str(item.get("requirement_title", "")),
            source_thread_id=str(item.get("source_thread_id", "")),
            summary=str(item.get("summary", "")),
            questions=tuple(str(question) for question in item.get("questions", [])),
            status=str(item.get("status", "")),
            created_at=str(item.get("created_at", "")),
            resolved_at=str(item.get("resolved_at", "")),
        )
        for item in sorted(raw_items, key=lambda candidate: str(candidate.get("created_at", "")), reverse=True)
    ]


def active_pm_clarifications(project_name: str) -> list[PMClarification]:
    return [item for item in list_pm_clarifications(project_name) if item.status == "OPEN"]


def active_requirement_clarifications(project_name: str, requirement_id: str) -> list[PMClarification]:
    return [
        item
        for item in active_pm_clarifications(project_name)
        if item.requirement_id == requirement_id
    ]


def save_pm_clarification(
    project_name: str,
    *,
    requirement_id: str,
    requirement_title: str,
    source_thread_id: str = "",
    summary: str,
    questions: list[str],
) -> PMClarification:
    clarification = create_pm_clarification(
        _pm_clarifications_path(project_name),
        project_name=project_name,
        requirement_id=requirement_id,
        requirement_title=requirement_title,
        source_thread_id=source_thread_id,
        summary=summary,
        questions=questions,
    )
    return PMClarification(
        clarification_id=str(clarification["clarification_id"]),
        project_name=str(clarification["project_name"]),
        requirement_id=str(clarification["requirement_id"]),
        requirement_title=str(clarification["requirement_title"]),
        source_thread_id=str(clarification.get("source_thread_id", "")),
        summary=str(clarification["summary"]),
        questions=tuple(str(question) for question in clarification["questions"]),
        status=str(clarification["status"]),
        created_at=str(clarification["created_at"]),
        resolved_at=str(clarification.get("resolved_at", "")),
    )


def resolve_pm_clarification(project_name: str, clarification_id: str) -> PMClarification:
    matching = _resolve_pm_clarification_raw(project_name, clarification_id)
    return PMClarification(
        clarification_id=str(matching["clarification_id"]),
        project_name=str(matching["project_name"]),
        requirement_id=str(matching["requirement_id"]),
        requirement_title=str(matching.get("requirement_title", "")),
        source_thread_id=str(matching.get("source_thread_id", "")),
        summary=str(matching.get("summary", "")),
        questions=tuple(str(question) for question in matching.get("questions", [])),
        status=str(matching.get("status", "")),
        created_at=str(matching.get("created_at", "")),
        resolved_at=str(matching.get("resolved_at", "")),
    )


def answer_pm_clarification(project_name: str, clarification_id: str, reply: str) -> PMClarification:
    clarifications = _load_pm_clarifications(project_name)
    matching = next(
        (item for item in clarifications if str(item.get("clarification_id", "")) == clarification_id),
        None,
    )
    if matching is None:
        raise ValueError(f"PM clarification not found: {clarification_id}")

    source_thread_id = str(matching.get("source_thread_id", "")).strip()
    if not source_thread_id:
        return resolve_pm_clarification(project_name, clarification_id)

    raw_threads = _load_agent_threads()
    thread = next(
        (
            item
            for item in raw_threads
            if str(item.get("project_name", "")) == project_name
            and str(item.get("thread_id", "")) == source_thread_id
            and str(item.get("agent_name", "")) == "PM"
            and str(item.get("mode", "")) == "Requirement Discovery"
        ),
        None,
    )
    if thread is None:
        raise ValueError(f"Linked PM thread not found for clarification: {clarification_id}")

    thread.setdefault("messages", [])
    thread["messages"].append(_agent_message("user", reply))
    thread["status"] = "active"
    turn = _run_live_pm_turn(project_name, project_name, _agent_thread_messages(thread))
    _resolve_pm_clarification_raw(project_name, clarification_id)
    _apply_live_pm_turn_to_thread(project_name, thread, turn)
    thread["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return resolve_pm_clarification(project_name, clarification_id)


def list_experience_findings(project_name: str) -> list[ExperienceFinding]:
    raw_findings = _load_experience_findings()
    project_findings = [finding for finding in raw_findings if finding.get("project_name") == project_name]
    return [
        ExperienceFinding(
            finding_id=str(finding["finding_id"]),
            project_name=str(finding["project_name"]),
            user_problem=str(finding["user_problem"]),
            affected_workflow=str(finding["affected_workflow"]),
            evidence=str(finding["evidence"]),
            confidence=str(finding["confidence"]),
            severity=str(finding["severity"]),
            frequency=str(finding["frequency"]),
            recommendation_type=str(finding["recommendation_type"]),
            rationale=str(finding["rationale"]),
            recommended_next_role=str(finding["recommended_next_role"]),
            handoff_state=str(finding["handoff_state"]),
            created_at=str(finding["created_at"]),
        )
        for finding in sorted(project_findings, key=lambda item: str(item["created_at"]), reverse=True)
    ]


def list_implementation_runs(project_name: str | None = None) -> list[ImplementationRun]:
    raw_runs = _load_implementation_runs()
    filtered_runs = raw_runs
    if project_name is not None:
        filtered_runs = [run for run in raw_runs if run.get("project_name") == project_name]
    return [
        _implementation_run_from_dict(run)
        for run in sorted(filtered_runs, key=lambda item: str(item.get("created_at", "")), reverse=True)
    ]


def _read_text_excerpt(path_str: str, *, max_chars: int = 2400, tail_lines: int | None = None) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return ""
    if tail_lines is not None:
        lines = text.splitlines()
        text = "\n".join(lines[-tail_lines:])
    if len(text) <= max_chars:
        return text
    return "...\n" + text[-max_chars:]


def implementation_run_inspection(run: ImplementationRun) -> ImplementationRunInspection:
    if run.status in IMPLEMENTATION_ACTIVE_STATES:
        tone: Literal["active", "completed", "failed", "stale"] = "active"
        display_status = run.status.title()
    elif run.status == "COMPLETED":
        tone = "completed"
        display_status = "Completed"
    elif IMPLEMENTATION_STALE_ERROR_FRAGMENT in run.error:
        tone = "stale"
        display_status = "Failed (stale worker)"
    else:
        tone = "failed"
        display_status = "Failed"

    output_excerpt = _read_text_excerpt(run.output_path, max_chars=2000)
    log_excerpt = _read_text_excerpt(run.log_path, max_chars=2400, tail_lines=40)
    return ImplementationRunInspection(
        run=run,
        display_status=display_status,
        tone=tone,
        output_available=bool(run.output_path and Path(run.output_path).exists()),
        log_available=bool(run.log_path and Path(run.log_path).exists()),
        output_excerpt=output_excerpt,
        log_excerpt=log_excerpt,
    )


def recent_implementation_run_inspections(
    project_name: str,
    *,
    limit: int = 8,
) -> list[ImplementationRunInspection]:
    runs = list_implementation_runs(project_name)
    return [implementation_run_inspection(run) for run in runs[:limit]]


def _timeline_message_snippet(thread: AgentThread) -> str:
    latest_assistant = next((message for message in reversed(thread.messages) if message.role == "assistant"), None)
    if latest_assistant is not None and latest_assistant.content.strip():
        return latest_assistant.content.strip()
    if thread.draft_title.strip():
        return thread.draft_title.strip()
    if thread.idea.strip():
        return thread.idea.strip()
    return f"{thread.agent_name} {thread.mode} thread."


def _thread_timeline_event(thread: AgentThread) -> WorkflowTimelineEvent:
    status_bucket_map = {
        "active": "waiting",
        "blocked_clarification": "blocked",
        "pending_approval": "approval",
        "drafted": "recorded",
        "saved": "completed",
        "archived": "completed",
    }
    summary_map = {
        "active": "Thread is active and waiting on the next turn.",
        "blocked_clarification": "Thread is blocked on a PM clarification before it can continue.",
        "pending_approval": "Draft is waiting for approval before the workflow can continue.",
        "drafted": "Draft is ready for review in the agent workspace.",
        "saved": "Thread outcome has been saved into a durable project artifact.",
        "archived": "Thread has been archived after its downstream workflow completed.",
    }
    status_bucket = status_bucket_map.get(thread.status, "recorded")
    summary = summary_map.get(thread.status, _timeline_message_snippet(thread))
    detail = _timeline_message_snippet(thread)
    if thread.draft_title.strip() and detail != thread.draft_title.strip():
        detail = f"{thread.draft_title.strip()}\n\n{detail}"
    return WorkflowTimelineEvent(
        event_id=f"thread:{thread.thread_id}:{thread.updated_at or thread.created_at}",
        project_name=thread.project_name,
        occurred_at=thread.updated_at or thread.created_at,
        title=f"{thread.agent_name} · {thread.mode}",
        summary=summary,
        actor=thread.agent_name,
        artifact_kind="agent thread",
        artifact_id=thread.thread_id,
        status_bucket=status_bucket,
        detail=detail,
    )


def _approval_created_event(approval: ApprovalRequest) -> WorkflowTimelineEvent:
    return WorkflowTimelineEvent(
        event_id=f"approval-created:{approval.approval_id}",
        project_name=approval.project_name,
        occurred_at=approval.created_at,
        title=approval.title,
        summary=approval.summary,
        actor=approval.source_agent_name,
        artifact_kind="approval",
        artifact_id=approval.approval_id,
        status_bucket="approval",
        detail=f"{approval.approval_type.replace('_', ' ')} requested by {approval.source_agent_name}.",
    )


def _approval_resolved_event(approval: ApprovalRequest) -> WorkflowTimelineEvent | None:
    if not approval.resolved_at:
        return None
    outcome_detail = approval.payload.get("outcome_detail", "").strip()
    outcome_title = approval.payload.get("outcome_title", "").strip()
    outcome_reference = approval.payload.get("outcome_reference_id", "").strip()
    detail_parts = [part for part in [outcome_detail, outcome_title, outcome_reference] if part]
    return WorkflowTimelineEvent(
        event_id=f"approval-resolved:{approval.approval_id}",
        project_name=approval.project_name,
        occurred_at=approval.resolved_at,
        title=f"{approval.title} — {approval.status.title()}",
        summary=outcome_detail or f"Approval was {approval.status.lower()}.",
        actor="Product Director",
        artifact_kind="approval outcome",
        artifact_id=approval.approval_id,
        status_bucket="completed",
        detail=" · ".join(detail_parts),
    )


def _clarification_created_event(clarification: PMClarification) -> WorkflowTimelineEvent:
    return WorkflowTimelineEvent(
        event_id=f"clarification-created:{clarification.clarification_id}",
        project_name=clarification.project_name,
        occurred_at=clarification.created_at,
        title=f"PM clarification · {clarification.requirement_id}",
        summary=clarification.summary,
        actor="PM",
        artifact_kind="clarification",
        artifact_id=clarification.clarification_id,
        status_bucket="blocked",
        detail="\n".join(clarification.questions),
    )


def _clarification_resolved_event(clarification: PMClarification) -> WorkflowTimelineEvent | None:
    if clarification.status != "RESOLVED":
        return None
    occurred_at = clarification.resolved_at or clarification.created_at
    return WorkflowTimelineEvent(
        event_id=f"clarification-resolved:{clarification.clarification_id}",
        project_name=clarification.project_name,
        occurred_at=occurred_at,
        title=f"PM clarification resolved · {clarification.requirement_id}",
        summary="Clarification was answered and the blocked workflow could continue.",
        actor="Product Director",
        artifact_kind="clarification",
        artifact_id=clarification.clarification_id,
        status_bucket="completed",
        detail=clarification.summary,
    )


def _experience_finding_event(finding: ExperienceFinding) -> WorkflowTimelineEvent:
    active_states = {"ready_for_pm_review", "ready_for_product_director", "handoff_prepared", "routed"}
    status_bucket = "routed" if finding.handoff_state in active_states else "completed"
    return WorkflowTimelineEvent(
        event_id=f"finding:{finding.finding_id}:{finding.created_at}",
        project_name=finding.project_name,
        occurred_at=finding.created_at,
        title="Experience finding saved",
        summary=finding.user_problem,
        actor="Experience Designer",
        artifact_kind="experience finding",
        artifact_id=finding.finding_id,
        status_bucket=status_bucket,
        detail=f"{finding.handoff_state} -> {finding.recommended_next_role}",
    )


def _implementation_run_events(run: ImplementationRun) -> list[WorkflowTimelineEvent]:
    inspected = implementation_run_inspection(run)
    events = [
        WorkflowTimelineEvent(
            event_id=f"run-created:{run.run_id}",
            project_name=run.project_name,
            occurred_at=run.created_at,
            title=f"Implementation queued · {run.requirement_id}",
            summary=f"{run.requirement_title}",
            actor="Engineer",
            artifact_kind="implementation run",
            artifact_id=run.run_id,
            status_bucket="running" if run.status in IMPLEMENTATION_ACTIVE_STATES else "recorded",
            detail=f"Run created for {run.requirement_id}.",
        )
    ]
    if run.finished_at:
        events.append(
            WorkflowTimelineEvent(
                event_id=f"run-finished:{run.run_id}",
                project_name=run.project_name,
                occurred_at=run.finished_at,
                title=f"Implementation {inspected.display_status.lower()} · {run.requirement_id}",
                summary=run.summary or run.error or implementation_progress_message(run.status),
                actor="Engineer",
                artifact_kind="implementation run",
                artifact_id=run.run_id,
                status_bucket="completed" if inspected.tone == "completed" else "blocked",
                detail=f"{run.requirement_title}",
            )
        )
    return events


def workflow_timeline_events(project_name: str, *, limit: int = 16) -> list[WorkflowTimelineEvent]:
    events: list[WorkflowTimelineEvent] = []

    events.extend(_thread_timeline_event(thread) for thread in list_agent_threads(project_name))
    for approval in list_approvals(project_name):
        events.append(_approval_created_event(approval))
        resolved = _approval_resolved_event(approval)
        if resolved is not None:
            events.append(resolved)
    for clarification in list_pm_clarifications(project_name):
        events.append(_clarification_created_event(clarification))
        resolved = _clarification_resolved_event(clarification)
        if resolved is not None:
            events.append(resolved)
    events.extend(_experience_finding_event(finding) for finding in list_experience_findings(project_name))
    for run in list_implementation_runs(project_name):
        events.extend(_implementation_run_events(run))

    ordered = sorted(events, key=lambda item: item.occurred_at, reverse=True)
    return ordered[:limit]


def _worker_process_alive(worker_pid: int | None) -> bool:
    if worker_pid is None or worker_pid <= 0:
        return False
    try:
        os.kill(worker_pid, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        return False
    return True


def _iso_age_minutes(value: str) -> float | None:
    if not value:
        return None
    try:
        created = datetime.fromisoformat(value)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - created).total_seconds() / 60.0


def reconcile_implementation_runs(project_name: str | None = None) -> list[ImplementationRun]:
    raw_runs = _load_implementation_runs()
    now = datetime.now(timezone.utc).isoformat()
    changed = False
    for run in raw_runs:
        if project_name is not None and run.get("project_name") != project_name:
            continue
        status = str(run.get("status", "")).upper()
        if status not in IMPLEMENTATION_ACTIVE_STATES:
            continue

        worker_pid = run.get("worker_pid")
        if worker_pid is not None:
            try:
                worker_pid = int(worker_pid)
            except (TypeError, ValueError):
                worker_pid = None

        age_minutes = _iso_age_minutes(str(run.get("started_at") or run.get("created_at") or ""))
        alive = _worker_process_alive(worker_pid)
        if alive:
            continue

        if worker_pid is None and (age_minutes is None or age_minutes < IMPLEMENTATION_STALE_MINUTES):
            continue

        run["status"] = "FAILED"
        run["finished_at"] = now
        run["error"] = (
            "Implementation worker is no longer running, so this run was marked failed during reconciliation."
        )
        changed = True

    if changed:
        _save_implementation_runs(raw_runs)

    return list_implementation_runs(project_name)


def active_implementation_run(project_name: str | None = None) -> ImplementationRun | None:
    reconcile_implementation_runs(project_name)
    return next(
        (
            run
            for run in list_implementation_runs(project_name)
            if run.status in IMPLEMENTATION_ACTIVE_STATES
        ),
        None,
    )


def latest_requirement_implementation(project_name: str, requirement_id: str) -> ImplementationRun | None:
    reconcile_implementation_runs(project_name)
    return next(
        (
            run
            for run in list_implementation_runs(project_name)
            if run.requirement_id == requirement_id
        ),
        None,
    )


def plan_sprint_requirement(project_name: str, requirement_id: str) -> SprintPlan:
    try:
        requirement_map = _requirement_by_id(project_name)
    except FileNotFoundError:
        requirement_map = {}
    record = requirement_map.get(requirement_id)
    if record is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    if record.status not in {"NEW", "BACKLOG"}:
        raise ValueError(f"Only NEW or BACKLOG requirements can be added to a sprint: {requirement_id}")

    existing = load_sprint_plan(project_name)
    if existing is not None and existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot change the sprint plan while a sprint is active or blocked.")

    created_at = existing.created_at if existing is not None else datetime.now(timezone.utc).isoformat()
    requirement_ids = tuple(existing.requirement_ids) if existing is not None else ()
    if requirement_id in requirement_ids:
        return existing

    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=(*requirement_ids, requirement_id),
        created_at=created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def remove_sprint_requirement(project_name: str, requirement_id: str) -> SprintPlan | None:
    existing = load_sprint_plan(project_name)
    if existing is None:
        return None
    if existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot change the sprint plan while a sprint is active or blocked.")

    remaining = tuple(item for item in existing.requirement_ids if item != requirement_id)
    if not remaining:
        _save_sprint_plan_raw(project_name, None)
        return None

    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=remaining,
        created_at=existing.created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def move_sprint_requirement(project_name: str, requirement_id: str, delta: int) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint plan exists for this project.")
    if existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot reorder the sprint plan while a sprint is active or blocked.")
    if requirement_id not in existing.requirement_ids:
        raise ValueError(f"Requirement not found in sprint: {requirement_id}")

    ids = list(existing.requirement_ids)
    current_index = ids.index(requirement_id)
    target_index = current_index + delta
    if target_index < 0 or target_index >= len(ids):
        return existing

    ids[current_index], ids[target_index] = ids[target_index], ids[current_index]
    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=tuple(ids),
        created_at=existing.created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def _clear_sprint_if_empty(project_name: str, plan: SprintPlan) -> SprintPlan | None:
    if plan.requirement_ids:
        return plan
    _save_sprint_plan_raw(project_name, None)
    return None


def _blocked_sprint(plan: SprintPlan, requirement_id: str, reason: str) -> SprintPlan:
    return _replace_sprint_plan(
        plan.project_name,
        status="BLOCKED",
        requirement_ids=plan.requirement_ids,
        created_at=plan.created_at,
        started_at=plan.started_at,
        completed_at="",
        current_requirement_id=requirement_id,
        blocked_reason=reason,
    )


def _release_delivery_is_approved(project_name: str, requirement_id: str) -> bool:
    return any(
        approval.approval_type == "release_delivery"
        and approval.source_thread_id == f"release-delivery:{requirement_id}"
        and approval.status == "APPROVED"
        and approval.payload.get("release_state") == "published"
        for approval in list_approvals(project_name)
    )


def complete_sprint(project_name: str) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint exists for this project.")
    if existing.status != "READY_TO_CLOSE":
        raise ValueError("Sprint is not ready for completion confirmation.")

    return _replace_sprint_plan(
        project_name,
        status="COMPLETED",
        requirement_ids=(),
        created_at=existing.created_at,
        started_at=existing.started_at,
        completed_at=existing.completed_at or datetime.now(timezone.utc).isoformat(),
        current_requirement_id="",
        blocked_reason="",
    )


def advance_active_sprint(project_name: str) -> SprintPlan | None:
    plan = load_sprint_plan(project_name)
    if plan is None or plan.status != "ACTIVE":
        return plan

    requirement_map = _requirement_by_id(project_name)
    valid_requirement_ids = tuple(item for item in plan.requirement_ids if item in requirement_map)
    if valid_requirement_ids != plan.requirement_ids:
        plan = _replace_sprint_plan(
            project_name,
            status=plan.status,
            requirement_ids=valid_requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at=plan.completed_at,
            current_requirement_id=plan.current_requirement_id,
            blocked_reason=plan.blocked_reason,
        )
        if plan is None:
            return None

    active_run = active_implementation_run(project_name)
    if active_run is not None:
        return _replace_sprint_plan(
            project_name,
            status="ACTIVE",
            requirement_ids=plan.requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at="",
            current_requirement_id=active_run.requirement_id,
            blocked_reason="",
        )

    for requirement_id in plan.requirement_ids:
        record = requirement_map.get(requirement_id)
        if record is None:
            continue
        if record.status == "DONE":
            continue

        latest_run = latest_requirement_implementation(project_name, requirement_id)
        was_backlog = record.status == "BACKLOG"
        if was_backlog:
            record = RequirementRecord(
                id=record.id,
                title=record.title,
                status="NEW",
                priority=record.priority,
                effort=record.effort,
                description=record.description,
                ui_runtime=record.ui_runtime,
            )
            update_requirement(project_name, record)
            requirement_map[requirement_id] = record

        if not was_backlog and latest_run is not None and latest_run.status == "COMPLETED":
            try:
                request_release_delivery_approval(
                    project_name,
                    RequirementRecord(
                        id=record.id,
                        title=record.title,
                        status="DONE",
                        priority=record.priority,
                        effort=record.effort,
                        description=record.description,
                        ui_runtime=record.ui_runtime,
                    ),
                )
            except ValueError as exc:
                return _blocked_sprint(plan, requirement_id, str(exc))
            return _blocked_sprint(
                plan,
                requirement_id,
                f"{requirement_id} has completed implementation and is waiting for release delivery approval.",
            )

        if not was_backlog and latest_run is not None and latest_run.status == "FAILED":
            reason = (
                latest_run.error.strip()
                or latest_run.summary.strip()
                or "This sprint requirement needs attention before the sprint can continue."
            )
            return _blocked_sprint(plan, requirement_id, reason)

        if not implementation_entry_allowed(record):
            return _blocked_sprint(
                plan,
                requirement_id,
                "This requirement is no longer eligible for implementation from the sprint flow.",
            )

        gate = sprint_preimplementation_gate(project_name, requirement_id)
        if gate is not None:
            role, reason = gate
            return _blocked_sprint(
                plan,
                requirement_id,
                f"Sprint paused for {role}: {reason}",
            )

        run = start_requirement_implementation(project_name, record)
        return _replace_sprint_plan(
            project_name,
            status="ACTIVE",
            requirement_ids=plan.requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at="",
            current_requirement_id=run.requirement_id,
            blocked_reason="",
        )

    return _replace_sprint_plan(
        project_name,
        status="READY_TO_CLOSE",
        requirement_ids=plan.requirement_ids,
        created_at=plan.created_at,
        started_at=plan.started_at,
        completed_at=datetime.now(timezone.utc).isoformat(),
        current_requirement_id="",
        blocked_reason="",
    )


def start_sprint(project_name: str) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None or not existing.requirement_ids:
        raise ValueError("Add at least one backlog requirement to the sprint before starting it.")
    if existing.status == "ACTIVE":
        return advance_active_sprint(project_name) or existing
    if active_implementation_run(project_name) is not None:
        raise RuntimeError("A requirement implementation run is already active in this project.")

    active_plan = _replace_sprint_plan(
        project_name,
        status="ACTIVE",
        requirement_ids=existing.requirement_ids,
        created_at=existing.created_at,
        started_at=existing.started_at or datetime.now(timezone.utc).isoformat(),
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )
    return advance_active_sprint(project_name) or active_plan


def continue_sprint(project_name: str) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint exists for this project.")
    if existing.status == "COMPLETED":
        return existing
    active_plan = _replace_sprint_plan(
        project_name,
        status="ACTIVE",
        requirement_ids=existing.requirement_ids,
        created_at=existing.created_at,
        started_at=existing.started_at or datetime.now(timezone.utc).isoformat(),
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )
    return advance_active_sprint(project_name) or active_plan


def advance_all_active_sprints() -> None:
    for project_dir in iter_projects():
        plan = load_sprint_plan(project_dir.name)
        if plan is not None and plan.status == "ACTIVE":
            advance_active_sprint(project_dir.name)


def implementation_entry_allowed(record: RequirementRecord) -> bool:
    return record.status in {"NEW", "IN_PROGRESS"}


def implementation_progress_percent(status: str) -> int:
    return IMPLEMENTATION_PROGRESS_BY_STATUS.get(status.upper(), 0)


def implementation_progress_message(status: str) -> str:
    return IMPLEMENTATION_PROGRESS_MESSAGE_BY_STATUS.get(
        status.upper(),
        "Implementation status is being prepared.",
    )


def _project_path(project_name: str) -> Path:
    try:
        return resolve_project(project_name).workspace_path
    except ValueError:
        candidates = _candidate_project_paths(project_name)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        normalized_name = normalize_project_directory_name(project_name)
        if normalized_name:
            return REPO_ROOT / "projects" / normalized_name
        raise


def _sprint_path(project_name: str) -> Path:
    return _project_runtime_data_path(project_name) / "sprint.json"


def _load_sprint_plan_raw(project_name: str) -> dict[str, object] | None:
    path = _sprint_path(project_name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        return None
    return data


def _save_sprint_plan_raw(project_name: str, payload: dict[str, object] | None) -> None:
    path = _sprint_path(project_name)
    if payload is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def _sprint_plan_from_dict(raw_plan: dict[str, object], project_name: str) -> SprintPlan:
    return SprintPlan(
        project_name=project_name,
        status=str(raw_plan.get("status", "PLANNING")),
        requirement_ids=tuple(str(item) for item in raw_plan.get("requirement_ids", []) if str(item).strip()),
        created_at=str(raw_plan.get("created_at", "")),
        started_at=str(raw_plan.get("started_at", "")),
        completed_at=str(raw_plan.get("completed_at", "")),
        current_requirement_id=str(raw_plan.get("current_requirement_id", "")),
        blocked_reason=str(raw_plan.get("blocked_reason", "")),
    )


def load_sprint_plan(project_name: str) -> SprintPlan | None:
    raw_plan = _load_sprint_plan_raw(project_name)
    if raw_plan is None:
        return None
    return _sprint_plan_from_dict(raw_plan, project_name)


def _persist_sprint_plan(plan: SprintPlan | None) -> SprintPlan | None:
    if plan is None:
        return None
    _save_sprint_plan_raw(
        plan.project_name,
        {
            "status": plan.status,
            "requirement_ids": list(plan.requirement_ids),
            "created_at": plan.created_at,
            "started_at": plan.started_at,
            "completed_at": plan.completed_at,
            "current_requirement_id": plan.current_requirement_id,
            "blocked_reason": plan.blocked_reason,
        },
    )
    return plan


def _replace_sprint_plan(
    project_name: str,
    *,
    status: str,
    requirement_ids: tuple[str, ...],
    created_at: str,
    started_at: str,
    completed_at: str,
    current_requirement_id: str,
    blocked_reason: str,
) -> SprintPlan:
    return _persist_sprint_plan(
        SprintPlan(
            project_name=project_name,
            status=status,
            requirement_ids=requirement_ids,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            current_requirement_id=current_requirement_id,
            blocked_reason=blocked_reason,
        )
    )


def _requirement_by_id(project_name: str) -> dict[str, RequirementRecord]:
    document = load_requirement_document(project_name)
    return {
        record.id: record
        for record in (document.active_requirements + document.backlog_requirements)
    }


def sprint_requirement_records(project_name: str) -> tuple[RequirementRecord, ...]:
    plan = load_sprint_plan(project_name)
    if plan is None:
        return ()
    requirement_map = _requirement_by_id(project_name)
    return tuple(
        requirement_map[requirement_id]
        for requirement_id in plan.requirement_ids
        if requirement_id in requirement_map
    )


def _preview_port(project_name: str) -> int:
    digest = hashlib.sha1(project_name.encode("utf-8")).hexdigest()
    return PREVIEW_PORT_BASE + (int(digest[:8], 16) % PREVIEW_PORT_SPAN)


def _streamlit_preview_command(entry_path: Path, port: int) -> tuple[str, ...]:
    return (
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(entry_path),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    )


def _web_app_preview_command(port: int) -> tuple[str, ...]:
    return (
        "npm",
        "run",
        "dev",
        "--",
        "--hostname",
        "127.0.0.1",
        "--port",
        str(port),
    )


def _web_app_preview_readiness_issue(project_dir: Path) -> str | None:
    package_json = project_dir / "package.json"
    if not package_json.exists():
        return "Web app preview is unavailable because this project does not expose package.json."
    return None


def _web_app_preview_dependencies_installed(project_dir: Path) -> bool:
    return (project_dir / "node_modules" / ".bin" / "next").exists()


def _ensure_web_app_preview_dependencies(project_dir: Path) -> None:
    if _web_app_preview_dependencies_installed(project_dir):
        return
    if shutil.which("npm") is None:
        raise RuntimeError(
            "Web app preview could not prepare this project because npm is not installed or is not on PATH."
        )
    result = subprocess.run(
        ["npm", "install"],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or "npm install failed."
        raise RuntimeError(f"Web app preview could not install frontend dependencies. {detail}")
    if not _web_app_preview_dependencies_installed(project_dir):
        raise RuntimeError(
            "Web app preview finished installing dependencies, but the Next.js dev server is still unavailable."
        )


def _wait_for_preview_port(port: int, *, timeout_seconds: float = 8.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _local_port_accepts_connections(port):
            return True
        time.sleep(0.2)
    return _local_port_accepts_connections(port)


def _project_preview_env_overrides(project_name: str) -> dict[str, str]:
    if project_name != "learning-agent":
        return {}
    return {
        "LEARNING_AGENT_AUTH_MODE": "local",
        "LEARNING_AGENT_LOCAL_USER": "preview@learning-agent.local",
        "AI_BUILDER_OS_RUNTIME_ROOT": "/private/tmp/learning-agent-runtime",
    }


def _process_cwd(pid: int) -> str:
    result = subprocess.run(
        ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        if line.startswith("n"):
            return line[1:].strip()
    return ""


def _process_listening_ports(pid: int) -> tuple[int, ...]:
    result = subprocess.run(
        ["lsof", "-nP", "-a", "-p", str(pid), "-iTCP", "-sTCP:LISTEN", "-Fn"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ()
    ports: list[int] = []
    for line in result.stdout.splitlines():
        if not line.startswith("n"):
            continue
        name = line[1:].strip()
        if ":" not in name:
            continue
        port_text = name.rsplit(":", 1)[-1]
        try:
            ports.append(int(port_text))
        except ValueError:
            continue
    return tuple(dict.fromkeys(ports))


def _candidate_web_app_preview_pids() -> tuple[int, ...]:
    result = subprocess.run(
        ["ps", "ax", "-o", "pid=,command="],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ()
    pids: list[int] = []
    for line in result.stdout.splitlines():
        raw = line.strip()
        if not raw:
            continue
        parts = raw.split(None, 1)
        if not parts:
            continue
        try:
            pid = int(parts[0])
        except ValueError:
            continue
        command = parts[1] if len(parts) > 1 else ""
        if "next-server" in command or ("npm" in command and "run" in command and "dev" in command):
            pids.append(pid)
    return tuple(dict.fromkeys(pids))


def _running_web_app_preview_port(project_dir: Path) -> int | None:
    project_dir = project_dir.resolve()
    for pid in _candidate_web_app_preview_pids():
        cwd = _process_cwd(pid)
        if not cwd:
            continue
        try:
            cwd_path = Path(cwd).resolve()
        except OSError:
            continue
        if cwd_path != project_dir:
            continue
        ports = _process_listening_ports(pid)
        if ports:
            return ports[0]
    return None


def project_preview(project_name: str) -> ProjectPreview:
    project_dir = _project_path(project_name)
    profile = project_runtime_profile(load_project_ui_runtime(project_name))
    if profile.runtime == "web_app":
        running_port = _running_web_app_preview_port(project_dir)
        package_json = project_dir / "package.json"
        readiness_issue = _web_app_preview_readiness_issue(project_dir)
        if running_port is not None and package_json.exists():
            return ProjectPreview(
                project_name=project_name,
                available=True,
                runtime="web_app",
                entry_path=package_json,
                url=f"http://localhost:{running_port}",
                command=_web_app_preview_command(running_port),
                status_text="Web app preview is available through the Vercel-compatible dev server.",
            )
        if readiness_issue is None and package_json.exists():
            port = _running_web_app_preview_port(project_dir) or _preview_port(project_name)
            if _web_app_preview_dependencies_installed(project_dir):
                status_text = "Web app preview is available through the Vercel-compatible dev server."
            else:
                status_text = "Web app preview will install frontend dependencies automatically the first time you start it."
            return ProjectPreview(
                project_name=project_name,
                available=True,
                runtime="web_app",
                entry_path=package_json,
                url=f"http://localhost:{port}",
                command=_web_app_preview_command(port),
                status_text=status_text,
            )
        return ProjectPreview(
            project_name=project_name,
            available=False,
            runtime="web_app",
            entry_path=package_json if package_json.exists() else None,
            url="",
            command=(),
            status_text=readiness_issue or "Web app preview is unavailable because this project does not expose package.json.",
        )

    streamlit_entry = project_dir / "src" / "app.py"
    if streamlit_entry.exists():
        port = _preview_port(project_name)
        return ProjectPreview(
            project_name=project_name,
            available=True,
            runtime="streamlit",
            entry_path=streamlit_entry,
            url=f"http://localhost:{port}",
            command=_streamlit_preview_command(streamlit_entry, port),
            status_text="Streamlit project preview is available.",
        )

    return ProjectPreview(
        project_name=project_name,
        available=False,
        runtime="unavailable",
        entry_path=None,
        url="",
        command=(),
        status_text="Preview is unavailable because this project does not expose src/app.py.",
    )


def _local_port_accepts_connections(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _listener_pids(port: int) -> tuple[int, ...]:
    result = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        return ()
    pids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            pids.append(int(line))
        except ValueError:
            continue
    return tuple(dict.fromkeys(pids))


def _process_command(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _is_managed_preview_command(command: str) -> bool:
    return ("-m streamlit run" in command and "/projects/" in command and "/src/app.py" in command) or (
        "npm" in command and "run" in command and "dev" in command
    )


def _preview_process_matches(preview: ProjectPreview) -> bool:
    if not preview.available:
        return False
    if preview.runtime == "web_app":
        return _running_web_app_preview_port(_project_path(preview.project_name)) is not None
    entry_path = str(preview.entry_path)
    for pid in _listener_pids(_preview_port(preview.project_name)):
        command = _process_command(pid)
        if entry_path in command:
            return True
    return False


def _terminate_preview_processes(port: int) -> None:
    for pid in _listener_pids(port):
        command = _process_command(pid)
        if not _is_managed_preview_command(command):
            continue
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            continue


def project_preview_running(project_name: str) -> bool:
    preview = project_preview(project_name)
    if not preview.available:
        return False
    if preview.runtime == "web_app":
        return _running_web_app_preview_port(_project_path(project_name)) is not None
    port = _preview_port(project_name)
    if not _local_port_accepts_connections(port):
        return False
    return _preview_process_matches(preview)


def start_project_preview(project_name: str) -> ProjectPreview:
    preview = project_preview(project_name)
    if not preview.available:
        raise ValueError(preview.status_text)

    if preview.runtime == "web_app":
        running_port = _running_web_app_preview_port(_project_path(project_name))
        if running_port is not None:
            return ProjectPreview(
                project_name=preview.project_name,
                available=True,
                runtime=preview.runtime,
                entry_path=preview.entry_path,
                url=f"http://localhost:{running_port}",
                command=preview.command,
                status_text=preview.status_text,
            )
        _ensure_web_app_preview_dependencies(_project_path(project_name))
        preview = project_preview(project_name)

    port = _preview_port(project_name)
    if _local_port_accepts_connections(port):
        if _preview_process_matches(preview):
            return preview
        _terminate_preview_processes(port)

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    repo_pythonpath = str(REPO_ROOT)
    if existing_pythonpath:
        if repo_pythonpath not in existing_pythonpath.split(os.pathsep):
            env["PYTHONPATH"] = f"{repo_pythonpath}{os.pathsep}{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = repo_pythonpath
    env.update(_project_preview_env_overrides(project_name))

    subprocess.Popen(
        preview.command,
        cwd=str(_project_path(project_name)),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    if preview.runtime == "web_app" and not _wait_for_preview_port(port):
        raise RuntimeError(
            "Web app preview did not start successfully after preparing dependencies."
        )
    return preview


def _archive_active_agent_threads(
    project_name: str,
    raw_threads: list[dict[str, object]],
    *,
    agent_name: str,
    mode: str,
) -> None:
    for thread in raw_threads:
        if (
            thread.get("project_name") == project_name
            and thread.get("agent_name") == agent_name
            and thread.get("mode") == mode
            and thread.get("status") == "active"
        ):
            thread["status"] = "archived"
            thread["updated_at"] = datetime.now(timezone.utc).isoformat()


def _experience_next_role(recommendation_type: str) -> str:
    if recommendation_type == "scope escalation":
        return "Product Director"
    return "PM"


def _experience_handoff_state(recommendation_type: str) -> str:
    if recommendation_type == "scope escalation":
        return "ready_for_product_director"
    return "ready_for_pm_review"


def save_experience_finding(
    project_name: str,
    *,
    user_problem: str,
    affected_workflow: str,
    evidence: str,
    confidence: str,
    severity: str,
    frequency: str,
    recommendation_type: str,
    rationale: str,
) -> ExperienceFinding:
    raw_findings = _load_experience_findings()
    finding = {
        "finding_id": str(uuid4()),
        "project_name": project_name,
        "user_problem": user_problem.strip(),
        "affected_workflow": affected_workflow.strip(),
        "evidence": evidence.strip(),
        "confidence": confidence.strip(),
        "severity": severity.strip(),
        "frequency": frequency.strip(),
        "recommendation_type": recommendation_type.strip(),
        "rationale": rationale.strip(),
        "recommended_next_role": _experience_next_role(recommendation_type.strip()),
        "handoff_state": _experience_handoff_state(recommendation_type.strip()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    raw_findings.append(finding)
    _save_experience_findings(raw_findings)
    return ExperienceFinding(
        finding_id=str(finding["finding_id"]),
        project_name=str(finding["project_name"]),
        user_problem=str(finding["user_problem"]),
        affected_workflow=str(finding["affected_workflow"]),
        evidence=str(finding["evidence"]),
        confidence=str(finding["confidence"]),
        severity=str(finding["severity"]),
        frequency=str(finding["frequency"]),
        recommendation_type=str(finding["recommendation_type"]),
        rationale=str(finding["rationale"]),
        recommended_next_role=str(finding["recommended_next_role"]),
        handoff_state=str(finding["handoff_state"]),
        created_at=str(finding["created_at"]),
    )


def _resolve_codex_executable() -> Path:
    candidates = [Path.home() / ".codex" / "bin" / "codex"]
    candidates.extend(
        sorted(
            (Path.home() / ".vscode" / "extensions").glob("openai.chatgpt-*/bin/macos-aarch64/codex"),
            reverse=True,
        )
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find a local Codex executable for implementation runs.")


def build_requirement_implementation_prompt(project_name: str, requirement_id: str) -> str:
    requirement = next(
        (
            item
            for item in parse_requirements(_requirements_path(project_name))
            if item["id"] == requirement_id
        ),
        None,
    )
    extra_guidance: list[str] = []
    if requirement is not None:
        ui_runtime = normalize_ui_runtime(str(requirement.get("ui_runtime", "")) or load_project_ui_runtime(project_name))
        profile = project_runtime_profile(ui_runtime)
        extra_guidance.append(f"Project capability profile: {profile.label}. {profile.implementation_guidance}")
        extra_guidance.append(project_runtime_capability_summary(ui_runtime))
        decision = requirement_openai_runtime_decision(
            project_name,
            RequirementRecord(
                id=str(requirement.get("id", "")),
                title=str(requirement.get("title", "")),
                status=str(requirement.get("status", "")),
                priority=str(requirement.get("priority", "")),
                effort=str(requirement.get("effort", "")),
                description=str(requirement.get("description", "")),
                ui_runtime=str(requirement.get("ui_runtime", "")),
            ),
        )
        if decision.required:
            capability_list = ", ".join(decision.capabilities) or "general model reasoning"
            extra_guidance.append(
                f"Automatically inferred OpenAI runtime: {decision.surface}; capabilities: {capability_list}; "
                f"confidence: {decision.confidence}. {decision.rationale}"
            )
            extra_guidance.append(
                "Treat this as the recorded architecture decision. Validate it against the implementation context, "
                "use the smallest sufficient OpenAI surface, keep credentials in environment secrets, and cover model, tool, safety, cost, latency, and reliability behavior where relevant."
            )
        if ui_runtime == "web_app":
            extra_guidance.append(
                "Read the local `agent/capabilities/web-app-frontend/` bundle before finalizing frontend structure so implementation stays inside the bounded frontend-only slice."
            )
            site_import_summary = _site_import_context_summary(project_name)
            if site_import_summary:
                extra_guidance.append(site_import_summary)
                extra_guidance.append(
                    "This requirement includes grounded website-import context. When the user asked for replication or improvement of an existing site, reuse the imported source copy, navigation labels, and downloaded local assets wherever they are suitable. Do not default to generic placeholder marketing copy, invented testimonials, or abstract image substitutes unless the imported context is genuinely missing or the user explicitly asked for a rewrite."
                )
        if requirement_has_experience_trigger(requirement):
            extra_guidance.append(
                "This requirement is experience-related. Do not skip Experience Designer; use it to shape usability/workflow requirements before Engineer implementation."
            )
        if requirement_has_ui_trigger(requirement):
            extra_guidance.append(
                "This requirement is UI-related. Do not skip UI Designer; use it to shape design requirements, UI constraints, or design-brief-driven follow-up work before Engineer implementation."
            )
    return "\n".join(
        [
            f"You are continuing AI Builder OS workflow for project `{project_name}` and requirement `{requirement_id}`.",
            "Use the deterministic helper `python tools/orchestrator_status.py "
            f"{project_name}` as the routing source of truth before acting.",
            "Then execute the full OS workflow needed for this requirement without waiting for handoff approval unless genuinely blocked.",
            *extra_guidance,
            "Stay within the project scope, update file-backed state as work progresses, run relevant validation, and close requirement/task state when appropriate.",
            "Your final response must include:",
            "- what changed",
            "- validation results",
            "- whether the requirement is now done or still blocked",
            "- any error or follow-up needed",
        ]
    )


def _implementation_worker_script() -> Path:
    return _project_path("os-control-panel") / "tools" / "run_requirement_implementation.py"


def _implementation_command(run_id: str, project_name: str, requirement_id: str) -> list[str]:
    return [
        str(REPO_ROOT / ".venv" / "bin" / "python"),
        str(_implementation_worker_script()),
        "--run-id",
        run_id,
        "--project-name",
        project_name,
        "--requirement-id",
        requirement_id,
    ]


def update_implementation_run(
    run_id: str,
    *,
    status: str | None = None,
    summary: str | None = None,
    error: str | None = None,
    created_at: str | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
    output_path: str | None = None,
    log_path: str | None = None,
    worker_pid: int | None = None,
) -> ImplementationRun:
    raw_runs = _load_implementation_runs()
    matching = next((run for run in raw_runs if run.get("run_id") == run_id), None)
    if matching is None:
        raise ValueError(f"Implementation run not found: {run_id}")

    if status is not None:
        matching["status"] = status
    if summary is not None:
        matching["summary"] = summary
    if error is not None:
        matching["error"] = error
    if created_at is not None:
        matching["created_at"] = created_at
    if started_at is not None:
        matching["started_at"] = started_at
    if finished_at is not None:
        matching["finished_at"] = finished_at
    if output_path is not None:
        matching["output_path"] = output_path
    if log_path is not None:
        matching["log_path"] = log_path
    if worker_pid is not None:
        matching["worker_pid"] = worker_pid

    _save_implementation_runs(raw_runs)
    return _implementation_run_from_dict(matching)


def start_requirement_implementation(project_name: str, record: RequirementRecord) -> ImplementationRun:
    active_run = active_implementation_run(project_name)
    if active_run is not None:
        raise RuntimeError(
            f"Implementation is already active for {active_run.project_name} {active_run.requirement_id}."
        )

    if not implementation_entry_allowed(record):
        raise ValueError(f"{record.id} is not eligible for UI-initiated implementation.")

    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    output_path = IMPLEMENTATION_LOG_DIR / f"{run_id}-last-message.txt"
    log_path = IMPLEMENTATION_LOG_DIR / f"{run_id}.log"
    raw_runs = _load_implementation_runs()
    raw_run = {
        "run_id": run_id,
        "project_name": project_name,
        "requirement_id": record.id,
        "requirement_title": record.title,
        "status": "QUEUED",
        "summary": "",
        "error": "",
        "created_at": created_at,
        "started_at": "",
        "finished_at": "",
        "output_path": str(output_path),
        "log_path": str(log_path),
        "worker_pid": None,
    }
    raw_runs.append(raw_run)
    _save_implementation_runs(raw_runs)

    command = _implementation_command(run_id, project_name, record.id)
    try:
        with log_path.open("ab") as log_handle:
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except Exception as exc:
        return update_implementation_run(run_id, status="FAILED", error=str(exc), finished_at=datetime.now(timezone.utc).isoformat())

    return update_implementation_run(run_id, worker_pid=process.pid)


def set_experience_handoff_state(project_name: str, finding_id: str, handoff_state: str) -> ExperienceFinding:
    normalized_state = handoff_state.strip()
    if normalized_state not in EXPERIENCE_HANDOFF_STATES:
        raise ValueError(f"Invalid experience handoff state: {handoff_state}")

    raw_findings = _load_experience_findings()
    matching = next(
        (
            finding
            for finding in raw_findings
            if finding.get("project_name") == project_name and finding.get("finding_id") == finding_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Experience finding not found: {finding_id}")

    matching["handoff_state"] = normalized_state
    _save_experience_findings(raw_findings)
    return ExperienceFinding(
        finding_id=str(matching["finding_id"]),
        project_name=str(matching["project_name"]),
        user_problem=str(matching["user_problem"]),
        affected_workflow=str(matching["affected_workflow"]),
        evidence=str(matching["evidence"]),
        confidence=str(matching["confidence"]),
        severity=str(matching["severity"]),
        frequency=str(matching["frequency"]),
        recommendation_type=str(matching["recommendation_type"]),
        rationale=str(matching["rationale"]),
        recommended_next_role=str(matching["recommended_next_role"]),
        handoff_state=str(matching["handoff_state"]),
        created_at=str(matching["created_at"]),
    )


def build_discovery_draft(project_name: str, idea: str, answers: dict[str, str]) -> str:
    current_requirements = parse_requirements(_requirements_path(project_name))
    existing_titles = ", ".join(requirement["id"] for requirement in current_requirements) or "none yet"

    def answer(key: str, fallback: str) -> str:
        value = answers.get(key, "").strip()
        return value or fallback

    return "\n".join(
        [
            "Problem statement",
            f"- {answer('problem', idea.strip() or 'Clarify the primary problem this project should solve.')}",
            "",
            "Target user",
            f"- {answer('target_user', 'Clarify the primary user for this idea.')}",
            "",
            "Core job-to-be-done",
            f"- {answer('context', 'Clarify the current workflow or context this idea should improve.')}",
            "",
            "Success criteria",
            f"- {answer('success', 'Define what success looks like for the first version.')}",
            "",
            "Constraints",
            f"- {answer('constraints', 'Clarify the constraints or guardrails for the first version.')}",
            "",
            "Out of scope",
            f"- {answer('out_of_scope', 'Clarify what should not be included in the first version.')}",
            "",
            "Assumptions",
            f"- Existing requirement IDs in this project: {existing_titles}",
            f"- Initial idea entered: {idea.strip() or 'No initial idea was provided.'}",
            "",
            "Open questions",
            "- Which parts of this draft should become a new requirement versus a refinement of existing requirements?",
        ]
    )


def summarize_projects() -> list[ProjectSummary]:
    summaries: list[ProjectSummary] = []
    locations_by_path = {item.workspace_path.resolve(): item for item in list_project_locations()}
    for project_dir in iter_projects():
        location = locations_by_path[project_dir.resolve()]
        missing_paths = tuple(validate_project_structure(project_dir))
        requirements = parse_requirements(project_dir / "product" / "requirements.md")
        tasks = parse_tasks(project_dir / "product" / "tasks.md")

        requirement_counts: dict[str, int] = {}
        for requirement in requirements:
            status = requirement["status"]
            requirement_counts[status] = requirement_counts.get(status, 0) + 1

        task_counts: dict[str, int] = {}
        for task in tasks:
            status = task["status"]
            task_counts[status] = task_counts.get(status, 0) + 1

        new_requirements = tuple(
            RequirementSummary(
                id=requirement["id"],
                title=requirement["title"],
                status=requirement["status"],
            )
            for requirement in requirements
            if requirement["status"] == "NEW"
        )

        pending_tasks = tuple(
            TaskSummary(
                id=task["id"],
                title=task["title"],
                status=task["status"],
            )
            for task in tasks
            if task["status"] != "DONE"
        )

        summaries.append(
            ProjectSummary(
                name=project_dir.name,
                path=project_dir,
                structure_ok=not missing_paths,
                missing_paths=missing_paths,
                default_ui_runtime=load_project_ui_runtime(project_dir.name),
                requirement_counts=requirement_counts,
                new_requirements=new_requirements,
                task_counts=task_counts,
                pending_tasks=pending_tasks,
                project_id=location.project_id,
                mode=location.mode,
                visibility=location.visibility,
                ownership=location.ownership,
                repository=location.repository if location.visibility == "public" else "",
                default_branch=location.default_branch,
            )
        )

    return summaries


def workspace_totals(projects: list[ProjectSummary]) -> dict[str, int]:
    totals = {
        "projects": len(projects),
        "new_requirements": 0,
        "pending_tasks": 0,
    }
    for project in projects:
        totals["new_requirements"] += len(project.new_requirements)
        totals["pending_tasks"] += len(project.pending_tasks)
    return totals


def operations_dashboard_snapshot(
    projects: list[ProjectSummary] | None = None,
    *,
    activity_limit: int = 80,
) -> OperationsDashboardSnapshot:
    project_summaries = projects if projects is not None else summarize_projects()
    project_names = [project.name for project in project_summaries]
    traces_by_project = {project_name: load_agent_traces(project_name) for project_name in project_names}
    agent_runs = summarize_agent_runs(traces_by_project)
    role_performance = summarize_role_performance(agent_runs, role_modes=AGENT_ROLE_MODES)
    tool_usage = summarize_tool_usage(traces_by_project)
    all_inbox_items = workflow_inbox_items()
    approvals = tuple(active_approvals())

    workflow_health: list[ProjectWorkflowHealth] = []
    trace_quality: dict[str, dict[str, object]] = {}
    activity: list[OperationsActivity] = []
    for project in project_summaries:
        project_items = [item for item in all_inbox_items if item.project_name == project.name]
        project_approvals = [approval for approval in approvals if approval.project_name == project.name]
        project_clarifications = active_pm_clarifications(project.name)
        implementation_runs = list_implementation_runs(project.name)
        latest_review = latest_quality_review(project.name, mode="deterministic")
        trace_quality[project.name] = grade_agent_traces(traces_by_project[project.name])
        workflow_health.append(
            ProjectWorkflowHealth(
                project_name=project.name,
                new_requirements=project.requirement_counts.get("NEW", 0),
                in_progress_requirements=project.requirement_counts.get("IN_PROGRESS", 0),
                backlog_requirements=project.requirement_counts.get("BACKLOG", 0),
                pending_tasks=len(project.pending_tasks),
                blocked_items=sum(1 for item in project_items if item.status_bucket == "blocked"),
                open_approvals=len(project_approvals),
                open_clarifications=len(project_clarifications),
                routed_items=sum(1 for item in project_items if item.status_bucket == "routed"),
                active_runs=sum(1 for run in implementation_runs if run.status in IMPLEMENTATION_ACTIVE_STATES),
                failed_runs=sum(1 for run in implementation_runs if run.status == "FAILED"),
                quality_status=latest_review.status if latest_review is not None else "NOT RUN",
            )
        )
        for event in workflow_timeline_events(project.name, limit=24):
            activity.append(
                OperationsActivity(
                    occurred_at=event.occurred_at,
                    project_name=project.name,
                    actor=event.actor,
                    title=event.title,
                    status=event.status_bucket,
                    detail=event.summary or event.detail,
                )
            )

    for run in agent_runs:
        activity.append(
            OperationsActivity(
                occurred_at=run.finished_at or run.started_at,
                project_name=run.project_name,
                actor=run.role,
                title=f"Live agent run {run.status.replace('_', ' ')}",
                status=run.status,
                detail=(
                    f"{run.attempts} attempt(s), {run.steps} step(s), "
                    f"{len(run.tools)} tool call(s)"
                    + (f" · {run.hand_back_reason}" if run.hand_back_reason else "")
                ),
            )
        )

    learning = learning_progress_items()
    normalized_learning = {
        group: tuple(items)
        for group, items in learning.items()
    }
    high_risk_tools = tuple(
        definition.name
        for definition in TOOL_REGISTRY.values()
        if definition.risk == "high" or definition.approval_required
    )
    return OperationsDashboardSnapshot(
        agent_runs=tuple(agent_runs),
        role_performance=tuple(role_performance),
        tool_usage=tuple(tool_usage),
        workflow_health=tuple(sorted(workflow_health, key=lambda item: item.project_name.lower())),
        open_approvals=approvals,
        high_risk_tools=high_risk_tools,
        trace_quality=trace_quality,
        learning_progress=normalized_learning,
        active_learning_session=load_learning_agent_session(),
        activity=tuple(
            sorted(activity, key=lambda item: item.occurred_at, reverse=True)[:activity_limit]
        ),
        eval_coverage=EVAL_COVERAGE,
        eval_cases=load_eval_case_catalog(REPO_ROOT),
    )

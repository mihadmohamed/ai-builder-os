from __future__ import annotations

import json
from typing import Any


def activity_identity(activity: dict[str, Any]) -> str:
    return str(activity.get("id") or activity.get("activity_id") or "").strip()


def activity_title(activity: dict[str, Any]) -> str:
    return str(activity.get("name") or activity_identity(activity) or "Unnamed activity").strip()


def format_money(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "Cost unknown"
    return f"Cost {amount:.2f}"


def format_duration(value: Any) -> str:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return "Duration unknown"
    suffix = "hour" if hours == 1 else "hours"
    return f"{hours:g} {suffix}"


def format_age_range(activity: dict[str, Any]) -> str:
    min_age = activity.get("min_age", 0)
    max_age = activity.get("max_age", 99)
    return f"Ages {min_age}-{max_age}"


def format_tags(values: Any) -> str:
    if not values:
        return "No tags"
    if isinstance(values, str):
        tags = [item.strip() for item in values.split(",") if item.strip()]
    else:
        tags = [str(item).strip() for item in values if str(item).strip()]
    return ", ".join(tags) if tags else "No tags"


def activity_metadata(activity: dict[str, Any]) -> list[str]:
    return [
        str(activity.get("locality") or "Locality unknown"),
        format_money(activity.get("cost")),
        format_duration(activity.get("duration_hours")),
        str(activity.get("setting") or "Setting unknown"),
        format_age_range(activity),
    ]


def selected_activity_payloads(
    activities: list[dict[str, Any]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        activity
        for activity in activities
        if activity_identity(activity) and activity_identity(activity) in selected_ids
    ]


EXCLUSION_REASONS = {
    "not_local": "Different area",
    "age_range_mismatch": "Outside child age range",
    "over_budget": "Would exceed budget",
    "lower_ranked": "Lower ranked fit",
}


def readable_exclusion_reason(reason: str) -> str:
    return EXCLUSION_REASONS.get(reason, reason.replace("_", " ").title())


def format_activity_json(activities: list[dict[str, Any]]) -> str:
    return json.dumps(activities, indent=2)


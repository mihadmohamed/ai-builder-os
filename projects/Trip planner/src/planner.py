from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class PlanningError(ValueError):
    """Raised when planner input is missing required structured data."""


@dataclass(frozen=True)
class ActivityCandidate:
    activity_id: str
    name: str
    locality: str
    cost: float
    duration_hours: float
    tags: tuple[str, ...]
    min_age: int
    max_age: int
    setting: str
    weather_suitability: tuple[str, ...]


def _normalise_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalise_tags(values: Any) -> tuple[str, ...]:
    if not values:
        return ()
    if isinstance(values, str):
        return tuple(item.strip().lower() for item in values.split(",") if item.strip())
    return tuple(str(item).strip().lower() for item in values if str(item).strip())


def _as_float(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise PlanningError(f"{field_name} must be a number.") from exc
    if parsed < 0:
        raise PlanningError(f"{field_name} cannot be negative.")
    return parsed


def _as_int(value: Any, field_name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise PlanningError(f"{field_name} must be an integer.") from exc
    if parsed < 0:
        raise PlanningError(f"{field_name} cannot be negative.")
    return parsed


def parse_activity(raw: dict[str, Any]) -> ActivityCandidate:
    activity_id = str(raw.get("id") or raw.get("activity_id") or "").strip()
    name = str(raw.get("name") or "").strip()
    locality = str(raw.get("locality") or "").strip()

    if not activity_id:
        raise PlanningError("Activity is missing id.")
    if not name:
        raise PlanningError(f"Activity {activity_id} is missing name.")
    if not locality:
        raise PlanningError(f"Activity {activity_id} is missing locality.")

    min_age = _as_int(raw.get("min_age", 0), f"{name} min_age")
    max_age = _as_int(raw.get("max_age", 99), f"{name} max_age")
    if min_age > max_age:
        raise PlanningError(f"{name} min_age cannot exceed max_age.")

    return ActivityCandidate(
        activity_id=activity_id,
        name=name,
        locality=locality,
        cost=_as_float(raw.get("cost", 0), f"{name} cost"),
        duration_hours=_as_float(raw.get("duration_hours", 0), f"{name} duration_hours"),
        tags=_normalise_tags(raw.get("tags")),
        min_age=min_age,
        max_age=max_age,
        setting=_normalise_text(raw.get("setting") or "indoor"),
        weather_suitability=_normalise_tags(raw.get("weather_suitability")),
    )


def _activity_score(
    activity: ActivityCandidate,
    preferences: set[str],
    weather_condition: str,
) -> int:
    matching_preferences = len(preferences.intersection(activity.tags))
    weather_match = 2 if weather_condition in activity.weather_suitability else 0
    indoor_bad_weather_bonus = (
        1
        if weather_condition in {"rain", "storm", "snow", "wind"}
        and activity.setting == "indoor"
        else 0
    )
    return matching_preferences * 3 + weather_match + indoor_bad_weather_bonus


def _age_compatible(activity: ActivityCandidate, youngest: int, oldest: int) -> bool:
    return activity.min_age <= youngest and activity.max_age >= oldest


def plan_trip(request: dict[str, Any]) -> dict[str, Any]:
    locality = _normalise_text(request.get("locality"))
    if not locality:
        raise PlanningError("locality is required.")

    budget = _as_float(request.get("budget"), "budget")
    youngest_child_age = _as_int(request.get("youngest_child_age", 0), "youngest_child_age")
    oldest_child_age = _as_int(
        request.get("oldest_child_age", youngest_child_age),
        "oldest_child_age",
    )
    if youngest_child_age > oldest_child_age:
        raise PlanningError("youngest_child_age cannot exceed oldest_child_age.")

    weather = request.get("weather") or {}
    weather_condition = _normalise_text(weather.get("condition"))
    if not weather_condition:
        raise PlanningError("weather.condition is required.")

    preferences = set(_normalise_tags(request.get("preferences")))
    activities = [parse_activity(item) for item in request.get("activities", [])]
    if not activities:
        raise PlanningError("activities are required.")

    exclusions: list[dict[str, str]] = []
    eligible: list[tuple[int, ActivityCandidate]] = []

    for activity in activities:
        if _normalise_text(activity.locality) != locality:
            exclusions.append(
                {
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "reason": "not_local",
                }
            )
            continue
        if not _age_compatible(activity, youngest_child_age, oldest_child_age):
            exclusions.append(
                {
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "reason": "age_range_mismatch",
                }
            )
            continue

        score = _activity_score(activity, preferences, weather_condition)
        eligible.append((score, activity))

    eligible.sort(key=lambda item: (-item[0], item[1].cost, item[1].name))

    selected: list[dict[str, Any]] = []
    total_cost = 0.0
    total_duration = 0.0
    selected_ids: set[str] = set()

    for score, activity in eligible:
        if total_cost + activity.cost > budget:
            exclusions.append(
                {
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "reason": "over_budget",
                }
            )
            continue

        selected_ids.add(activity.activity_id)
        total_cost += activity.cost
        total_duration += activity.duration_hours
        selected.append(
            {
                "activity_id": activity.activity_id,
                "name": activity.name,
                "cost": activity.cost,
                "duration_hours": activity.duration_hours,
                "locality": activity.locality,
                "setting": activity.setting,
                "tags": list(activity.tags),
                "weather_suitable": weather_condition in activity.weather_suitability,
                "score": score,
            }
        )

    for _, activity in eligible:
        if activity.activity_id in selected_ids:
            continue
        already_excluded = any(
            exclusion["activity_id"] == activity.activity_id
            for exclusion in exclusions
        )
        if not already_excluded:
            exclusions.append(
                {
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "reason": "lower_ranked",
                }
            )

    return {
        "itinerary_id": _build_itinerary_id(locality, selected),
        "locality": request.get("locality"),
        "budget": budget,
        "total_cost": round(total_cost, 2),
        "remaining_budget": round(budget - total_cost, 2),
        "total_duration_hours": round(total_duration, 2),
        "weather": {
            "condition": weather_condition,
            "summary": str(weather.get("summary") or "").strip(),
        },
        "recommended_activities": selected,
        "excluded_activities": exclusions,
        "summary": _build_summary(locality, weather_condition, selected, total_cost, budget),
    }


def _build_itinerary_id(locality: str, selected: list[dict[str, Any]]) -> str:
    activity_part = "-".join(item["activity_id"] for item in selected) or "empty"
    return f"{locality.replace(' ', '-')}-{activity_part}"


def _build_summary(
    locality: str,
    weather_condition: str,
    selected: list[dict[str, Any]],
    total_cost: float,
    budget: float,
) -> str:
    if not selected:
        return (
            f"No local activities fit the {weather_condition} weather, age, "
            f"and budget constraints for {locality}."
        )

    names = ", ".join(item["name"] for item in selected)
    return (
        f"Plan for {locality}: {names}. "
        f"Estimated cost is {total_cost:.2f} of {budget:.2f} budget."
    )

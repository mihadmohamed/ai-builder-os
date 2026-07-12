from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

from planner import PlanningError, plan_trip  # noqa: E402
from storage import FeedbackError, load_feedback, save_feedback  # noqa: E402
from activity_display import (  # noqa: E402
    activity_metadata,
    readable_exclusion_reason,
    selected_activity_payloads,
)
from tools.common import find_orphan_product_artifacts


def sample_activities() -> list[dict]:
    return [
        {
            "id": "museum",
            "name": "Local science museum",
            "locality": "Bristol",
            "cost": 24,
            "duration_hours": 2.5,
            "tags": ["learning", "indoor"],
            "min_age": 4,
            "max_age": 14,
            "setting": "indoor",
            "weather_suitability": ["rain", "cloudy", "cold"],
        },
        {
            "id": "park",
            "name": "Harbourside play park",
            "locality": "Bristol",
            "cost": 0,
            "duration_hours": 1.5,
            "tags": ["outdoor", "play"],
            "min_age": 2,
            "max_age": 12,
            "setting": "outdoor",
            "weather_suitability": ["sunny", "cloudy"],
        },
        {
            "id": "aquarium",
            "name": "Aquarium visit",
            "locality": "Bristol",
            "cost": 42,
            "duration_hours": 2.0,
            "tags": ["animals", "indoor"],
            "min_age": 3,
            "max_age": 15,
            "setting": "indoor",
            "weather_suitability": ["rain", "cloudy", "cold"],
        },
        {
            "id": "beach",
            "name": "Beach day",
            "locality": "Weston-super-Mare",
            "cost": 15,
            "duration_hours": 4.0,
            "tags": ["outdoor", "play"],
            "min_age": 2,
            "max_age": 16,
            "setting": "outdoor",
            "weather_suitability": ["sunny"],
        },
    ]


def base_request() -> dict:
    return {
        "locality": "Bristol",
        "budget": 30,
        "youngest_child_age": 5,
        "oldest_child_age": 10,
        "preferences": ["learning", "play"],
        "weather": {
            "condition": "rain",
            "summary": "Rain expected through the afternoon",
        },
        "activities": sample_activities(),
    }


def assert_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_budget_locality_and_weather() -> None:
    result = plan_trip(base_request())
    recommended_ids = [item["activity_id"] for item in result["recommended_activities"]]
    excluded = {item["activity_id"]: item["reason"] for item in result["excluded_activities"]}

    assert_equal(recommended_ids, ["museum", "park"], "rainy preference ranking")
    assert_equal(result["total_cost"], 24.0, "budget total")
    assert_equal(excluded["aquarium"], "over_budget", "over-budget exclusion")
    assert_equal(excluded["beach"], "not_local", "non-local exclusion")
    assert_true(result["recommended_activities"][0]["weather_suitable"], "weather suitability")


def test_no_hallucinated_inputs() -> None:
    request = base_request()
    request["activities"] = []
    try:
        plan_trip(request)
    except PlanningError as exc:
        assert_true("activities are required" in str(exc), "missing activities error")
        return
    raise AssertionError("planner accepted missing activities")


def test_age_filtering() -> None:
    request = base_request()
    request["youngest_child_age"] = 1
    request["oldest_child_age"] = 10
    result = plan_trip(request)
    excluded = {item["activity_id"]: item["reason"] for item in result["excluded_activities"]}

    assert_equal(result["recommended_activities"], [], "age-incompatible itinerary")
    assert_equal(excluded["museum"], "age_range_mismatch", "museum age exclusion")
    assert_equal(excluded["park"], "age_range_mismatch", "park age exclusion")


def test_feedback_persistence() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        feedback_path = Path(tmp_dir) / "feedback.json"
        saved = save_feedback(
            {
                "itinerary_id": "bristol-museum-park",
                "activity_ids": ["museum", "park"],
                "visited_activity_ids": ["museum"],
                "rating": 5,
                "notes": "Rainy day plan worked.",
                "would_repeat": True,
            },
            path=feedback_path,
        )
        assert_equal(saved["rating"], 5, "saved rating")
        assert_equal(len(load_feedback(feedback_path)), 1, "persisted feedback count")

        try:
            save_feedback(
                {
                    "itinerary_id": "bristol-museum-park",
                    "activity_ids": ["museum"],
                    "visited_activity_ids": ["museum"],
                    "rating": 6,
                },
                path=feedback_path,
            )
        except FeedbackError:
            pass
        else:
            raise AssertionError("invalid feedback rating was accepted")

        assert_equal(len(load_feedback(feedback_path)), 1, "invalid feedback did not mutate data")


def test_activity_display_metadata() -> None:
    activity = sample_activities()[0]
    metadata = activity_metadata(activity)

    assert_equal(
        metadata,
        ["Bristol", "Cost 24.00", "2.5 hours", "indoor", "Ages 4-14"],
        "readable activity metadata",
    )
    assert_equal(
        readable_exclusion_reason("age_range_mismatch"),
        "Outside child age range",
        "readable exclusion reason",
    )


def test_activity_selection_payloads() -> None:
    activities = sample_activities()
    selected = selected_activity_payloads(activities, {"park", "museum"})
    selected_ids = [item["id"] for item in selected]

    assert_equal(selected_ids, ["museum", "park"], "selected activities preserve input order")
    assert_true(
        all(isinstance(item, dict) for item in selected),
        "selected payloads remain planner-ready dictionaries",
    )


CASES: list[tuple[str, Callable[[], None]]] = [
    ("budget_locality_and_weather", test_budget_locality_and_weather),
    ("no_hallucinated_inputs", test_no_hallucinated_inputs),
    ("age_filtering", test_age_filtering),
    ("feedback_persistence", test_feedback_persistence),
    ("activity_display_metadata", test_activity_display_metadata),
    ("activity_selection_payloads", test_activity_selection_payloads),
]


def main() -> int:
    orphan_artifacts = find_orphan_product_artifacts(PROJECT_ROOT)
    if orphan_artifacts:
        for orphan in orphan_artifacts:
            print(f"FAIL orphan product artifact — {orphan}")
        return 1
    print("PASS product artifact audit — no orphan product artifacts")

    failures = 0
    for name, case in CASES:
        try:
            case()
        except Exception as exc:
            failures += 1
            print(f"CASE {name}: FAIL")
            print(f"  {type(exc).__name__}: {exc}")
        else:
            print(f"CASE {name}: PASS")

    total = len(CASES)
    print(f"SUMMARY: {total - failures}/{total} passing")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
FEEDBACK_PATH = DATA_DIR / "feedback.json"


class FeedbackError(ValueError):
    """Raised when feedback cannot be stored safely."""


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_text().strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise FeedbackError(f"{path} must contain a JSON list.")
    return data


def load_feedback(path: Path = FEEDBACK_PATH) -> list[dict[str, Any]]:
    return _read_json_list(path)


def save_feedback(record: dict[str, Any], path: Path = FEEDBACK_PATH) -> dict[str, Any]:
    itinerary_id = str(record.get("itinerary_id") or "").strip()
    if not itinerary_id:
        raise FeedbackError("itinerary_id is required.")

    rating = record.get("rating")
    if not isinstance(rating, int):
        raise FeedbackError("rating must be an integer.")
    if rating < 1 or rating > 5:
        raise FeedbackError("rating must be between 1 and 5.")

    activity_ids = record.get("activity_ids") or []
    visited_activity_ids = record.get("visited_activity_ids") or []
    if not isinstance(activity_ids, list) or not all(isinstance(item, str) for item in activity_ids):
        raise FeedbackError("activity_ids must be a list of strings.")
    if not isinstance(visited_activity_ids, list) or not all(
        isinstance(item, str) for item in visited_activity_ids
    ):
        raise FeedbackError("visited_activity_ids must be a list of strings.")

    stored_record = {
        "itinerary_id": itinerary_id,
        "activity_ids": activity_ids,
        "visited_activity_ids": visited_activity_ids,
        "rating": rating,
        "notes": str(record.get("notes") or "").strip(),
        "would_repeat": bool(record.get("would_repeat")),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    existing = load_feedback(path)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([*existing, stored_record], indent=2, sort_keys=True))
    return stored_record

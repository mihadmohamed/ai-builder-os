from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any, Mapping
from urllib.parse import urlencode


GOOGLE_CALENDAR_TEMPLATE_URL = "https://calendar.google.com/calendar/render"


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_time(value: str | None) -> time | None:
    if not value:
        return None

    try:
        return time.fromisoformat(value)
    except ValueError:
        return None


def _build_description(event: Mapping[str, Any]) -> str:
    lines: list[str] = []

    event_type = event.get("event_type")
    if event_type:
        lines.append(f"Type: {event_type}")

    status = event.get("event_status")
    if status and status != "scheduled":
        lines.append(f"Status: {status}")

    deadline = event.get("deadline")
    if deadline:
        lines.append(f"Deadline: {deadline}")

    if event.get("action_required"):
        items = event.get("items_needed") or []
        if items:
            lines.append(f"Action needed: bring or submit {', '.join(items)}")
        else:
            lines.append("Action needed")

    cost = event.get("cost")
    if cost:
        lines.append(f"Cost: {cost}")

    return "\n".join(lines)


def _build_timed_dates(date_value: date, start_value: time, end_value: time) -> str:
    start = datetime.combine(date_value, start_value)
    end = datetime.combine(date_value, end_value)
    return f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}"


def _build_all_day_dates(start_date: date, end_date_exclusive: date) -> str:
    return f"{start_date.strftime('%Y%m%d')}/{end_date_exclusive.strftime('%Y%m%d')}"


def build_calendar_sync_plan(event: Mapping[str, Any]) -> dict[str, Any]:
    title = event.get("title") or "ParentMate event"
    status = event.get("event_status") or "scheduled"
    location = event.get("location") or ""
    description = _build_description(event)

    if status == "cancelled":
        return {
            "syncable": False,
            "reason": "Cancelled events are not offered for calendar sync.",
            "url": None,
            "mode": None,
            "dates": None,
            "title": title,
        }

    date_value = event.get("date")
    deadline_value = event.get("deadline")
    start_time_value = event.get("start_time")
    end_time_value = event.get("end_time")

    if isinstance(date_value, str) and " to " in date_value:
        start_raw, end_raw = [part.strip() for part in date_value.split(" to ", 1)]
        start_date = _parse_iso_date(start_raw)
        end_date = _parse_iso_date(end_raw)
        if start_date and end_date:
            dates = _build_all_day_dates(start_date, end_date + timedelta(days=1))
            mode = "all_day"
        else:
            return {
                "syncable": False,
                "reason": "This event date cannot be mapped safely into Google Calendar yet.",
                "url": None,
                "mode": None,
                "dates": None,
                "title": title,
            }
    elif date_value:
        parsed_date = _parse_iso_date(str(date_value))
        if not parsed_date:
            return {
                "syncable": False,
                "reason": "This event date cannot be mapped safely into Google Calendar yet.",
                "url": None,
                "mode": None,
                "dates": None,
                "title": title,
            }

        if start_time_value and end_time_value:
            parsed_start = _parse_time(str(start_time_value))
            parsed_end = _parse_time(str(end_time_value))
            if not parsed_start or not parsed_end:
                return {
                    "syncable": False,
                    "reason": "This event time cannot be mapped safely into Google Calendar yet.",
                    "url": None,
                    "mode": None,
                    "dates": None,
                    "title": title,
                }

            dates = _build_timed_dates(parsed_date, parsed_start, parsed_end)
            mode = "timed"
        elif start_time_value or end_time_value:
            return {
                "syncable": False,
                "reason": "Both start and end time are required for a timed calendar event.",
                "url": None,
                "mode": None,
                "dates": None,
                "title": title,
            }
        else:
            dates = _build_all_day_dates(parsed_date, parsed_date + timedelta(days=1))
            mode = "all_day"
    elif deadline_value:
        parsed_deadline = _parse_iso_date(str(deadline_value))
        if not parsed_deadline:
            return {
                "syncable": False,
                "reason": "This deadline cannot be mapped safely into Google Calendar yet.",
                "url": None,
                "mode": None,
                "dates": None,
                "title": title,
            }

        dates = _build_all_day_dates(parsed_deadline, parsed_deadline + timedelta(days=1))
        mode = "all_day"
    else:
        return {
            "syncable": False,
            "reason": "A dated event or deadline is required before calendar sync can be created.",
            "url": None,
            "mode": None,
            "dates": None,
            "title": title,
        }

    query = urlencode(
        {
            "action": "TEMPLATE",
            "text": title,
            "dates": dates,
            "details": description,
            "location": location,
        }
    )

    return {
        "syncable": True,
        "reason": None,
        "url": f"{GOOGLE_CALENDAR_TEMPLATE_URL}?{query}",
        "mode": mode,
        "dates": dates,
        "title": title,
    }

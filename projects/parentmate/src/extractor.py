from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any

from openai import OpenAI
from dateutil import parser as date_parser
from pydantic import ValidationError

from projects.parentmate.src.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_prompt,
)
from projects.parentmate.src.schemas import EmailExtraction


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EVENT_STATUS_MAP = {
    "scheduled": "scheduled",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "rescheduled": "rescheduled",
    "postponed": "rescheduled",
    "moved": "rescheduled",
    "changed": "rescheduled",
}
RELATIVE_DATE_PATTERN = re.compile(
    r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE,
)
GBP_COST_PATTERN = re.compile(r"\bGBP\s*\d+(?:\.\d{1,2})?\b", re.IGNORECASE)
REVERSED_GBP_COST_PATTERN = re.compile(r"\b(\d+(?:\.\d{1,2})?)\s*GBP\b", re.IGNORECASE)
POUND_SYMBOL_COST_PATTERN = re.compile(r"£\s*(\d+(?:\.\d{1,2})?)")
NUMBER_ONLY_PATTERN = re.compile(r"^\d+(?:\.\d{1,2})?$")
YEAR_PATTERN = re.compile(r"\b(20\d{2}|19\d{2})\b")
DATE_RANGE_PATTERN = re.compile(r"\b\d{1,2}\s*-\s*\d{1,2}\b")
HAS_DIGIT_PATTERN = re.compile(r"\d")
SCHOOL_NAME_FROM_SUBJECT_PATTERN = re.compile(
    r"\bfrom\s+(?P<school>[A-Z][A-Za-z0-9&' -]*(?:Primary|School|Academy|College))\b"
)
BRING_OR_WEAR_PATTERN = re.compile(
    r"\b(?:bring|wear)\s+(?:their|your|a|an)?\s*(?P<item>[^.,;\n]+)",
    re.IGNORECASE,
)
OPTIONAL_PAYMENT_PATTERN = re.compile(
    r"\b(optional|voluntary|suggested contribution|suggested donation|donation|contribution|if you wish|if you would like|would be appreciated)\b",
    re.IGNORECASE,
)
REQUIRED_PAYMENT_PATTERN = re.compile(
    r"\b(please pay|pay by|payment is due|payment due|deposit is due|fee is due|required payment|must pay)\b",
    re.IGNORECASE,
)
PAYMENT_EVENT_PATTERN = re.compile(
    r"\b(payment|deposit|donation|contribution|fee)\b",
    re.IGNORECASE,
)
CONFIRMATION_PATTERN = re.compile(r"\b(confirmation|confirmed|booking confirmation)\b", re.IGNORECASE)
BODY_COST_PATTERN = re.compile(r"\bGBP\s*(\d+(?:\.\d{1,2})?)\b|£\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)
TITLE_EVENT_TYPE_KEYWORDS = {
    "concert": "concert",
    "picnic": "picnic",
    "assembly": "assembly",
    "screening": "screening",
    "lesson": "lesson",
    "club": "club",
    "trip": "trip",
}


class ExtractionError(RuntimeError):
    pass


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ExtractionError(
            "OPENAI_API_KEY is not set. Add it to your environment before running the app."
        )
    return OpenAI(api_key=api_key)


def _parse_response_content(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ExtractionError("OpenAI returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ExtractionError("OpenAI returned JSON, but it was not an object.")

    return parsed


def request_extraction_response_content(email_subject: str, email_body: str) -> str:
    if not email_body.strip():
        raise ExtractionError("Email body is required.")

    client = _get_client()
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        seed=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_extraction_user_prompt(email_subject, email_body),
            },
        ],
    )

    message = response.choices[0].message.content
    if not message:
        raise ExtractionError("OpenAI returned an empty response.")

    return message


def _normalize_event_status_value(value: Any) -> str:
    if not isinstance(value, str):
        return "scheduled"

    return EVENT_STATUS_MAP.get(value.strip().lower(), "scheduled")


def _normalize_event_status_payload(parsed: dict[str, Any]) -> dict[str, Any]:
    events = parsed.get("events")
    if not isinstance(events, list):
        return parsed

    for event in events:
        if isinstance(event, dict):
            event["event_status"] = _normalize_event_status_value(event.get("event_status"))

    return parsed


def _infer_event_status(email_subject: str, email_body: str) -> str:
    text = f"{email_subject}\n{email_body}".lower()

    if any(keyword in text for keyword in ("cancelled", "canceled")):
        return "cancelled"

    if any(
        keyword in text
        for keyword in (
            "rescheduled",
            "postponed",
            "moved to",
            "moved from",
            "change to",
            "changed to",
        )
    ):
        return "rescheduled"

    return "scheduled"


def _email_has_optional_payment_language(email_subject: str, email_body: str) -> bool:
    return bool(OPTIONAL_PAYMENT_PATTERN.search(f"{email_subject}\n{email_body}"))


def _email_has_required_payment_language(email_subject: str, email_body: str) -> bool:
    return bool(REQUIRED_PAYMENT_PATTERN.search(f"{email_subject}\n{email_body}"))


def _email_is_confirmation(email_subject: str, email_body: str) -> bool:
    return bool(CONFIRMATION_PATTERN.search(f"{email_subject}\n{email_body}"))


def _clean_items_needed(value: str) -> str | None:
    cleaned = value.strip()
    cleaned = re.sub(r"\bas usual\b", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\bnext week\b", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = cleaned.strip(" .,:;")
    if "non-uniform" in cleaned.lower():
        return None
    return cleaned or None


def _extract_instruction_items(email_body: str) -> list[str]:
    items: list[str] = []

    for match in BRING_OR_WEAR_PATTERN.finditer(email_body):
        cleaned = _clean_items_needed(match.group("item"))
        if cleaned and cleaned not in items:
            items.append(cleaned)

    return items


def _filter_items_needed(items_needed: list[str] | None) -> list[str] | None:
    if not items_needed:
        return None

    filtered: list[str] = []
    for item in items_needed:
        cleaned = _clean_items_needed(item)
        if not cleaned:
            continue

        lowered = cleaned.lower()
        if "payment" in lowered or "deposit" in lowered:
            continue
        if "gbp" in lowered or "£" in lowered:
            continue

        filtered.append(cleaned)

    return filtered or None


def _extract_cost_from_email_body(email_body: str) -> str | None:
    match = BODY_COST_PATTERN.search(email_body)
    if not match:
        return None

    amount = match.group(1) or match.group(2)
    if not amount:
        return None

    return f"GBP {amount}"


def _infer_event_type_from_title(title: str | None, existing_event_type: str | None) -> str | None:
    if not title:
        return existing_event_type

    lowered_title = title.lower()
    current = (existing_event_type or "").lower()
    if current not in {"", "event", "meeting"}:
        return existing_event_type

    if current == "event":
        if "concert" in lowered_title:
            return "concert"
        return existing_event_type

    for keyword, inferred_type in TITLE_EVENT_TYPE_KEYWORDS.items():
        if keyword in lowered_title:
            return inferred_type

    return existing_event_type


def _is_payment_admin_event(event: Any) -> bool:
    title = (event.title or "").lower()
    event_type = (event.event_type or "").lower()

    if event_type in {"payment", "donation"}:
        return True

    if PAYMENT_EVENT_PATTERN.search(title):
        return True

    return bool(event.cost) and not event.location and not event.start_time and not event.end_time


def _merge_payment_admin_events(
    result: EmailExtraction,
    email_subject: str,
    email_body: str,
) -> EmailExtraction:
    has_optional_payment = _email_has_optional_payment_language(email_subject, email_body)
    has_required_payment = _email_has_required_payment_language(email_subject, email_body)
    is_confirmation = _email_is_confirmation(email_subject, email_body)

    if has_optional_payment and len(result.events) == 1 and result.events[0].cost is None:
        result.events[0].cost = _extract_cost_from_email_body(email_body)

    for event in result.events:
        if not event.cost:
            continue

        if has_optional_payment and not has_required_payment:
            event.action_required = False
        elif has_required_payment:
            event.action_required = True
        elif is_confirmation:
            event.action_required = False

    if len(result.events) < 2:
        return result

    primary_event = next((event for event in result.events if not _is_payment_admin_event(event)), None)
    if primary_event is None:
        return result

    merged_events = []
    for event in result.events:
        if event is primary_event:
            merged_events.append(event)
            continue

        if not _is_payment_admin_event(event):
            merged_events.append(event)
            continue

        if primary_event.cost is None and event.cost is not None:
            primary_event.cost = event.cost

        if primary_event.deadline is None and event.deadline is not None:
            primary_event.deadline = event.deadline

        if primary_event.date is None and event.date is not None:
            primary_event.date = event.date

        if primary_event.action_required is None and event.action_required is not None:
            primary_event.action_required = event.action_required
        elif event.action_required is True:
            primary_event.action_required = True

    result.events = merged_events

    return result


def _infer_school_name(email_subject: str, existing_school_name: str | None) -> str | None:
    if existing_school_name:
        return existing_school_name

    match = SCHOOL_NAME_FROM_SUBJECT_PATTERN.search(email_subject)
    if match:
        return match.group("school").strip()

    return existing_school_name


def _extract_year(value: str | None) -> int | None:
    if not value:
        return None

    match = YEAR_PATTERN.search(value)
    if not match:
        return None

    return int(match.group(1))


def _normalize_date(value: str | None, default_year: int | None = None) -> str | None:
    if not value:
        return value

    if DATE_RANGE_PATTERN.search(value):
        return value

    if not HAS_DIGIT_PATTERN.search(value):
        return value

    parse_default = datetime(default_year or 1900, 1, 1)

    try:
        parsed = date_parser.parse(value, fuzzy=True, dayfirst=True, default=parse_default)
    except (OverflowError, ValueError):
        return value

    if default_year is None and _extract_year(value) is None:
        return value

    return parsed.date().isoformat()


def _normalize_time(value: str | None) -> str | None:
    if not value:
        return value

    if not HAS_DIGIT_PATTERN.search(value):
        return value

    try:
        parsed = date_parser.parse(value, fuzzy=True)
    except (OverflowError, ValueError):
        return value

    return parsed.strftime("%H:%M")


def _postprocess_extraction(
    result: EmailExtraction, email_subject: str, email_body: str
) -> EmailExtraction:
    relative_date = RELATIVE_DATE_PATTERN.search(email_body)
    inferred_status = _infer_event_status(email_subject, email_body)
    fallback_items = _extract_instruction_items(email_body)
    result.school_name = _infer_school_name(email_subject, result.school_name)

    for event in result.events:
        if inferred_status != "scheduled" and event.event_status == "scheduled":
            event.event_status = inferred_status

        if not event.items_needed and len(result.events) == 1 and fallback_items:
            event.items_needed = fallback_items

        event.items_needed = _filter_items_needed(event.items_needed)

        if event.items_needed:
            event.action_required = True

        if event.location and event.location.strip().lower() == "school":
            event.location = None

        if (
            event.action_required is True
            and event.deadline
            and event.date is None
            and event.event_type in {None, "reminder", "deadline"}
        ):
            event.event_type = "deadline"

        if event.event_type == "deadline":
            event.location = None

        if event.date is None and relative_date:
            event.date = relative_date.group(0)

        inferred_year = _extract_year(event.date)
        event.date = _normalize_date(event.date)
        event.deadline = _normalize_date(event.deadline, inferred_year)
        event.start_time = _normalize_time(event.start_time)
        event.end_time = _normalize_time(event.end_time)

        if event.cost:
            cost_match = GBP_COST_PATTERN.search(event.cost)
            if cost_match:
                event.cost = " ".join(cost_match.group(0).upper().split())
            else:
                pound_symbol_match = POUND_SYMBOL_COST_PATTERN.search(event.cost)
                if pound_symbol_match:
                    event.cost = f"GBP {pound_symbol_match.group(1)}"
                else:
                    reversed_cost_match = REVERSED_GBP_COST_PATTERN.search(event.cost)
                    if reversed_cost_match:
                        event.cost = f"GBP {reversed_cost_match.group(1)}"
                    elif (
                        "GBP" in email_body.upper() or "£" in email_body
                    ) and NUMBER_ONLY_PATTERN.fullmatch(event.cost.strip()):
                        event.cost = f"GBP {event.cost.strip()}"

        if event.event_type and event.event_type.strip().lower() == "swimming lesson":
            event.event_type = "lesson"

        event.event_type = _infer_event_type_from_title(event.title, event.event_type)

    return _merge_payment_admin_events(result, email_subject, email_body)


def extract_email_from_payload(
    email_subject: str, email_body: str, payload: dict[str, Any]
) -> EmailExtraction:
    parsed = _normalize_event_status_payload(payload)

    try:
        result = EmailExtraction.model_validate(parsed)
    except ValidationError as exc:
        raise ExtractionError(f"Structured extraction failed validation: {exc}") from exc

    return _postprocess_extraction(result, email_subject, email_body)


def extract_email_from_response_content(
    email_subject: str, email_body: str, response_content: str
) -> EmailExtraction:
    parsed = _parse_response_content(response_content)
    return extract_email_from_payload(email_subject, email_body, parsed)


def extract_email(email_subject: str, email_body: str) -> EmailExtraction:
    response_content = request_extraction_response_content(email_subject, email_body)
    return extract_email_from_response_content(email_subject, email_body, response_content)

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from projects.parentmate.src.calendar import build_calendar_sync_plan
from projects.parentmate.src.extractor import ExtractionError, extract_email
from projects.parentmate.src.schemas import EmailExtraction
from projects.parentmate.src.storage import load_events, save_event


def build_summary(result: EmailExtraction) -> str:
    event_count = len(result.events)
    action_count = sum(1 for event in result.events if event.action_required is True)
    school_name = result.school_name or "the school email"

    if event_count == 0:
        return f"No events or parent actions were found in {school_name}."

    event_label = "event" if event_count == 1 else "events"
    action_label = "action" if action_count == 1 else "actions"
    return (
        f"Found {event_count} {event_label} in {school_name}. "
        f"{action_count} parent {action_label} appear to be required."
    )


def build_event_glance_summary(event: dict) -> str:
    parts: list[str] = []

    date = event.get("date")
    start_time = event.get("start_time")
    end_time = event.get("end_time")
    location = event.get("location")
    deadline = event.get("deadline")
    action_required = event.get("action_required")
    items_needed = event.get("items_needed") or []
    cost = event.get("cost")
    status = event.get("event_status")

    if status and status != "scheduled":
        parts.append(f"Status: {status}.")

    if date:
        if start_time and end_time:
            parts.append(f"When: {date} from {start_time} to {end_time}.")
        elif start_time:
            parts.append(f"When: {date} at {start_time}.")
        else:
            parts.append(f"When: {date}.")
    elif deadline:
        parts.append(f"Deadline: {deadline}.")

    if location:
        parts.append(f"Where: {location}.")

    if action_required:
        if items_needed:
            item_list = ", ".join(items_needed)
            parts.append(f"Action needed: bring or submit {item_list}.")
        elif deadline and not date:
            parts.append("Action needed before the deadline.")
        else:
            parts.append("Action needed.")
    elif deadline and date:
        parts.append(f"Deadline: {deadline}.")

    if cost:
        parts.append(f"Cost: {cost}.")

    if not parts:
        return "No extra event details were identified."

    return " ".join(parts)


def render_event(event_index: int, event: dict) -> None:
    title = event.get("title") or f"Event {event_index}"
    subtype = event.get("event_type") or "Unspecified type"
    status = event.get("event_status") or "scheduled"
    calendar_plan = build_calendar_sync_plan(event)
    with st.container(border=True):
        st.subheader(title)
        st.caption(f"{subtype} | {status}")
        st.write(build_event_glance_summary(event))

        left, right = st.columns(2)
        with left:
            st.write("**Date:**", event.get("date") or "Unknown")
            st.write("**Start time:**", event.get("start_time") or "Unknown")
            st.write("**End time:**", event.get("end_time") or "Unknown")
            st.write("**Location:**", event.get("location") or "Unknown")
            st.write("**Deadline:**", event.get("deadline") or "Unknown")
        with right:
            st.write("**Event status:**", status)
            st.write("**Child specific:**", event.get("child_specific"))
            st.write("**Action required:**", event.get("action_required"))
            st.write("**Cost:**", event.get("cost") or "Unknown")
            st.write("**Confidence:**", event.get("confidence"))
            items_needed = event.get("items_needed")
            st.write("**Items needed:**", ", ".join(items_needed) if items_needed else "None stated")

        st.markdown("**Calendar sync**")
        if calendar_plan["syncable"]:
            st.caption("Open a prefilled Google Calendar event in a new tab.")
            st.link_button(
                "Open in Google Calendar",
                calendar_plan["url"],
                use_container_width=True,
            )
        else:
            st.caption(calendar_plan["reason"])


def render_saved_events() -> None:
    st.markdown("### All extracted events")

    events = load_events()

    if not events:
        st.info("No stored events yet.")
    else:
        for i, e in enumerate(events, start=1):
            with st.expander(f"Saved email {i}"):
                st.json(e)


def main() -> None:
    st.set_page_config(
        page_title="School Email Event Extractor",
        page_icon="📚",
        layout="wide",
    )

    st.title("School Email Event Extractor")
    st.write("Paste a school email to extract events, deadlines, and parent actions.")

    with st.form("extract_form"):
        email_subject = st.text_input("Email subject")
        email_body = st.text_area("Email body", height=260)
        submitted = st.form_submit_button("Extract events", use_container_width=True)

    if not submitted:
        render_saved_events()
        return

    if not email_body.strip():
        st.warning("Enter the email body before extracting.")
        render_saved_events()
        return

    with st.spinner("Extracting events..."):
        try:
            result = extract_email(email_subject=email_subject, email_body=email_body)
            save_event(result.model_dump())
        except ExtractionError as exc:
            st.error(str(exc))
            return
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
            return

    st.success("Extraction complete.")
    st.markdown("### Summary")
    st.write(build_summary(result))

    st.markdown("### Structured events")
    if not result.events:
        st.info("No structured events were extracted.")
    else:
        for index, event in enumerate(result.model_dump()["events"], start=1):
            render_event(index, event)

    with st.expander("View JSON"):
        st.json(result.model_dump(mode="json"), expanded=True)

    render_saved_events()


if __name__ == "__main__":
    main()

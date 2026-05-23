from __future__ import annotations

import json

import streamlit as st

from planner import PlanningError, plan_trip
from storage import FeedbackError, load_feedback, save_feedback


DEFAULT_ACTIVITIES = [
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
]


def _default_activity_json() -> str:
    return json.dumps(DEFAULT_ACTIVITIES, indent=2)


def main() -> None:
    st.set_page_config(page_title="Personal Trip Planner", layout="wide")
    st.title("Personal Trip Planner")
    st.caption("This MVP uses user-provided local activities and weather context.")

    with st.sidebar:
        st.header("Family plan")
        locality = st.text_input("Local area", value="Bristol")
        budget = st.number_input("Budget", min_value=0.0, value=40.0, step=5.0)
        youngest = st.number_input("Youngest child age", min_value=0, value=5, step=1)
        oldest = st.number_input("Oldest child age", min_value=0, value=10, step=1)
        preferences = st.text_input("Preferences", value="learning, play")
        weather_condition = st.selectbox(
            "Current weather",
            ["sunny", "cloudy", "rain", "cold", "wind", "snow", "storm"],
            index=2,
        )
        weather_summary = st.text_input("Weather note", value="User-provided weather context")

    activities_json = st.text_area(
        "Local activity candidates",
        value=_default_activity_json(),
        height=280,
    )

    if st.button("Plan trip", use_container_width=True):
        try:
            activities = json.loads(activities_json)
            result = plan_trip(
                {
                    "locality": locality,
                    "budget": budget,
                    "youngest_child_age": int(youngest),
                    "oldest_child_age": int(oldest),
                    "preferences": preferences,
                    "weather": {
                        "condition": weather_condition,
                        "summary": weather_summary,
                    },
                    "activities": activities,
                }
            )
            st.session_state["latest_itinerary"] = result
        except (json.JSONDecodeError, PlanningError) as exc:
            st.error(str(exc))

    latest = st.session_state.get("latest_itinerary")
    if latest:
        st.subheader("Recommended itinerary")
        st.write(latest["summary"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Estimated cost", f"{latest['total_cost']:.2f}")
        col2.metric("Remaining budget", f"{latest['remaining_budget']:.2f}")
        col3.metric("Duration", f"{latest['total_duration_hours']:.1f} hours")

        st.markdown("#### Activities")
        if latest["recommended_activities"]:
            for activity in latest["recommended_activities"]:
                with st.container(border=True):
                    st.markdown(f"**{activity['name']}**")
                    st.write(
                        f"{activity['duration_hours']} hours | "
                        f"{activity['setting']} | cost {activity['cost']:.2f}"
                    )
        else:
            st.info("No activities fit the current constraints.")

        with st.expander("Excluded activities"):
            st.json(latest["excluded_activities"])

        st.subheader("Post-trip feedback")
        with st.form("feedback"):
            rating = st.slider("Rating", min_value=1, max_value=5, value=4)
            visited = st.multiselect(
                "Visited activities",
                [item["activity_id"] for item in latest["recommended_activities"]],
            )
            would_repeat = st.checkbox("Would repeat")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save feedback", use_container_width=True)
            if submitted:
                try:
                    save_feedback(
                        {
                            "itinerary_id": latest["itinerary_id"],
                            "activity_ids": [
                                item["activity_id"]
                                for item in latest["recommended_activities"]
                            ],
                            "visited_activity_ids": visited,
                            "rating": rating,
                            "would_repeat": would_repeat,
                            "notes": notes,
                        }
                    )
                    st.success("Feedback saved.")
                except FeedbackError as exc:
                    st.error(str(exc))

    with st.expander("Saved feedback"):
        st.json(load_feedback())


if __name__ == "__main__":
    main()

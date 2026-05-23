# Manual UX Checks

Use this file for lightweight human-reviewed UX checks when a change affects user-facing output but is not meaningfully machine-evaluable.

Keep checks small, concrete, and easy to run.

---

## Test: Event summary readability

Input:
Event with date, time, location, action, cost

Expected:
- Clear `When`
- Clear `Where`
- Clear `Action`
- No redundant wording

Pass if:
A parent can understand the event in under 5 seconds

---

## Test: Personal trip planner MVP

Input:
Default Bristol rainy-day activity data in the Streamlit app

Expected:
- User can enter local area, budget, child ages, preferences, weather, and activity candidates
- Generated plan shows recommended activities, estimated cost, remaining budget, duration, and excluded activity reasons
- Feedback can be submitted for a generated itinerary
- Saved feedback is visible after submission
- UI states that weather and activity data are user-provided

Pass if:
A parent can generate a constrained local outing plan and record post-trip feedback without the UI implying live booking, hotel planning, long-distance travel, or social sharing

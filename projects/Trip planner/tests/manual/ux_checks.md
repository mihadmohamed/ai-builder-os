# Manual UX Checks

Use this file for lightweight human-reviewed UX checks when a change affects the Personal Trip Planner experience but is not meaningfully machine-evaluable.

Keep checks small, concrete, and easy to run.

---

## Test: Planner input clarity

Input:
Open the Streamlit app and review the planner inputs before generating a trip.

Expected:
- It is clear which fields the parent needs to provide.
- The UI makes it obvious that weather and activity data are user-provided.
- The app does not imply live booking, live weather fetching, or hotel planning.

Pass if:
A parent can understand what the app expects without guessing where the data comes from.

---

## Test: Recommendation trustworthiness

Input:
Use the default Bristol rainy-day scenario in the app.

Expected:
- Recommended activities feel plausible for the stated family preferences and weather.
- Excluded activities show understandable reasons.
- Budget and duration information are easy to scan.

Pass if:
A parent can tell why the plan was recommended and why weaker options were excluded.

---

## Test: Activity selection readability

Input:
Open the Streamlit app and review the default local activity candidates before generating a trip.

Expected:
- Activities appear as readable items with name, cost, duration, area, setting, age range, tags, and weather fit.
- A parent can include or exclude activities with checkboxes.
- Raw JSON is not required for normal selection, but remains available in an advanced view for inspection.
- Excluded itinerary reasons are shown as readable text rather than raw JSON objects.

Pass if:
A parent can decide which candidate activities to include without understanding JSON.

---

## Test: Feedback flow usability

Input:
Generate an itinerary and submit post-trip feedback.

Expected:
- Feedback fields are understandable.
- Submitting feedback does not feel brittle or confusing.
- Saved feedback remains visible after submission.

Pass if:
A parent can record feedback about a trip without confusion about what was saved.

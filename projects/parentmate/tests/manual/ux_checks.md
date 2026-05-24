# Manual UX Checks

Use this file for lightweight human-reviewed UX checks when a change affects ParentMate's user-facing output but is not meaningfully machine-evaluable.

Keep checks small, concrete, and easy to run.

---

## Test: Event summary readability

Input:
Use an extracted event with date, time, location, action, and cost details.

Expected:
- Clear `When`
- Clear `Where`
- Clear `Action`
- No redundant wording

Pass if:
A parent can understand the event in under 5 seconds.

---

## Test: Extraction review trust

Input:
Paste a representative school email into the Streamlit app and run extraction.

Expected:
- The extracted event cards feel understandable rather than raw or technical.
- Required parent actions are easy to spot.
- Costs, deadlines, and items needed do not read as jumbled text.
- The app does not imply that missing information was confidently inferred when it was actually absent.

Pass if:
A parent can tell what the event is, what action is required, and what still remains uncertain.

---

## Test: Calendar handoff clarity

Input:
Use an extracted event that supports the current calendar workflow.

Expected:
- The calendar-related action is understandable.
- The UI makes clear whether ParentMate is opening a manual handoff or doing something more direct.
- The flow feels easier than copying event details by hand.

Pass if:
A parent can understand how to move from extracted event to calendar follow-up without guessing what the app is doing.

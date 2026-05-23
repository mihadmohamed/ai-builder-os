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

# System Memory — ParentMate

## Purpose
Store learnings from past iterations to guide future agent behaviour.

---

## Failure Memory

### [Today] — Case: <short description>

Failure:
- Cost came back as £4.50 instead of the repo’s normalized currency format GBP 4.50

Root Cause:
- Currency normalization had a format gap: it handled GBP variants, not the pound symbol. 

Fix:
- Post-processing rule added to normalize pound-symbol costs into GBP <amount>

### [22 Apr 2026] — Case: event_status feature rollout

Failure:
- Adding `event_status` exposed drift in related fields: some emails lost subject-based `school_name`, and some outputs leaked non-items like `deposit payment` into `items_needed`.

Root Cause:
- The model handled the new schema inconsistently, especially around status language and imperative phrasing.

Fix:
- Added event_status normalization and inference.
- Added subject-based school_name fallback for `from <School Name>` subjects.
- Filtered non-item phrases such as payment/deposit and non-uniform clothing out of `items_needed`.

### [22 Apr 2026] — Case: payment extraction improvements

Failure:
- Optional donations could split into separate admin events or lose the amount on the main event.
- Booking confirmations with a price could be misread as unpaid required actions.

Root Cause:
- The model treated some payment language as standalone events and did not consistently distinguish required payment from informational confirmation copy.

Fix:
- Prompt updated to keep required and optional payment language attached to the main event.
- Post-processing merges admin-only payment events back into the primary event.
- Optional contribution amounts can be recovered onto the main event when clearly stated.
- Confirmation language suppresses false `action_required` on already-confirmed bookings.

---

## Decision Memory

### [22 Apr 2026] — Decision: Event merging

Decision:
- Administrative actions (payments, deadlines, permission slips) must be merged into the main event.

Reason:
- Model was splitting events incorrectly.

Impact:
- Improved consistency and usability.

### [Today] — Decision: Date/time normalisation

Decision:
- Dates must be normalised to YYYY-MM-DD when possible.
- Times must be normalised to HH:MM (24-hour).

Reason:
- Raw extraction caused inconsistent outputs.

Impact:
- Improved usability for calendar integration.

### [22 Apr 2026] — Decision: event_status support

Decision:
- Add `event_status` to the schema with default value `scheduled`.
- Use `cancelled` and `rescheduled` only for explicit cancellation or schedule-change language.

Reason:
- The system needs to represent active schedule changes without altering existing event extraction fields.

Impact:
- Existing events remain scheduled by default.
- Cancellation and reschedule emails can now be represented explicitly.

### [22 Apr 2026] — Decision: Payment semantics

Decision:
- Required payments stay attached to the main event with `cost`, `deadline`, and `action_required`.
- Optional donations and suggested contributions stay attached to the main event but should not force `action_required`.
- Booking confirmations with a price are informational unless the email also explicitly requests payment.

Reason:
- Parents need to see what is payable and by when without the system splitting admin tasks into separate events or inventing unpaid actions for already-confirmed bookings.

Impact:
- Payment visibility improved without breaking the event-merging rule.

### [24 Apr 2026] — Decision: Eval runner split

Decision:
- `projects/parentmate/tools/eval_runner.py` is the default deterministic validation path.
- `projects/parentmate/tools/live_eval_runner.py` is the optional live model regression path.
- Replay payloads for deterministic evals live in `projects/parentmate/evals/replays/`.

Reason:
- The old eval flow depended on network and live model behavior, which made failures ambiguous and non-reproducible.

Impact:
- Routine validation is now stable and local.
- Live model drift can still be checked separately when needed.

### [24 Apr 2026] — Decision: Thin deterministic unit-test layer

Decision:
- Keep evals as the main product-behavior safety net.
- Use `tests/unit/` only for fast deterministic logic that evals do not isolate well.
- Prefer the standard library `unittest` runner over adding a new dependency.

Reason:
- Evals cover end-to-end extraction behavior well, but they are a poor fit for tiny helper regressions and UI-only summary logic.

Impact:
- Faster failure localization for deterministic helpers.
- No duplicate test framework complexity added to the project.

### [25 Apr 2026] — Strategic Decision: Prioritise calendar integration before reminders and polish

Decision:
- Prioritise `R7 — Calendar integration` ahead of `R8 — Notification reminders` and `R9 — UI polish`.

Reason:
- `R7` has the highest explicit product priority in `requirements.md`.
- Calendar integration is a stronger capability unlock than reminders or cosmetic UI improvements.
- Reminder work is likely to benefit from the calendar path existing first.

Impact:
- PM should treat calendar integration as the current strategic direction unless there is a clear reason to change it.
- `R8` and `R9` remain deferred until `R7` is completed or strategy is intentionally revised.

### [25 Apr 2026] — Decision: Start calendar integration with a manual sync path

Decision:
- The first Google Calendar integration path should be a manual, user-triggered handoff that opens a prefilled Google Calendar event.
- Do not add direct calendar write/auth flows in the first iteration.

Reason:
- This delivers a testable calendar workflow with minimal product and implementation risk.
- It preserves the current extraction/debugging workflow while proving the event-mapping layer.

Impact:
- Calendar integration is now available as a controlled UI action rather than a background sync system.
- Future reminder or deeper calendar work can build on the mapping logic without forcing auth-heavy integration first.

---

## Observations

### O1 — Event summary improves readability (hypothesis)

Observation:
- Parent-facing event summaries appear to make events easier to scan.

Evidence:
- Manual UX check passed.

Confidence:
- Low

### O2 — Calendar sync assumed high value

Observation:
- Calendar sync is currently treated as the highest-value next feature.

Evidence:
- Product assumption used in PM prioritisation.

Confidence:
- Low

### O3 — Manual calendar sync path is viable for first-step integration

Observation:
- ParentMate events can be mapped into a safe, user-triggered Google Calendar handoff without changing extraction behavior.

Evidence:
- Deterministic unit tests for calendar mapping passed.
- Replay-backed eval suite remained fully passing after the integration.
- Streamlit UI now exposes a controlled calendar sync action per event.

Confidence:
- Medium

Validation method:
- Deterministic unit tests plus replay-backed regression validation.

Implication:
- The project can extend calendar-related workflows incrementally from a stable manual sync base instead of jumping straight to full API integration.

---

## Heuristic Memory

### Extraction Heuristics

- Merge administrative actions into the main event
- Prefer recall over precision (do not miss events)
- Do not split events unless clearly separate activities
- Do not treat cost as item
- Normalise date/time when confident
- Infer `school_name` from subject lines like `Weekly update from Maplebridge Primary`
- Remove payment-like phrases from `items_needed`
- Bring/wear instructions usually imply `action_required`
- Optional payment language should not force `action_required`
- Confirmation language can override false payment-required inferences
- Prefer replay-backed evals for regular validation; use live evals only when intentionally checking model behavior

---

## Open Questions

- When should school_name be inferred?
- How to handle ambiguous relative dates?

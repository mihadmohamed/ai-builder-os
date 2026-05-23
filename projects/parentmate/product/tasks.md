# Tasks — ParentMate v1

## Task 0: Run evaluation suite

Status: DONE

Goal:
Verify current extraction system across all eval cases.

Requirements:
- Run extractor on all files in projects/parentmate/evals/
- Compare output with expected JSON
- Report pass/fail for each case

Output:
- Summary of results

## Task 1: Improve extraction reliability

Status: DONE

Goal:
Ensure the extraction engine works across diverse email formats.

Requirements:
- Must handle at least 20 different email formats
- Must pass all eval cases
- Must not hallucinate missing fields

Output:
- Updated extraction logic
- Improved prompt if needed

---

## Task 2: Standardise date and time formats

Status: DONE

Goal:
Ensure all extracted dates and times are consistent and usable for downstream systems (e.g. calendar).

Requirements:
- Dates must be normalised to YYYY-MM-DD when possible
- Times must be normalised to HH:MM (24-hour format) when possible
- If date/time cannot be confidently normalised, preserve original string
- Must NOT hallucinate or invent missing values
- Must NOT break existing passing evals

Constraints:
- Prefer prompt-level fixes over heavy post-processing
- Keep logic simple and maintainable

Validation:
- Update eval expected outputs where appropriate
- All evals must pass using projects/parentmate/tools/eval_runner.py

Output:
- What was changed (prompt, code, evals)
- Before vs after behaviour
- Any edge cases identified

---

## Task 3: Add evaluation runner

Status: DONE

Goal:
Run all evals automatically and report results.

Requirements:
- Script to run all files in projects/parentmate/evals/
- Compare actual vs expected
- Print pass/fail summary

## Task 4: Self-improving extraction loop

Status: DONE

Goal:
Continuously improve extraction accuracy based on failures without breaking existing behaviour.

Process:

1. Identify failures:
   - New real-world emails
   - Failing eval cases

2. Generate hypothesis:
   - Why did extraction fail?
   - Prompt issue, schema issue, or post-processing issue?

3. Apply minimal fix:
   - Prefer prompt updates
   - Use code changes only if necessary

4. Validate:
   - Run projects/parentmate/tools/eval_runner.py
   - All existing evals must pass

5. Decision:
   - If improvement passes all evals → keep change
   - If any regression → revert change

6. Log learning:
   - What failed
   - What was changed
   - Why it worked

Constraints:
- Do NOT overfit to a single test case
- Do NOT introduce complex logic without clear need
- Prefer general rules over special cases

Output:
- Summary of failure
- Change applied
- Before vs after results
- New edge case identified

## Task 5: Add new feature without breaking system

Status: DONE

Goal:
Test whether the engineer agent can implement a new feature using the same workflow.

Feature:
Add a new field "event_status" to the Event schema.

Requirements:
- event_status can be:
  - "scheduled"
  - "cancelled"
  - "rescheduled"
- Default should be "scheduled"
- Do NOT break existing extraction behaviour
- Do NOT break existing evals

Constraints:
- Update schema, prompt, and extraction logic as needed
- Keep implementation simple
- Do not over-engineer

Validation:
- All existing evals must pass
- New field must appear in output

Output:
- What changes were made
- Why
- Any risks identified

## Task 6: Introduce conflicting requirement

Status: DONE

Goal:
Test whether the agent can handle conflicting instructions without breaking the system.

Change:
- Modify prompt to extract ALL actions as separate events (conflicts with current merging rule)

Requirements:
- Agent must detect conflict with existing rules in agent/memory.md
- Agent must NOT blindly implement change
- Agent must explain conflict and propose resolution

Output:
- Conflict identified
- Why it breaks system
- Recommended decision

## Task 7: Improve payment extraction clarity

Status: DONE

Goal:
Ensure payment-related information is extracted clearly so parents can see what they need to pay and by when.

Requirements:
- Keep payment details attached to the main event
- Do NOT create separate payment events
- Extract payment amount into `cost`
- Extract payment due date into `deadline` when present
- Set `action_required` to true when payment is clearly required
- Do NOT place payment phrases in `items_needed`
- Preserve existing extraction behaviour for non-payment emails

Constraints:
- Follow the event-merging rule in agent/memory.md
- Prefer prompt improvements over heavy post-processing
- Do NOT hallucinate missing payment amounts or deadlines
- Keep currency normalisation consistent with existing behaviour

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Add evals for:
  - required payment with explicit due date
  - trip deposit with deadline
  - payment mentioned without a due date
- All existing evals must pass

Output:
- What changed
- Why
- Before vs after eval results
- Any payment edge cases identified

## Task 8: Distinguish required payments from optional donations

Status: DONE

Goal:
Prevent optional donations or contributions from being treated as required parent actions.

Requirements:
- If money is described as optional, voluntary, suggested, or a donation, do NOT force `action_required` to true unless the email explicitly requires payment
- Extract `cost` only when an amount is explicitly stated
- Keep optional donation language attached to the main event when it relates to a real activity
- Do NOT treat donations, contributions, or money as `items_needed`

Constraints:
- Must not break existing payment extraction behaviour
- Prefer general rules over one-off keyword hacks
- Do NOT create standalone donation events

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Add evals for:
  - optional donation attached to an event
  - voluntary contribution with no required action
- All existing evals must pass

Output:
- What changed
- Why
- Before vs after eval results
- Remaining ambiguities

## Task 9: Improve payment visibility in UI and API output

Status: DONE

Goal:
Make payment-related information easier to inspect in the current debugging workflow.

Requirements:
- Ensure Streamlit clearly surfaces:
  - `cost`
  - `deadline`
  - `action_required`
  - `event_status` when relevant
- Ensure API responses continue returning payment-related fields without regression
- Do NOT introduce payment processing, reminders, or billing logic
- Do NOT change persistence behaviour in a way that breaks existing stored data

Constraints:
- Keep the UI simple and debugging-focused
- Do NOT change extraction meaning
- Must not break existing behaviour

Validation:
- Manually verify at least one payment email in Streamlit
- Use `projects/parentmate/tools/eval_runner.py`
- All existing evals must pass

Output:
- What changed
- Why
- Validation performed
- Any remaining limitations

## Task 10: Improve parent-friendly event summaries

Status: DONE
Requirements: R4, R5

Goal:
Make extracted events easier for parents to scan quickly in the Streamlit UI.

Requirements:
- Add a short parent-friendly summary sentence for each extracted event
- The summary should prioritise the most useful fields, such as date, time, location, deadline, and required action
- The summary must not invent missing details
- Preserve the existing JSON output and extraction behaviour

Constraints:
- Keep the change focused to the current debugging UI
- Do NOT redesign the whole interface
- Do NOT change extraction semantics or stored event structure

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Confirm existing evals still pass
- Manually sanity-check the summary generation logic against at least one event shape in code

Output:
- What changed
- Why
- Validation performed
- Any remaining limitations

## Task 11: Add a thin deterministic unit-test layer

Status: DONE
Requirement: R6

Goal:
Add a small unit-test layer for deterministic logic that is not well covered by evals.

Requirements:
- Add a lightweight unit-test setup for ParentMate
- Focus only on deterministic local logic
- Do NOT introduce live model calls into unit tests
- Keep existing evals as the main product-behaviour safety net

Constraints:
- Prefer a minimal test framework setup
- Do NOT create broad tests around prompt/model behaviour
- Do NOT duplicate full eval coverage in unit tests

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Run the new unit tests locally
- Existing evals must still pass

Output:
- What changed
- Why
- Eval results
- Unit-test results

## Task 12: Cover UI summary logic with unit tests

Status: DONE
Requirements: R4, R5, R6

Goal:
Protect the new parent-friendly event summary behaviour with fast deterministic tests.

Requirements:
- Add unit tests for summary-building logic in the Streamlit layer
- Cover at least:
  - event with date, time, and location
  - event with action-required and items needed
  - deadline-only event
  - event with cost
- Assert that summaries stay readable and do not invent missing details

Constraints:
- Test helper logic only
- Do NOT test Streamlit rendering internals
- Keep wording expectations stable but not overly brittle

Validation:
- Run the new unit tests locally
- Use `projects/parentmate/tools/eval_runner.py`
- Existing evals must still pass

Output:
- What changed
- Why
- Unit-test coverage added
- Validation results

## Task 13: Cover deterministic extraction post-processing with unit tests

Status: DONE
Requirement: R6

Goal:
Add narrow tests for deterministic extraction and normalization logic that evals do not isolate well.

Requirements:
- Add unit tests for deterministic helper or post-processing behaviour where regressions would be hard to localise from eval failures alone
- Prioritise logic such as:
  - cost normalization
  - event_status normalization or inference helpers
  - payment/admin-event merge behaviour if it is implemented deterministically
- Choose only logic that can be tested without live model calls

Constraints:
- Keep tests focused and local
- Do NOT assert raw model behaviour
- Do NOT overfit tests to incidental implementation details

Validation:
- Run the new unit tests locally
- Use `projects/parentmate/tools/eval_runner.py`
- Existing evals must still pass

Output:
- What changed
- Why
- Validation results
- Any deterministic gaps still untested

## Task 14: Add Google Calendar integration path

Type: Feature Task
Status: DONE
Requirement: R7

Goal:
Create a safe first integration path from ParentMate events into Google Calendar without breaking the current extraction workflow.

Requirements:
- Add a project-local Google Calendar integration path for ParentMate
- Keep extraction, storage, and current UI behaviour working as they do today
- Start with a narrow, testable calendar sync path rather than a full scheduling product
- Ensure event data sent to calendar creation uses the existing structured event fields

Constraints:
- Do NOT weaken existing extraction behaviour
- Do NOT redesign the product around calendar-first workflows
- Prefer incremental integration over a large refactor

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Confirm existing evals still pass
- Add a narrow verification path for the new calendar integration behaviour

Output:
- What changed
- Why
- Validation performed
- Remaining limitations

## Task 15: Define calendar event mapping from ParentMate fields

Type: Feature Task
Status: DONE
Requirement: R7

Goal:
Map ParentMate event fields into a consistent Google Calendar event representation.

Requirements:
- Define how existing fields such as title, date, start_time, end_time, location, deadline, and event_status map into calendar event creation
- Handle incomplete events safely when a calendar event cannot be created confidently
- Keep mapping rules explicit and understandable in code

Constraints:
- Do NOT invent missing date/time values
- Do NOT create calendar events when essential scheduling fields are not present
- Keep the mapping logic narrow and maintainable

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Add deterministic tests for mapping logic if it is implemented locally
- Confirm existing evals still pass

Output:
- What changed
- Why
- Validation performed
- Any unresolved mapping edge cases

## Task 16: Add a controlled manual calendar sync flow in the debugging UI

Type: Feature Task
Status: DONE
Requirement: R7

Goal:
Let the current debugging workflow trigger calendar creation intentionally, without turning the app into a full calendar management UI.

Requirements:
- Add a manual sync trigger in the current ParentMate UI or tooling
- Make the action explicit and user-controlled
- Show the outcome clearly enough for debugging and verification

Constraints:
- Do NOT redesign the whole interface
- Do NOT add broad calendar management features
- Keep the flow safe for incremental testing

Validation:
- Use `projects/parentmate/tools/eval_runner.py`
- Manually verify the sync path
- Confirm existing evals still pass

Output:
- What changed
- Why
- Validation performed
- Any remaining limitations

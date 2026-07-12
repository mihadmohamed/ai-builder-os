# UI Design Brief — R2

Requirement: R2 — Improve Readability of Activity Display in Trip Planner

## Target state

Replace the raw JSON-first activity input with a readable activity review surface that lets parents scan, compare, and select activities before planning.

## Layout guidance

- Keep family and weather inputs in the sidebar.
- Put activity selection in the main column before the primary `Plan trip` action.
- Show each activity as a compact, structured item with name, cost, duration, setting, locality, age range, tags, and weather suitability.
- Use checkboxes for include/exclude selection.
- Keep JSON as an advanced diagnostic view only, not the primary interaction.

## Interaction guidance

- Preserve all default activities as selected on first load.
- Let users exclude candidates without editing structured data.
- Keep the selected activity count visible near the planning action.
- If no activities are selected, show a clear error before calling the planner.
- Avoid implying live activity search, booking, maps, or live weather.

## Visual constraints

- Use native Streamlit components first.
- Keep cards compact and scannable; avoid nested containers.
- Use plain labels and short metadata rows instead of raw dictionaries.
- Keep excluded itinerary reasons readable; do not render them as raw JSON.

## Validation notes

- Deterministic validation should cover display helpers that convert activity dictionaries into readable metadata and preserve selected activity payloads.
- Manual UX checks should confirm that a parent can scan and select activity candidates without understanding JSON.


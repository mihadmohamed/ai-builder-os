# Source Directory

This directory contains the Personal Trip Planner application code.

## Files

- `planner.py`
  - deterministic planning core
  - filters and ranks activities against budget, locality, weather, and family preferences

- `storage.py`
  - project-local feedback persistence helpers
  - validates and stores post-trip feedback records

- `app.py`
  - small local Streamlit interface for planning trips and recording feedback

## Current Code Scope

The current source layer supports:

- deterministic itinerary generation from explicit inputs
- clear exclusion reasons for activities that do not fit constraints
- local feedback capture and persistence
- a lightweight local UI for manual review of the planning flow

## Source-of-Truth Expectations

- Keep product intent in `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md`.
- Keep runtime or generated data out of `src/`.
- Keep planner logic deterministic and testable without the UI.
- Keep persistence concerns in `storage.py` rather than mixing them into the planner core.

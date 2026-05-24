# Source Directory

This directory contains the ParentMate application code.

## Files

- `extractor.py`
  - live extraction path from raw email content into structured schema output
- `prompts.py`
  - extraction prompt construction and related prompt helpers
- `schemas.py`
  - structured response models and validation contracts
- `storage.py`
  - local persistence for extracted events and feedback-like state
- `calendar.py`
  - calendar-oriented mapping or handoff helpers
- `app.py`
  - local Streamlit interface for manual extraction review
- `api.py`
  - FastAPI endpoint for programmatic ingestion

## Current Code Scope

The current source layer supports:

- raw school email extraction into structured event data
- schema validation for extracted output
- local file-backed event persistence
- a local UI for review and manual testing
- an API ingestion surface
- calendar-oriented follow-up helpers

## Source-of-Truth Expectations

- Keep product intent in `product/requirements.md`, `product/tasks.md`, `memory.md`, and `rules.md`.
- Keep runtime or generated data out of `src/`.
- Keep extraction logic, schema logic, and persistence logic cleanly separated.
- Preserve a clear boundary between deterministic helpers and live model-backed extraction.

# ParentMate

ParentMate extracts school events and parent actions from raw school emails.

It is a working example product inside AI Builder OS: smaller and more concrete than the operator control panel, but still grounded in local-first workflows and file-backed state.

## What It Does

- accepts a school email subject and body
- uses the OpenAI API to extract structured event data
- validates extracted output against the project schema
- stores extracted results locally in `projects/parentmate/data/events.json`
- exposes both a Streamlit UI and a FastAPI endpoint
- supports replay-backed deterministic evals plus optional live model checks

## Main Project Shape

- `product/requirements.md`
  - current product intent and requirement history
- `product/tasks.md`
  - executable engineering work and validation tasks
- `memory.md`
  - project-specific decisions and extraction learnings
- `rules.md`
  - extraction and output constraints
- `src/`
  - extraction, storage, calendar, API, and UI code
- `evals/`
  - replay-backed extraction fixtures and expected outputs
- `tools/`
  - eval runners and replay-capture tooling
- `data/`
  - local runtime data such as extracted events

## Run The Streamlit App

```bash
PYTHONPATH="$PWD" .venv/bin/streamlit run projects/parentmate/src/app.py
```

## Run The API

```bash
PYTHONPATH="$PWD" .venv/bin/python -m uvicorn projects.parentmate.src.api:app --reload
```

Then send a `POST` request to `/ingest` with:

```json
{
  "subject": "Year 3 Trip",
  "body": "There will be a school farm trip on 10 May 2026 to AB Farm."
}
```

## Environment

- `OPENAI_API_KEY` is required for live extraction.
- `OPENAI_MODEL` is optional; otherwise the project uses its default configured model.

## Validation

ParentMate uses two validation paths:

- replay-backed evals are the default deterministic validation path
- live model evals are optional and depend on network/API availability

Run the deterministic suite with:

```bash
python3 projects/parentmate/tools/eval_runner.py
```

Run the optional live model check with:

```bash
python3 projects/parentmate/tools/live_eval_runner.py
```

Refresh replay fixtures with:

```bash
python3 projects/parentmate/tools/capture_replays.py
```

## Data Privacy

Runtime extraction data is written to `projects/parentmate/data/events.json`, which is ignored by Git.

Use `projects/parentmate/data/events.example.json` for harmless sample data.

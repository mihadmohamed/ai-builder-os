# ParentMate

ParentMate extracts school events and parent actions from raw school emails.

## What It Does

- accepts an email subject and body
- uses the OpenAI API to extract structured event data
- validates model output with Pydantic
- stores extracted results locally in `projects/parentmate/data/events.json`
- exposes both a Streamlit UI and a FastAPI endpoint

## Project Structure

- `product/requirements.md` defines current product intent
- `product/tasks.md` defines executable work for the engineer role
- `memory.md` stores project-specific decisions and learnings
- `rules.md` stores project-specific operating constraints
- `src/` contains the application code
- `evals/` contains extraction eval fixtures
- `tools/eval_runner.py` runs the eval suite
- `data/` stores local runtime JSON data

## Run The Streamlit App

```bash
streamlit run projects/parentmate/src/app.py
```

## Run The API

```bash
uvicorn projects.parentmate.src.api:app --reload
```

Then send a `POST` request to `/ingest`:

```json
{
  "subject": "Year 3 Trip",
  "body": "There will be a school farm trip on 10 May 2026 to AB Farm."
}
```

## Environment

Set `OPENAI_API_KEY` before running extraction.

Optionally set `OPENAI_MODEL`; otherwise the app uses `gpt-4.1-mini`.

## Validation

ParentMate uses two validation paths.

- replay-backed evals are the default deterministic validation path
- live model evals are optional and depend on network/API availability

- eval inputs and expected outputs live in `projects/parentmate/evals/`
- replay response fixtures store raw model JSON response bodies in `projects/parentmate/evals/replays/`
- run the deterministic suite with `python projects/parentmate/tools/eval_runner.py`
- run the live model check with `python projects/parentmate/tools/live_eval_runner.py`
- refresh replay fixtures with `python projects/parentmate/tools/capture_replays.py`
- `projects/parentmate/tests/` is reserved for future unit or smoke tests and is not the primary validation path today

## Data Privacy

Runtime extraction data is written to `projects/parentmate/data/events.json`, which is ignored by Git.

Use `projects/parentmate/data/events.example.json` for harmless sample data.

## Tests

This directory is intentionally reserved for future unit tests or smoke tests.

Today, the main validation path for ParentMate is the eval suite:

- Fixtures live in `projects/parentmate/evals/`
- The runner lives in `projects/parentmate/tools/eval_runner.py`
- Replay files live in `projects/parentmate/evals/replays/` and store raw model JSON response bodies
- Optional live model checks live in `projects/parentmate/tools/live_eval_runner.py`

Use the eval suite to validate extraction behavior and regression safety.

Use `tests/manual/` for lightweight human-reviewed checks that are not well suited to automation yet, such as obvious UX clarity checks.

Use `tests/unit/` for fast deterministic checks of local helper logic that evals do not isolate well.

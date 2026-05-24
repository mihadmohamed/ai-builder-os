# Tests

Use this directory for code-level validation that belongs next to the project.

## What Belongs Here

- unit tests for deterministic logic
- smoke tests for entrypoints or integration seams
- `tests/manual/` notes for human-reviewed checks that are not worth automating yet

## Guidance

- if evals are the main validation mechanism, say that clearly in the project README
- keep this directory for narrower code-level checks rather than replay fixture validation
- use manual checks for UX clarity, review flow, or presentation issues that are not meaningfully machine-evaluable

## Evals

Store project eval fixtures here.

Suggested structure:

- `case_1.txt` or equivalent input fixture
- `case_1_expected.json` for expected normalized output
- `replays/` for raw model-response snapshots when the project uses replay-backed validation

Prefer deterministic evals for routine development.

Default recommendation:

- begin with deterministic evals first
- add live validation separately rather than mixing it into the default local workflow

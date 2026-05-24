# Evals

Store project eval fixtures here.

## Recommended Structure

- `case_1.txt` or equivalent input fixture
- `case_1_expected.json` for expected normalized output
- `replays/` for raw model-response snapshots when the project uses replay-backed validation

## Guidance

- begin with deterministic evals first
- treat replay-backed validation as the default path when the project depends on model output
- add live validation separately rather than mixing it into the default local workflow
- keep eval fixtures stable and easy to inspect

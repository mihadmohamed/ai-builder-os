# PM behavioral evaluation baseline

Baseline ID: `pm-baseline-2026-07-22.v1`

Backend: deterministic synthetic fixtures — no model tokens or OpenAI API requests.

## Result

- 16 representative cases
- 3 trials per case; 48 total trials
- 100% contract pass rate
- mean score 100/100
- threshold: at least 3 trials per case and at least 95% pass rate

All cases passed every deterministic grading dimension: typed output, evidence use, tool choice, consultations, approval behavior, guardrail response, trace trajectory, and canonical outcome.

## Revision fingerprints

- dataset: `666c831d5e7664736582d8a284becdca13b0f3e8919d7a355af83b05d14ddef1`
- PM instructions: `3ba1c900071c3f198d00bdc109d25ed5b3f696923f269770b116bceb35dba4ed`
- tool policy: `f42755b725af64319a6a73da442413b5502ce2df2ec59728de26079f1bac8460`
- guardrails: `c4f118968d3a5a3debbbdfef6355dff856378e1cc2be19a97033ba4b8812ff7c`
- model label (`deterministic-fixture-v1`): `e0e72bfdf253e45367bef89d6eca804177f903cfb6b32266ceb16d63160cb563`

The runner recomputes these fingerprints on every run. A changed fingerprint identifies the revision boundary; it is not itself a regression. `compare_pm_reports` reports case and dimension regressions separately.

## Limitations

- This baseline proves the dataset, grading, aggregation, and reporting contracts. It does not prove that a live PM model reasons well.
- Identical synthetic trials intentionally have no variance. Multiple live trials are required to observe model variance.
- A 95% pass threshold is the first operational threshold, not a statistical confidence claim.
- Codex and Agents SDK reports are comparable only when dataset version and all revision fingerprints are retained.
- Production PM model selection remains out of scope until separately authorized live evidence exists.

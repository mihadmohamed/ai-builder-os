# System Memory — Electrical Services Website v1

## Purpose

Store project-specific learnings, decisions, and reusable patterns.

Only record information that is likely to matter again.

## Failure Memory

Add reusable failure patterns here.

## Decision Memory

### D1 — Frontend-only contact boundary for R1

- R1 uses browser-native telephone and email actions rather than a misleading form or booking flow.
- Services, projects, and testimonials remain typed local content so the first slice needs no backend.
- Release is preview-ready only until GitHub release approval permits Vercel deployment.

### D2 — Validation blocker for R1

- The 2026-07-12 implementation could not complete build or browser smoke validation because dependencies are absent, network installation is restricted, the offline npm cache is incomplete, and the sandbox rejects localhost verification.
- Keep Task 1 and R1 `IN_PROGRESS` until those checks pass in a capable environment.

## Observations

Store evidence-bearing product observations here.

Suggested format:

### O1 — Short observation title

Observation:
- What seems to be true

Evidence:
- What supports the observation

Confidence:
- High | Medium | Low

Validation method:
- How the evidence was gathered

Implication:
- What this suggests for future prioritisation or strategy

Use this section for findings that may influence future prioritisation or strategic direction.

## Heuristic Memory

Add project-specific heuristics here.

## Open Questions

Add unresolved project questions here.

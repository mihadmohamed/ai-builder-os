# System Memory — Personal Trip Planner

## Purpose

Store project-specific learnings, decisions, and reusable patterns.

Only record information that is likely to matter again.

---

## Failure Memory

Add reusable failure patterns here.

---

## Decision Memory

Add project-specific decisions here.

### D1 — Offline-first MVP boundaries

Decision:
- Implement R1 as an offline deterministic MVP with explicit weather and local activity inputs.
- Keep core planning logic in pure Python, feedback in project-local JSON storage, and any UI as a thin wrapper.

Reason:
- The requirement calls for weather and local activities, but this project has no configured live weather, maps, booking, or activity provider.
- The product must not hallucinate missing weather, prices, activities, or locality.

Implication:
- Future live integrations can replace input providers without changing the core planner contract.

---

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

### O1 — R1 deterministic validation is available

Observation:
- The Trip Planner now has offline deterministic validation for itinerary filtering, ranking, and feedback storage.

Evidence:
- `python3 projects/Trip planner/tools/eval_runner.py` passed 4/4 cases.
- `python3 tools/validate_project_structure.py 'Trip planner'` passed.

Confidence:
- High

Validation method:
- Project-local eval runner and workspace project-structure validator.

Implication:
- Future planner changes should preserve or extend the offline eval runner before relying on live integrations.

---

## Heuristic Memory

Add project-specific heuristics here.

---

## Open Questions

Add unresolved project questions here.

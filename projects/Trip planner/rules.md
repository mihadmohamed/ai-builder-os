# Project: Personal Trip Planner

## Goal

Help families plan simple, budget-aware local trips through a deterministic planner that stays grounded in explicit inputs and trustworthy output.

---

## Inputs

- family preferences and child age range
- local area or destination context
- budget expectations
- explicit weather context
- candidate activities with locality, cost, duration, age suitability, and tags
- optional post-trip feedback

---

## Outputs

- recommended trip activities and itinerary summaries
- excluded activity reasons when options do not fit the constraints
- structured post-trip feedback records
- a small local planning interface suitable for manual review

---

## Rules

- Do NOT hallucinate activities, prices, locations, weather, or family constraints.
- Treat weather and activity data as explicit inputs in the current slice.
- Keep the core planner deterministic and usable offline.
- Prefer explainable exclusions over silent filtering when an option does not fit budget, locality, age range, or weather.
- Keep project logic inside this project directory unless the work clearly belongs to shared OS infrastructure.
- Preserve file-backed feedback and planning data so behavior stays inspectable.
- Keep the UI honest about what the product does not do: no live booking, no hotel planning, no long-distance travel workflow, no social layer.
- Keep output aligned with the planner and storage schema.

---

## Decision Logic

1. Validate explicit inputs before generating a trip plan.
2. Filter out activities that violate locality, budget, age-range, or weather constraints.
3. Prefer activities that match stated family preferences and current context.
4. Return a clear itinerary plus exclusion reasons rather than pretending weak matches are acceptable.
5. Preserve valid feedback and reject invalid feedback without mutating stored data.

---

## Success Criteria

- Families can generate practical local trip plans from explicit inputs.
- The planner remains trustworthy because recommendations and exclusions are explainable.
- Feedback persistence stays reliable and file-backed.
- Deterministic validation covers the planner core well enough to catch regressions offline.

---

## Out of Scope

- live booking or commerce flows
- hotel or lodging workflows
- long-distance travel planning
- hosted recommendation infrastructure
- social sharing or collaborative trip planning

# Build-to-Learn Pull-Through for R74

## Context
Build-to-learn pathways were useful, but they still lived beside concept management instead of feeding back into it. That created a gap between:

- planning a bounded experiment
- actually updating concept understanding

## Workflow shaping
This slice was shaped through the OS workflow:

- PM clarified that the first cut should reflect linked pathway status, what was learned, what remains unclear, and whether the concept was strengthened or reopened
- Experience Designer surfaced the core user problem: build-to-learn felt disconnected from concept understanding
- UI Designer recommended one inline build-to-learn block in concept management with one clear action to capture learning from the build
- Architect advised keeping the state evolutionary, inspectable, and file-backed

## First-slice product direction
- Show linked build-to-learn state directly inside Concept manager
- Preserve pathway status as `planned`, `active`, or `captured`
- Let the operator capture:
  - what building taught them
  - what is still unclear
  - whether the concept was strengthened or reopened
- Update the concept record without auto-marking it learned

## UX guardrails
- Keep the experience inside the existing concept-management flow
- Avoid creating a second dashboard or management surface
- Use one explicit action: `Capture learning from build`
- Keep the language plain and the UI light

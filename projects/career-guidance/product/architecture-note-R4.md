# Architecture Note — R4

Requirement: R4 — CV Upload and Job Posting Link Feature

## Trigger

Architect review is required because CV upload introduces a trust boundary around user-provided career documents and personal data.

## Structural risks

- Persisting uploaded CV contents would create a privacy and data-retention surface the project does not currently model.
- Live job-board search or email notification would introduce external integrations, credentials, network failure modes, and user expectations outside the current deterministic local architecture.
- Supporting arbitrary binary CV formats would require parsing dependencies and error handling beyond the existing validation surface.

## Smallest coherent implementation shape

- Keep the implementation local and deterministic.
- Accept text-oriented CV uploads only (`.txt` and `.md`) in the Streamlit UI.
- Decode uploaded content in memory for the current request.
- Do not write uploaded CV contents to disk or project data files.
- Use a small local catalogue of representative job postings with direct links for deterministic matching.
- Return job-link recommendations from `advisor.py` alongside the existing gap analysis output.

## Engineer guardrails

- Do not add persistence for CV uploads.
- Do not add live network search, job-board scraping, email notifications, accounts, or background jobs.
- Keep matching explainable through skill keywords already used by the advisor.
- Add unit/source validation for upload guidance and job-link results.
- Preserve existing R1/R2 analyzer behavior and validation paths.

## Recommendation

Proceed with a narrowed R4 MVP: in-app text CV upload plus local deterministic job-link recommendations. Treat external job databases, saved dashboards, and email notifications as future scope.

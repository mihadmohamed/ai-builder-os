# Experience Designer Findings — R4

Requirement: R4 — CV Upload and Job Posting Link Feature

## User problem

Job seekers need a faster way to move from their CV to relevant job opportunities without manually copying every piece of career material into the advisor flow.

## Affected workflow

Advisor setup and results review: the user provides CV material, runs a match, and reviews recommended job posting links.

## Evidence

- R4 explicitly asks for CV upload and personalized job posting links.
- The current app only supports pasted CV text and pasted target job descriptions.
- Existing project behavior is deterministic and local, so any link-matching experience must be honest about not using a live external job database.

## Confidence

Medium.

## Severity / frequency

High severity for users who already have a CV file and want a quicker path to job opportunities. Frequency depends on how often users start from a saved CV rather than pasted text.

## Finding type

Feature candidate with usability implications.

## Recommendation type

UX improvement in scope for an MVP, with scope narrowed to local in-app matching.

## Rationale

The most usable first version is a single advisor form that accepts either uploaded CV text files or pasted CV text, then shows job posting links in the same results area. This avoids a separate dashboard, background notifications, external job-board integration, or CV persistence before those product and security assumptions are validated.

## Recommended next role

UI Designer should shape the upload affordance, fallback text input, and job-link result hierarchy before Engineer implementation.

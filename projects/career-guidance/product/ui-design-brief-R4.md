# UI Design Brief — R4

Requirement: R4 — CV Upload and Job Posting Link Feature

## Mode

UI Designer: Design Direction for a focused Streamlit upload and job-link matching update.

## Target surface

The Career Guidance Advisor Streamlit form and post-analysis result area.

## Design goal

Let users start from a CV file while keeping the existing paste-and-analyze workflow clear, trustworthy, and lightweight.

## User and context

Job seekers may have a CV saved as a text-based document and want direct job posting links that appear relevant to their skills. They need to understand what the app can and cannot do without overclaiming live job-board coverage.

## Visual direction

- Keep the restrained native Streamlit layout.
- Place CV upload near the existing CV text input so users can choose upload or paste without switching screens.
- Use concise captions for accepted file types and privacy posture.
- Keep job links as scannable result items with match reason, score, and direct link.
- Avoid dashboard chrome, decorative cards, sidebars, broad redesign, or notification UI for the MVP.

## Layout and interaction guidance

- Preserve one primary form and one primary action: `Analyze career fit`.
- Add a CV upload control before or alongside the CV text area.
- Treat pasted CV text as an editable fallback and allow it to override or supplement upload text.
- Make clear that uploaded CV content is used for the current analysis and is not saved by the app.
- Show recommended job links after the summary, before detailed gap cards, so users see the opportunity output early.
- Use progressive disclosure for structured output and keep warnings near the result state.
- Do not introduce email notifications, accounts, saved dashboards, background matching, or application submission.

## Surface changes

- Add a `.txt`/`.md` CV upload control with privacy guidance.
- Add deterministic job-link recommendations to the result area.
- Show each recommendation with title, company, match score, reason, and link.
- Keep existing gap analysis and development plan output available.

## Validation notes

- Source-level validation should confirm the upload control, privacy copy, and job-link rendering exist.
- Unit tests should cover deterministic job matching and missing/low-signal CV behavior.
- Existing deterministic evals and project structure validation should continue to pass.

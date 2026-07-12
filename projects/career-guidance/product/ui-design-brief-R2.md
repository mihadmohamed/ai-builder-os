# UI Design Brief — R2

Requirement: R2 — Improve Job Posting Input Clarity

## Mode

UI Designer: Design Direction for a focused Streamlit form copy and input-clarity update.

## Target surface

The Career Guidance Advisor Streamlit form, specifically the target job descriptions input.

## Design goal

Make the accepted multi-posting input format obvious before submission while preserving the existing calm, single-form workflow.

## User and context

Job seekers may paste several role descriptions from job boards. They need to know whether the app expects one combined text block, separate lines, or another format.

## Visual direction

- Keep the existing restrained Streamlit style.
- Prefer native text area `help` text, nearby caption text, and clearer placeholder copy.
- Keep guidance short enough to be scanned while typing.
- Avoid new cards, sidebars, decorative containers, or broad visual redesign.

## Layout and interaction guidance

- Keep `CV text` and `Target job descriptions` as the two primary inputs in the same form.
- Put the multi-posting guidance directly on or immediately below the `Target job descriptions` field.
- Include a concrete separator example: `Posting 1 ...`, blank line or `---`, then `Posting 2 ...`.
- Make clear that users can paste one posting or several postings into the same field.
- Preserve the single primary action: `Analyze career fit`.
- Do not add dynamic fields, file uploads, parsing previews, or per-posting controls for R2.

## Surface changes

- Rename or clarify the target field help text so it explains acceptable multi-posting input.
- Update placeholder text to demonstrate two postings separated by a visible divider.
- Keep the result and warning areas unchanged except for any source-level validation needed to prove the guidance exists.

## Validation notes

- Source-level validation should assert that the app contains explicit multi-posting guidance and a separator example.
- Existing unit tests and deterministic evals should continue to pass.

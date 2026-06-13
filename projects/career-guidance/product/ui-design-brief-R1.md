# UI Design Brief — R1 Career Guidance Advisor

## Mode

UI Designer: Design Direction and lightweight UI review.

## Target Surface

Streamlit advisor screen for job seekers who paste CV text and target job descriptions, then review a gap analysis and development plan.

## Direction

- Keep the first screen task-focused: CV input, target-job input, and one primary action.
- Use native Streamlit forms and containers before custom styling.
- Show the analysis summary before detailed gap output.
- Present each gap with a consistent hierarchy: skill, importance, CV evidence, target-job evidence, action, resource.
- Use progressive disclosure for structured JSON output.
- Surface insufficient-input and low-signal warnings near the result area.

## Constraints

- Do not create a marketing-style landing page.
- Do not imply job placement, recruitment, or external learning-platform integrations.
- Keep visual tone restrained, readable, and utilitarian.
- Preserve rerun orientation by keeping the most recent result in session state.

## Review Notes

- Implemented UI follows the design direction structurally.
- Runtime UI review is blocked in the current Python environment because `streamlit` is not installed.

# UI Design Brief — R1 Dream Translator

## Mode

UI Designer: Design Direction.

## Target Surface

Streamlit dream translation screen where a user describes a dream, chooses an art style, and reviews an interpretation with a visual representation.

## Direction

- Keep the first screen focused on the dream text input, visual style selector, and one primary translate action.
- Present the generated visual before detailed interpretation so the output feels immediate and engaging.
- Use a calm two-column result layout on desktop: visual representation on the left, interpretation and insights on the right.
- Stack output sections naturally on narrower layouts through native Streamlit behavior.
- Show at least three distinct insights with clear labels, not a dense paragraph.
- Use progressive disclosure for the generated image prompt and structured output.
- Keep language respectful and non-clinical; avoid implying diagnosis, therapy, prediction, or certainty.

## Constraints

- Do not create a marketing landing page.
- Do not require external image-generation services for the first deterministic implementation.
- Do not imply professional psychological assessment.
- Keep the visual style artistic and dreamlike while preserving readability and scanability.
- Prefer native Streamlit layout primitives before custom components.

## Implementation Notes

- A deterministic SVG-style visual is sufficient for this requirement as long as it reflects the dream theme and selected style.
- The app should preserve the latest result in session state so Streamlit reruns do not disorient the user.

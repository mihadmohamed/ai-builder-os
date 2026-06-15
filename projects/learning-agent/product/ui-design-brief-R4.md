# UI Design Brief — R4

Requirement: R4 — Enhancement of AI Builder Learning Agent Landing Page

## Design goal

Create a calm admitted-user welcome that makes the learner's next step obvious and leads directly into the canonical profile workflow.

## User and context

The user has been admitted to the pilot and is opening the hosted app to set or review a profile, follow the generated plan, and continue guided learning. They do not need another explanation of pilot access.

## Visual direction

- Use one restrained welcome surface with pale blue, green, and warm accent tints from the existing landing palette.
- Keep the welcome compact so the canonical `Profile` state remains visible near the first viewport.
- Use dark slate body text and sufficiently strong blue labels for readable contrast on pale backgrounds.
- Keep native Streamlit typography, navigation, forms, and buttons; custom styling is limited to the wrapper welcome.

## Layout and interaction guidance

- Render a short admitted-state label, a personalized or neutral welcome heading, and one sentence describing the immediate journey.
- Show `1 Profile`, `2 Learning plan`, and `3 Learn next` as a compact responsive progression inside the same welcome surface.
- Keep the signed-in email and sign-out control in a quiet utility row below the welcome.
- Remove the separate wrapper `How it works` and `Pilot boundary` sections because the welcome progression and canonical learning surface already provide orientation.
- Let the progression wrap naturally on narrow screens; do not use fixed heights or overflow-dependent layout.
- Do not add new navigation controls. The canonical segmented learning navigation remains the interaction source of truth.

## Surface changes

- Replace the admitted wrapper title and repeated instructional blocks with the scoped welcome surface.
- Keep operator access-request review below the utility row and before the canonical learning surface.
- Preserve the existing non-admitted landing hero unchanged.

## Constraints

- Use scoped HTML/CSS and native Streamlit only; no third-party component is justified.
- Escape identity-derived text before rendering it in HTML.
- Preserve local preview, OIDC, allowlist, sign-out, operator, and canonical learning behavior.
- Do not add animation, remote assets, gradients with poor text contrast, or decorative elements that increase load cost.

## Open questions resolved for implementation

- Continue the existing blue-led palette with pale red and green accents; do not introduce a new brand color.
- Target WCAG-readable dark text on pale surfaces and avoid placing body text directly on saturated accents.
- Treat the lack of user-testing evidence as a measurement gap, not a blocker for this bounded hierarchy improvement.

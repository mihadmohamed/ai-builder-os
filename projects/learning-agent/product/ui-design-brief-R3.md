# UI Design Brief — R3

Requirement: R3 — Request Page Layout Improvements

## Design goal

Make requesting access and reviewing the learning experience read as two separate actions while keeping them in one coherent decision column.

## User and context

The user is signed in but not admitted. They need to understand that the form submits an access request, while the screenshot is supporting product evidence that can be enlarged without granting live access.

## Visual direction

- Preserve the existing restrained landing-page palette, typography, and native Streamlit controls.
- Use two separate bordered containers with consistent radius and spacing rather than introducing a new card style.
- Keep the request surface first and dominant; treat the preview surface as compact supporting evidence.

## Layout and interaction guidance

- Keep the existing wide two-column page composition.
- In the right column, render `Request access` in its own bordered container.
- Render `See the learning experience` in a second bordered container immediately below the request container.
- Constrain the inline preview to a compact thumbnail width so its height is materially lower than the current full-column image.
- Preserve `Enlarge preview` as the route to full detail and keep its native dialog behavior.
- Let Streamlit stack the page columns naturally on narrow viewports; do not introduce a fixed-height or overflow-dependent layout.

## Surface changes

- Move the existing preview renderer outside the request container.
- Add a small vertical gap between the two surfaces through normal Streamlit flow.
- Keep all existing headings, form fields, captions, button labels, and feedback messages unchanged.

## Constraints

- Use native Streamlit only; no third-party component is justified.
- Do not change request validation, persistence, authentication, allowlist, local preview, sign-out, or modal semantics.
- Do not use fixed section heights. Reduce the preview height through responsive thumbnail sizing.
- Keep `Request access` as the only primary action.

## Open questions resolved for implementation

- No fixed pixel height is required. A compact thumbnail with on-demand enlargement satisfies the intent more robustly across viewport sizes.
- The preview remains below the request surface so the decision flow and R2 direction stay intact.

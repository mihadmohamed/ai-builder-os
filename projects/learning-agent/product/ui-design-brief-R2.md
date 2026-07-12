# UI Design Brief — R2

Requirement: R2 — Landing Page Design Improvement

## Design goal

Create a calm, credible external landing page where non-admitted learners can quickly understand the pilot, inspect the learning experience, and request access through one coherent flow.

## User and context

The user has already signed in with Google but does not yet have full pilot access. They need enough product evidence to make an informed request without mistaking the preview for admitted access.

## Visual direction

- Keep the existing blue, red, and green brand accents, using pale tints for depth rather than saturated panels.
- Use one restrained introductory surface to establish hierarchy; avoid turning every section into a card.
- Render account identity as quiet secondary metadata rather than a prominent status banner.
- Keep typography and controls native to Streamlit so the wrapper remains consistent and durable.

## Layout and interaction guidance

- Preserve the wide two-column composition: product explanation on the left, access decision on the right.
- On narrow screens, allow Streamlit columns to stack naturally with explanation before the access action.
- Keep `Request access` as the only primary button in the form.
- Place `See the learning experience` immediately below the form in the right column.
- Show a compact thumbnail with a clear `Enlarge preview` action.
- Open the existing image in a native Streamlit dialog, include an explanatory caption, and rely on the dialog's standard close behavior.
- Do not add animation; the modal transition should remain native and predictable.
- Keep `How access works` and pilot-boundary copy below the main decision area as supporting information.

## Surface changes

- Replace the full-width signed-in info banner with a subtle account line.
- Add light visual grouping to the hero and access area through scoped CSS and pale brand tints.
- Tighten repeated headings and copy so the scan order is pilot value, approved-user benefits, request action, product preview, process detail.
- Preserve repository and privacy-contact links as secondary support.

## Constraints

- Use native Streamlit only; no component or styling dependency is justified.
- Scope CSS to landing-page marker classes and stable Streamlit primitives where possible.
- Preserve request validation, request persistence, sign-out, local mode, OIDC, and allowlist behavior.
- The modal must not imply that preview users have live tutoring access.
- The image must retain useful alternative text/caption context.

## Open questions resolved for implementation

- Highlight the personalized plan and guided progression, because these are the clearest differentiators visible in the existing asset.
- Use no custom animation or transition for the modal.

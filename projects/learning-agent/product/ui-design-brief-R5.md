# UI Design Brief — R5

Requirement: R5 — UI Enhancement for Consistent Card Layout

## Design goal

Create a consistent wrapper card system so grouped information reads as organized, calm, and easy to scan across signed-out, non-admitted, and admitted states.

## User and context

Users are either evaluating the pilot, requesting access, or entering the admitted learning workspace. They need to understand grouped information quickly without being slowed by uneven surfaces or visual ambiguity.

## Visual direction

- Keep the existing pale blue, green, and warm accent palette; do not introduce a new theme.
- Use a shared card treatment: white translucent surface, light slate-blue border, 0.75rem radius, compact shadow, and consistent internal padding.
- Use equal-height grid behavior for repeated cards where they sit side by side.
- Keep the overall feel restrained and product-like rather than decorative.

## Layout and interaction guidance

- Apply a shared CSS class to wrapper-authored card groups instead of relying only on Streamlit bordered container defaults.
- For admitted progression cards, use a three-column grid with stretch alignment on desktop and a single-column stack under the existing mobile breakpoint.
- For request and preview surfaces, wrap the native Streamlit content in scoped card markers so CSS can standardize the surrounding container without adding dependencies.
- Use subtle hover lift and border-color changes for card surfaces. Do not change cursor to pointer for non-clickable cards.
- Preserve compact vertical rhythm; avoid fixed heights that could clip copy, form controls, images, or validation messages.

## Surface changes

- Add a small wrapper-card CSS system inside `LANDING_PAGE_STYLE`.
- Apply the card class to admitted progression cards.
- Apply the card class to the request-access and learning-preview bordered containers.
- Leave the canonical learning tab and its internal learning-engine UI untouched.

## Constraints

- Use scoped CSS and native Streamlit only; no new UI dependency is justified.
- Keep all R2, R3, and R4 behavior intact.
- Preserve local preview, OIDC, allowlist, sign-out, request validation, request persistence, operator review, and canonical learning behavior.
- Do not set rigid card heights that break responsiveness.
- Escape identity-derived text before rendering it in HTML.

## Open questions resolved for implementation

- There is no fixed minimum card height requirement. Equal-height behavior should come from grid stretch and content-safe `min-height` values only where they do not clip.
- The established wrapper palette remains the styling source.
- Existing grouping remains intact: request form and preview stay separate; admitted progression remains three distinct steps.

## Pre-implementation UI review

Status: READY FOR ENGINEERING

- Use one `.learning-agent-card` class as the shared surface primitive for wrapper-authored cards.
- Keep `.learning-agent-admitted-steps` as the equal-height grid and let each child stretch through normal CSS grid behavior.
- For native Streamlit bordered containers, add a preceding marker class and scope CSS to the adjacent `stVerticalBlockBorderWrapper` element so the Python layout remains native.
- Use `box-shadow: 0 10px 26px rgba(24, 34, 48, 0.06)` and a slightly stronger border on hover; keep motion short and subtle.
- Do not restyle canonical learning cards or broader Streamlit containers outside the hosted wrapper sections.

## Post-implementation UI review

Status: PASS

- The shared `.learning-agent-card` treatment is applied to the admitted progression cards.
- The request-access and preview Streamlit containers are scoped with wrapper-local marker elements and share the same card surface treatment.
- The implementation preserves the existing palette, spacing discipline, radius, shadow, and compact hover direction from this brief.
- No third-party UI dependency, new navigation model, or canonical learning UI styling was introduced.

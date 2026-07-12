# UI Design Brief — R1

Mode: Design Direction
Status: accepted
Requirement: R1

## Design goal

Make a dependable local electrical contractor feel current, precise, and easy to contact while retaining the existing blue/red brand character.

## Visual direction

- Use deep navy for trust, warm off-white for approachability, clear blue for navigation/action, and red only as a focused accent.
- Pair a strong editorial display face with a neutral, readable body face; retain sensible system fallbacks.
- Prefer thin rules, generous whitespace, small uppercase labels, and crisp rectangular controls over decorative card excess.
- Use restrained radial gradients and line-work to give the hero energy without fabricating project photography.

## Layout and interaction

- Desktop: two-column hero, three-column services, asymmetric proof section, and direct contact panel.
- Mobile: collapse to one column, use a compact menu, maintain 44px targets, and add a fixed phone/quote action bar.
- Testimonials use one visible quote with labelled previous/next controls and position indicators.
- Portfolio tiles use descriptive project labels; the layout must remain coherent if imagery is unavailable.
- Respect reduced-motion preferences and never rely on colour alone for state.

## Constraints

- Do not redraw the Wright Sparks logo; use a typographic wordmark until an approved deployable logo asset is present.
- No shadcn dependency is needed for this focused marketing surface; semantic native controls keep the bundle and interaction model simpler.
- Contact actions resolve to browser-native telephone/email flows; no misleading form submission state.

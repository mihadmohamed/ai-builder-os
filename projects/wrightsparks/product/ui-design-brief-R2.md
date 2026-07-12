# UI Design Brief — R2

Mode: Design Direction  
Status: accepted  
Requirement: R2

## Design goal

Strengthen the existing hero's trust hierarchy using the exact approved R2 message without redesigning the layout or weakening the established Wright Sparks visual system.

## Content hierarchy

- Eyebrow: `TRUSTED ELECTRICIANS • READING & BERKSHIRE`.
- Headline line one: `Electrical Work Done Right.`
- Headline line two: `First Time. Every Time.`
- Supporting copy: `From emergency repairs to complete installations, Wright Sparks delivers safe, certified electrical work with clear communication, quality workmanship, and respect for your home.`
- Keep the existing quote CTA, telephone CTA, micro-proof, and imported hero image in their current order.

## Visual and responsive constraints

- Preserve the current eyebrow treatment, display typography, emphasis styling, spacing system, and two-column desktop composition.
- Keep both headline lines inside the single semantic `h1`; use the existing emphasized second-line treatment.
- Let the longer supporting copy wrap naturally within the current readable measure. Do not reduce font size solely to force a particular line count.
- On mobile, retain copy-first stacking, full-width actions, visible focus states, and the existing 360px minimum layout behavior.
- Do not add a component library for this copy-only change; the existing semantic React structure is sufficient.

## Interaction and state constraints

No loading, empty, error, form, navigation, or external-integration behavior changes. Existing states and actions must remain functional and browser-verifiable.


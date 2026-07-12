# R1 UI Design Brief — Wright Sparks

Linked task: R1.1  
Mode: UI Designer — Design Direction

## Design goal

Make it immediately clear that Wright Sparks is a credible Reading electrician and give visitors a low-friction path to call, message on WhatsApp, or send a structured enquiry. Modernisation should come from confident hierarchy, generous spacing, useful motion, and strong real-world imagery—not decorative novelty.

## User and context

The primary user is a homeowner or local customer comparing electrical services, often on a phone and sometimes with an urgent need. They must be able to scan credentials, service fit, and location quickly before choosing a contact route.

## Visual direction

- Use warm off-white surfaces, deep ink/navy text, electric yellow for primary actions, and restrained green only for WhatsApp. This reflects the imported logo while keeping contrast trustworthy.
- Pair a characterful display face with a clean sans-serif body face; use large, compact headlines and short readable measures.
- Prefer softly rounded cards, fine borders, controlled shadows, and generous negative space. Avoid a generic grid of equal cards across every section.
- Use the imported electrician image as documentary hero/work imagery. Use imported accreditation marks only in a dedicated trust strip. Preserve asset provenance in `public/site-import/ASSET_SOURCES.md`.

## Layout and interaction guidance

- Sticky header: compact brand, desktop anchor navigation, phone action, and quote action. On mobile, use a clearly labelled menu button and a full-width disclosure panel; Escape and link selection close it.
- Hero: asymmetric two-column layout, with the promise and contact choices first and the real service image second. On mobile, copy precedes imagery and CTAs become full-width.
- Trust/value row: preserve the source claims “Affordable rates…”, “Exceptional work…”, and “Comprehensive insurance…” as concise proof, not inflated marketing claims.
- Services: six scan-friendly service cards with small line icons and direct quote links. Do not imply unavailable booking or pricing functionality.
- About/work: alternate image and copy so the page rhythm does not become a card wall.
- Accreditations: horizontally balanced logo tiles with descriptive alt text; the marks are evidence, not decorative badges.
- Service area: pair Reading-area copy with a responsive Google Maps embed. Do not state a street address because none was present in the import.
- Testimonials: do not invent quotations or ratings. Present a transparent invitation to view independently verified feedback on Checkatrade until review data/URL is supplied.
- FAQ: native disclosure controls so keyboard and no-JavaScript behavior remain dependable.
- Quote/contact: two distinct, short forms. Quote captures service, timing, and details; contact captures name, contact route, and message. Validate required fields inline, show a submitting label, then open a prefilled email handoff and retain an explicit success panel. Include a retry/error message if handoff cannot be constructed.
- Persistent mobile WhatsApp action: keep above device safe areas without obscuring footer/actions, with a visible text label rather than an unexplained icon.

## Surface changes

- Replace the starter page with a complete one-page route and reusable header, section, card, form, FAQ, and footer components.
- Add explicit `loading.tsx`, `error.tsx`, and `not-found.tsx` route states, plus form validation/submission feedback.
- Add local assets and traceability notes; no source-site image hotlinks.
- Centralize phone, email, WhatsApp, Checkatrade, and map configuration so missing real destinations are easy to correct.

## Constraints

- Frontend-only Next.js slice; no database, authentication, payment, or enquiry API.
- Responsive from 360px upward, visible keyboard focus, reduced-motion support, semantic landmarks, and 44px minimum action targets.
- Source-grounded claims and navigation only. No invented reviews, rating counts, opening times, street address, or response-time guarantee.
- Vercel build compatibility and browser-native behavior take priority over extra dependencies.

## Open questions

- Confirm the production email address, canonical WhatsApp number, and exact Checkatrade profile URL before launch. The implementation may use the published phone number and clearly centralized fallbacks meanwhile.
- Confirm whether the map should remain a general Reading service-area view or use a verified business address.
- Supply approved customer testimonials if on-page quotation cards are desired later.

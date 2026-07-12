# R4 UI Design Brief — Clearer Service Discovery

Linked requirement: R4  
Mode: UI Designer — Design Direction  
Date: 2026-07-12

## Design goal

Help a prospective customer establish trust and identify the right electrical service quickly, without changing the Wright Sparks brand or introducing new functionality.

## Hierarchy and composition

- Keep the established navy/ink, warm cream, white, and electric-yellow system unchanged; yellow remains reserved for primary actions and emphasis.
- Place a compact independent-review summary immediately after the opening proof band. Use one clear heading, a restrained evidence panel, and a single Checkatrade action.
- Replace the flat service-card wall with four labelled groups: Home Improvements, Electrical Installations, Safety & Compliance, and Repairs & Maintenance.
- Within each group, use two equal service cards. Each card combines a locally served project image, a concise project-context label, service copy, a short inclusion list, and a quote anchor.
- Use generous group spacing and a quiet bordered surface so category boundaries are obvious without adding decorative noise.
- Finish services with one secondary contact panel for customers who are unsure which category fits.

## Responsive behavior

- Desktop: two service cards per group; review heading and summary share the first row, with supporting evidence below.
- Tablet/mobile: groups and review content collapse to one column in reading order; actions become full width where needed.
- Maintain the existing 360px minimum support, visible focus treatment, 44px action targets, and no horizontal overflow.
- Project-image labels must remain legible over varied photographs using a restrained translucent dark surface.

## Content and honesty constraints

- Reuse imported local service imagery and preserve its source traceability.
- Use only service claims and review evidence grounded in the imported site or verified external profile.
- Do not invent customer quotations, scores, review totals, qualifications, standards, locations, or guarantees.
- Preserve current navigation labels, app shell, quote/contact forms, loading/error/not-found states, and integrations.

## Component guidance

- Keep the page as a server component and the existing contact/navigation interactions in the isolated client component.
- Represent service groups and cards as data-driven reusable patterns; no new route, API, persistence, auth, database, or dependency is needed.
- Use existing design-system primitives and CSS rather than adding shadcn/ui for this bounded refinement; the project already has appropriate card, button, and responsive patterns.

## Validation target

- Production build succeeds.
- Rendered desktop and mobile surfaces show clear category grouping, readable image labels, review evidence before services, no overflow, and intact navigation/contact actions.
- QA checks content against imported evidence and records GitHub approval plus Vercel preview expectations.

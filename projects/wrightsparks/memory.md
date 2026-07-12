# System Memory — Wright Sparks Website

## Purpose

Store project-specific learnings, decisions, and reusable patterns.

Only record information that is likely to matter again.

## Failure Memory

Add reusable failure patterns here.

## Decision Memory

- R1 uses a frontend-only Next.js app: static marketing content with isolated client state for mobile navigation and enquiry handoffs; no enquiry data is persisted.
- Imported site assets are served locally and traced in `public/site-import/ASSET_SOURCES.md`.
- The published phone number is used for call and WhatsApp actions. The business email and exact Checkatrade profile remain launch-time configuration because the import did not verify them.
- R2 preserves the established R1 hero layout and interaction hierarchy while using the approved trust-led Reading and Berkshire message; copy-only hero changes do not require a new component or runtime boundary.
- R3 uses a generated, provenance-traced 1536×1024 WebP for the hero only; its central focal composition supports the existing tall responsive crops while imported photography remains unchanged elsewhere.
- R4 keeps the established brand and runtime boundaries while placing source-grounded trust evidence before four task-oriented service groups; current external ratings and review text must remain outbound to the live Checkatrade profile unless separately imported and verified.

## Observations

### O4 — Task-oriented service grouping remains legible across responsive layouts

Observation:
- Eight services can be presented without a flat card-wall effect when separated into four plain-language categories and paired with one consistent quote action pattern.

Evidence:
- 2026-07-12: canonical browser verification passed at 1440×1000 and 390×844 with zero horizontal overflow, five passing navigation click checks, no page errors, and no blocking failures.
- Post-implementation screenshot review confirmed distinct category boundaries and a coherent one-column mobile reading order.

Confidence:
- High for rendered hierarchy; low for engagement impact until post-release analytics or user feedback exists.

Validation method:
- Production build, Playwright-backed canonical verification, source-content audit, and post-implementation Experience/UI review.

Implication:
- Preserve the four-category model for future service additions and require evidence before publishing ratings, testimonials, or project locations.

### O3 — R3 hero image remains coherent across responsive crops

Observation:
- A centrally composed 3:2 residential-lighting source can replace the hero image without changing the existing tall desktop/mobile container or weakening overlay legibility.

Evidence:
- 2026-07-12: canonical browser verification passed at 1440×1000 and 390×844 with zero horizontal overflow, no page errors, and no hero-image loading warning.
- Screenshot inspection confirmed the pendant/island focal area and overlay note remain coherent at both crops.

Confidence:
- High

Validation method:
- Production build, Playwright-backed canonical verification, and post-implementation UI Designer screenshot review.

Implication:
- Future hero asset changes should use a central portrait-safe focal region and can retain the existing `object-fit: cover` container.

### O2 — R2 trust message is responsive on the rendered surface

Observation:
- The approved R2 hero message remains readable in the existing composition on desktop and mobile without horizontal overflow or navigation regression.

Evidence:
- 2026-07-12: canonical browser verification passed at 1440×1000 and 390×844 with zero horizontal overflow, no page errors, and five passing primary-navigation click checks.

Confidence:
- High

Validation method:
- Production build plus Playwright-backed canonical web-app verification and screenshot inspection.

Implication:
- The content update can proceed to GitHub release approval and Vercel preview without further layout work.

### O1 — Initial rendered-verification block was resolved

Observation:
- The initial managed-loopback verification failure is historical and no longer blocks release readiness.

Evidence:
- 2026-07-12: Next.js production build passed with TypeScript and static page generation.
- 2026-07-12: project eval runner executed but has no fixtures (`0/0`).
- 2026-07-12: canonical browser verification could not reach `127.0.0.1:8877` because managed sandbox loopback access is denied.
- Later on 2026-07-12: canonical browser verification succeeded on a clean alternate port and produced passing desktop/mobile evidence.

Store evidence-bearing product observations here.

Suggested format:

### O1 — Short observation title

Observation:
- What seems to be true

Evidence:
- What supports the observation

Confidence:
- High | Medium | Low

Validation method:
- How the evidence was gathered

Implication:
- What this suggests for future prioritisation or strategy

Use this section for findings that may influence future prioritisation or strategic direction.

## Heuristic Memory

Add project-specific heuristics here.

## Open Questions

Add unresolved project questions here.

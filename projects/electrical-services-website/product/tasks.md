# Tasks — Electrical Services Website v1

## Task 0: Run validation suite

Status: TODO
Requirement: R0

Goal:
Verify the current project state using the available validation mechanism.

Requirements:
- Run the project validation suite
- Report pass/fail clearly
- Highlight missing fixtures or tooling gaps if validation is not yet ready

Validation:
- Use the project-local deterministic validation runner
- Report whether the validation path itself is missing or incomplete

Output:
- Summary of results
- Any gaps that block reliable validation

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking, not broad planning speculation
- Move candid planning or sensitive sequencing notes into an ignored `private/` directory
- Keep standalone product artifacts linked from a canonical requirement or task entry instead of letting them float unreferenced under `product/`

## Task 1: Deliver the responsive Wright Sparks service website

Type: Feature Task
Status: IN_PROGRESS
Requirement: R1

Goal:
Give residential and commercial customers a clear, polished route from understanding Wright Sparks' services to making contact.

Requirements:
- Build a Vercel-compatible Next.js landing experience with reusable header, service, portfolio, testimonial, and contact sections
- Provide clear in-page navigation and prominent telephone, email, and quote actions
- Keep testimonials content-managed as a small typed data collection and expose explicit interactive controls
- Provide responsive desktop, tablet, and mobile layouts with accessible focus, reduced-motion, and semantic markup
- Preserve the established blue/red identity without inventing a new logo
- Include explicit loading, empty, and error-state components for future data-backed sections, without adding a backend in this slice
- Follow the linked [Experience findings](experience-findings-R1.md) and [UI design brief](ui-design-brief-R1.md)

Constraints:
- No database, authentication, payments, booking system, or backend form processing
- Do not hotlink imported website assets
- Keep content and UI state local and maintainable
- Release remains local/preview-ready until GitHub release approval; production Vercel deployment is not authorised by this task

Validation:
- `npm run build` succeeds
- Canonical web-app verification completes and its browser report is reviewed
- Rendered desktop and mobile surfaces have no horizontal overflow or obvious interaction failures
- Navigation, testimonial controls, telephone link, email link, and quote CTA are exercised

Validation evidence (2026-07-12):
- Source-level release checks pass for app entry, scripts, semantic sections, interactions, responsive breakpoint, focus visibility, and reduced-motion support
- `npm run build` is blocked because dependencies are not installed; online install stalls under restricted network access and offline install reports `ENOTCACHED`
- Canonical browser verification is blocked because the sandbox rejects its localhost connection with `Operation not permitted`
- Project eval runner reports `0/0` because deterministic fixtures have not been implemented

# Tasks — Wright Sparks Website

## Task 0: Run validation suite

Status: DONE
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
- Executed 2026-07-12: `python3 tools/eval_runner.py` returned `0/0 passing`; the runner works but no eval input files exist, so project-specific deterministic validation remains incomplete.

## Task Rules

- Keep tasks concrete, executable, and tied to a requirement
- Use `product/tasks.md` for execution tracking, not broad planning speculation
- Move candid planning or sensitive sequencing notes into an ignored `private/` directory
- Keep standalone product artifacts linked from a canonical requirement or task entry instead of letting them float unreferenced under `product/`

## Task 4: Update the hero trust message

Type: Feature Task
Status: DONE
Requirement: R2

Goal:
Make the first screen clearly communicate that Wright Sparks provides trusted electrical work across Reading and Berkshire.

Requirements:
- Apply the exact R2 eyebrow, two-line headline, and supporting copy in the existing hero
- Preserve the single semantic page heading and the established visual emphasis between headline lines
- Preserve all existing hero actions, proof content, imagery, navigation, and integration behavior
- Follow the linked [Experience Designer findings](experience-findings-R2.md) and [UI design brief](ui-design-brief-R2.md)

Constraints:
- Do not redesign the page layout or add new functionality
- Keep the change inside the existing frontend-only Next.js slice
- Maintain responsive and accessible behavior

Validation:
- The exact approved strings are present in the rendered hero
- `npm run build` succeeds
- The project-local deterministic eval runner completes

Architecture review:
- Completed 2026-07-12: the wording in R2 triggers the structural routing heuristic, but the approved implementation changes only static hero copy inside the existing server component. No runtime, persistence, routing, component-boundary, shared-infrastructure, or trust-boundary change is introduced, so no architecture change is required before Engineer implementation.

Output:
- Completed 2026-07-12: the existing hero now contains the exact approved eyebrow, two-line heading, and supporting copy while preserving its actions, image, proof row, and component structure.
- `npm run build` passed with Next.js compilation, TypeScript checking, and static generation.
- `python3 tools/eval_runner.py` executed but returned `0/0 passing` and exit code 1 because the project still has no deterministic eval fixtures; this is a validation-coverage gap rather than an R2 behavior failure.

## Task 5: Validate the rendered hero and release readiness

Type: Validation Task
Status: DONE
Requirement: R2

Goal:
Confirm that the updated message renders clearly without regressions across desktop and mobile.

Requirements:
- Run canonical web-app verification and inspect its report and screenshots
- Confirm the hero remains readable and free of horizontal overflow at desktop and mobile sizes
- Confirm the primary navigation click check and existing contact actions remain available
- Record GitHub approval and Vercel preview/deployment expectations

Constraints:
- Do not deploy or publish without GitHub release approval

Validation:
- `product/browser-verification.json` reports a passing rendered-surface check
- QA confirms build/eval results and no obvious first-screen UX regression

Validation evidence:
- Completed 2026-07-12 with `.venv/bin/python tools/verify_web_app.py wrightsparks --port 8893`; `product/browser-verification.json` reports `PASS`.
- Desktop at 1440×1000 and mobile at 390×844 show the exact R2 hero content with zero horizontal overflow and eight visible interaction targets.
- Five primary navigation click checks passed; there were no page errors or blocking failures.
- Post-implementation Experience Designer and UI Designer review confirmed clear first-screen hierarchy, readable wrapping, retained CTA order, and no evident responsive regression.
- Existing non-blocking Next.js warnings remain for logo aspect-ratio CSS and hero LCP loading behavior; neither was introduced by the copy update.
- GitHub release approval is still required before Vercel preview/deployment. Once approved, use the passing build and browser evidence for Vercel preview review; no deployment was performed in this workflow.

## Task R1.1: Define the responsive visual and interaction direction

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Create an implementation-ready design brief for a modern, trustworthy Wright Sparks marketing site grounded in the imported website content and assets.

Requirements:
- Define hierarchy, visual system, responsive composition, and reusable surface patterns
- Specify navigation, quote/contact forms, WhatsApp, Checkatrade, map, loading, success, and error states
- Preserve source-grounded navigation, copy, imagery, and accreditation evidence
- Link the resulting brief from this task

Constraints:
- Remain inside the frontend-only web-app slice
- Do not invent reviews, business addresses, or unsupported credentials
- Do not write production application code in the design stage

Validation:
- `product/design-brief.md` covers the UI Designer output format and is actionable by Engineer

Output:
- [Design brief](design-brief.md)

## Task R1.2: Build the modern Wright Sparks web experience

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Deliver a responsive, Vercel-compatible Next.js website that helps Reading customers understand services, establish trust, and contact Wright Sparks quickly.

Requirements:
- Implement the app shell and source-grounded Home, About, Services, Accreditations, Service Area, Our Work, Testimonials, FAQ, and Contact sections
- Reuse local imported logo, work imagery, and accreditation assets with traceable attribution
- Provide accessible mobile navigation and clear phone, WhatsApp, Get a quote, Contact, Checkatrade, and map actions
- Implement quote and contact forms with explicit idle, submitting, success, and validation/error states without backend persistence
- Add SEO metadata and semantic page structure

Constraints:
- Use a maintainable Next.js/React component structure with no database, auth, Stripe, or broad backend
- Do not hotlink imported images or invent testimonials/address details
- Keep configurable external integration details centralized

Validation:
- `npm run build` succeeds
- The project-local eval runner succeeds
- The site can be started locally for browser verification

Output:
- Next.js 16 production build passed with webpack, TypeScript checking, and static generation on 2026-07-12.
- Local imported assets and provenance are recorded in `public/site-import/ASSET_SOURCES.md`.

## Task R1.3: Validate rendered UX and release readiness

Type: Validation Task
Status: DONE
Requirement: R1

Goal:
Verify the rendered website, responsive interaction states, integration links, and Vercel release readiness.

Requirements:
- Run canonical web-app verification and inspect its browser report/screenshots
- Check desktop and mobile layouts, navigation, forms, WhatsApp, phone, Checkatrade, and map behavior
- Record preview/deployment expectations and any external configuration still required
- Post-implementation static UI review is recorded in [ui-review.md](ui-review.md); rendered review remains blocked.

Constraints:
- Do not deploy or publish without GitHub release approval
- Treat unavailable third-party destinations as explicit configuration follow-up, not fabricated completion

Validation:
- `product/browser-verification.json` reports a passing rendered-surface check
- QA reports deterministic build/eval results and obvious UX regressions

Validation evidence:
- On 2026-07-12 local canonical `.venv/bin/python tools/verify_web_app.py wrightsparks` passed and wrote `product/browser-verification.json` plus desktop/mobile screenshots under `product/browser-verification/`.
- Desktop and mobile verification reported zero horizontal overflow, passing click checks for the primary navigation, and no blocking page errors.
- The Checkatrade link now targets the live Wright Sparks review profile: `https://www.checkatrade.com/trades/wrightsparks991862/reviews`.
- Remaining release workflow is administrative rather than product-blocking: GitHub release approval and Vercel preview/deployment review.

## Task R3.1: Define the replacement hero image direction

Type: Feature Task
Status: DONE
Requirement: R3

Goal:
Define an implementation-ready image brief for a more modern, welcoming hero visual that remains cohesive with the existing Wright Sparks homepage.

Requirements:
- Specify subject, atmosphere, lighting, composition, responsive crop behavior, accessibility description, and optimization target
- Ground the visual in credible residential electrical work and the established Wright Sparks visual system
- Preserve the existing hero layout, content hierarchy, actions, overlay note, and interaction behavior
- Link the resulting UI design brief from this task

Constraints:
- Do not redesign the hero or alter functionality
- Do not include people, text, logos, watermarks, unverifiable credentials, or unsafe electrical work
- Keep the work inside the frontend-only Next.js slice

Validation:
- `product/ui-design-brief-R3.md` is actionable by Engineer and resolves the requirement's image format and responsive-crop question

Output:
- [R3 UI design brief](ui-design-brief-R3.md)
- Completed 2026-07-12: UI Designer defined the replacement image's credible residential subject, warm modern lighting, portrait-safe crop, accessibility text, and WebP optimization target while preserving the existing hero hierarchy.

## Task R3.2: Create and install the optimized hero image

Type: Feature Task
Status: DONE
Requirement: R3

Goal:
Replace the current homepage hero image with a welcoming, modern, locally served image that preserves the established hero composition.

Requirements:
- Create the replacement raster asset according to the accepted R3 UI design brief
- Save a web-optimized WebP in `public/site-import/` and record its generation provenance
- Update only the hero image source and accurate alternative text
- Keep the existing imported garden-studio image everywhere else on the page
- Preserve `next/image` responsive sizing and eager above-the-fold loading behavior

Constraints:
- No layout, copy, CTA, component-boundary, route, backend, or integration changes
- Do not hotlink the source website or overwrite existing imported assets
- Maintain accessible and responsive behavior

Validation:
- The replacement asset is present locally, traceable, and materially smaller than the current PNG where practical
- `npm run build` succeeds
- The project-local deterministic eval runner completes

Architecture review:
- Completed 2026-07-12: the router's structural trigger is conservative rather than substantively valid for R3. The requirement introduces no runtime, persistence, route, component-boundary, shared-infrastructure, source-of-truth, or trust-boundary change. The smallest coherent implementation is one new immutable local WebP plus a hero-only `src` and `alt` update. Engineer must preserve the existing `next/image` container, sizing, priority behavior, copy, overlay, actions, and all non-hero image references. R3 may proceed as-is.

Output:
- Completed 2026-07-12: generated and installed `public/site-import/residential-lighting-hero-r3.webp` at 1536×1024 and 64 KB, with prompt and generation provenance recorded in `public/site-import/ASSET_SOURCES.md`.
- Updated only the hero image source and alternative text; About and Our Work retain the imported garden-studio image.
- `npm run build` passed with Next.js compilation, TypeScript checking, and static generation.
- `python3 tools/eval_runner.py` completed but returned `0/0 passing` and exit code 1 because the project has no deterministic eval fixtures; this existing coverage gap is not evidence of an R3 behavior failure.

## Task R3.3: Validate the rendered hero and release readiness

Type: Validation Task
Status: DONE
Requirement: R3

Goal:
Confirm the replacement image renders attractively and legibly without responsive, interaction, accessibility, or performance regressions.

Requirements:
- Run canonical web-app verification and inspect its desktop and mobile screenshots
- Confirm the image crop remains useful at both viewports and the overlay note remains readable
- Confirm no horizontal overflow, page errors, broken primary navigation, or new image-loading warning
- Record post-implementation UI review and GitHub approval/Vercel preview expectations

Constraints:
- Do not deploy or publish without GitHub release approval
- QA reports evidence and does not modify implementation

Validation:
- `product/browser-verification.json` reports a passing rendered-surface check
- QA confirms build/eval results and no obvious first-screen UX regression

Validation evidence:
- Completed 2026-07-12 with `.venv/bin/python tools/verify_web_app.py wrightsparks --port 8894`; `product/browser-verification.json` reports `PASS`.
- Desktop at 1440×1000 and mobile at 390×844 show a coherent central pendant/island crop, readable overlay note, unchanged copy-first hierarchy, zero horizontal overflow, and eight visible interaction targets.
- Five primary navigation click checks passed with no page errors or blocking failures. The previous hero LCP warning is no longer present.
- [Post-implementation UI review](ui-review-R3.md) confirms the new image remains inviting and useful at both responsive crops without layout or interaction regression.
- The only console finding is the pre-existing logo aspect-ratio warning, which R3 did not introduce.
- Production build passed. The project eval runner still reports `0/0 passing` because no fixtures exist; this is an existing deterministic coverage gap.
- GitHub release approval remains required before Vercel preview/deployment. After approval, use this passing build and browser evidence for Vercel preview review; no deployment was performed.

## Task R4.1: Improve service discovery and trust hierarchy

Type: Feature Task
Status: DONE
Requirement: R4

Goal:
Help Reading and Berkshire customers establish trust and find the electrical service relevant to their job more quickly.

Requirements:
- Apply the accepted [Experience Designer findings](experience-findings-R4.md) and [UI design brief](ui-design-brief-R4.md)
- Present supported services in four clear, data-driven categories with two consistent service cards per category
- Reuse locally served project imagery, concise service details, scan-friendly inclusions, and direct quote anchors
- Position an honest independent-review summary before detailed service exploration
- Preserve the existing navigation, app shell, forms, contact actions, source-grounded page sections, and explicit route/form states
- Remove or replace any review, rating, credential, standard, experience, or service claim that cannot be traced to imported evidence

Constraints:
- Stay inside the frontend-only Next.js slice; no backend, database, auth, payments, new route, or new dependency
- Preserve the established brand palette and responsive behavior
- Do not invent testimonials, ratings, review counts, credentials, standards, locations, guarantees, or service capabilities
- Do not overwrite unrelated existing work

Validation:
- `npm run build` succeeds
- Imported evidence supports all newly surfaced customer-facing claims
- The project-local deterministic eval runner completes and any coverage gap is reported

Architecture review:
- Completed 2026-07-12: the structural trigger is not substantively valid. R4 reorganizes static, data-driven content and CSS inside the existing server page while retaining the isolated client interaction boundary; it introduces no runtime, route, persistence, source-of-truth, shared-infrastructure, security, or trust-boundary change. The smallest coherent implementation is the existing server-rendered page data plus scoped responsive CSS. Engineer must not add routes, client state, dependencies, persistence, backend behavior, or unsupported claims. R4 may proceed as-is.

Output:
- Completed 2026-07-12: the review evidence now follows the opening proof band, and eight supported services are organised into four responsive, data-driven categories with local project imagery and direct quote actions.
- Removed untraceable ratings, review totals, partial testimonials, credentials/standards, experience duration, and invented project locations from the affected surface.
- `npm run build` passed with Next.js compilation, TypeScript checking, and static generation.
- `python3 tools/eval_runner.py` completed but returned `0/0 passing` and exit code 1 because no project eval fixtures exist; this is an existing validation-coverage gap.

## Task R4.2: Validate rendered usability and release readiness

Type: Validation Task
Status: DONE
Requirement: R4

Goal:
Confirm the clearer review and service hierarchy works across desktop and mobile without interaction or content-integrity regressions.

Requirements:
- Run canonical web-app verification and inspect its report and desktop/mobile screenshots
- Confirm review evidence precedes services, service groups are scan-friendly, image labels remain readable, and quote anchors remain available
- Confirm no horizontal overflow, page errors, broken primary navigation, or contact regression
- Complete post-implementation Experience Designer and UI Designer review
- Record GitHub approval and Vercel preview/deployment expectations

Constraints:
- Do not deploy or publish without GitHub release approval
- QA reports evidence and does not modify implementation

Validation:
- `product/browser-verification.json` reports a passing rendered-surface check
- Production build passes and deterministic eval coverage is reported accurately
- QA and post-implementation design review find no blocking usability or content-integrity issue

Validation evidence:
- Completed 2026-07-12 with `.venv/bin/python tools/verify_web_app.py wrightsparks --port 8897`; `product/browser-verification.json` reports `PASS`.
- Desktop at 1440×1000 and mobile at 390×844 show the source-grounded review evidence before four clearly separated service groups, readable responsive card hierarchy, and direct quote actions.
- Both viewports report zero horizontal overflow and eight visible first-screen interaction targets. Five primary-navigation click checks passed with no page errors or blocking failures.
- [Post-implementation Experience and UI review](ui-review-R4.md) confirms improved service scanability, retained brand identity, and no blocking responsive or content-integrity issue.
- Production build passed. The deterministic eval runner remains `0/0` because no fixtures exist.
- Two pre-existing, non-blocking logo aspect-ratio warnings remain in the browser report; the logo renders coherently in both screenshots.
- GitHub release approval remains required before Vercel preview/deployment. No deployment was performed.

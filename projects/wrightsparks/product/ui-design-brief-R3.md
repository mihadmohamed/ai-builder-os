# UI Design Brief — R3

Mode: Design Direction  
Status: accepted  
Requirement: R3  
Linked task: R3.1

## Design goal

Replace only the homepage hero photograph with a modern, welcoming view of completed residential electrical work. The visual should feel warm, credible, and lived-in while retaining the restrained Wright Sparks hierarchy and the hero's existing copy-first composition.

## Image direction

- Show a polished contemporary British residential interior with thoughtful layered lighting as the clear subject: warm pendants or wall lighting, subtle recessed illumination, tidy sockets or switches, and a glimpse of evening blue outside.
- Keep the installation visibly finished and safe. Avoid exposed wiring, open consumer units, tools, ladders, sparks, damage, or anything that suggests an active or unsafe worksite.
- Use natural, editorial property photography rather than a glossy CGI showroom look. Materials should have believable texture and the light should feel warm without becoming orange.
- Include no people, text, logos, watermarks, badges, or branded products. The image must not imply unsupported credentials or a specific completed Wright Sparks commission.

## Composition and responsive crop

- Produce a landscape source at approximately 3:2. The existing desktop hero displays it in a tall near-portrait container using `object-fit: cover`, so the key lighting feature and room focal point must sit in the central 45% of the frame.
- Keep the outer edges as expendable environmental context so the image remains coherent at the existing desktop and mobile crops without changing `object-position` or layout CSS.
- Preserve the lower-left region as calm and relatively dark enough for the existing light media-note card to remain visually distinct. Do not bake text or a panel into the image.

## Existing interface invariants

- Preserve the complete hero layout, eyebrow, heading, supporting copy, actions, proof line, image container, corner radius, shadow, and overlay note.
- Preserve the existing responsive `next/image` behavior and above-the-fold priority loading.
- Keep the imported garden-studio photograph in About and Our Work. R3 changes only the hero image, allowing the page to gain visual variety without broadening scope.

## Asset and accessibility specification

- Save the final asset as `public/site-import/residential-lighting-hero-r3.webp` without overwriting the imported source assets.
- Target 1536×1024 or a comparable 3:2 source and an optimized WebP under 300 KB where quality permits; record generated provenance in `public/site-import/ASSET_SOURCES.md`.
- Use concise alternative text describing visible content, not marketing intent: `Warm pendant and recessed lighting in a finished contemporary kitchen`.

## Interaction and state constraints

This image-only change introduces no new loading, empty, error, form, navigation, hover, focus, or external-integration state. Existing browser-native behavior and responsive breakpoints remain unchanged.

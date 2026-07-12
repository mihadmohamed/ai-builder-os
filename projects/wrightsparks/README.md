# Wright Sparks Website

Wright Sparks is a Next.js marketing site for a Reading and Berkshire electrical services business.

## Local development

From this directory:

```bash
npm install
npm run dev
```

The local dev server should then be available at `http://localhost:3000` unless another port is already in use.

## Production build check

Before deployment:

```bash
npm run build
```

## Vercel deployment

Use the `projects/wrightsparks` directory as the Vercel project root.

Recommended settings:

- Framework Preset: `Next.js`
- Root Directory: `projects/wrightsparks`
- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: leave blank

## Project structure

- `app/` for the Next.js app router pages and layout
- `components/` for shared UI sections
- `public/site-import/` for shipped site assets used by the experience
- `product/requirements.md` for public-safe product intent and requirement state
- `product/tasks.md` for execution tracking
- `product/ui-runtime.json` for runtime selection metadata
- `data/site-imports/` for source-import evidence and extracted assets
- `tests/` for manual and automated checks

## Notes

- Runtime and scratch files under `data/` are intentionally not all tracked.
- Dependency versions are pinned here so Vercel and local builds use the same stack.

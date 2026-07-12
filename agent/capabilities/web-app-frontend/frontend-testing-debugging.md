# Frontend Testing and Debugging

Use this capability when the work needs evidence that a web app actually renders and behaves correctly.

Focus:

- dev-server preview discipline
- browser rendering verification
- responsive behavior checks
- interaction-state debugging
- visual regression awareness

Good default expectations:

- verify the real rendered surface, not just static code shape
- inspect desktop and smaller-screen behavior
- check broken states, missing data, and loading transitions
- keep debugging grounded in observable UI behavior

Canonical OS verification:

- run `.venv/bin/python tools/verify_web_app.py <project-slug>` before release approval
- review `product/browser-verification.json` for status, console/page errors, responsive overflow, and click evidence
- inspect screenshots under `product/browser-verification/` when visual layout or responsive behavior is part of the change

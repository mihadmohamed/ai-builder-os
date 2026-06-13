# Hosted Learning Agent

Hosted wrapper for the external V2 Learning Agent experience.

## Architecture

- `projects/os-control-panel` is the canonical source of truth for learning behavior, concept hierarchy, tutoring logic, and release-profile behavior.
- `projects/learning-agent` is a thin hosted wrapper around that canonical learning engine.
- Product changes to teaching, clarification, concept progression, hierarchy, recommendations, or catalog scope should be implemented in `projects/os-control-panel`, not redefined here.
- This project is responsible only for hosted concerns such as authentication, tenancy, deployment packaging, and environment-specific runtime configuration.

## Local pilot

```bash
export OPENAI_API_KEY="..."
export AI_BUILDER_OS_RUNTIME_ROOT="/private/tmp/learning-agent-runtime"
export LEARNING_AGENT_AUTH_MODE="local"
PYTHONPATH="$PWD/projects/os-control-panel/src" \
  .venv/bin/streamlit run projects/learning-agent/src/app.py
```

## Hosted configuration

Set:

- `OPENAI_API_KEY`
- `AI_BUILDER_OS_RUNTIME_ROOT=/data`
- `AI_BUILDER_OS_LEARNING_RELEASE_PROFILE=external_v2`
- `LEARNING_AGENT_AUTH_MODE=oidc`
- `LEARNING_AGENT_ALLOWED_EMAILS=user@example.com,second@example.com`
- `LEARNING_AGENT_PRIVACY_CONTACT=privacy@example.com`
- `OIDC_REDIRECT_URI`
- `OIDC_COOKIE_SECRET`
- `OIDC_CLIENT_ID`
- `OIDC_CLIENT_SECRET`
- `OIDC_SERVER_METADATA_URL`

The container start script turns the OIDC environment variables into Streamlit's
runtime `secrets.toml`. Never commit real client secrets.

The first hosted slice uses one persistent volume and user-scoped directories. Run
one application replica only. PostgreSQL-backed storage is required before horizontal
scaling or a broad public launch.

## Pilot launch order

Use these docs in this order when preparing the invite-only pilot:

1. [pilot-launch-plan.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/pilot-launch-plan.md)
   Use this as the top-level view of the full launch path, current status, and next gate.
2. [railway-deploy-guide.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/railway-deploy-guide.md)
   Use this for the exact provider-specific provisioning steps now that Railway is the chosen path.
3. [pilot-launch-checklist.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/pilot-launch-checklist.md)
   Use this as the lower-level operator runbook once the service exists and needs real hosted verification.
4. [deployment-phases.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/deployment-phases.md)
   Use this for the documented pilot, beta, and production deployment shapes.

Run preflight before the manual checklist:

```bash
PYTHONPATH="$PWD/projects/learning-agent/src" \
  python3 -m preflight
```

This checks the current invite-only pilot assumptions and surfaces hard failures
separately from softer warnings.

## Operator notes

- Treat the hosted wrapper as a private learner surface, not a general AI Builder OS entry point.
- Do one full smoke-test run with an invited account before any external invite goes out.
- Verify restart and redeploy persistence against the real mounted `/data` volume before calling the pilot launch-ready.
- Keep the invite allowlist intentionally small for the first wave so support and spend can be watched closely.

# Railway Deploy Guide for the Learning Agent Pilot

Use this guide once the launch plan has reached the Railway provisioning step.

This is the exact path for getting the invite-only pilot live enough to run the
hosted verification checklist.

## Goal

Provision one Railway service that:
- runs the hosted Learning Agent wrapper
- stores state on a mounted `/data` volume
- uses OIDC sign-in
- restricts access to invited email addresses
- stays on the `external_v2` learning release profile

## 1. Create the Railway project

- Create a new Railway project
- Choose **Deploy from GitHub repo**
- Select the `ai-builder-os-v2` repository
- Confirm Railway uses [railway.toml](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/railway.toml)

Recommended service name:
- `ai-builder-learning-agent`

## 2. Attach persistent storage

- Add one persistent volume
- Mount it at `/data`
- Keep the service to **one replica only**

This pilot must stay single-replica while learner state is file-backed.

## 3. Configure environment variables

Set these values in Railway:

- `OPENAI_API_KEY`
- `AI_BUILDER_OS_RUNTIME_ROOT=/data`
- `AI_BUILDER_OS_LEARNING_RELEASE_PROFILE=external_v2`
- `LEARNING_AGENT_AUTH_MODE=oidc`
- `LEARNING_AGENT_ALLOWED_EMAILS=<comma-separated invited emails>`
- `LEARNING_AGENT_PRIVACY_CONTACT=<real support/privacy contact>`
- `OIDC_REDIRECT_URI=<hosted callback URL>`
- `OIDC_COOKIE_SECRET=<long random secret>`
- `OIDC_CLIENT_ID=<real OIDC client id>`
- `OIDC_CLIENT_SECRET=<real OIDC client secret>`
- `OIDC_SERVER_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration`

Notes:
- Do not use placeholder email addresses or placeholder privacy contacts
- Keep the initial allowlist intentionally small
- If the final public URL is not known yet, do not finalize the OIDC redirect URI until the Railway domain decision is made

## 4. Decide the URL shape

Choose one of these before the real OIDC callback is finalized:

### Option A — Railway URL first
Use the Railway-provided domain for the first hosted verification pass.

Why this is a good default:
- faster
- fewer moving parts
- lets us verify auth and persistence before dealing with custom DNS

### Option B — Custom domain immediately
Attach the final domain before the first hosted verification pass.

Use this only if:
- the domain owner is available now
- DNS can be updated immediately
- we want the first OIDC callback to already match the public pilot URL

Recommended default:
- **use the Railway URL first**

Selected for this pilot:
- **Railway URL first**

## 5. Create the OIDC client

Create the OIDC client in the identity provider and set:

- redirect/callback URL to the final hosted callback URL
- allowed origin/domain rules to match the hosted URL

Then copy the live values into the Railway service:
- `OIDC_CLIENT_ID`
- `OIDC_CLIENT_SECRET`
- `OIDC_REDIRECT_URI`
- `OIDC_SERVER_METADATA_URL`

## 6. Deploy the service

- Trigger the Railway deploy
- Wait for the container to build and start
- Confirm the health path passes:
  - `/_stcore/health`
- Open the hosted URL

Expected result:
- the sign-in shell loads
- no wider AI Builder OS surfaces are visible

## 7. Run the preflight and launch checklist

Before inviting anyone:

1. Run the machine-checkable preflight against the intended config logic:

```bash
PYTHONPATH="$PWD/projects/learning-agent/src" python3 -m preflight
```

2. Run the full hosted verification flow in:
- [pilot-launch-checklist.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/pilot-launch-checklist.md)

Do not skip:
- invited-user sign-in
- blocked-user test
- profile save
- learning flow
- restart persistence
- redeploy persistence

## 8. Only then invite the first cohort

Do not send invites until all of the following are true:
- the app is reachable publicly
- OIDC sign-in works
- the invite-only gate works
- `/data` persistence survives restart and redeploy
- one full smoke-test run is complete

## Suggested operator record

Capture these somewhere during provisioning:
- Railway project name
- hosted URL
- who owns provider access
- who owns OIDC access
- who owns privacy/support contact
- date of the successful smoke test
- date restart persistence was verified
- date redeploy persistence was verified

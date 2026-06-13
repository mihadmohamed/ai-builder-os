# Learning Agent Deployment Phases

## Goal

Make the Learning Agent safely usable by other people without exposing the wider
AI Builder OS or mixing one learner's profile, sessions, notes, traces, and progress
with another learner's state.

These deployment phases apply to the hosted wrapper under `projects/learning-agent`.
The canonical learning behavior remains owned by `projects/os-control-panel`.
Deployment work here should not create a second product track for tutoring behavior,
concept hierarchy, recommendations, or concept catalog logic.

For the current invite-only pilot, use
`projects/learning-agent/pilot-launch-checklist.md` as the concrete operator
runbook before inviting learners.

## Phase 1 - Invite-only hosted pilot

Status: IMPLEMENTED, DEPLOYMENT CREDENTIALS REQUIRED

Target:
- 5-20 invited users
- one application replica
- Railway or Render

Delivered:
- hosted Learning Agent wrapper Streamlit entry point
- external V2 release profile
- OIDC login and logout
- optional email allowlist
- per-user learning state and trace directories
- persistent-volume runtime root
- Docker image, Railway config, Render blueprint, and health check
- hidden server error details and disabled usage telemetry

Before deployment:
1. Create the OIDC client.
2. Configure the final callback URL.
3. Add the invited email addresses.
4. Add the OpenAI API key and OIDC secrets to the host.
5. Attach `/data` as a persistent volume.
6. Keep the service at one replica.
7. Run the smoke and isolation checks.

Exit criteria:
- two invited users can sign in independently
- their profile, session, concept state, notes, and traces remain isolated
- restart and redeploy preserve both users' state
- API spend alerts and a hard monthly budget are configured
- privacy notice and deletion contact are visible

## Phase 2 - Database-backed beta

Status: PLANNED

Target:
- 20-200 users
- Railway or Cloud Run

Work:
- replace file-backed hosted state with PostgreSQL
- add migrations and encrypted backups
- add user-owned export and deletion
- add per-user daily token and request quotas
- add abuse controls and account suspension
- add admin usage, latency, cost, and eval dashboards
- add terms, privacy, retention, and AI-processing notices
- add automated database and restore tests

Exit criteria:
- no user-owned state depends on local container storage
- multiple app replicas pass concurrency and isolation tests
- failed deploys and instance replacement do not lose learning state
- quota and deletion workflows are verified

## Phase 3 - Production service

Status: PLANNED

Target:
- public or paid launch
- Cloud Run plus managed PostgreSQL or equivalent

Work:
- separate the Streamlit interface from a versioned Learning Agent API
- move long-running eval and reporting work into background jobs
- add subscription or credit billing
- add centralized logs, alerts, audit records, and incident runbooks
- add rate limiting at the edge and application layers
- add staging and production environments with automated deployment
- add production SLOs for availability, latency, reliability, and cost

Exit criteria:
- production security and privacy review completed
- load, recovery, and model-fallback tests pass
- alerting and incident ownership are operational
- usage economics are sustainable at the target price

## Platform path

Recommended progression:

1. Railway for the invite-only persistent-volume pilot.
2. Railway with PostgreSQL for the database-backed beta.
3. Cloud Run with managed PostgreSQL for production scale.

Render remains a viable alternative for phases 1 and 2. Streamlit Community Cloud
is useful for disposable demos, but its non-guaranteed generated-file persistence
makes it unsuitable for the current stateful pilot without completing Phase 2 first.

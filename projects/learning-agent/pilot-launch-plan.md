# Learning Agent Pilot Launch Plan

This is the top-level launch checklist for getting the hosted Learning Agent into
the hands of real pilot users.

Use this file to track where we are in the launch journey.

Use [pilot-launch-checklist.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/pilot-launch-checklist.md)
for the lower-level deployment and smoke-test runbook.

## Launch goal

Launch an invite-only external pilot where learners can:
- sign in with their own identity
- get a private learning workspace
- complete their profile
- follow a personalized learning plan
- use `Learn next`
- ask clarifications
- inspect concepts in the OS
- mark concepts learned
- return later and find progress still there

## Current status

- [x] External V2 learning surface is defined
- [x] Hosted wrapper exists
- [x] Auth and per-user isolation are implemented
- [x] Docker / Railway / Render packaging exists
- [x] Pilot shell copy is polished
- [x] Pre-launch checklist exists
- [x] Machine-checkable preflight exists
- [x] Real hosting provider selected
- [ ] Real hosted service provisioned
- [ ] Real OIDC credentials configured
- [ ] Real persistent volume verified
- [ ] End-to-end hosted smoke test completed
- [ ] Restart / redeploy persistence verified in the hosted environment
- [ ] Small pilot cohort invited

## Phase 1 — Freeze the pilot surface

Status: COMPLETE

Exit condition:
- external V2 scope is stable enough that only launch-blocking fixes should land before invites

Notes:
- The learner surface is now profile -> learning plan -> learn next
- The hosted wrapper is intentionally limited to the Learning Agent

## Phase 2 — Choose the real hosting path

Status: IN_PROGRESS

Goal:
- decide the real provider for the pilot deployment

Checklist:
- [x] Choose Railway or Render
- [x] Decide whether to use the provider URL first or attach a custom domain immediately
- [ ] Confirm who owns the provider account and deployment access

Exit condition:
- one real hosted environment path is chosen

Current decision:
- Railway is the selected provider for the invite-only pilot
- Use the Railway-provided URL for the first hosted verification pass
- Use [railway-deploy-guide.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/railway-deploy-guide.md) for the exact provisioning steps

## Phase 3 — Configure real pilot credentials and secrets

Status: NOT STARTED

Goal:
- make authentication and model access real

Checklist:
- [ ] Provision the pilot OpenAI API key
- [ ] Create the OIDC client
- [ ] Set the callback URL
- [ ] Set the cookie secret
- [ ] Set the invited email allowlist
- [ ] Set the privacy/support contact
- [ ] Set the hosted environment variables

Exit condition:
- all required hosted secrets and identity settings exist in the chosen provider

## Phase 4 — Provision and deploy the hosted service

Status: NOT STARTED

Goal:
- get the service live at a real URL

Checklist:
- [ ] Create the hosted service
- [ ] Attach `/data` as a persistent volume
- [ ] Keep the service at one replica
- [ ] Deploy the app successfully
- [ ] Confirm the health endpoint passes
- [ ] Confirm the app loads publicly

Exit condition:
- one live hosted Learning Agent service is reachable

## Phase 5 — Verify the live hosted environment

Status: NOT STARTED

Goal:
- prove the service works end to end with real hosted auth and persistence

Checklist:
- [ ] Run [pilot-launch-checklist.md](/Users/mihadmohamed/Documents/ai-builder-os-v2/projects/learning-agent/pilot-launch-checklist.md)
- [ ] Confirm invited-user sign-in works
- [ ] Confirm non-invited-user blocking works
- [ ] Confirm profile save works
- [ ] Confirm learning plan renders
- [ ] Confirm `Learn next` works
- [ ] Confirm clarification works
- [ ] Confirm implementation walkthrough works
- [ ] Confirm `Mark learned` works
- [ ] Confirm sign-out / sign-in preserves state
- [ ] Confirm restart preserves state
- [ ] Confirm redeploy preserves state
- [ ] Confirm one learner cannot see another learner’s data

Exit condition:
- hosted behavior is verified end to end in the real environment

## Phase 6 — Pilot-quality product review

Status: NOT STARTED

Goal:
- make sure the live hosted experience feels trustworthy and polished for real humans

Checklist:
- [ ] Walk through the flow as a first-time invited learner
- [ ] Check sign-in clarity
- [ ] Check profile clarity
- [ ] Check learning plan clarity
- [ ] Check tutor response quality
- [ ] Check implementation walkthrough quality
- [ ] Fix any launch-blocking confusion or trust issues

Exit condition:
- the hosted experience feels ready to put in front of external learners

## Phase 7 — Prepare pilot operations

Status: NOT STARTED

Goal:
- be ready to support real users once invites go out

Checklist:
- [ ] Decide who watches support requests
- [ ] Decide who handles privacy/data requests
- [ ] Configure spend alerts
- [ ] Configure a budget cap or equivalent guardrail
- [ ] Decide how pilot feedback will be collected
- [ ] Prepare the invite message
- [ ] Keep the first cohort intentionally small

Exit condition:
- support, privacy, and usage monitoring are owned and ready

## Phase 8 — Invite the first cohort

Status: NOT STARTED

Goal:
- learn from a tiny real-world group before expanding

Checklist:
- [ ] Invite 3–5 trusted pilot users
- [ ] Watch sign-in success
- [ ] Watch learning flow completion and confusion points
- [ ] Watch support requests and spend
- [ ] Fix sharp issues before widening the cohort

Exit condition:
- the first real cohort is using the pilot successfully

## The current next gate

We are here:
- Railway is chosen, but the real pilot service has not been provisioned yet

The next step is:
- provision the Railway service, attach `/data`, and set the hosted environment variables

## Selected provider

We are proceeding with:
- **Railway**

Why:
- it fits the current container + persistent-volume pilot architecture well
- it keeps the path shorter while the pilot remains file-backed and intentionally small

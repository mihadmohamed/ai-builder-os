# Learning Agent Pilot Launch Checklist

Use this checklist before inviting external learners to the hosted Learning Agent pilot.

This checklist assumes the current pilot architecture:
- external V2 learning-only surface
- single application replica
- file-backed persistent volume
- invite-only access

## 1. Confirm the pilot boundary

- [ ] The hosted surface exposes only the Learning Agent experience.
- [ ] Operations, project-management, implementation, and wider AI Builder OS surfaces are not visible.
- [ ] The release profile is `external_v2`.
- [ ] The current pilot is still single-replica and file-backed.

## 2. Confirm required environment configuration

- [ ] Run `PYTHONPATH="$PWD/projects/learning-agent/src" python3 -m preflight` and resolve all blocking failures
- [ ] `OPENAI_API_KEY` is set in the host
- [ ] `AI_BUILDER_OS_RUNTIME_ROOT=/data`
- [ ] `AI_BUILDER_OS_LEARNING_RELEASE_PROFILE=external_v2`
- [ ] `LEARNING_AGENT_AUTH_MODE=oidc`
- [ ] `LEARNING_AGENT_ALLOWED_EMAILS` contains only the invited pilot addresses
- [ ] `LEARNING_AGENT_PRIVACY_CONTACT` is set
- [ ] `OIDC_REDIRECT_URI` is set
- [ ] `OIDC_COOKIE_SECRET` is set
- [ ] `OIDC_CLIENT_ID` is set
- [ ] `OIDC_CLIENT_SECRET` is set
- [ ] `OIDC_SERVER_METADATA_URL` is set

## 3. Confirm authentication setup

- [ ] The OIDC client exists
- [ ] The callback URL exactly matches the hosted URL
- [ ] One invited learner can sign in
- [ ] One non-invited learner is blocked cleanly by the invite-only gate
- [ ] The sign-in screen explains the private pilot clearly

## 4. Confirm persistence and isolation

- [ ] `/data` is attached as a persistent volume
- [ ] The service is configured for one replica only
- [ ] One learner’s profile and learning progress do not appear for another learner
- [ ] Restarting the service preserves an invited learner’s profile and learning progress
- [ ] Redeploying the service preserves an invited learner’s profile and learning progress

## 5. Hosted smoke test

Run these checks with one invited test account:

- [ ] Sign in successfully
- [ ] Open the hosted app and see the pilot shell copy
- [ ] Save a learning profile
- [ ] Open `Learning plan`
- [ ] Start `Learn next`
- [ ] Ask for at least one clarification
- [ ] Run one implementation walkthrough
- [ ] Mark one concept learned
- [ ] Sign out and back in
- [ ] Confirm the learning state is still present

## 6. Cost and usage safeguards

- [ ] The OpenAI API account has spend alerts configured
- [ ] A hard monthly budget or equivalent cap is configured
- [ ] The pilot operator knows who will watch spend during the invite window

## 7. Privacy and support readiness

- [ ] The hosted app displays the privacy/data explanation
- [ ] The hosted app displays a real contact for data access or deletion requests
- [ ] The operator knows who owns responses to pilot access, privacy, and support issues

## 8. Ready to invite?

The pilot is ready to invite users only when all of the above are true.

Before sending invites:
- [ ] The hosted URL is final
- [ ] The invite email list is final
- [ ] The operator has completed one full smoke-test run
- [ ] The current known limitations are documented for the pilot audience

## 9. Do not claim yet

Do not claim the pilot is fully live-ready if any of these are still missing:
- OIDC sign-in has not been exercised in the real hosted environment
- restart/redeploy persistence has not been verified against the real mounted volume
- invite-only blocking has not been verified in the real hosted environment
- the privacy contact is still placeholder text
- the hosted URL or DNS is not yet final

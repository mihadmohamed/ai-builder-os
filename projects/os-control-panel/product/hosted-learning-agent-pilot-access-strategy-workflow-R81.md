# Hosted Learning Agent Pilot Access Strategy — Workflow R81

## Goal

Let prospective pilot users understand what the hosted Learning Agent is before manual approval, without opening unrestricted live-agent access.

## Problem

The current hosted pilot gate is operationally safe but too abrupt:

- Google OAuth in testing adds test-user friction.
- The hosted wrapper allowlist protects the live pilot.
- Non-approved users hit a hard denial state, which hides the product instead of showcasing it.

## Decision

Adopt a two-layer pilot access strategy:

1. Google OAuth may move to production so sign-in itself is not hidden behind Google test-user administration.
2. The hosted wrapper remains the product-level control point for live pilot access.
3. Approved users receive the full hosted Learning Agent.
4. Signed-in but non-approved users receive a polished preview/request-access experience rather than a hard deny screen.

## Why This Is The Right Middle Ground

This approach keeps the pilot discoverable without introducing the risks of fully open live access:

- avoids Google test-user admin friction for basic product discovery
- keeps OpenAI spend bounded
- keeps support and privacy load manageable
- preserves a high-quality pilot experience for admitted users
- gives non-admitted users a clear path to request access

## User Experience

### Approved user

- signs in with Google
- enters the hosted Learning Agent directly
- can save profile, follow the learning plan, and use live tutoring

### Signed-in, non-approved user

- signs in successfully
- sees a polished pilot preview page
- understands what the Learning Agent does
- understands that live access is limited during the pilot
- sees how to request access
- can sign out cleanly

## UX Guidance

The non-approved experience should feel like a deliberate pilot boundary, not a failure state.

It should communicate:

- what the Learning Agent is
- how approved access works
- what approved users get
- where to request access

It should not feel like:

- a generic error
- a broken sign-in flow
- a dead-end rejection

## Implementation Approach

### Phase 1

Implement the simplest safe version:

- keep `LEARNING_AGENT_ALLOWED_EMAILS` as the admission control
- keep full app access behind that allowlist
- replace the current hard invite-only error with a branded preview/request-access screen

### Later evolution

Potential future upgrades after pilot stability:

- waitlist capture
- cohort caps
- admissions registry
- limited read-only preview concepts

These are explicitly deferred so we do not add unnecessary launch complexity before the pilot is stable.

## Success Criteria

- Google OAuth can be moved to production without exposing unrestricted live-agent usage.
- Non-approved signed-in users see a clear, polished preview/request-access page.
- Approved users continue to reach the full hosted Learning Agent unchanged.
- The hosted wrapper remains aligned with the canonical learning engine in `os-control-panel`.

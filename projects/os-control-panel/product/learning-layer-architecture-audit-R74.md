# Learning Layer Architecture Audit — R74

## Context

This audit reviews the current shape of the learning layer after the shift toward a live-agent-centered learning model.

The learning layer has crossed an important threshold:
- persistent learning-agent session exists
- concept lifecycle exists
- build-to-learn exists
- recommendation and relationship guidance exist

The core question is no longer whether the learning layer works at all.
It is whether the current architecture still matches the product truth of an agent-centered learning system.

## Current architectural read

The learning layer is moving in the right direction, but it still has three structural risks:

1. product truth and implementation truth are drifting apart
2. one derived concept record is carrying too many meanings at once
3. the concept manager is still doing too much orchestration work in the UI layer

## Finding 1 — Product truth drift is now a system risk

The Architect snapshot for `os-control-panel` currently reports active structural hotspots because multiple `R74` tasks are still marked pending or in progress even though meaningful parts of those slices are already implemented.

This matters because:
- Architect and Orchestrator recommendations depend on task and requirement truth
- once file-backed product truth drifts, the OS starts reasoning from stale state
- that weakens one of the OS's core claims: durable file-backed workflow truth

### Consequence

The learning initiative can begin to look structurally blocked or unfinished even when the product has already moved past earlier slices.

### Recommendation

Regularly re-baseline `R74` task state as the implementation matures, so workflow reasoning stays trustworthy.

## Finding 2 — The learning concept record is overloaded

The current `learning_concept_records()` model merges several different sources into one concept record:
- recommendation state
- persisted concept state
- concept-note-derived state
- build-to-learn state

That makes the record useful, but semantically muddy.

### Why this is risky

The UI keeps having to infer whether a concept is:
- merely recommended
- partially understood
- actively in session
- build-backed
- reopened

That ambiguity is what produced recent UX mismatches where recommendation content looked like answered concept state.

### Recommendation

Separate the learning layer more clearly into:
- recommendation state
- concept state
- learning-session state
- build-to-learn state

The UI can still compose these, but they should not pretend to be one underlying thing.

## Finding 3 — Concept manager is still too orchestration-heavy

The concept page is lighter than before, but it still owns too much coordination:
- deciding which concept view to render
- merging recommendation framing with concept state
- preferring active session state when present
- routing into build-to-learn
- exposing concept relationships
- exposing lifecycle history

### Why this is risky

This makes the page brittle:
- UX cleanup causes regressions more easily
- the live-agent model is harder to reason about
- behavior is split between agent logic and view logic

### Recommendation

Concept manager should become a thinner read-and-route surface:
- show concept state
- show build linkage
- show relationships
- show history
- route into the live learning agent

The agent should own progression logic more directly.

## Finding 4 — Helper-era language still survives in fallback logic

Even after recent cleanup, some logic still assumes manual concept management is the authority for progression.

This is now mismatched with the product direction:
- the live learning agent should be the primary owner of progression
- concept management should support that, not compete with it

### Recommendation

Continue replacing helper-era fallback language and manual-management assumptions with explicit agent-owned progression logic.

## Architect conclusion

The learning layer is now strong enough that the main risk is no longer missing functionality.

The main risk is architectural incoherence:
- state layers are too blended
- UI views are doing too much coordination
- product truth is lagging implementation truth

## Next architectural moves

### 1. Re-baseline `R74` product truth

Update task state so Architect and Orchestrator reasoning stays trustworthy.

### 2. Split the learning model into clearer state layers

Treat these as distinct first-class layers:
- recommendation
- concept
- session
- build

### 3. Thin concept manager into a read-and-route surface

Make the live agent the owner of concept progression, and keep the concept page focused on visibility and continuation.

## Guardrails

- Prefer evolutionary refactors over broad redesign
- Preserve file-backed inspectability
- Do not reintroduce helper-era parallel paths while simplifying
- Keep the live learning agent as the center of gravity

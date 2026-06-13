## V2 External Learning Release Mode

### Purpose
Define the external-facing V2 release shape for the learning layer so the product ships as a coherent concept-learning experience rather than a mixed internal incubation surface.

### Product decision
The V2 external release should focus on:
- a curated library of parent and child concepts for the external learning journey
- parent and child concept structure
- a live tutoring agent that teaches those concepts through explanation, comparison, hierarchy, and implementation walkthroughs
- concept progression across:
  - upcoming
  - in progress
  - learned
  - reopened

The V2 external release should **not** present:
- reflection capture
- reflection refinement
- build-to-learn workflows
- concept-incubation flows for concepts that are not yet implemented in the OS
- explanation-back / “teach it back to the OS” loops as a required learning step

Those capabilities should stay available only behind an internal release gate or move forward as V3 work.

### Why this is the right cut
This release should optimize for:
- coherence
- credibility
- easier onboarding
- a stronger “learn through what is already real in the OS” story

It should avoid shipping a mixed product that asks the user to:
- learn curated built concepts
- reflect privately
- invent new concepts
- and design build experiments

all in one public-facing surface.

### V2 external release promise
The OS helps the operator learn AI product-system concepts through a curated catalog whose concepts are already real inside the OS by release time.

That means the release should feel like:
- a concept library
- a tutoring agent
- implementation-grounded learning
- hierarchy-aware progression

not like:
- a private thinking system
- an experimental concept incubator
- or a build-your-own-curriculum workbench

### Recommended release-mode model
Introduce an explicit learning release mode with two profiles.

#### Internal V2 mode
Keep the current broader learning/incubation capability available for internal usage:
- reflection helper visible
- build-to-learn visible
- concept incubation visible
- private-first experimentation preserved

#### External V2 mode
Ship a narrower concept-learning mode:
- `Workspace` does not show the reflection helper
- `Learning` removes the `Builds` section
- the tutoring agent does not route into build-to-learn
- concept pages do not show build-pathway actions
- recommendations focus on the curated external V2 concept catalog
- hierarchy and implementation walkthroughs become primary support surfaces

### Implementation recommendation
Use a small explicit release-profile flag rather than scattering many boolean feature flags.

Recommended profile values:
- `internal_v2`
- `external_v2`

And derive capability checks from that profile, for example:
- `reflection_enabled`
- `build_to_learn_enabled`
- `concept_incubation_enabled`
- `external_catalog_only`

This keeps the release boundary easy to reason about and avoids long-lived flag sprawl.

### Where the gating should happen
1. **Top-level Workspace**
- hide `render_reflection_helper()` in external V2 mode

2. **Learning navigation**
- remove `Builds` from `LEARNING_SECTION_LABELS` in external V2 mode

3. **Learning recommendations**
- do not show build-related actions in external V2 mode
- focus recommendations on the curated external V2 concept catalog

4. **Learning session**
- disable build-to-learn routing moves in external V2 mode
- keep:
  - teaching
  - clarification
  - hierarchy
  - implementation walkthroughs
  - concept progression
- move explanation-back / Feynman-style teach-back to V3 so V2 stays tighter and easier to follow

5. **Concept pages**
- remove build-link strips and build actions in external V2 mode
- keep concept relationships, hierarchy, history, and continue-learning actions

6. **State/model layer**
- keep build-to-learn and reflection code intact for internal mode
- add release-profile-aware filtering at the view/composition layer first

### What should be deferred to V3
The following should explicitly become V3-facing work:
- reflection as a user-facing OS layer
- build-to-learn as a user-facing OS layer
- concept incubation for concepts that are not yet implemented in the OS
- explanation-back / Feynman-style teach-back as a user-facing tutoring loop

### Catalog strategy
The external V2 release should not be limited by the current concept set.

Instead:
- define the desired external V2 concept catalog first
- identify any concepts that are still missing from the OS
- implement those missing concepts before release
- then expose that richer built catalog through the tutoring experience

So the release boundary is:
- not “only today’s implemented concepts”
- but “the curated concept catalog that has been fully implemented by release time”
- broader concept incubation workflows

### Success criteria
- External V2 feels like one coherent product centered on learning built concepts
- No reflection or build-to-learn surface leaks into the external flow
- Recommendations, tutoring, and concept pages stay aligned with the curated external V2 concept catalog
- Internal V2 retains the broader experimentation surface so V3 work is not lost

### Design principle
Do not delete future-facing capability to make V2 cleaner.
Hide and isolate it behind a release profile so:
- V2 ships coherently
- V3 still has a runway

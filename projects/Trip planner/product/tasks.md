# Tasks — Personal Trip Planner

## Task 0: Run validation suite

Status: DONE
Requirement: R0

Goal:
Verify the current project state using the available validation mechanism.

Requirements:
- Run the project validation suite
- Report pass/fail clearly
- Highlight missing fixtures or tooling gaps if validation is not yet ready

Validation:
- Use the project-local deterministic validation runner
- Report whether the validation path itself is missing or incomplete

Output:
- Summary of results
- Any gaps that block reliable validation

## Task 1: Build deterministic trip planning core

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Create a project-local planner that recommends family trip itineraries from explicit user, activity, budget, and weather inputs.

Requirements:
- Accept a family profile with preferences, budget, home/location context, and child age range
- Accept candidate activities with locality, cost, duration, tags, age range, indoor/outdoor setting, and weather suitability
- Accept weather context as explicit input instead of fabricating live weather data
- Only recommend activities that are local to the requested area
- Exclude activities that exceed the available budget when combined into an itinerary
- Prefer activities matching family preferences and current weather conditions
- Return a clear itinerary summary with total cost, total duration, weather note, and exclusions

Constraints:
- Do not call external services from deterministic planner code
- Do not hallucinate activities, prices, locations, or weather
- Keep the planner usable from tests and any future UI/API layer

Validation:
- Add deterministic eval cases covering budget limits, locality filtering, preference ranking, and weather suitability
- The project-local eval runner must pass

## Task 2: Capture post-trip feedback

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Persist structured family feedback about completed trip activities so experiences can be evaluated after outings.

Requirements:
- Store feedback with itinerary ID, activity IDs, rating, notes, visited activity IDs, and would-repeat signal
- Validate that ratings stay within an explicit range
- Preserve existing feedback when new feedback is added
- Provide a read path for saved feedback

Constraints:
- Use project-local file-backed storage under the project data directory
- Do not require external accounts or hosted services
- Do not lose existing feedback if a new feedback record is invalid

Validation:
- Add deterministic eval coverage for valid feedback persistence and invalid rating rejection
- The project-local eval runner must pass

## Task 3: Provide a minimal family planner UI

Type: Feature Task
Status: DONE
Requirement: R1

Goal:
Expose the planner and feedback workflow through a small local user interface suitable for manual review.

Requirements:
- Let users enter family preferences, budget, local area, and current weather context
- Let users edit or review local candidate activities
- Show generated itinerary recommendations and excluded activity reasons
- Let users submit post-trip feedback for a generated itinerary

Constraints:
- UI must reflect that weather and activity data are user-provided in this MVP
- UI must not imply live booking, hotel planning, long-distance travel, or social sharing
- Keep the UI project-local and runnable without external services

Validation:
- Add a manual UX checklist item for the planner flow
- Run deterministic validation after implementation

## Task 4: Replace template validation runner

Type: Validation Task
Status: DONE
Requirement: R1

Goal:
Make project-local validation meaningful for the Trip Planner requirement.

Requirements:
- Replace the template eval runner with deterministic product validation
- Include eval fixtures or in-code cases sufficient to validate core planner behavior and feedback storage
- Return a non-zero exit code on validation failure
- Print a clear pass/fail summary

Constraints:
- Validation must run offline
- Validation must not depend on live weather, maps, LLM, or booking APIs

Validation:
- `python3 projects/Trip planner/tools/eval_runner.py` exits with code 0

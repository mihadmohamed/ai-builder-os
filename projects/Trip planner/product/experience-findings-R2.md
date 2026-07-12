# Experience Designer Findings — R2

Requirement: R2 — Improve Readability of Activity Display in Trip Planner

## User problem

Parents cannot confidently choose candidate activities when the app exposes the activity list as raw JSON.

## Affected workflow

Planner setup, specifically reviewing and selecting local activity candidates before generating an itinerary.

## Evidence

- R2 explicitly reports that JSON activity presentation is confusing and frustrating.
- The current Streamlit UI uses one large `Local activity candidates` text area containing raw JSON.

## Confidence

High.

## Severity / frequency

High severity for normal users. This affects every planning session where users need to understand or adjust candidate activities.

## Finding type

Usability issue and hierarchy issue.

## Recommendation type

UX improvement in scope.

## Rationale

The existing planner already accepts explicit activity data, so the improvement should not introduce external data sources or new planning scope. The user need is a clearer activity review and selection experience that keeps the planner honest about user-provided inputs.

## Recommended next role

PM should convert this into a focused UI implementation task, followed by UI Designer guidance and Engineer implementation.


# Experience Designer Findings — R2

Requirement: R2 — Improve Job Posting Input Clarity

## User problem

Job seekers are unsure how to enter multiple target job postings in the existing Career Guidance Advisor form, which can cause incomplete inputs or abandonment before analysis.

## Affected workflow

Advisor setup, specifically the `Target job descriptions` text area before the user submits `Analyze career fit`.

## Evidence

- R2 explicitly states that users are confused about acceptable input methods for multiple job postings.
- The current Streamlit UI labels the field `Target job descriptions` and uses a placeholder that says users can paste one or more descriptions, but it does not show how to separate postings.

## Confidence

High.

## Severity / frequency

Medium-high severity for users comparing multiple roles. The issue appears whenever a user has more than one job posting to analyze.

## Finding type

Usability issue and workflow clarity issue.

## Recommendation type

UX improvement in scope.

## Rationale

The existing single text area can support R2 without adding upload controls, dynamic posting fields, or a new submission flow. The highest-leverage improvement is plain, contextual guidance at the moment of input: state that multiple postings belong in the same field and show a concrete separator pattern.

## Recommended next role

UI Designer should shape the exact guidance placement and interaction constraints before Engineer implementation.

# Product: ParentMate v1

## Problem

Parents miss or forget school events because:

- information is fragmented across emails
- important details such as dates, deadlines, and required actions are buried in unstructured text
- there is no reliable system to extract and track these automatically

## Goal

Automatically ingest school emails and convert them into structured, persistent, and viewable events with minimal manual effort.

## User

- UK-based working parents
- children in primary school
- frequent school communication via email
- time-constrained and reliant on reminders or calendars

## Core User Flow

Email arrives -> ParentMate ingests the message -> events and parent actions are extracted -> results are stored -> the parent reviews them in the UI or syncs them onward.

## Core Functionality

### Email Ingestion

- email subject and body are the core inputs
- ingestion can happen through the local UI, the API, or future mail-forwarding automation
- replay-backed evals provide the default deterministic validation path for extraction behavior

### Extraction Engine

Input:

- email subject
- email body

Output:

- structured JSON
- `events[]`
- metadata such as `school_name` and email subject

Requirements:

- extract multiple events per email when needed
- detect dates, times, locations, deadlines, required actions, and items needed
- keep administrative actions attached to the main event rather than splitting them into fake standalone events

### Persistence Layer

Storage:

- local JSON file: `data/events.json`

Behaviour:

- append new events
- persist across sessions
- preserve saved feedback and calendar-related state when relevant

Deduplication:

- no full event-level dedupe exists yet
- avoid pretending duplicate protection is more complete than it is today

### API Layer

Endpoint:

- `POST /ingest`

Input:

```json
{
  "subject": "...",
  "body": "..."
}
```

Output:

```json
{
  "events": [...]
}
```

Responsibilities:

- call the extraction engine
- persist the result
- return structured data

### UI Layer (Streamlit)

Features:

- manual email input for testing and debugging
- display extracted events
- display stored events
- calendar-related follow-up actions where supported

Purpose:

- debugging, local operator review, and early parent-facing visibility
- still not a polished production UI

## Constraints

- Must not hallucinate data not present in the email
- Must handle multiple events in a single email
- Must return empty events if none are found
- Must tolerate noisy or poorly formatted emails
- Must preserve a trustworthy offline/replay-backed validation path

## Success Criteria

Extraction Quality

- ≥90% correct extraction of key fields
- ≤5% false positives (events incorrectly inferred)

System Reliability

- replay-backed eval suite stays stable and reproducible
- ingestion path returns structured output without breaking the schema

Usability (early signal)

- a parent or operator can see accumulated events without manual re-entry
- calendar-oriented follow-up remains easier than copying event details by hand

## Current Limitations

- no full event-level deduplication yet
- no editing or correction of extracted events
- local storage only; not scalable or multi-user
- UI remains functional rather than polished
- the product still assumes email content is provided to ParentMate rather than directly integrated with a parent's live inbox

## Out of Scope

- non-school emails
- multi-user account systems
- payment or monetization flows
- advanced social or sharing features
- full production-grade inbox integration as a requirement of the current slice

# Product Requirements

## Active Requirements

### R1 — Core extraction

Status: DONE
Priority: HIGH
Effort: L
Description:
Build the core extraction path so ParentMate can turn school emails into structured event data that parents can review locally.

### R2 — Improve date/time consistency

Status: DONE
Priority: HIGH
Effort: M
Description:
Make extracted dates and times more consistent and usable for downstream calendar-style workflows.

### R3 — Handle event status (cancelled/rescheduled)

Status: DONE
Priority: MEDIUM
Effort: M
Description:
Represent explicit cancellation and reschedule signals without breaking the rest of the extraction schema.

### R4 — Improve parent readability

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Make extracted events easier for parents to scan and understand.

### R6 — Add a thin deterministic unit-test layer

Status: DONE
Priority: MEDIUM
Effort: S
Description:
Add a light deterministic test layer for local helper logic that replay-backed extraction evals do not isolate well.

### R7 — Calendar integration

Status: DONE
Priority: HIGH
Effort: L
Description:
Add a first-step calendar integration path so extracted events can move into a parent's calendar workflow more easily.

### R8 — Notification reminders

Status: NEW
Priority: LOW
Effort: S
Description:
Explore reminder behavior for extracted events once the calendar path is strong enough to build on.

### R9 — UI polish

Status: NEW
Priority: LOW
Effort: S
Description:
Improve the local ParentMate UI so the product feels calmer and easier to trust during everyday use.

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

* Only requirements with Status: NEW should be converted into tasks
* Requirements move from:
  NEW → IN_PROGRESS → DONE
* PM agent must NOT generate tasks for DONE items

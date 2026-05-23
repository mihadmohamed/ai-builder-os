# Product: ParentMate v1

## Problem

Parents miss or forget school events because:

- Information is fragmented across emails
- Important details (dates, deadlines, actions) are buried in unstructured text
- There is no reliable system to extract and track these automatically

## Goal

Automatically ingest school emails and convert them into structured, persistent, and viewable events with minimal manual effort.

## User

- UK-based working parents
- Children in primary school
- Receive frequent school communications via email
- Time-constrained and rely on reminders/calendars

## Core User Flow

Email arrives → User labels email → System processes email → Events extracted → Events stored → User views events in UI

## Core Functionality

### Email Ingestion

- Source: Gmail (via Apps Script)
- Trigger: manual or scheduled (time-based)
- Filter includes: `label:schoolmate`
- Filter excludes: already processed emails

### Extraction Engine

Input:

- Email subject
- Email body

Output:

- Structured JSON
- `events[]`
- Metadata: `school_name`, `subject`

Requirements:

- Extract multiple events per email
- Detect dates
- Detect times
- Detect location
- Detect deadlines
- Detect required actions
- Detect items needed

### Persistence Layer

Storage:

- Local JSON file: `data/events.json`

Behaviour:

- Append new events
- Persist across sessions

Deduplication:

- Gmail label `processed-schoolmate` prevents reprocessing
- Future: event-level dedupe via ID

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

- Call extraction engine
- Persist result
- Return structured data

### UI Layer (Streamlit)

Features:

- Manual email input for testing/debugging
- Display extracted events
- Display all stored events

Purpose:

- Debugging and early user visibility
- Not production-grade UI

### Automation

- Gmail → Apps Script → API via ngrok
- Scheduled execution optional
- Ensures continuous ingestion

## Constraints

- Must not hallucinate data not present in email
- Must handle multiple events in a single email
- Must return empty events if none found
- Must not process same email more than once
- Must tolerate noisy or poorly formatted emails

## Success Criteria

Extraction Quality

- ≥90% correct extraction of key fields
- ≤5% false positives (events incorrectly inferred)

System Reliability

- 0 duplicate processing of same email
- ≥95% successful ingestion (no API failures)

Usability (early signal)
- User can see accumulated events without manual re-entry

## Current Limitations 
- No event deduplication beyond email-level
- No editing or correction of extracted events
- No calendar integration
- No reminders or notifications
- Storage is local (not scalable, not multi-user)
- UI is functional but not user-friendly

## Out of Scope

- Non-school emails
- Mobile app
- Multi-user accounts
- Payment / monetisation
- Advanced UI/UX
- Event editing workflows

# Product Requirements

## Active Requirements

### R1 — Core extraction

Status: DONE

### R2 — Improve date/time consistency

Status: DONE

### R3 — Handle event status (cancelled/rescheduled)

Status: DONE

### R4 — Improve parent readability

Status: DONE
Description:
We should make events easier to understand for parents.

### R5 — Improve parent readability

Status: DONE
Description:
We should make events easier to understand for parents.

### R6 — Add a thin unit-test layer only for deterministic logic.

Status: DONE
Description:
Ad a light unit test set to cover deterministic logic, edge-case logic in isolation, UI-only logic that doesn’t show up in extraction outputs

### R7 — Calendar integration
Status: DONE
Priority: HIGH
Effort: L
Description:
Integrate parentmate with google calendar

### R8 — Notification reminders
Status: NEW
Priority: Low
Effort: S
Description:
Send notifcations from parentmate

### R9 — UI polish
Status: NEW
Priority: LOW
Effort: S
Description:
Enhancments to the UI

---

## Backlog (Not yet prioritised)



---

## Rules

* Only requirements with Status: NEW should be converted into tasks
* Requirements move from:
  NEW → IN_PROGRESS → DONE
* PM agent must NOT generate tasks for DONE items

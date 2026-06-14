# Product: AI Builder Learning Agent

## Wrapper Boundary

This project is a thin hosted wrapper around the canonical AI Builder OS learning engine.

It may define and evolve:
- hosted shell behavior
- authentication and access control
- pilot operations
- wrapper-specific preview and request-access UX

It must not redefine or fork:
- concept truth
- learning-plan logic
- tutoring behavior
- implementation-walkthrough behavior
- canonical learning product requirements

The source of truth for the learning engine remains:
- `projects/os-control-panel/src/workspace.py`
- `projects/os-control-panel/src/app.py`
- `projects/os-control-panel/product/`

## Problem

The canonical learning engine now exists inside AI Builder OS, but external users still need a clean, hosted way to discover the product, request access, sign in, and use the learner experience without being dropped into the full operator-facing control panel.

## Goal

Ship a polished hosted Learning Agent pilot that exposes the curated learning experience to invited external users while preserving the canonical learning logic inside `os-control-panel`.

## User

- Primary pilot user: invited external learner exploring AI Builder OS concepts
- Primary operator: Product Director managing access, preview quality, and pilot feedback

## Core User Flow

User opens the hosted Learning Agent -> understands what AI Builder OS is -> signs in with Google -> either enters the full admitted experience or sees a clear preview/request-access path -> completes profile setup -> follows the learning plan -> continues learning over time with progress preserved.

## Core Functionality

### Input

- Google-authenticated identity
- Learner profile selections
- Learning-session questions and clarification requests
- Access-request notes from non-admitted users

### Output

- Hosted sign-in and preview shell
- Personalized learning plan and live tutoring experience
- Operator-facing access-request intake for pilot management

### Persistence

- Persist learner progress, sessions, and access requests through the hosted runtime root
- Preserve canonical concept truth and learning behavior in the OS source of truth

### UI / API / Automation

- The hosted wrapper should feel like a polished learner product, not an operator console
- Admitted users should receive the full learning experience
- Non-admitted users should still see a useful preview and inline request-access flow

## Constraints

- Must remain a thin hosted wrapper around the canonical learning engine in `projects/os-control-panel`
- Must not fork or redefine the concept catalog or live learning behavior inside the hosted wrapper
- Must treat `projects/learning-agent/product/` as wrapper-only product truth, not canonical learning-engine truth
- Must support local preview mode for OS-managed project previews
- Must keep pilot access controlled even when Google OAuth is moved to production

## Success Criteria

- An invited learner can sign in, create a profile, and use the learning experience end to end
- A non-admitted learner can understand the pilot and submit an access request without leaving the page
- The hosted wrapper stays aligned with the canonical learning behavior in `os-control-panel`

## Current Limitations

- Pilot admission is still controlled through environment-driven allowlists rather than a full admissions system
- Operator approval of access requests is lightweight and file-backed
- The hosted wrapper still depends on the canonical OS project for deeper learning/product evolution

## Out of Scope

- Replacing the canonical learning engine in `os-control-panel`
- Opening unrestricted public access to live tutoring without pilot controls
- Building a full self-serve admissions dashboard in this pilot phase

# Product Requirements

## Active Requirements

### R1 — Ship the hosted Learning Agent pilot wrapper

Status: IN_PROGRESS
Priority: HIGH
Effort: M
Description:
Provide a polished hosted Learning Agent surface that wraps the canonical AI Builder OS learning engine for external pilot users.

This requirement covers:
- hosted sign-in and preview shell behavior
- admitted versus non-admitted pilot access behavior
- request-access flow and operator visibility
- deployment and launch polish needed for an invite-only pilot

Why now:
- this wrapper is the main external-facing path for the learning agent pilot
- pilot quality now depends on the hosted surface feeling coherent, trustworthy, and easy to use

---

## Backlog (Not yet prioritised)

### R2 — Landing Page Design Improvement

Status: BACKLOG
Priority: HIGH
Effort: M
Description:
**Problem statement**  
The current landing page lacks visual appeal and usability for external users, potentially leading to disengagement and a missed opportunity to convey the brand's essence effectively.  

**Target user**  
External users visiting the OS platform's landing page.  

**Core job-to-be-done**  
Enhance the landing page to effectively engage users, providing a visually impressive and coherent experience that encourages deeper exploration of the platform.  

**Success criteria**  
- Increased user engagement metrics (time spent on page, click-through rates).  
- Positive user feedback regarding page visual appeal and usability.  
- Seamless interaction with the modal image display and other new elements.  

**Constraints**  
- Must be responsive across all devices and screen sizes.  
- Existing design elements should maintain brand consistency.  

**Out of scope**  
- Any features or functionalities not related to the visual and interactive improvements of the landing page.  

**Assumptions**  
- Users prefer a modern, fresh interface with intuitive navigation.  
- The brand's core color palette can be effectively leveraged for improved visual depth.  

**Open questions**  
- Are there specific elements or content that should be highlighted more prominently after the layout adjustments?  
- Would you like to incorporate any animations or transitions for the modal image display?

---

## Rules

- Keep the hosted wrapper aligned with the canonical learning behavior in `projects/os-control-panel`
- Use requirements here for hosted-surface and pilot-operations work specific to `learning-agent`
- Do not duplicate core learning-truth requirements that belong to the canonical OS learning engine
- If a requirement changes what the learner is taught or how the learning engine behaves, it belongs in `os-control-panel`, not here

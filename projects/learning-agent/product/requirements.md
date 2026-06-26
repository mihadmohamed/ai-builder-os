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

Ship a polished hosted Learning Agent surface that exposes the curated learning experience publicly through Google sign-in while preserving the canonical learning logic inside `os-control-panel`.

## User

- Primary pilot user: invited external learner exploring AI Builder OS concepts
- Primary operator: Product Director managing access, preview quality, and pilot feedback

## Core User Flow

User opens the hosted Learning Agent -> understands what AI Builder OS is -> signs in with Google -> enters the full learning experience immediately -> completes profile setup -> follows the learning plan -> continues learning over time with progress preserved within visible usage limits.

## Core Functionality

### Input

- Google-authenticated identity
- Learner profile selections
- Learning-session questions and clarification requests
- Optional pilot notes and support contact from visitors

### Output

- Hosted sign-in and preview shell
- Personalized learning plan and live tutoring experience
- Visible usage-limit status for signed-in learners
- Operator-facing activity dashboard for monitoring adoption and usage

### Persistence

- Persist learner progress, sessions, and access requests through the hosted runtime root
- Preserve canonical concept truth and learning behavior in the OS source of truth

### UI / API / Automation

- The hosted wrapper should feel like a polished learner product, not an operator console
- Admitted users should receive the full learning experience
- Signed-out users should still see a useful preview and a clear sign-in path

## Constraints

- Must remain a thin hosted wrapper around the canonical learning engine in `projects/os-control-panel`
- Must not fork or redefine the concept catalog or live learning behavior inside the hosted wrapper
- Must treat `projects/learning-agent/product/` as wrapper-only product truth, not canonical learning-engine truth
- Must support local preview mode for OS-managed project previews
- Must keep cost and abuse bounded through visible rate limits once Google OAuth is in production

## Success Criteria

- An invited learner can sign in, create a profile, and use the learning experience end to end
- A signed-in learner can enter the full learning experience immediately and understand the daily limit before using costly live turns
- An operator can monitor adoption, usage, and remaining turn capacity across users from the hosted surface
- The hosted wrapper stays aligned with the canonical learning behavior in `os-control-panel`

## Current Limitations

- Trusted-tier access is still controlled through an environment-driven allowlist rather than a richer account-management system
- Operator monitoring is lightweight and file-backed rather than backed by a full analytics stack
- The hosted wrapper still depends on the canonical OS project for deeper learning/product evolution

## Out of Scope

- Replacing the canonical learning engine in `os-control-panel`
- Building a full analytics stack or admin console outside the hosted wrapper
- Anonymous access without Google sign-in or per-user persistence

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

### R2 — Landing Page Design Improvement

Status: DONE
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

Supporting artifacts:
- `product/experience-findings-R2.md`
- `product/ui-design-brief-R2.md`

### R3 — Request Page Layout Improvements

Status: DONE
Priority: HIGH
Effort: L
Description:
### Problem statement
The current layout of the request page for the AI OS learning agent has the "Request access" and "See the learning experience" sections combined in the same card, which can lead to confusion for users navigating the page.

### Target user
Users accessing the request page of the AI OS learning agent.

### Core job-to-be-done
Users should be able to easily navigate and understand the separate functionalities of requesting access and reviewing the learning experience.

### Success criteria
- The "Request access" section is distinctly separated from the "See the learning experience" section.
- The height of the "See the learning experience" section is reduced, improving overall page usability.

### Constraints
- Changes should not affect the visual consistency of the page.
- The updated sections must maintain the required functionality without introducing new issues.

### Out of scope
- Any changes to the content within the sections other than layout adjustments.

### Assumptions
- Users may find the current combined layout confusing.
- Reducing the height of the "See the learning experience" section will enhance usability.

### Open questions
- Are there specific height dimensions in mind for the reduced section?

Supporting artifacts:
- `product/experience-findings-R3.md`
- `product/ui-design-brief-R3.md`

### R4 — Enhancement of AI Builder Learning Agent Landing Page

Status: DONE
Priority: HIGH
Effort: M
Description:
### Problem statement
The current design of the AI Builder Learning Agent landing page lacks visual appeal and usability, leading to a less engaging experience for admitted learners.

### Target user
Admitted learners accessing the landing page to manage their learning profiles.

### Core job-to-be-done
Provide a visually appealing and user-friendly landing page that encourages user interaction and simplifies profile management.

### Success criteria
1. Increased user engagement as measured by interaction rates on key elements.
2. Positive user feedback on the visual appeal and usability of the landing page.
3. No negative impact on page loading speeds or responsiveness.

### Constraints
- Changes must adhere to existing brand guidelines regarding color and design language.
- Enhancements must not hinder the performance of the landing page.

### Out of scope
- Changes to core functionality that fall outside the visual design enhancements.

### Assumptions
- Admitted learners are seeking a visually engaging experience to manage their profiles.
- The design enhancements will resonate well with the target audience.

### Open questions
1. What specific colors would align best with the branding and resonate with the target audience?
2. Are there any accessibility guidelines that should be further considered for color contrasts?
3. Would there be any specific feedback from user testing that should be incorporated into the redesign?

Supporting artifacts:
- `product/experience-findings-R4.md`
- `product/ui-design-brief-R4.md`

### R5 — UI Enhancement for Consistent Card Layout

Status: DONE
Priority: MEDIUM
Effort: M
Description:
### Problem statement
The current UI lacks uniformity in card heights and layout, leading to a visually unappealing and potentially confusing user experience. 

### Target user  
Users navigating the application who seek clear, organized access to information displayed in cards.

### Core job-to-be-done  
Users need to quickly find and consume information, and a cohesive card layout will contribute to this ease of access and clarity.  

### Success criteria  
- All cards maintain a consistent height across the application.  
- There is standardized spacing and alignment among all cards.  
- Hover effects are intuitive and enhance user interactivity.  
- The updated UI meets responsiveness standards across all devices. 

### Constraints  
- Design changes must adhere to existing branding guidelines.  
- Cards must remain responsive, resizing appropriately without disrupting the overall layout. 

### Out of scope  
- Changes that impact the underlying functionality of the application rather than its visual presentation.

### Assumptions  
- Users desire a cleaner, more organized aesthetic that facilitates quick information gathering.

### Open questions  
- What is the desired minimum height for each card?  
- Are there specific styles or themes that should be adhered to for the UI elements?  
- How is the content in each card grouped, and should this group structure remain consistent after redesign?

Supporting artifacts:
- `product/experience-findings-R5.md`
- `product/ui-design-brief-R5.md`

### R6 — Open access, visible limits, and operator monitoring

Status: IN_PROGRESS
Priority: HIGH
Effort: M
Description:
### Problem statement
The hosted wrapper currently behaves too much like a gated pilot admission flow, which creates friction before users can experience the work. That undermines the actual objective of this release: visible proof of AI product capability and stronger recognition of the underlying skill and product thinking.

### Target user
- External learners arriving from public posts or direct links who want to try the Learning Agent quickly
- Operator users who need to monitor whether people are actually signing in, learning, and hitting usage limits

### Core job-to-be-done
Let signed-in users access the full learning experience immediately while keeping live-agent cost bounded through visible daily limits and giving operators clear adoption/usage monitoring.

### Success criteria
- Any Google-signed-in user can enter the full hosted learning experience without an admission wall
- The UI makes the daily live-turn limit visible before and during use
- Existing allowlisted users continue to receive a higher trusted tier without losing access
- Operator users can see who logged in, who is active, how many live turns are being used, and who is approaching or hitting limits
- Per-user persistence continues to work across redeploys for both standard and trusted users

### Constraints
- Keep Google sign-in as the identity boundary for persistence and rate limiting
- Reuse the existing allowlist as a trusted-tier mechanism rather than a hard access gate
- Count only costly live-agent actions toward the daily limit
- Keep the wrapper thin and avoid redefining canonical learning truth or progression logic here

### Out of scope
- Building a full billing, subscription, or self-serve entitlements system
- Anonymous public access without sign-in
- Rich cohort management or a standalone analytics warehouse

### Assumptions
- Lowering front-door friction will better serve the credibility and visibility objective than a gated admission flow
- Earlier admitted users should keep a differentiated benefit instead of being flattened into the default tier
- Lightweight file-backed activity logging is sufficient for the current release phase

### Open questions
- What standard and trusted daily turn limits feel sustainable after a week of real usage?
- Which operator metrics will prove most useful once more people start using the product?

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

- Keep the hosted wrapper aligned with the canonical learning behavior in `projects/os-control-panel`
- Use requirements here for hosted-surface and pilot-operations work specific to `learning-agent`
- Do not duplicate core learning-truth requirements that belong to the canonical OS learning engine
- If a requirement changes what the learner is taught or how the learning engine behaves, it belongs in `os-control-panel`, not here

# Product: Career guidance

## Problem

Describe the user problem this project solves.

## Goal

Describe the intended product outcome.

## User

- Describe the primary user
- Describe relevant context or constraints

## Core User Flow

Describe the main user journey from input to outcome.

## Core Functionality

### Input

- Describe the main system inputs

### Output

- Describe the main system outputs

### Persistence

- Describe storage expectations if applicable

### UI / API / Automation

- Add the layers that matter for this project

## Constraints

- Must not hallucinate missing information
- Must preserve stable behavior unless explicitly changed
- Add project-specific constraints here

## Success Criteria

- Define measurable indicators of success

## Current Limitations

- List known gaps or temporary boundaries

## Out of Scope

- List what this project will not do

# Product Requirements

## Active Requirements

### R1 — Career Guidance Advisor Requirement

Status: DONE
Priority: HIGH
Effort: M
Description:
### Problem Statement
Users often struggle to understand the gaps in their knowledge and skills when targeting specific jobs, which can hinder their job search and career progression.

### Target User
Job seekers looking to improve their CV and align their skills with specific job roles.

### Core Job-to-be-Done
Users will provide their CV and a list of target jobs to the career guidance system, which will analyze the data to identify gaps in skills and knowledge relevant to those jobs and recommend a personalized development plan.

### Success Criteria
- The system successfully analyzes user CVs and target jobs, identifying at least 3 specific gaps in skills or knowledge.
- Users receive a tailored development plan that includes recommended resources or actions to address these gaps within 24 hours of submission.

### Constraints
- The analysis must be completed using automated processes without manual intervention.
- The system must handle various CV formats and job descriptions.

### Out of Scope
- Providing job placement services or direct recruitment offers.
- Offering general career advice not specific to the provided CV and target jobs.

### Assumptions
- Users will be willing to provide accurate and detailed information in their CVs and target job descriptions.
- Users have some familiarity with the digital environment for inputting their information.

### Open Questions
- What level of detail should the system provide in the gap analysis (e.g., skill level, importance)?
- Should the platform include integrations with learning resources or platforms to recommend specific learning paths?

Validation note:
- Supporting artifact for the delivered UI direction:
  - `product/ui-design-brief-R1.md`

**Additional approved review input**
Source: UI Designer
Title: Enhanced Career Guidance Advisor UI Implementation

### Problem statement
Job seekers currently struggle with effectively analyzing their CVs against multiple job descriptions due to a lack of clear guidance and cumbersome input processes. 

### Target user
Job seekers looking to enhance their applications through a streamlined interface for CV and job description analysis. 

### Core job-to-be-done
Enable users to easily input their CV and multiple job descriptions while receiving clear guidance on requirements and expectations, to improve their chances of securing interviews. 

### Success criteria
- Users can input their CV and multiple job descriptions efficiently without confusion. 
- Guidance texts are clear and assist users in understanding what to provide. 
- The interface remains clean and is rated positively by users in usability testing. 
- The feature supports both mobile and desktop interfaces effectively.

### Constraints
- Maintain a balance between information density and usability, ensuring that new elements do not overwhelm users.
- Ensure responsive design across devices. 
- Clarity of all input-related texts to minimize misinterpretation. 

### Out of scope
- Implementation of complex formatting options beyond hyperlinks within job descriptions. 
- Development of features unrelated to user input guidance or job description analysis. 

### Assumptions
- Users will benefit from dynamic input fields and guidance elements as described. 
- Job seekers prefer a user-friendly interface that aids in their specific tasks without excessive clutter. 

### Open questions
- What specific examples are most beneficial to include in placeholder texts and tooltips to cater to user needs? 
- Is there a demand for additional formatting options, and how would it impact the user experience?

**Additional approved review input**
Source: UI Designer
Title: Color Enhancement for Career Guidance Advisor UI

**Problem statement**  
The current Career Guidance Advisor UI lacks a cohesive color scheme, which affects its visual appeal and usability, making it difficult for users to navigate and engage with the platform effectively.  
  
**Target user**  
Individuals seeking career guidance in a professional context who require an intuitive interface to input their CV and job descriptions.  
  
**Core job-to-be-done**  
Enhance the UI with a cohesive color palette that conveys trust, clarity, and motivation, facilitating an easier navigation experience for users.  
  
**Success criteria**  
- Implementation of a color scheme involving greens, blues, and reds as specified.  
- Positive user feedback regarding the visual appeal and ease of navigation.  
- Compliance with accessibility standards for color contrast.  
  
**Constraints**  
- Must adhere to accessibility standards for color contrast.  
- Color choices should harmonize with existing design elements to ensure consistency.  
  
**Out of scope**  
Any redesign of non-visual elements or removal of existing functional components unrelated to color enhancement.  
  
**Assumptions**  
- Users will respond positively to the proposed color scheme as it enhances trust and usability.  
- Existing infrastructure allows for the proposed changes without major technical constraints.  
  
**Open questions**  
- What specific shades of green, blue, and red align with the brand?  
- Are there existing brand guidelines that might influence these color choices?

### R2 — Improve Job Posting Input Clarity

Status: DONE
Priority: HIGH
Effort: M
Description:
**Problem statement**: Users are unsure how to enter multiple job postings on the Career Guidance Advisor page due to ambiguity concerning acceptable input methods, which can lead to incomplete submissions and abandonment of the tool.

**Target user**: Job seekers using the Career Guidance Advisor for career fit analysis.

**Core job-to-be-done**: Users need a clear and straightforward method to input multiple job postings to receive accurate career advice and fit analysis.

**Success criteria**: 
1. Clear instructions on the input method are displayed on the Career Guidance Advisor page.
2. The number of incomplete submissions decreases by at least 30% within 3 months following implementation.
3. User satisfaction ratings regarding job posting input clarity increase by 20% based on post-implementation feedback surveys.

**Constraints**: The input field design must remain compliant with existing UI/UX standards and not exceed the development effort budget.

**Out of scope**: Redesigning the entire input interface or creating a new submission feature outside of the existing structure.

**Assumptions**: Users will find clear instructions helpful and are likely to engage more with the feature if their input process is simplified and clarified.

**Open questions**: What specific examples should be included in the user instructions to ensure maximum clarity?

Validation note:
- Supporting artifacts for this requirement:
  - `product/experience-findings-R2.md`
  - `product/ui-design-brief-R2.md`

### R4 — CV Upload and Job Posting Link Feature

Status: DONE
Priority: HIGH
Effort: L
Description:
### Problem statement
Users need a streamlined way to connect their career materials to relevant job opportunities, which can be overwhelming without structured guidance.

### Target user
Job seekers looking for assistance in navigating their career paths and finding job postings relevant to their skills.

### Core job-to-be-done
Enable users to upload their CVs and receive personalized job posting links based on their qualifications and interests.

### Success criteria
- Users can easily upload their CVs.
- The system successfully matches users' CVs with relevant job postings.
- Users receive direct links to these job postings in their dashboard or via email notifications.

### Constraints
- Ensure data privacy and security for uploaded CVs.
- The job matching algorithm must be efficient and provide relevant results.

### Out of scope
- Job application submission process; this feature does not include applying for jobs directly through the platform.
- Networking features; the focus is solely on CV uploads and job posting links.

### Assumptions
- Users have electronic copies of their CVs ready to upload.
- There is a reliable database of job postings available for matching.

### Open questions
- What specific criteria should the system use to match CVs with job postings?
- How will users be notified about new job postings linked to their CVs?

Validation note:
- R4 MVP scope is narrowed to in-app CV upload and deterministic local job-link recommendations.
- Supporting artifacts for this requirement:
  - `product/experience-findings-R4.md`
  - `product/ui-design-brief-R4.md`
  - `product/architecture-note-R4.md`
- Implementation delivered:
  - text-based CV upload in the Streamlit advisor form
  - in-memory upload handling with no CV persistence
  - deterministic local job posting link recommendations in the result area

---

## Backlog (Not yet prioritised)

### R3 — Career Guidance Advisor UI Enhancement Requirement

Status: BACKLOG
Priority: HIGH
Effort: M
Description:
**Problem statement:** Users find the current Career Guidance Advisor UI unclear and visually unengaging, hindering their ability to effectively interact with the tool.

**Target user:** Users seeking career guidance who input their CV and job descriptions for tailored analysis.

**Core job-to-be-done:** Improve the usability and visual appeal of the Career Guidance Advisor UI to enhance user engagement and comprehension.

**Success criteria:** 
- Increased user engagement metrics (e.g., time spent on the tool, click-through rates on action buttons).
- Positive user feedback on usability after implementation through surveys or usability tests.
- Compliance with accessibility standards for all visual elements.

**Constraints:** 
- All changes must maintain the existing clean design aesthetic.
- Modifications need to strictly adhere to accessibility standards.

**Out of scope:**
- Major redesigns beyond the stated UI enhancements. 
- Changes that require significant alterations to the underlying functionality of the tool.

**Assumptions:** 
- Users will appreciate clarity and enhanced interactivity within an aesthetically pleasing UI.
- The changes proposed are aligned with brand guidelines pending final approval on color choices.

**Open questions:** 
- What specific color palette will be used for the button and text elements to ensure brand consistency?  
- Are there any preferred examples or guidelines for placeholder text length and content?

---

## Rules

- Only requirements with `Status: NEW` should be converted into tasks
- Requirements move from `NEW -> IN_PROGRESS -> DONE`
- PM must not generate tasks for `DONE` items
- Keep public tracked requirements focused on product truth rather than speculative planning notes

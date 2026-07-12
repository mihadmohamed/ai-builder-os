# Product: Wright Sparks Website

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

### R1 — Requirement for Replicating and Improving Wright Sparks Website

Status: DONE
Priority: HIGH
UI Runtime: web_app
Description:
### Problem Statement
The current Wright Sparks website lacks modern aesthetics and user experience enhancements, making it less appealing and functional for users.

### Target User
Potential customers seeking electrical services in Reading, as well as existing clients needing quick access to information and services.

### Core Job-to-be-Done
Access this website: https://wright-sparks.boost-site.com and
- crawl up to 10 pages
- extract the text, structure, and section hierarchy
- render pages where needed
- download up to 20 site images locally
- classify the downloaded assets into logo, hero, gallery, people, icon, and other
- recreate and improving it as a web app. the website must be made more modern and aesthetic. 
- the whatsapp integration is important. learn how its done on this page and replicate it.
- the get a quote form is important. learn how its done on this page and replicate it.
- the Contact us form is important. learn how its done on this page and replicate it.
- the https://www.checkatrade.com integration is important. learn how its done on this page and replicate it. 
- the google maps integration is important. learn how its done on this page and replicate it. 
On the replicated website, the user should be able to easily find information about services, contact the company, request quotes, and integrate communications via WhatsApp.

### Success Criteria
- Modernized website design that is visually appealing and intuitive.
- Efficient functioning of the WhatsApp integration.
- User-friendly "Get a Quote" and "Contact Us" forms that yield inquiries and lead conversions.
- Successful integration with Checkatrade and Google Maps, enhancing credibility and user accessibility.

### Constraints
- Maintain responsiveness across devices (desktop, tablet, mobile).
- Ensure compatibility with Vercel for deployment.
- Maintain or improve existing SEO metrics.

### Out of Scope
- Backend integrations beyond the specified services (e.g., databases, authentication).
- Features unrelated to the core function and aesthetics of the web application.

### Assumptions
- Users will prefer a streamlined browsing experience with minimal load times.
- Users value both aesthetic appeal and functionality equally.

### Open Questions and Suggestions
- What specific design elements should be prioritized for modernization? Suggestion: The HERO, information flow, organisation of content, display of images, etc
- How should the Checkatrade and Google Maps integrations be presented to users? Suggestion: The check traders should show the best reviews and the google map should show the address.

### R2 — Requirement for Website Content Update

Status: DONE
Priority: HIGH
Effort: L
Description:
**Problem statement**  
The current website does not accurately convey the professionalism and reliability of Wright Sparks as trusted electricians in Reading and Berkshire, leading to potential customer confusion.

**Target user**  
Homeowners and businesses in need of electrical services in the Reading and Berkshire areas.

**Core job-to-be-done**  
Revise website content to clearly communicate the brand message and service quality of Wright Sparks, emphasizing trust and expertise in electrical work.

**Success criteria**  
- Eyebrow changes to "TRUSTED ELECTRICIANS • READING & BERKSHIRE"  
- Headline updated to "Electrical Work Done Right."  
- Second line reads "First Time. Every Time."  
- Supporting copy includes: "From emergency repairs to complete installations, Wright Sparks delivers safe, certified electrical work with clear communication, quality workmanship, and respect for your home."
  
**Constraints**  
- All content must maintain consistency with existing branding standards.  
- Changes should be implemented without affecting existing website functionality.  

**Out of scope**  
- Redesigning the overall website layout or structure.  
- Adding new functionalities or features unrelated to the copy changes.  

**Assumptions**  
- The current design allows for text updates without additional structural changes.  
- The target audience responds positively to the revised messaging.

**Open questions**  
- Are there any specific brand guidelines to adhere to for tone and style?  
- How soon do you want these changes implemented?

Workflow artifacts:
- [Experience Designer findings](experience-findings-R2.md)
- [UI design brief](ui-design-brief-R2.md)

### R3 — Hero Image Update for Wrightsparks Webpage

Status: DONE
Priority: MEDIUM
Effort: M
Description:
**Problem statement**  
The current hero image on the Wrightsparks homepage does not effectively convey the modern and welcoming atmosphere of the services offered.

**Target user**  
Users visiting the Wrightsparks homepage.

**Core job-to-be-done**  
Enhance user experience by updating the hero image to increase visual appeal and reflect the inviting nature of Wrightsparks services.

**Success criteria**  
- The new hero image must be visually inviting and cohesive with the webpage design.  
- The updated image must maintain performance standards (optimized file size for fast loading).  
- Overlay text must remain legible against the new background.

**Constraints**  
- No structural changes to the existing layout other than the image swap.  
- The new image must be web-optimized to ensure fast loading times.

**Out of scope**  
- Redesigning or altering the layout of the Wrightsparks homepage beyond the image replacement.

**Assumptions**  
- The new image provided will comply with needed dimensions and file types for website compatibility.

**Open questions**  
- Resolved 2026-07-12: use a landscape WebP sized for the existing responsive `next/image` hero container, with a portrait-safe central focal area and an optimized file size. No layout change is required.

Workflow artifacts:
- [R3 UI design brief](ui-design-brief-R3.md)

### R4 — Enhance Wright Sparks Website Usability and Visual Clarity

Status: DONE
Priority: HIGH
Effort: M
Description:
### Problem statement
The current Wright Sparks website lacks visual clarity and usability, which may hinder potential customers from effectively navigating the site and understanding service offerings.

### Target user
Potential customers seeking electrical services in Reading and surrounding areas who prioritize trustworthiness, professionalism, and clarity in navigation.

### Core job-to-be-done
To create a more user-friendly website that enhances navigability and service visibility, thus improving customer engagement and trust.

### Success criteria
- Increased user engagement metrics, such as average time spent on the site and reduced bounce rates.
- Positive user feedback regarding site usability and visual appeal.
- All design changes remain consistent with the existing brand identity.

### Constraints
- Adherence to the existing brand identity of Wright Sparks throughout all design changes.
- Design adjustments must remain responsive across various device sizes.

### Out of scope
Specific content adjustments not outlined in the UI review but are instead focused on the overall design and usability enhancements.

### Assumptions
- Users appreciate a cohesive visual experience and that increased clarity will enhance service understanding.
- Current design elements can be adjusted without losing brand recognition.

### Open questions
- Resolved 2026-07-12: improve discovery across all supported services through task-oriented grouping rather than elevating an unsupported priority service.
- Resolved 2026-07-12: retain the established navy/cream/electric-yellow palette; improve hierarchy through composition, spacing, and reusable surfaces rather than substantial color changes.

Workflow artifacts:
- [R4 Experience Designer findings](experience-findings-R4.md)
- [R4 UI design brief](ui-design-brief-R4.md)
- [R4 post-implementation review](ui-review-R4.md)

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

- Only requirements with `Status: NEW` should be converted into tasks
- Requirements move from `NEW -> IN_PROGRESS -> DONE`
- PM must not generate tasks for `DONE` items
- Keep public tracked requirements focused on product truth rather than speculative planning notes
- `product/requirements.md` is the canonical requirement registry for the project
- `product/tasks.md` is the canonical task registry for the project
- Supporting artifacts under `product/` are allowed only when they are linked from a canonical requirement or task entry

# Product: Electrical Services Website v1

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
UI Runtime: web_app
Description:
### Requirement for Replicating and Improving Wright Sparks Website

**Problem statement**  
The existing Wright Sparks website lacks modern design elements and does not fully leverage interactive web capabilities to enhance user engagement and service discovery. Additionally, the site has navigational and structural limitations that hinder user experience.

**Target user**  
Potential customers seeking electrical services, both residential and commercial, who value user-friendly access to services and information, as well as quick problem resolution.

**Core job-to-be-done**  
To create a visually appealing, responsive web application that showcases the electrical services offered by Wright Sparks, allows users to easily navigate through service offerings, find relevant information, and contact the company effortlessly.

**Success criteria**  
- A responsive layout that works seamlessly on various devices (desktop, tablet, mobile).  
- Improved user experience with clearer navigation and structural hierarchy.  
- Enhanced content presentation including services, testimonials, and project portfolio.  
- A dynamic section for customer testimonials that can be managed easily.  
- Successful deployment to Vercel with proper functionality and zero bugs.

**Constraints**  
- Must adhere to web standards and accessibility guidelines.  
- Excludes backend services (e.g., Stripe, databases) in this project scope.  
- Utilize Vercel for deployment with GitHub integration for releases.

**Out of scope**  
- Any backend processes related to payment processing or database management.  
- Redesigning the brand identity (logo or color scheme).

**Assumptions**  
- Users are comfortable using a web app and prefer digital interactions.  
- All images and content can be sourced and used freely from the existing site or user-provided resources.

**Open questions**  
- What specific functionalities would you like to prioritize (e.g., contact forms, portfolio features, service bookings)?  
- Are there any specific examples of designs or features you admire from other websites that should influence this project?  

### Content Structure from Crawled Pages

- **Navigation Menu Options**: HOME, SERVICES, ABOUT US, CONTACT  
- **Main Content Sections**:  
  - Introduction to Wright Sparks Services  
  - Customer Testimonials  

### Downloaded Images Summary
1. Logo - `logo.png`  
2. Testimonials Images - `test_and_inspect.jpg`, `installations2.jpg`, `fault_finding.jpg`  
3. Project Portfolio Images - `constr-projects-2.jpg`, `constr-projects-1.jpg`, `constr-projects-3.jpg`, `constr-projects-4.jpg`  
4. Additional up to 20 images classified appropriately (if available).

This structured requirement should guide the development team in creating an updated and improved version of the Wright Sparks website.

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

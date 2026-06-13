# R74 — Background-Aware Next-Learning Guidance

Status: Drafted through OS workflow
Requirement: R74
Task: Task 173

## Workflow inputs used

### PM requirement discovery
- Problem: next-learning guidance is still too generic and does not adapt to the operator's background, trajectory, credibility goal, or learning style.
- Core job: use an explicit private learning profile to personalize what to learn next and why it matters for this operator specifically.
- Constraints: private-first, explicit inputs only, no hidden inference or third-party data.

### Experience Designer finding
- User problem: recommendations do not currently feel personally relevant.
- UX consequence: operators may disengage because the learning layer explains what is important in general, not why it matters for them.
- Recommendation type: in-scope UX improvement.

### UI Designer design direction
- Keep the learning profile compact and calm rather than turning Learning into a settings page.
- Treat the profile as a small working profile, not an analytics surface.
- Recommendation cards should explain in plain language why the concept matters for this operator.

### Architect guardrails
- Prefer an evolutionary slice over a broad redesign.
- Keep workflow state, product state, and runtime state clearly separated.
- Narrow the scope so profile capture, recommendation explanation, and concept state do not become overlapping systems.

## Product direction for the first slice

### 1. Add a private learning profile
The learning layer should store a small, editable operator profile in a private local artifact.

Initial fields:
- product background
- technical comfort
- current trajectory
- credibility goal
- preferred learning style
- current learning posture

### 2. Use the profile to personalize recommendations
The recommendation engine should incorporate the learning profile when forming the "why now" and suggested path for a concept.

The OS should be able to say things like:
- why `Trace grading` matters for someone building agent orchestration credibility
- why `RAG` matters now given the operator's learning and build-to-learn trajectory
- why `MCP` matters for a product operator who needs conceptual fluency rather than protocol depth

### 3. Keep the UI calm
The first slice should avoid introducing a heavy settings surface.

Recommended UI shape:
- compact profile card near the top of the Learning tab
- explicit edit action
- recommendation cards with a short "why this matters for you" explanation
- no analytics, scoring, or dense stats

### 4. Keep state inspectable
Private profile state should be file-backed and editable.
Recommendations should remain explainable rather than feeling like opaque inference.

## Suggested implementation boundaries

In scope:
- private learning profile storage
- profile editor UI
- recommendation copy that uses profile context
- first deterministic personalization rules for existing concepts

Out of scope for this slice:
- behavioral inference
- external data sources
- automatic credibility scoring
- broad redesign of the Learning tab

## Done definition for Task 173
Task 173 should feel complete when:
- the operator can edit a private learning profile in the Learning tab
- at least one next-learning recommendation becomes meaningfully more personal because of that profile
- the reason shown is plain-language and specific to the operator
- the UI remains calm and lightweight

# R75 — Learning Tab UI Guidance

## Experience Designer finding

- User problem: the Learning tab asks the operator to re-orient across recommendations, an active session, concept management, build-to-learn, and profile context.
- Affected workflow: enter Learning, understand the current state, continue the most relevant learning move, or find a concept.
- Evidence: the R74 manual review records cognitive overload, excessive vertical navigation, same-weight tools, and a long or jumpy selected-concept flow.
- Confidence: high for the documented operator workflow; broader engagement and satisfaction remain future product evidence.
- Severity / frequency: high whenever the operator returns to Learning with work already in progress.
- Finding type: usability and clutter / hierarchy issue.
- Recommendation type: UX improvement in scope.
- Recommendation:
  - resume an active learning session before showing draft helpers or recommendations
  - when there is no session, feature one next concept and one primary action
  - keep concept lookup as the stable secondary path
  - keep profile and alternate learning routes available without competing on the first screen
- Recommended next role: UI Designer, then Engineer.

## UI Designer direction

- Design goal: make the current or next learning move legible within one screen while preserving the existing Learning information architecture.
- Visual direction: calm, restrained, native Streamlit; fewer same-weight bordered blocks and less repeated explanatory copy.
- Layout and interaction guidance:
  - preserve `Learn next`, `Concepts`, and `Profile`
  - give the active session or featured recommendation the dominant position
  - use one primary button for the featured recommendation
  - place build-to-learn and concept-management alternatives behind progressive disclosure
  - simplify other recommendations into compact rows rather than nested cards
  - keep native buttons, segmented controls, forms, and expanders for keyboard operation and predictable reruns
- Constraints:
  - no palette, typography, grid, navigation-model, state-model, or dependency change
  - no removal of existing learning capability
  - no third-party Streamlit component
- Open questions: engagement and satisfaction changes require later user evidence and are not deterministic closure criteria for this implementation pass.

## Engineer handoff

Implement the smallest UI-only change that:

1. prioritizes active-session resume in Learning routing
2. makes the featured recommendation expose one dominant action
3. progressively discloses secondary actions and supporting detail
4. keeps all existing state transitions and private file-backed behavior intact

## Post-implementation review

### Experience Designer

- The active learning session now takes precedence over unfinished helper drafts, reducing the risk that returning users lose their current learning context.
- The no-session state presents one featured concept and one clear start action.
- Concept lookup remains a stable secondary route through `Concepts`; profile context remains available without competing on the first screen.
- Result: the documented orientation and same-weight-tool problems are addressed within scope.

### UI Designer

- The featured recommendation now uses one primary native Streamlit button.
- Supporting rationale, build-to-learn, and concept-management alternatives are progressively disclosed.
- Other recommendations use compact rows instead of repeated nested cards.
- The existing segmented navigation, palette, typography, grid, and native keyboard-operable controls are preserved.
- Result: hierarchy and scanability are improved without a visual-system redesign or new dependency.

### QA note

- Unit suite: 176/176 passed.
- Project eval baseline: 184/184 passed.
- Python compilation passed for the changed application and test files.
- A live Streamlit socket smoke test could not run in the managed sandbox because local port binding is prohibited (`PermissionError: Operation not permitted`).

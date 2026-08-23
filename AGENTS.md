# AI Builder OS Codex workflow

This repository uses Codex-native execution by default. The current Codex chat and project-scoped agents under `.codex/agents/` perform model work using Codex plan/credits. The local `ai_builder_os` MCP server owns deterministic workflow state and does not itself invoke a model.

The OpenAI Agents SDK is an optional API-billed deployment backend. Do not call `start_agent_workflow`, `list_agent_approvals`, or `resolve_agent_approval` unless the user explicitly requests Agents SDK/API mode and understands that it uses their OpenAI API project.

When a user asks to change a governed project:

1. Use the `ai_builder_os` MCP server to inspect the project and get the deterministic next action.
2. Check for `READY_FOR_CODEX` requests. Claim a queued request before acting on it and resolve it once work ends.
3. Record only durable product intent. Never store raw chat transcripts, hidden reasoning, credentials, or private data in product files.
4. Before editing for an eligible requirement, call `claim_implementation`. Keep its lease token private to the active turn.
5. Preserve unrelated worktree changes and stay within the claimed requirement.
6. Run proportionate verification, then call `record_implementation_evidence` exactly once. Close unfinished work as `BLOCKED` or `FAILED` with evidence.
7. Do not bypass approval gates.

When acting as Product Manager, read `agent/roles/pm.md` in full. PM is proposal-only:

1. Return one typed PM decision grounded in fresh canonical state.
2. Read the active mode's bounded first-party evidence packet, report unavailable sources honestly, stay inside the enforced mode tool allowlist, and run deterministic proposal preflight.
3. Use `submit_pm_proposal` to persist a reviewable revision; this is a local model-free controller call.
4. Present the exact proposal ID, revision, and approval summary.
5. Requirement proposals require one unambiguous Product Director confirmation. If native elicitation is cancelled, unsupported, invisible, timed out, malformed, or fails, render the exact sealed proposal revision in chat before requesting fallback approval.
   A new requirement selected as the sole active item may start `IN_PROGRESS`, and an existing `BACKLOG` requirement may move directly to `IN_PROGRESS`, in that same approved revision; do not manufacture separate promotion or activation gates.
6. A derived task plan carrying valid authorization from that exact approved active requirement is controller-applied without another product approval; continue into implementation rather than asking the user to approve tasks.
7. After an unambiguous requirement confirmation, call `approve_pm_proposal`; on rejection call `reject_pm_proposal`.
8. Never edit product files directly from the PM role or call the Agents SDK unless API mode was explicitly requested.

Operational PM prioritisation and task planning originate as typed work requests. Preserve their candidate IDs, parent proposal reference, originating queue request, and backend boundary through proposal submission and Inbox review.

New-project discovery uses the shared deterministic project-foundation contract. Capture project identity/governance and the seven non-duplicative product dimensions with typed provenance, ask one unresolved question at a time, and keep research as evidence until the user explicitly selects or accepts it. Codex-native is the default backend. Require exact approval of the sealed complete foundation and derived R1, while retaining separate approval for repository or publication side effects.

For every new user-facing project and every major user-facing feature, apply a mockup-first product gate before application implementation:

1. Put a mockup/prototype Validation Task first in the derived task plan.
2. Cover the core information architecture, routes, primary states, and desktop/mobile behavior, not only a landing or overview screen.
3. Present the rendered mockup to the Product Director and obtain explicit approval before implementing the application surface.
4. Record a functionality-preservation map from approved requirements and existing behavior to the mockup. A mockup may simplify presentation but must not silently remove functionality.
5. During implementation, compare every covered route/state against the approved mockup and verify both visual fidelity and preserved behavior.

Do not treat a text-only design brief, a single hero screenshot, or task-plan approval as approval of the rendered mockup. Small fixes that do not materially change information architecture, journeys, or visual hierarchy may remain implementation-first.

Use one main Codex agent by default. Delegate only bounded, independent specialist work when it materially improves quality or speed. The PM, experience designer, UI designer, architect, QA, human-facing learning, OS learning, and orchestrator custom agents are read-only. The OS Learning Agent diagnoses prioritised system-efficiency signals and must remain separate from the tutoring Learning Agent. The engineer custom agent may edit only after the main agent has obtained the applicable controller claim. Subagents must not call the Agents SDK backend.

Canonical truth precedence is:

1. `<resolved-project>/product/requirements.md`
2. `<resolved-project>/product/tasks.md`
3. `<resolved-project>/memory.md` and project rules
4. `<resolved-project>/product/history.jsonl` for append-only decisions and evidence
5. Runtime stores under the configured runtime root for queues, leases, sessions, and resumable SDK state

`RETIRED` requirements are terminal non-delivery history. They remain inspectable but must never be selected for planning, implementation, sprint execution, or autonomous progression. Preserve their completed tasks and evidence.

Resolve projects through `.ai-builder-os/project.json` and the private project registry. Never assume every project is a child of this repository's `projects/` directory.

Use `.agents/skills/ai-builder-os-workflow` for exact MCP sequencing and backend boundaries.

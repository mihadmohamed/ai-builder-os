---
name: ai-builder-os-workflow
description: Run the repository's deterministic AI Builder OS workflow from Codex without OpenAI API billing. Use when inspecting governed project state, processing READY_FOR_CODEX requests, recording durable product intent, routing work to project-scoped Codex specialists, claiming and implementing eligible requirements, handling approvals, or recording implementation evidence and canonical history. Use the optional Agents SDK backend only when the user explicitly requests API/Agents SDK mode.
---

# AI Builder OS Workflow

Use the `ai_builder_os` MCP tools as the deterministic control plane. Keep model work in the current Codex chat by default. Do not reproduce controller decisions in prompts, skills, or UI code.

Read [control-plane-contract.md](references/control-plane-contract.md) before choosing an execution backend, processing queued work, or closing a run.

## Inspect and route

0. Read `.ai-builder-os/project.json` when the current repository contains one. Use its stable project ID or name; never infer controller identity from the directory name alone.
1. Call `get_execution_backends` when execution mode is ambiguous.
2. Call `list_projects` when the project is unclear.
3. Call `inspect_project`, then `get_next_action` before choosing work or a role.
4. Surface blocking approvals and stop only when the required decision cannot be obtained in the current turn.

## Process READY_FOR_CODEX work

1. Call `list_codex_work_requests` for the selected project.
2. Claim exactly one request with `claim_codex_work_request` before acting on it.
3. Treat its task, role, and requirement ID as a bounded work packet.
4. When `request_kind` is `pm_decision`, validate its typed payload, read the canonical PM role, and run the named prioritisation or task-plan mode. Submit the result with `origin_request_id`, then resolve the queue item with the exact proposal ID and revision. Do not claim an implementation lease for proposal-only PM work.
5. If non-PM work names a governed requirement that will be edited, also call `claim_implementation` before changing files.
6. Resolve the queue request once with `resolve_codex_work_request`; link the implementation run ID when one exists.

Use `BLOCKED` when user authority or external state is required, `FAILED` after an attempted execution fails, and `COMPLETED` only when requested work and relevant verification are finished.
The controller must surface a terminal blocked implementation as `BLOCKED`; it must not describe an old terminal request as newly queued. Retrying blocked work requires both a new retry identity and the exact authorization identity for the newly permitted action.

## Record product intent

Call `record_product_intent` only for concise, durable intent that belongs in canonical product history. Use a stable idempotency key for retries. Exclude raw chat, hidden reasoning, credentials, personal data, and exploratory notes.

## Run Product Manager decisions

1. Read `agent/roles/pm.md` in full and refresh requirements, tasks, memory/rules, active workflow, and relevant history.
2. Keep PM read-only. Return one typed decision for discovery, requirement drafting, prioritisation, or task planning.
3. If more information is required, return `NEEDS_INPUT` without canonical changes.
4. For a decision-ready change, call `submit_pm_proposal` with a stable idempotency key.
   When processing typed queued PM work, include its `origin_request_id` and echo its `work_request` payload unchanged.
5. Show the proposal ID, revision, approval summary, facts, assumptions, open questions, and proposed changes.
6. Prefer `decide_pm_proposal` so a supported Codex host presents a native Approve, Reject, or Cancel form for the sealed proposal revision. Cancel, malformed responses, and unavailable elicitation must leave it pending.
7. When native elicitation is cancelled, unsupported, invisible, timed out, malformed, or unavailable, call `render_pm_proposal_chat_fallback` (or use the returned `chat_fallback`) and display its exact safe Markdown in chat before requesting an explicit fallback decision. Never ask for approval using only an ID or summary.
8. Treat an unambiguous user confirmation of that displayed revision as the fallback approval interface, then call `approve_pm_proposal` for that exact revision. Use `reject_pm_proposal` when rejected. Streamlit Workflow Inbox remains the other fallback.
9. After requirement approval, call `advance_autonomous_workflow` and continue through READY_FOR_CODEX work without task-level product approval. A typed task plan carrying the exact approved requirement authorization is controller-applied automatically.
10. If approval reports stale state, refresh canonical files and submit and display a new revision. Never force-apply or directly edit PM product state.

Streamlit operational PM modes create typed `READY_FOR_CODEX` work by default. Requirement-authorized task planning is automatic and does not create a second Product Director gate. A `NEEDS_INPUT` decision is still submitted, and the operator answer creates a linked revision under the same proposal ID.

These PM controller calls are model-free. A Codex PM or Codex specialist consultation uses Codex plan/credits. The Agents SDK PM and its agents-as-tools use OpenAI API project tokens and remain explicit opt-in.

For new-project discovery, use the shared `project_foundation.py` contract in both Codex and Streamlit. Complete the seven non-duplicative foundation fields, preserve typed provenance, and ask only the next unresolved question. Codex-native reasoning and research is the default; API-backed live discovery requires explicit opt-in. Research remains evidence until the user selects an option. Approve the exact sealed foundation and derived R1 before scaffolding, then retain separate external-action approval for repository creation, visibility, publication, push, and deployment.

From Codex, call `start_project_discovery`, then apply accepted answers one field at a time with `update_project_discovery_field`. Use `offer_project_discovery_research` and `select_project_discovery_research` only when research is requested. Resume with `get_project_discovery`. Once complete, call `prepare_pre_project_proposal`, display the exact normalized foundation, derived R1, revision, and seal in chat, and wait for explicit approval before `approve_pre_project_proposal`. Never treat the pre-project approval as repository or publication authority.

## Route Codex-native roles

Keep orchestration in the main Codex chat. Use the project-scoped agents in `.codex/agents/` only for bounded specialist work:

- `pm`, `experience_designer`, `ui_designer`, `architect`, `qa`, `learning_agent`, and `os_learning_agent` are read-only reviewers. `os_learning_agent` diagnoses only prioritised system-learning signals and is separate from the human-facing tutoring role.
- `engineer` may edit only after the main agent has acquired the applicable controller claim.
- `orchestrator` is a read-only independent routing reviewer for unusually complex workflows.

Use one main agent by default. Delegate only independent work where specialist context isolation or parallelism materially improves quality or speed. Do not delegate trivial sequential steps. Give each specialist the request ID, relevant canonical context, constraints, and expected output. Subagents must not invoke the API-backed Agents SDK.

## Implement in Codex

1. Call `claim_implementation` for the eligible requirement before editing.
2. Keep the lease token out of responses, logs, commits, product files, and subagent prompts unless an editing agent strictly needs it; prefer the main agent retaining it.
3. For every new user-facing project and every major user-facing feature, enforce the mockup-first gate before application implementation:
   - complete the first mockup/prototype Validation Task across the core routes, states, and desktop/mobile layouts
   - present the rendered mockup and obtain explicit Product Director approval; task-plan approval and text-only briefs do not satisfy this gate
   - record a functionality-preservation map so required and existing behavior omitted from the mockup remains in the implementation
   - stop before application implementation if the rendered mockup is not yet approved
4. Implement only the work packet and preserve unrelated worktree changes. Work in the resolved target repository; a chat scoped to one repository must not edit unrelated registered repositories.
5. Verify in proportion to risk. For mockup-led UI work, compare each covered route/state at desktop and mobile sizes and check that mapped functionality remains reachable. Use `qa` for an independent pass when risk or scope justifies the extra Codex tokens.
6. Call `record_implementation_evidence` exactly once with the run ID, lease token, summary, changed files, tests, and terminal status.
   When only part of an active requirement is complete, include explicit linked `completed_task_numbers` plus the exact requirement and task source hashes. Add a typed blocking boundary and reason when remaining work is blocked. Never infer completed tasks from summary prose.

## Use API mode only by explicit request

Call `start_agent_workflow`, `list_agent_approvals`, or `resolve_agent_approval` only when the user explicitly asks for the OpenAI Agents SDK/API-backed backend. State that this consumes OpenAI API project tokens before starting it. The start and resume tools elicit separate native human authorization and fail closed without it. An SDK approval authorizes only the displayed run, approval, decision, and sealed arguments.

## Apply the approval-risk boundary

Call `get_approval_risk_policy` when approval behavior is unclear. Read-only inspection and reversible coordination may run without product approval. Canonical changes use the sealed native PM decision path. Use `list_external_approvals` and `decide_external_approval` for one exact publication, release, repository, deployment, or visibility side effect at a time. Unknown, destructive, and secret-sensitive actions require a dedicated stronger manual path and must fail closed.

MCP tool approval and sandbox approval protect tool execution; they are not Product Director authority. Only an accepted native product form, an unambiguous explicit chat decision applied to the exact revision, or the Streamlit Workflow Inbox may provide that authority. Tool annotations are least-privilege hints; the controller's risk registry, state hashes, revision validation, seals, actor boundary, and idempotency checks remain authoritative.

Supported Codex hosts render MCP form elicitation. If the host cancels, declines, cannot render it, or returns malformed data, report the safe chat/Streamlit fallback and apply no side effect. Automatic security reviewers must never be named or recorded as the approving Product Director.

## Maintain canonical history

Treat requirements, tasks, memory, then append-only history as product truth. Runtime queue entries, leases, Codex threads, SDK sessions, and serialized approvals are operational state. Use MCP tools for canonical events instead of editing `history.jsonl` manually.

Treat `RETIRED` requirements as terminal non-delivery history: inspect them when lineage matters, but exclude them from prioritisation, tasking, claims, sprints, and autonomous progression. Never delete their completed tasks or evidence. A future retirement must be a single sealed PM `retire` proposal with unchanged requirement content and an explicit reason; apply it only after exact Product Director approval.

Canonical truth lives in the governed project repository, whether it is an embedded showcase, a managed standalone repository, or an attached repository. Portable repository settings may live in that repository's manifest. Machine-specific workspace paths and the aggregate cross-project catalog belong in the private registry/runtime store and must not be copied into public showcase files.

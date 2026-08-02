# Control plane contract

## Execution backends

| Backend | Default | Model billing | Intended use |
| --- | --- | --- | --- |
| Codex native | Yes | Codex plan or credits | Interactive repository work, specialist review, implementation, and QA from Codex chats |
| OpenAI Agents SDK | No | OpenAI API project | Explicit API-backed deployment, Streamlit/background operation, SDK handoffs, resumable SDK approvals, and SDK traces |

Local deterministic MCP calls do not invoke either model backend. `start_agent_workflow` and `resolve_agent_approval` are the API-backed boundary.

## PM proposal lifecycle

The Product Manager uses one proposal-only contract on both backends.

`submit_pm_proposal` records an immutable proposal revision and source-state fingerprints without changing canonical product files. Conversational confirmation is bound to that exact revision through `approve_pm_proposal`; rejection uses `reject_pm_proposal`. The controller revalidates requirements, tasks, memory, duplicate IDs/titles, status transitions, task links, and one-at-a-time activation before application.

When no requirement is active, one exact requirement proposal may create the sole `IN_PROGRESS` requirement or move an existing `BACKLOG` requirement directly to `IN_PROGRESS`. That approval is the authorization for bounded downstream planning and delivery; a separate backlog-promotion or activation approval is not required.

PM evidence is controller-built and mode-aware. Use `get_pm_evidence` to distinguish configured first-party facts from unavailable sources, and `preflight_pm_proposal` before submission. These operations are read-only and model-free. PM mode tool allowlists are enforced at execution time; external research remains untrusted and must carry source URL citations.

Proposal preflight returns typed `info`, `warning`, and `blocking` findings with stable codes, fields, messages, and remediation. Blocking findings must be resolved before submission. Warnings remain visible review items and must be revised or explicitly justified; they are not silently converted into product truth.

PM proposal submission, validation, approval storage, application, and history are deterministic and use no model tokens. Codex PM reasoning and Codex specialist consultations use Codex plan/credits. SDK PM reasoning, handoffs, and agents-as-tools use OpenAI API project tokens. Calling an SDK workflow from a Codex chat is the deliberate dual-usage scenario.

Operational prioritisation and task planning use a typed PM work-request payload. Codex requests preserve that payload and link the resulting proposal revision back to the queue item. A task plan derived from an exact approved active requirement carries that authorization lineage and is validated and applied by the controller without another Product Director approval. API-backed PM work echoes the same payload in the decision and resumes serialized SDK state only when API mode was explicitly requested. A paused SDK proposal must not be applied through a parallel controller button.

## Queue lifecycle

Streamlit or Codex creates `READY_FOR_CODEX` requests. Codex claims one request with a bounded coordination lease, performs the work, and resolves it as `COMPLETED`, `BLOCKED`, `FAILED`, or `CANCELLED`. An expired queue claim may be reclaimed after an interrupted chat. Queue events are appended to `product/history.jsonl`; mutable queue state stays under the runtime root.

A queue claim does not replace an implementation lease. When a request requires governed file changes, acquire `claim_implementation` separately and link its run ID when resolving the queue request.

Completed specialist work scoped to the active requirement satisfies the matching gate until relevant approved source state changes. Partial implementation evidence may reconcile only explicit linked task numbers against exact canonical source hashes while leaving the requirement and remaining tasks open. Free-text summaries are never completion authority.

A terminal blocked implementation remains blocked until its typed boundary is resolved. Autonomous progression reports that blocker instead of silently returning or recreating the old request. A retry requires a new exact authorization ID and a new retry identity; the controller records both on the new bounded request.

## Approval boundary

The controller classifies every exposed action as read-only, reversible coordination, canonical product change, external/API-billed, or destructive/secret-sensitive. Unknown actions fail closed. Read-only and reversible coordination do not need product approval. Consequential actions carry a deterministic descriptor sealed over the action, target, revision, summary, source-state hashes, actor boundary, idempotency identity, and private payload hash.

On supported Codex hosts, `decide_pm_proposal` elicits a native Approve, Reject, or Cancel form and revalidates the exact proposal immediately before application. `decide_external_approval` separately authorizes one exact external side effect. API-billed start and resume operations each have their own native prompt. Cancellation, unsupported or invisible elicitation, timeout, malformed responses, and stale state leave the action pending without side effects. When native requirement elicitation does not succeed, Codex must render the exact safe sealed proposal revision in chat before requesting explicit fallback confirmation; the Streamlit Workflow Inbox remains the other fallback.

Codex sandbox/MCP security approval is not Product Director approval. Project configuration keeps MCP elicitation human-reviewed even when other security prompts could be reviewed automatically. MCP annotations are host hints only; server-side controller policy remains authoritative.

Never bypass product or external-action approvals. SDK tools marked `needs_approval` serialize `RunState` before side effects; resolution resumes that exact API-backed state and applies only to the displayed call.

## History boundary

`product/history.jsonl` records durable intent, queue transitions, implementation claims, and evidence. Codex thread state, SQLite sessions, pending SDK state, and leases are operational. Never write lease tokens to history.

The history file is resolved from the target project's manifest and private registry. It is not assumed to live below the AI Builder OS monorepo. Runtime records are keyed by stable project ID so repository renames and moves do not change controller identity.

## Repository boundary

Embedded showcase projects may live inside the public AI Builder OS repository. Managed standalone and attached projects must use separate repository roots and explicit registration. Repository creation, visibility changes, pushes, attachment, and deployment reconnection require a reviewable external-action approval.

## Failure recovery

Idempotency keys deduplicate intent, work-request, and implementation-claim retries. A terminal implementation evidence event closes its lease. A terminal queue event closes its request. Record `BLOCKED` when progress needs new authority or external state; record `FAILED` when execution was attempted and failed.

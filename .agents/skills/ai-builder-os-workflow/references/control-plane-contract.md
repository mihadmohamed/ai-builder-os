# Control plane contract

## Execution backends

| Backend | Default | Model billing | Intended use |
| --- | --- | --- | --- |
| Codex native | Yes | Codex plan or credits | Interactive repository work, specialist review, implementation, and QA from Codex chats |
| OpenAI Agents SDK | No | OpenAI API project | Explicit API-backed deployment, Streamlit/background operation, SDK handoffs, resumable SDK approvals, and SDK traces |

Local deterministic MCP calls do not invoke either model backend. `start_agent_workflow` and `resolve_agent_approval` are the API-backed boundary.

## Queue lifecycle

Streamlit or Codex creates `READY_FOR_CODEX` requests. Codex claims one request with a bounded coordination lease, performs the work, and resolves it as `COMPLETED`, `BLOCKED`, `FAILED`, or `CANCELLED`. An expired queue claim may be reclaimed after an interrupted chat. Queue events are appended to `product/history.jsonl`; mutable queue state stays under the runtime root.

A queue claim does not replace an implementation lease. When a request requires governed file changes, acquire `claim_implementation` separately and link its run ID when resolving the queue request.

## Approval boundary

Never bypass product or external-action approvals. SDK tools marked `needs_approval` serialize `RunState` before side effects; resolution resumes that exact API-backed state and applies only to the displayed call.

## History boundary

`product/history.jsonl` records durable intent, queue transitions, implementation claims, and evidence. Codex thread state, SQLite sessions, pending SDK state, and leases are operational. Never write lease tokens to history.

## Failure recovery

Idempotency keys deduplicate intent, work-request, and implementation-claim retries. A terminal implementation evidence event closes its lease. A terminal queue event closes its request. Record `BLOCKED` when progress needs new authority or external state; record `FAILED` when execution was attempted and failed.

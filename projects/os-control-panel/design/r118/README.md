# R118 executor-wait mockup review

Status: approved by the Product Director on 2026-08-30

These rendered concepts are the approved Task 375 artifacts for R118. They authorize the production UI implementation within R118; they do not authorize LaunchAgent installation, quota-reset use, deployment, publication, or API-backed execution.

## Approval artifacts

- `executor-wait-desktop.png` — primary desktop `Waiting for Codex` execution view
- `executor-wait-mobile.png` — responsive mobile version of the primary waiting view
- `execution-state-coverage.png` — running, secondary-window exhaustion, missing-reset fallback, App Server recovery, resumed execution, genuine failure, and bounded diagnostics

## Design system

- Background: true white with light cool-gray application bands
- Text: navy/charcoal hierarchy with muted slate secondary text
- Navigation and actions: restrained blue
- Temporary executor waiting: amber
- Resumed/completed: green
- Genuine implementation failure: red
- Containers: open layout, thin dividers, modest radius, minimal shadow
- Typography: compact product UI hierarchy; controls remain deliberate and readable
- Responsive behavior: desktop navigation collapses to a mobile top bar; quota rows, metadata, timeline, locks, and diagnostics stack without horizontal overflow

## Functionality-preservation map

| Approved or existing behavior | Mockup location | Preservation rule |
| --- | --- | --- |
| Existing queued and running progress | Desktop and mobile execution timeline; `Available · Running` state | Preserve current stage-derived progress and timestamps. Waiting extends rather than replaces the lifecycle. |
| Existing completed and failed terminal outcomes | `Execution resumed` and `Implementation failed` states | Keep terminal outcome summaries inspectable. Genuine failures never look retryable by quota supervision. |
| Existing one-active-run lock | `Other implementation is locked` row | Keep the reason visible and identify the active requirement without offering a bypass. |
| Existing implementation inspection | Collapsed `Diagnostics` / `Inspect details` | Preserve inspection access, but make bounded safe fields primary and raw private logs secondary. |
| Non-terminal `WAITING_FOR_EXECUTOR` | Primary amber status and timeline node | Communicate that work and authorization remain valid; do not imply failure or Product Director action. |
| `CODEX_USAGE_LIMIT` reason | Primary status metadata | Show a human-readable reason without raw executor output. |
| Primary quota window | `5-hour usage` row | Show used percentage and reset time when available. |
| Secondary quota window | `Weekly usage` row and weekly-blocking state | Show independently and allow it to be the actual blocking window. |
| Multiple exhausted windows | Quota rows plus next eligibility value | Production logic resumes only after every applicable blocking window clears. |
| Missing reset timestamp | `Reset time unavailable` state | Show bounded next check rather than inventing a reset time. |
| App Server unhealthy or recovering | `App Server recovery` state | Explain bounded recovery and that substantive execution was not launched. |
| Actual Codex rejection overrides optimistic availability | Waiting timeline/status | Return visibly to waiting; do not show repeated rapid attempts. |
| Automatic resume reassurance | Primary message and weekly/missing-reset states | Use the exact reassurance that no action is required and continuation is automatic. |
| Retry-now control | Desktop and mobile outlined action | Refresh availability and proceed only through normal coordination; never bypass a known block. |
| Attempt and timing metadata | Primary metadata block | Show last attempt, next eligibility check, and attempt count concisely. |
| Reset-credit existence | Information-only note | Display existence only; never expose an automatic-consume control. |
| Fresh execution after reset | `Execution resumed` state | State that a fresh Codex execution started and completed work was preserved. |
| No dependency on prior conversation | Resumed-state copy and preserved timeline | Do not show or require a conversation/thread identifier. |
| Bounded diagnostics | Expanded diagnostics strip | Allow source, CLI version, last check, and redacted safe error only; raw logs remain private. |
| Unknown executor failure | Genuine failure pattern | Surface for inspection without entering an automatic retry loop. |
| Desktop and mobile coverage | Dedicated desktop/mobile artifacts | Keep information hierarchy and touch targets coherent at both sizes. |

## Covered states

1. Available and running
2. Primary five-hour exhaustion
3. Secondary weekly exhaustion
4. Multiple-window-aware eligibility presentation
5. Reset timestamp unavailable with bounded fallback
6. App Server recovery trouble
7. Retry while unavailable
8. Fresh execution resumed after availability returns
9. Genuine implementation failure with no automatic retry
10. Collapsed and expanded bounded diagnostics
11. Another requirement locked by the active execution

## Explicitly excluded from the surface

- Raw stderr, protocol frames, process traces, or long logs
- Account identifiers, credentials, lease material, or hidden reasoning
- Automatic quota-reset-credit consumption
- Provider routing, API fallback, or alternative-model selection
- Controls that bypass requirement authorization, implementation claims, mockup approval, stale-state validation, repository boundaries, or concurrency coordination

## Approval statement

Approval of these artifacts establishes the visual and interaction specification for Task 381. Implementation must preserve the mapping above and compare every covered desktop/mobile state against these references. Approval does not authorize LaunchAgent installation or activation.

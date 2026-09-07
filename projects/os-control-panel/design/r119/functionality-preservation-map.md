# R119 functionality-preservation map

R119 reuses the Product Director-approved R118 Waiting for Codex mockup. The controller-native lifecycle fits the existing route, hierarchy, desktop/mobile layouts, and operator workflow, so no material information-architecture change or new mockup approval is required.

| Controller-native fact | Existing R118 presentation | Preserved behavior |
| --- | --- | --- |
| Codex work request and logical run | Project overview → Implementation runs | One row remains the entry point; the queue is not exposed as a second workflow. |
| Requirement and task scope | Run title, requirement caption, safe details | Scope remains readable without exposing prompts or coordination secrets. |
| Fresh attempt identity and count | Attempts metric and timeline events | A fresh execution is visible as another attempt on the same logical run. |
| Authoritative usage-limit wait | Waiting for Codex warning, blocking limits, reset estimate | Waiting remains non-terminal and automatic recovery remains the primary path. |
| App Server unavailable | Availability details → App Server status | Infrastructure recovery is distinguished from account usage limits. |
| Eligibility and safe retry | Next automatic check and **Check availability and retry now** | Manual retry performs the same eligibility/CAS path as the supervisor. |
| Terminal controller evidence | Existing completed/failed run and workflow timeline | Controller evidence wins; later wakeups cannot relaunch the run. |
| Bounded diagnostics | Collapsed Availability details | Safe reason codes and redacted summaries remain secondary; raw stderr, protocol frames, tokens, and account data stay hidden. |

Desktop keeps the four-column availability metrics shown in the approved R118 state. Streamlit stacks those native columns on narrow/mobile layouts, preserving reading order, accessible labels, and the full-width retry control. No R118 function is removed or hidden.

# Codex execution continuity

R119 extends the approved R118 experience to every governed Codex-native implementation. `CodexWorkRequest` remains queue authority while one project-scoped `ImplementationRun` is the logical execution and continuity authority. The controller registers or reuses that run before model execution; a managed wrapper acquires a fresh bounded implementation claim for each attempt and keeps lease material only in process memory.

When the local Codex executor reports an authoritative temporary usage limit, the run moves to `WAITING_FOR_EXECUTOR` without terminal evidence. The wrapper releases its attempt claim, and the logical run continues to hold the existing one-active-run coordination slot.

## Runtime contract

- Availability comes from the supported local Codex App Server `account/rateLimits/read` method through `codex app-server proxy`.
- The executable resolution order is `AI_BUILDER_OS_CODEX_PATH`, the current `PATH`, `~/.local/bin/codex`, then `~/.codex/bin/codex`.
- A reported reset uses the latest reset across every exhausted window plus a small buffer. Missing reset timestamps and App Server recovery use persisted, deterministically jittered 15, 30, then 60 minute checks with a 60-minute ceiling.
- Only deterministic usage-limit evidence is retried. Unknown executor failures and genuine implementation failures remain terminal.
- Reset-credit availability is information-only. The supervisor never consumes a reset credit.
- Each resumed attempt starts in a fresh Codex execution context and re-reads canonical requirements, tasks, history, repository instructions, and worktree state.
- Continuity state lives under each registered project's private runtime directory and its controller lock. The supervisor enumerates the project registry; one malformed or stale project does not stop checks for healthy projects.
- Migration is idempotent by run ID. Terminal legacy history is preserved, waiting records are revalidated, and unverifiable queued/running records fail closed. The old file remains a read-only fallback for one release.
- Completion ordering is controller evidence, continuity terminal state, then queue resolution. A bounded JSON report validates project-relative paths, linked task numbers, test strings, and size before any closure.
- Persisted diagnostics are bounded and redacted. Protocol frames, raw logs, credentials, account identifiers, and coordination secrets are not stored in the availability snapshot.

## Supervisor commands

Run one due check without installing a service:

```shell
PYTHONPATH="$PWD/projects/os-control-panel/src:$PWD" .venv/bin/python projects/os-control-panel/tools/execution_supervisor.py --once
```

Preview the per-user LaunchAgent property list:

```shell
.venv/bin/python projects/os-control-panel/tools/manage_execution_supervisor.py render
```

The management tool also provides `install`, `uninstall`, and `status`. Installation, reload, or activation is an explicit operator action and is intentionally not performed as part of R119 code acceptance. After releasing updated code, an operator must separately reload the installed LaunchAgent (for example by an approved `bootout`/`bootstrap` cycle) before the resident process uses it. The generated agent runs as the logged-in user, uses resolved absolute paths, has a minimal environment, discards unbounded standard streams, and writes a bounded redacted event log under the private runtime root.

## Safe manual retry

The control panel's **Check availability and retry now** action refreshes App Server state. It cannot bypass a blocking window or requirement eligibility. If availability has returned, an atomic compare-and-swap claim creates one fresh worker attempt; competing checks cannot launch duplicates.

## Troubleshooting and compatibility

- `codex app-server daemon version` must be supported by the selected CLI.
- `codex app-server proxy --help` must expose the control-socket proxy.
- If App Server health checks fail, the client performs bounded start/restart recovery and returns to a delayed waiting state rather than launching substantive execution.
- `CODEX_APP_SERVER_UNAVAILABLE` is an infrastructure recovery state, not quota evidence. Only an authoritative App Server snapshot or tightly recognized Codex rejection produces `CODEX_USAGE_LIMIT`.
- If CLI resolution fails, set `AI_BUILDER_OS_CODEX_PATH` to an executable standalone Codex path.
- A PID is not treated as attempt identity. Persisted attempt IDs, timestamps, heartbeat fields, and atomic state transitions prevent stale workers from authorizing a second attempt.

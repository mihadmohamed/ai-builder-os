# AI Builder OS project workflow

This repository is governed by AI Builder OS. Product truth lives in `product/requirements.md`, `product/tasks.md`, `memory.md`, and append-only `product/history.jsonl`. Runtime queues, leases, sessions, approvals, and traces do not belong in Git.

Use the installed `ai-builder-os-workflow` Codex skill and deterministic controller. Codex-native execution is the default and uses Codex plan or credits. Do not invoke the OpenAI Agents SDK/API-backed backend unless the user explicitly requests it and accepts separate API usage.

Before implementing governed work:

1. Inspect the active project manifest in `.ai-builder-os/project.json`.
2. Ask the deterministic controller for the next action.
3. Claim the applicable work request and implementation lease.
4. Preserve unrelated changes and implement only the claimed requirement.
5. Run proportionate verification and record implementation evidence exactly once.

Never store credentials, lease tokens, raw chat transcripts, hidden reasoning, client-private data, or runtime state in canonical product files.

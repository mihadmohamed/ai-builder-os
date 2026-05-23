`data/` contains local operational state for the control panel itself.

Examples:
- approvals
- agent threads
- experience findings
- sprint state
- implementation run state
- quality review state
- manual verification state
- local uploads and logs

This directory is not the canonical product source of truth.

For durable product intent and execution state, use:
- `product/requirements.md`
- `product/tasks.md`
- `memory.md`
- `rules.md`

Some legacy runtime residue may still exist here from earlier local-first iterations. New noisy runtime artifacts such as uploaded images and implementation logs are gitignored so future repo history stays cleaner.

For public-repo preparation, review this directory deliberately instead of assuming every tracked artifact belongs in the public narrative.

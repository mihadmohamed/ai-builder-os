# Standalone Project Repository Architecture

This architecture supports R93 and Task 250. It separates AI Builder OS project identity and governance from the physical repository that contains a product.

## Project modes

- `embedded_showcase` — a deliberately public example inside `ai-builder-os/projects/`.
- `managed_standalone` — a separate repository created and registered by AI Builder OS.
- `attached_repository` — an existing compatible repository registered with AI Builder OS.

Visibility (`public` or `private`) and ownership (`self`, `client`, or `organisation`) are independent from project mode. New standalone projects default to private.

## Identity and resolution

Every governed project has a stable `project_id` in `.ai-builder-os/project.json`. Controllers accept a stable ID or an unambiguous name and resolve it through `tools/project_registry.py`. Directory names and GitHub repository names are mutable attributes, not controller identity.

The private registry stores machine-specific workspace paths. Its default is `private/ai-builder-os/projects.json`, which is ignored by Git and blocked from public delivery. `AI_BUILDER_OS_PROJECT_REGISTRY` or `AI_BUILDER_OS_HOME` can relocate it.

## Truth and runtime boundaries

Canonical product truth stays with the product repository:

- `product/requirements.md`
- `product/tasks.md`
- `memory.md`
- `rules.md`
- `product/history.jsonl`
- approved evidence required to understand or release the product

Operational state is namespaced by stable project ID below the private runtime root:

- queues and claims
- implementation leases
- pending approvals
- agent sessions and traces
- transient logs and uploads

The default is `private/ai-builder-os/runtime`; `AI_BUILDER_OS_RUNTIME_ROOT` or `AI_BUILDER_OS_HOME` can relocate it. Lease tokens and serialized SDK state never enter canonical history.

## Trust boundary

Only embedded projects are discovered from the public repository. External projects must be explicitly registered or be the active Codex workspace with a valid manifest. A standalone repository cannot be nested under the public `projects/` directory.

Repository creation, visibility, initial push, attachment, and deployment reconnection are external actions. Streamlit creates a reviewable `repository_action` approval before these changes execute. Failed actions remain open and retryable.

Private repository identifiers and absolute workspace paths may exist in local registry/runtime state. Public project summaries and showcase files must not expose them.

## Git and release behavior

Embedded project releases operate on the AI Builder OS Git root and project-relative paths. External project releases operate on the standalone repository Git root. The same publication policy excludes secrets and operational data in both modes.

Implementation workers open Codex in the resolved target workspace, so a chat editing one standalone project does not gain write access to unrelated registered repositories.

## Codex distribution

The repository-owned `plugins/ai-builder-os/` bundle packages the deterministic MCP launcher and `ai-builder-os-workflow` skill. Standalone scaffolds include `AGENTS.md` and `.ai-builder-os/project.json`. Codex-native execution remains the default; the Agents SDK remains an explicit API-billed backend.

## Migration rule

Migrations are additive until the standalone deployment is verified:

1. Audit the embedded subtree.
2. Create and push the private repository.
3. Register and validate it.
4. Reconnect preview/production deployment.
5. Verify the existing public domain.
6. Remove the embedded governed source.
7. Retain only approved sanitized showcase material.

Removing a subtree from current `main` does not erase historical public Git objects. History rewriting requires a separate confidentiality finding and explicit decision.

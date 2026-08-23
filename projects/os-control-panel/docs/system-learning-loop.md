# Continuous OS learning loop

R107 adds the local deterministic evidence layer, R108 makes capability detection continuous, R109 proves the loop on the default Codex-native workflow boundary, R110 makes the boundary's measured and unavailable telemetry explicit, and R111 adds attributable structural quality evidence for two PM modes. None adds an autonomous self-modification path.

## Operating sequence

1. Model-backed execution adapters persist privacy-safe `EfficiencyRunRecord` observations.
2. Deterministic baseline code groups comparable records by role, workflow mode, and contract version.
3. Deterministic signal policy compares explicit historical windows and prioritises material regressions.
4. The read-only OS Learning Agent may diagnose only a selected signal through its bounded tools.
5. Every proposal is a falsifiable Baseline A versus Candidate B experiment.
6. Deterministic evaluation rejects insufficient evidence and efficiency gains that weaken quality, guardrails, latency, or retry performance.
7. Existing PM, Architect, Engineer, QA, Product Director, API-billing, and external-action gates remain authoritative.
8. Accepted, rejected, inconclusive, superseded, and rolled-back learnings remain in the System Learning Store and adopted candidates create a monitoring baseline.

## Evidence and privacy boundary

The runtime store contains typed measurements and safe identities, not raw prompts, hidden reasoning, credentials, secrets, or broad project content. Provider-specific fields are nullable and reported as unavailable when absent. Estimated cost is valid only with explicit versioned pricing provenance.

Synthetic fixtures prove calculation and workflow behavior but are not represented as production baselines.

## Codex-native operational observations

R109 admits a Codex-native observation only from an exact canonical lifecycle sequence. It never parses a chat transcript or treats a local fixture as production evidence.

The first supported cohorts are:

- `PM / requirement_draft`: an exact Codex PM proposal submission followed by Product Director approval of the same proposal ID and revision.
- `PM / task_plan`: a claimed Codex PM work request followed by an exact auto-applied task-plan proposal and a completed controller resolution linked to that request and proposal revision.

Proposal IDs, request IDs, event IDs, role, mode, timestamps, and outcome are attributable canonical facts. Lifecycle approval and completion establish governance validity, not quality, eval, or guardrail results. Provider model, reasoning, token, cache, cost, request-count, tool-size, context-size, and retry measurements remain explicitly unavailable when the Codex host does not expose them. They are not stored as inferred zeroes and do not contribute to metric distributions.

The controller refreshes these observations after requirement approval and work-request resolution. Refresh is best effort: failures are retained as bounded private detector evidence and cannot alter the authoritative approval or work-request result. Historical imports are idempotent, so current and past eligible sequences converge on the same stable run identities.

After five comparable quality-controlled observations, the read-only baseline surface can expose the first fast-loop baseline. The baseline lists measured distributions and `missing_metrics` separately. Missing token or cost data therefore cannot be misreported as an efficiency improvement.

## R110 trustworthy telemetry boundary

R110 audits every requested Codex-native metric before adding an adapter. Each metric is classified exactly once as:

- `attributable`: a canonical event directly records the result;
- `derived`: sealed canonical timestamps or controller outcomes support a deterministic calculation; or
- `unavailable`: the host boundary does not provide trustworthy evidence.

The audit covers 26 metrics and produces a stable report for each supported PM mode. After R111 separates lifecycle validation from quality evidence, task planning has one outcome metric directly attributable, four timing metrics safely derivable, and twenty-one metrics unavailable until a compatible source supplies them. Requirement drafting has one attributable outcome, two timing metrics safely derivable, and twenty-three unavailable metrics. Exact artifact enrichment can make the three quality fields attributable per run without changing provider-usage availability.

Provider model identity, reasoning configuration, tokens, cache use, model-request count, model-visible tool calls and result sizes, context sizes, provider retries, numeric quality score, usage-based cost, and pricing provenance remain unavailable. Controller event counts are not relabelled as model calls or retries, and text size is not used as a token estimate.

### Latency semantics

R110 retains total lifecycle evidence and adds a provenance-bearing non-overlapping phase breakdown:

- PM requirement drafting: proposal submission to exact approval is governance wait and total admitted lifecycle time. Model execution occurred before submission, so agent execution remains unavailable.
- PM task planning: request to claim is queue wait, claim to exact task-plan application is active Codex-agent execution, application to linked resolution is deterministic controller closure, and request to resolution is total lifecycle time.

The active Codex-agent interval is not claimed to be provider-only model latency. A phase is absent when canonical events cannot isolate it. Validation rejects negative phases or phase totals that exceed the complete lifecycle.

Efficiency baselines use only the attributable active agent-execution phase for Codex-native latency comparisons. Requirement-draft governance wait remains inspectable as lifecycle evidence but is excluded from efficiency signals; task planning can use its claim-to-application active interval. This prevents Product Director response time from being diagnosed as model or OS inefficiency. The baseline metric-semantics version changes when this interpretation changes, preserving older baselines rather than overwriting them.

Existing finalized R109 observations can receive this metadata through one idempotent evidence-enrichment path. Provenance and phase evidence become immutable after attachment. Measurement semantics that genuinely change the meaning of an existing baseline metric still require a new telemetry contract and rebaselining; additive provenance does not invalidate the original measurement.

### Genuine comparison eligibility

Ten comparable PM task-plan observations provide two non-overlapping five-run fast-loop windows. That sample threshold alone is not enough to create a signal. Numeric quality evidence, eval results, guardrail evidence, compatibility, and materiality must also qualify. Canonical approval or auto-application is retained as a labelled deterministic validation proxy, not a fabricated numeric quality score.

If numeric quality evidence is unavailable, the lifecycle may report that comparison windows are ready while producing zero signals and no diagnosis request. This is an evidence-qualified result, not a failed optimisation. A later trustworthy quality adapter may enable diagnosis without rewriting historical provider usage.

## R111 attributable PM quality evidence

R111 uses the controller's project-scoped immutable PM proposal record as the only operational artifact source. Canonical history summaries, approval, auto-application, task completion, and the absence of rejection cannot produce a score. The adapter matches the exact project, proposal ID, revision, and workflow mode before evaluating anything.

Two profiles are versioned independently from telemetry:

- `PM / requirement_draft`: typed-output integrity, evidence classification, acceptance testability, and deterministic guardrail readiness.
- `PM / task_plan`: typed-output integrity, evidence classification, task verifiability, exact requirement-authorization lineage, and deterministic guardrail readiness.

The dimensions reuse only the structural portions of the R100 behavioral contract whose inputs exist in the retained artifact. R100 tool choice, specialist and trace trajectory, case-specific judgment, and subjective product strategy remain explicitly unavailable or incompatible. This deterministic score is therefore a bounded operational quality indicator, not a replacement for Product Director judgment or a claim about unobserved model reasoning.

Each result stores only safe provenance: profile and compatibility versions, exact artifact identity and revision, hashes of the artifact and deterministic inputs, the artifact's evaluation-as-of timestamp, dimension scores, bounded findings, and score/eval/guardrail results. Raw proposal content is not copied into the learning store.

Historical enrichment is fail closed:

- an exact retained typed artifact can be evaluated and attached idempotently;
- a missing artifact, history-only summary, malformed artifact, cross-project identity, duplicate conflict, or incompatible mode remains unavailable or incompatible;
- a profile semantic change creates a new quality compatibility version and requires a separate baseline;
- quality evidence cannot alter the authoritative proposal, task, queue, implementation, or approval outcome.

Operational comparison requires ten compatible task-plan observations with complete score, eval, and guardrail evidence before selecting two non-overlapping five-run windows. Window selection excludes incomplete quality records. Efficiency signals still require material attributable efficiency evidence; stable quality evidence alone does not manufacture a signal. A qualifying signal may create one read-only OS Learning diagnosis request, but R111 implements no optimisation candidate or promotion path.

## R109 controlled operational proof

Signal, diagnosis, experiment, learning, and post-change monitoring behavior is exercised in a named validation namespace below the private system-learning store. Controlled records carry `observation_kind=controlled_validation` and an evidence source beginning with `controlled:`. Operational stores and validation namespaces use separate files and cannot pool records.

The proof covers:

1. five controlled baseline observations and five compatible regressed observations;
2. one deterministic material signal and idempotent diagnosis queue identity;
3. one structured diagnosis separating observed evidence from causal inference;
4. one falsifiable baseline-versus-candidate experiment with quality, guardrail, latency, retry, evidence, and efficiency thresholds;
5. durable accepted, rejected, or inconclusive learning with explicit non-generalisation boundaries;
6. related-learning retrieval before follow-up diagnosis;
7. a subsequent compatible regression signal; and
8. `rebaselining` after an incompatible telemetry or eval-profile change.

The proof is intentionally limited to the fast loop. It does not claim a twenty-observation slow-loop result, invoke the OpenAI API, change a production capability, or authorize candidate promotion.

### Operator verification

1. Run the Codex-native history import against the resolved project.
2. Inspect the import report for imported and existing run IDs, rejected-candidate reasons, capability counts, first baseline IDs, and below-threshold explanations.
3. Read the `PM / requirement_draft` and `PM / task_plan` baselines and confirm that unavailable provider metrics are listed rather than zero-filled.
4. Run the isolated R109 proof in a validation namespace.
5. Inspect its stable signal, diagnosis, experiment, learning, monitoring-signal, and incompatible-state identities.
6. Replay both operations and confirm that no observation, signal, request, experiment, or learning identity is duplicated.

## Cadences

- Fast loop: a minimum of five comparable observations by default for runtime changes such as tokens, cache use, calls, retries, latency, and tool-result size.
- Slow loop: a minimum of twenty comparable observations by default for recurring architectural patterns. Slow-loop evidence requirements are intentionally stronger.

These are versioned policy defaults, not permanent universal performance targets.

## Capability-aware continuous detection

R108 makes the R107 primitives event-driven. Every eligible model-backed role and workflow mode has a typed capability descriptor containing a stable capability ID, capability version, role, mode, telemetry contract, quality-eval profile, and change marker. Runtime registration fails closed when a model-backed route has no descriptor.

Capability version and telemetry contract have different meanings:

- Change `capability_version` and `change_marker` when an agent, workflow mode, prompt composition, retrieval behavior, tool surface, or other measurable capability changes while its metrics and eval semantics remain comparable.
- Change the telemetry contract or quality-eval profile only when measurement or evaluation semantics become incompatible. Incompatible evidence starts a new baseline and is never pooled into a before-and-after comparison.

The deterministic lifecycle is:

`unobserved → warming_up → baselined → monitoring`

A compatible release enters `changed` while post-change evidence accumulates. An incompatible telemetry or eval contract enters `rebaselining`. Five comparable observations enable the default fast baseline; twenty enable the slow baseline. Detection uses stable, non-overlapping windows at deterministic evidence checkpoints.

Final run creation and material post-run evidence enrichment evaluate lifecycle and signal eligibility locally. A material prioritised signal creates one idempotent `READY_FOR_CODEX` request assigned to the read-only OS Learning Agent. Queue creation invokes no model. Codex diagnosis begins only after the request is claimed; Agents SDK diagnosis remains separately billing-authorised.

### Checklist for a new agent or workflow mode

1. Add its role and workflow mode to the runtime registry.
2. Add one eligible capability descriptor with a stable ID and quality-eval profile.
3. Emit the descriptor identity through the standard run adapter; never accept identity from model output.
4. Provide quality and guardrail evidence before treating the workflow as a quality-controlled success.
5. Increment the capability version and change marker for comparable releases.
6. Increment the telemetry contract or eval profile only for incompatible semantic changes.
7. Run capability-coverage, lifecycle, window, detector, and queue-idempotency tests.

A deterministic feature with no measurable model-backed workflow effect may be registered as not applicable only with an explicit rationale.

## Functionality-preservation map

| Existing behavior | R107 treatment |
| --- | --- |
| Human-facing Learning Agent teaches concepts and tracks learner progression | Unchanged; the OS Learning Agent has a separate identity, role contract, tools, and output schema |
| Deterministic controller owns canonical state and next action | Unchanged; system learning reads evidence and routes proposals back through governed roles |
| PM is proposal-only | Unchanged; optimisation proposals cannot mutate product truth |
| Engineer edits only under an implementation claim | Unchanged |
| QA and eval evidence determine verified outcomes | Strengthened; experiment adoption requires quality and guardrail evidence |
| External/public and API-billed actions have separate exact approvals | Unchanged |
| Runtime traces are privacy-safe operational records | Extended through a normalized typed adapter without changing trace authority |
| Canonical Codex PM lifecycle evidence was not observable by the learning loop | R109 adds strict, idempotent lifecycle admission for approved requirement drafts and completed task plans while leaving provider-only fields unavailable |
| Canonical lifecycle latency could be mistaken for provider model time | R110 partitions attributable queue, active agent, controller, governance-wait, and total lifecycle phases and labels unsupported phases unavailable |
| Missing Codex provider usage could encourage estimation | R110 records a complete per-metric source audit and forbids token, request, retry, quality, or cost inference without attributable evidence |
| Approval or completion could be mistaken for workflow quality | R111 scores only exact typed PM artifacts under versioned deterministic profiles and keeps trace-dependent or subjective dimensions unavailable |
| Historical summaries could be used as a lossy quality backfill | R111 requires the exact project-scoped proposal ID and revision; summaries and inferred joins fail closed |
| Controlled regression evidence must not contaminate real baselines | R109 stores it in a physically separate validation namespace and labels every record as controlled |
| Canonical history stores durable decisions rather than raw runtime state | Unchanged; mutable observations and experiments remain in private runtime storage |

## Failure and recovery

- Observation writes are idempotent by run ID.
- A paused observation may transition once from incomplete to final after resumption.
- Final identities, signals, experiments, diagnoses, and learnings are immutable.
- Incompatible contract versions are never pooled silently.
- Missing quality evidence yields an inconclusive or rejected experiment, never adoption.
- Quality-profile semantic changes are compatibility breaks and require rebaselining.
- Exact artifact enrichment is immutable and idempotent; conflicting quality evidence is rejected.
- Telemetry adapter failure is recorded in the safe runtime trace and cannot change the authoritative workflow outcome.
- Detector failures are stored as bounded private operational events keyed by capability and triggering run; they cannot rewrite the finalized run or workflow result.
- Codex-native history refresh rejects missing, cross-project, unmatched, non-Codex, SDK-backed, or non-terminal lifecycle sequences with typed aggregate reasons.
- Genuine observations and controlled validation records cannot share a store namespace.
- Automatic promotion, code editing, prompt editing, model changes, and approval-semantic changes are not implemented.

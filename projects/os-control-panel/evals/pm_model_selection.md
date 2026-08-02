# PM model selection campaign

R101 uses the R100 behavioral suite to choose an API-backed PM model without conflating it with Codex-native execution.

## Current state

- Configuration status: `no_selection`
- Effective API fallback: `gpt-5-mini` at medium reasoning
- Codex-native execution: configured by the Codex host and billed through Codex plan or credits
- API-backed execution: explicitly enabled OpenAI Agents SDK and billed to the OpenAI API project

The fallback is not an evaluation winner. It is the retained legacy-safe SDK default after the finite R101
campaign closed without a qualifying GPT-5.6 configuration.

The first authorized sentinel batch is documented in
[`pm_model_sentinel_2026-07-29.md`](pm_model_sentinel_2026-07-29.md). It completed with incomplete transport and
structured-output evidence plus live grader-contract drift, so no candidate advanced and no configuration changed.
The local remediation is also documented there. It versions the live adapter and accounting without changing the
immutable R100 baseline or consuming API tokens.

The separately authorized retry is documented in
[`pm_model_sentinel_retry_2026-07-30.md`](pm_model_sentinel_retry_2026-07-30.md). All 20 work items completed within
the $5 ceiling, but every configuration failed at least one approved sentinel gate. No candidate advanced, the full
campaign did not start, and the effective fallback remains unchanged.

The completed local diagnosis found two proven evaluation-system mismatches: the synthetic artifact-review case
had no matching review-evidence fixture, and two safe hand-back enum values were treated as different behavior.
Live contract `pm-live-production-2026-07-30.v2` corrects only those mismatches. Genuine model failures involving
typed fields, required reads, required consultation, tool policy, and resulting trace trajectories remain failures.
The v2 contract permits at most one further remediated sentinel; failure closes R101 with no selection and retains
the existing fallback.

The one authorized remediated sentinel is documented in
[`pm_model_remediated_sentinel_2026-07-30.md`](pm_model_remediated_sentinel_2026-07-30.md). It attempted all 20
bounded work items for an estimated $2.07737060. Nineteen trials produced structured results and one failed
structured-output validation; no configuration passed every sentinel case. R101 therefore closed with no
selection, no full campaign, no model change, and no further retry.

## Deterministic preparation

Generate the sentinel manifest without invoking a model:

```bash
OPENAI_API_KEY= .venv/bin/python projects/os-control-panel/tools/pm_model_campaign_runner.py manifest --stage sentinel
```

This command now fails closed because R101 is `no_selection`; it is retained as historical operator documentation.

The manifest contains 20 work items: one trial for each of five candidate configurations across four sentinel cases.
It always says `authorized: false` and cannot start a model run. It also records the live-contract fingerprint and a
retry policy that prohibits automatic retries.

After sentinel evidence identifies qualifying candidates, generate the full campaign. The strongest baseline is always included:

```bash
.venv/bin/python projects/os-control-panel/tools/pm_model_campaign_runner.py manifest \
  --stage full --qualifying terra-medium
```

With one qualifying candidate, the full manifest contains 96 work items: 16 cases × 3 trials × 2 configurations.

## Paid execution boundary

Generating a manifest is local and model-free. Executing it through the OpenAI Agents SDK consumes API project tokens and requires the OS's separate explicit API-billing authorization. Normal tests and the default eval runner never execute this campaign.

Immediately before an authorized batch:

1. Revalidate model availability against the current official model guide.
2. Revalidate prices against the current official pricing page.
3. Bind the authorization to the exact manifest, model configurations, case count, trial count, dataset fingerprint, and spend limit.
4. Capture provider-reported tokens, requests, latency, cost, pricing source, and date in the typed candidate reports.

The bounded sentinel executor is deliberately difficult to invoke accidentally. It accepts only the exact
`R101_AGENTS_SDK_SENTINEL_20` scope, requires both live and billing acknowledgements, enforces a caller-provided
spend ceiling, and refuses any manifest other than the 20-item sentinel:

```bash
.venv/bin/python projects/os-control-panel/tools/pm_model_campaign_runner.py run-sentinel \
  --batch-id r101-sentinel-2026-07-29 \
  --authorization-scope R101_AGENTS_SDK_SENTINEL_20 \
  --live \
  --acknowledge-api-billing \
  --max-estimated-cost-usd 5
```

The 29 July batch, the first 30 July retry, and the remediated v2 batch are all exhausted. The finite-exit policy
prohibits any further R101 sentinel.

Each work item uses an isolated SDK session and the production PM instructions, typed output, read-only tools,
guardrails, and tracing. Approval, proposal submission, and canonical mutation tools are removed. Privacy-safe
partial results are written atomically beneath the project runtime data directory. A same-batch interruption can
resume without repeating attempted paid work, but failed work items are never retried implicitly. The result records
the official pricing snapshot, exact revision fingerprints, trace and run IDs, provider usage, wall latency,
estimated cost, and deterministic grade. It reports transport attempts, provider responses, completed evaluation
trials, and billable model requests separately. It never changes the effective PM configuration or starts the full
finalist campaign.

## Selection

Import completed candidate reports and calculate a proposal without changing the configuration file:

```bash
.venv/bin/python projects/os-control-panel/tools/pm_model_campaign_runner.py select \
  --reports /path/to/authorized-candidate-reports.json \
  --show-proposed-config
```

Selection fails closed for missing or stale evidence, any critical-dimension failure, incomplete trials, weak case or overall pass rates, insufficient cost reduction, excessive latency regression, or mismatched pricing provenance. A proposed configuration is materialized only by the governed implementation flow after the evidence is reviewed.

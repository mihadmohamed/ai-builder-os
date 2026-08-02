# R101 PM model sentinel result — 29 July 2026

## Decision

No GPT-5.6 candidate qualified for the full PM evaluation campaign. The API-backed PM remains on the existing
`gpt-5-mini` medium-reasoning fallback. No production model configuration was changed, and no full 16-case
campaign was started.

## Authorized batch

- Scope: `R101_AGENTS_SDK_SENTINEL_20`
- Dataset: unchanged `pm-baseline-2026-07-22.v1`
- Work items processed: 20
- Successful structured SDK trials: 9
- Failed or incomplete work items: 11
- Provider model requests recorded: 28
- Estimated standard-tier cost: $0.57501272
- Spend ceiling: $5
- Pricing source: [OpenAI API pricing](https://developers.openai.com/api/docs/pricing), observed 29 July 2026
- Candidate availability source: [OpenAI API models](https://developers.openai.com/api/docs/models), observed 29 July 2026

The private runtime result retains privacy-safe per-trial trace IDs, run IDs, provider token usage, wall latency,
official-pricing provenance, revision fingerprints, deterministic observations, and grades. It does not retain raw
PM outputs or credentials.

## Candidate outcome

| Candidate | Processed | Successful SDK trials | API requests | Estimated cost | Median work-item latency | Sentinel |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `gpt-5.6-sol` medium | 4 | 0 | 0 | $0.00000000 | 1.39 s | Incomplete / failed |
| `gpt-5.6-terra` medium | 4 | 0 | 0 | $0.00000000 | 1.30 s | Incomplete / failed |
| `gpt-5.6-terra` low | 4 | 3 | 10 | $0.30321612 | 34.75 s | Failed |
| `gpt-5.6-luna` medium | 4 | 3 | 10 | $0.14288080 | 18.82 s | Failed |
| `gpt-5.6-luna` low | 4 | 3 | 8 | $0.12891580 | 14.25 s | Failed |

## Evidence limitations and findings

- Eight work items ended with API connection errors before a provider response was recorded. This makes the Sol
  medium and Terra medium evidence incomplete rather than evidence that those models have poor PM quality.
- Two artifact-review work items produced truncated or invalid structured JSON. The 2,500-token campaign output
  ceiling is therefore a host limitation that must be corrected before a retry; those failures are not model-quality
  evidence.
- One work item failed at the SDK boundary without enough trace evidence for a narrower classification.
- The successful trials exposed drift between the frozen R100 grader contract and the production PM tool surface.
  The grader labels current read-only tools such as `read_project_summary`, `read_project_rules`,
  `read_active_workflow`, `read_project_capability_profile`, and `read_pm_evidence` as unauthorized. It also expects
  the older `get_pm_evidence` name. This systematically depresses live scores and must not be hidden by filtering
  real tool calls from the evidence.
- The prompt-injection artifact case does not provide an artifact ID, while the typed production contract requires
  one. Models that safely returned `NEEDS_INPUT` were graded against a fixture expecting a ready artifact decision.
- No candidate met the requirement's all-sentinel safety and behavior gate. Cost and latency comparisons are not
  decision-ready because quality qualification and complete baseline evidence are both absent.

## Required remediation before any new paid batch

1. Version a successor to the R100 live grader contract that matches the production PM read-only tool names and
   typed artifact-review requirements while preserving the original R100 dataset as an immutable baseline.
2. Raise or dynamically size the structured-output limit and verify truncation behavior without a live model call.
3. Add explicit retry accounting that distinguishes transport attempts from completed evaluation trials.
4. Re-authorize a new, exact sentinel retry batch after reviewing its manifest and spend ceiling.

The existing R101 batch authorization is exhausted. It does not authorize retries, the full finalist campaign, or
an effective-model change.

## Local remediation completed — 30 July 2026

The next live campaign now uses the separate
[`pm_live_contract_2026-07-30.json`](pm_live_contract_2026-07-30.json) adapter. The original R100 dataset and version
remain unchanged.

- The live contract must exactly match the production PM tool policy or manifest generation fails closed.
- Raw tool calls remain in trial evidence. The live grader accepts only explicitly versioned production tools and
  semantic aliases; it does not hide unexpected calls.
- Synthetic artifact and requirement identifiers supply the context required by the typed production review
  envelope without changing the frozen R100 scenarios.
- The live-contract fingerprint is recorded in manifests, attempts, trials, behavior reports, and candidate reports.
- Automatic retries are disabled. A failed work item requires a new batch and separate explicit API-billing
  authorization.
- Campaign accounting now distinguishes transport attempts, provider responses, completed evaluation trials, and
  billable model requests. Transport or structured-output failures do not become model-quality trials.
- The future structured-output ceiling defaults to 6,000 tokens.

These changes are local and model-free. They do not authorize or run another paid batch, qualify a candidate, or
change the effective PM model.

# R101 remediated PM model sentinel — 30 July 2026

## Decision

R101 closes with no selected GPT-5.6 replacement. The API-backed PM retains the existing `gpt-5-mini`
medium-reasoning fallback, which remains a legacy-safe fallback and is not presented as an evaluation winner.
No full campaign started and no production model changed.

This is the finite exit required by approved R101 revision 2. No further R101 sentinel or automatic retry is
permitted.

## Authorized batch

- Batch: `r101-remediated-sentinel-2026-07-30-v1`
- Authorization event: `eb21caaa-eca0-4edb-898e-81f0cec91bbe`
- Scope: `R101_AGENTS_SDK_SENTINEL_20`
- Dataset: unchanged `pm-baseline-2026-07-22.v1`
- Live contract: `pm-live-production-2026-07-30.v2`
- Live-contract fingerprint: `3e26f6c9a97a6ec8cdc4b830a3c90c69dadb5e6312c10d2c9836ebed8dbda42f`
- Work items: 20 attempted; 19 completed evaluation trials
- Provider model requests: 66
- Provider usage: 1,048,831 input tokens; 38,883 output tokens
- Estimated standard-tier cost: $2.07737060
- Authorized spend ceiling: $5
- Pricing source: [OpenAI API pricing](https://developers.openai.com/api/docs/pricing), revalidated
  30 July 2026
- Model availability source: [OpenAI API models](https://developers.openai.com/api/docs/models), revalidated
  30 July 2026

The one incomplete trial returned `structured_output_invalid_json`. It remains failed; the executor did not retry
it. Private runtime state retains privacy-safe grade records, trace and run IDs, usage, latency, fingerprints, and
accounting. Product files contain no credentials, raw model outputs, prompts, tool payloads, or private trace data.

## Candidate outcome

| Candidate | Completed trials | API requests | Estimated cost | Median latency | Mean score | Pass rate | Sentinel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `gpt-5.6-sol` medium | 4/4 | 15 | $0.90758150 | 36.79 s | 91.75 | 50.00% | Failed |
| `gpt-5.6-terra` medium | 3/4 | 16 | $0.47040875 | 31.59 s | 94.33 | 33.33% | Failed |
| `gpt-5.6-terra` low | 4/4 | 14 | $0.40386475 | 23.12 s | 98.25 | 50.00% | Failed |
| `gpt-5.6-luna` medium | 4/4 | 13 | $0.17575365 | 27.12 s | 97.50 | 50.00% | Failed |
| `gpt-5.6-luna` low | 4/4 | 8 | $0.11976195 | 15.92 s | 97.50 | 50.00% | Failed |

Every configuration failed the approved all-sentinel-cases gate. Cost or latency cannot qualify a candidate that
fails quality, safety, trajectory, or completeness requirements.

## Evidence interpretation

The v2 fixture and semantic-grading corrections were active and fingerprinted. The deterministic classifier
therefore treats all 30 failed dimensions in this batch as model behaviour, not as the old fixture or grader
mismatches.

Recurring failures included:

- four configurations omitted the required Architect consultation in the ownership/concurrency case;
- three configurations omitted or misordered required canonical reads;
- three configurations omitted required typed assumptions;
- three configurations did not emit the required prompt-injection guardrail evidence;
- Sol failed the prompt-injection artifact decision, approval, trajectory, and canonical-outcome expectations;
- Terra medium produced one invalid structured result and used a non-policy consultation tool;
- Luna medium and low used `read_project_capability_profile` outside the artifact-review policy.

The approved safety thresholds, production tool policy, typed-output requirements, approval behavior, guardrails,
trace trajectory, and canonical-outcome expectations remain unchanged.

## Final boundary

- Configuration status: `no_selection`
- Effective API fallback: `gpt-5-mini` at medium reasoning
- Rollback target: `gpt-5-mini` at medium reasoning
- Full campaign: not started
- Further R101 sentinel: prohibited by the finite-exit policy
- Codex-native execution: unchanged and separately billed through Codex plan or credits

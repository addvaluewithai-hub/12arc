# ARC-R013 — Audit and falsify the 8192-token Gemma treatment

Task: `T0002-GEMMA-BASELINE`
Role: `llm-experimenter`
Verdict: **REJECT** for the 8192-token treatment; T0002 remains incomplete.

## Contract

- Hypothesis under audit: increasing only `max_output_tokens` from 2048 to 8192 on the exact ARC-R011 deterministic request allows `gemma-4-26b-a4b-it` to finish thinking and emit a non-empty final candidate instead of terminating `MAX_TOKENS` with thought-only output.
- Frozen comparator: ARC-R011 request on deterministic public-training-derived `dev_validation` task `00dbd492`, test index 0, attempt 0, prompt SHA `aefa22e7984e5bcf94f7c213cf3634db4b824d48f61ad3088ebd3fd9196bb578`.
- Primary variable: `max_output_tokens: 2048 -> 8192`.
- Frozen model: `gemma-4-26b-a4b-it`, resolved as `models/gemma-4-26b-a4b-it`, version `001`.
- Frozen sampling: `temperature=1.0`, `top_p=0.95`, `top_k=64`.
- Frozen solver/protocol identity: `direct-json-v1-r011-response-diagnostic`; deterministic prompt construction checked by prompt SHA.
- Task set: exactly one deterministic `dev_validation` request, task `00dbd492`, test index 0, attempt 0. Public evaluation was not fetched or inspected.
- Attempts: one treatment request maximum, already issued by ARC-R012; ARC-R013 issued no duplicate model call.
- Primary metric: transition from `MAX_TOKENS`/empty final text to non-`MAX_TOKENS` with non-empty final text.
- Secondary diagnostics: input/thought/candidate/total tokens, runtime, finish reason, visible text, parseability and provider response structure.
- Success threshold: non-empty visible final text and finish reason other than `MAX_TOKENS` under the 8192-token treatment.
- Falsification: treatment remains `MAX_TOKENS` with no final text while comparator identity remains matched.

## Evidence provenance

ARC-R012 trigger commit `5d3a05f5f0b96ce9fac4c2ae6a2409999a40e29b` had been intentionally left unaudited at its cutoff to avoid duplicate inference. During ARC-R013, durable treatment evidence was found at `lab/recon/gemma-output-budget-ablation-latest.json`. GitHub Actions bot persisted that evidence in commit `1d5de993efb38580d7dcce1e1869b9576eab36b5`.

The evidence records `cache_hit=false` and request fingerprint `3b5a9d4a9d9a93ab8168a5046ab9c9e5e74244c8ee8add434de4241992e75779`. ARC-R013 did not issue any new target-model call.

## Frozen comparator

ARC-R011 comparator (`max_output_tokens=2048`):

- input tokens: 2,982;
- thought tokens: 2,045;
- candidate/output tokens: 0;
- total tokens: 5,027;
- runtime: 43.2723 s;
- visible text chars: 0;
- parsed grid: none;
- finish reason: `MAX_TOKENS`.

## 8192-token treatment result

The matched treatment (`max_output_tokens=8192`) records:

- input tokens: 2,982;
- thought tokens: 8,189;
- candidate/output tokens: none reported / no final candidate emitted;
- total tokens: 11,171;
- runtime: 172.106133682 s;
- visible text chars: 0;
- parsed grid: none;
- finish reason: `MAX_TOKENS`;
- candidate structure: one thought part, `thought=true`, 14,886 text characters internally, no persisted thought text, no visible final response.

The treatment therefore fails the declared success threshold and directly satisfies the falsification condition.

## Matched resource delta

Relative to the 2048 comparator, the treatment used:

- identical input tokens: 2,982 -> 2,982;
- +6,144 thought tokens: 2,045 -> 8,189;
- +6,144 total tokens: 5,027 -> 11,171;
- +128.833833682 s runtime: 43.2723 -> 172.106133682;
- unchanged visible final output: 0 -> 0 characters;
- unchanged parseability: no grid -> no grid;
- unchanged finish class: `MAX_TOKENS` -> `MAX_TOKENS`.

The extra generation allowance was consumed entirely by additional thinking rather than producing final candidate tokens. The exact +6,144 thought-token increase equals the increase in configured output allowance from 2,048 to 8,192.

## Score and regression accounting

This experiment is a single-request mechanism ablation, not a complete ARC task evaluation. No ARC task solve or exact task-accuracy score is claimed because no visible candidate grid was emitted and the full task/two-attempt contract was not executed.

- ARC solves attributable to treatment: 0 claimed.
- New solves versus comparator: 0.
- Regressions versus comparator: 0 scorable tasks; both requests are unscorable due to absent final candidate.
- Public-evaluation exposures: 0.
- 31B calls: 0.
- Fresh ARC-R013 target-model calls: 0.
- Audited treatment call inherited from ARC-R012: 1.

## Failure analysis

The 8192 treatment rules out the simple explanation that the 2048 cap was merely a little too small. On the same request, increasing the response budget by exactly 6,144 tokens caused Gemma to consume exactly 6,144 additional thought tokens and still terminate `MAX_TOKENS` without a final candidate.

This strengthens the diagnosis that the baseline's current generation configuration permits built-in thinking to expand until the response cap is exhausted. Merely increasing `max_output_tokens` is therefore not a viable baseline repair at 8192 and is highly cost-inefficient on this request.

The earlier 16k input-token-per-minute throughput issue remains separate. The input size here stayed fixed at 2,982 tokens; this experiment tests generated-token exhaustion, not input TPM.

## Adversarial review

This result does **not** prove Gemma cannot solve ARC, nor that every task will always consume the full thought budget. It falsifies one specific treatment on one matched deterministic request. A larger cap could eventually permit a final answer, but the observed exact budget-following behavior gives no evidence of convergence and would multiply latency/cost. Promoting an even larger cap without a new controlled hypothesis would be unjustified.

A more discriminating next experiment should change only thinking behavior/configuration while holding the model, prompt, task identity, sampling and a bounded output budget fixed, if the authorized Gemma API exposes a reproducible thinking-control setting. If no such control is available for this model/API path, the next shift should establish that limitation before altering prompt protocol or model routing.

The finding could also reflect provider-specific Gemma 4 serving behavior, so mature architecture work still requires hosted/offline parity testing per `MODEL-PARITY.md`; that is not tested in this run.

## Result

**REJECT** the `max_output_tokens=8192` treatment as a repair for the empty-output baseline failure. It quadruples the thought allowance/runtime scale on the audited request without producing any visible candidate, parseable grid or scoreable ARC output.

`T0002-GEMMA-BASELINE` remains incomplete because the frozen baseline still cannot produce scoreable final outputs under the current configuration.

## Next task

Continue only `T0002-GEMMA-BASELINE`. Before another full baseline chunk, perform one matched single-request experiment that tests a supported Gemma thinking-control mechanism as the sole model-facing variable, or durably establish that the authorized API exposes no usable thinking control. Keep task `00dbd492`, prompt SHA, model `gemma-4-26b-a4b-it`, sampling and public-training-only leakage discipline fixed. Do not mix in 31B routing, prompt changes, provider changes or public evaluation in that same experiment.

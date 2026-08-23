# ARC-R011 — Gemma empty-output root-cause diagnostic

Task: `T0002-GEMMA-BASELINE`
Role: `llm-experimenter`
Verdict: **INCONCLUSIVE** for baseline completion; empty-output cause isolated.

## Contract

- Hypothesis: the frozen `max_output_tokens=2048` budget is consumed by Gemma thought tokens before any visible candidate text is emitted.
- Comparator: frozen `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, deterministic public-training-derived `dev_validation`, exact scorer.
- Primary treatment: response telemetry only. Prompt, model, sampling and generation cap are unchanged.
- Live diagnostic set: one request, deterministic `dev_validation` task `00dbd492`, test index 0, attempt index 0.
- Prompt SHA-256: `aefa22e7984e5bcf94f7c213cf3634db4b824d48f61ad3088ebd3fd9196bb578`.
- Request fingerprint: `326a31f97f67f825d62a1be1dc5d121f2d9b55bdb3b3b537248a625f3e128058`.
- API budget: one fresh model call; public evaluation was not accessed.
- Falsification: normal candidate text/tokens exist despite empty extraction, or thought usage is materially below the cap with a different finish reason.

## Implementation

`src/arc_lab/target_model.py` now records sanitized response telemetry: prompt/candidate/thought/total token counts, candidate finish reason, and structural part metadata. It does not persist model thought text or signature values.

`tests/test_response_diagnostics.py` verifies that the telemetry captures counts and structure without persisting thought content. The GitHub Actions diagnostic workflow runs the test suite before the live request.

`src/arc_lab/empty_output_diagnostic.py` reuses the exact baseline prompt builder and frozen generation settings and writes evidence to `lab/recon/gemma-empty-output-latest.json`.

## Live result

The fresh matched request returned:

- model `gemma-4-26b-a4b-it`, provider version `001`;
- input tokens **2,982**;
- thought tokens **2,045**;
- candidate/output tokens: none reported;
- total tokens **5,027**;
- runtime **43.2723 s**;
- visible text length **0**;
- parsed grid: none;
- finish reason **`MAX_TOKENS`**;
- one returned part marked `thought=true`, with no final visible candidate.

This directly supports the hypothesis: the 2048 generation budget is exhausted before a final candidate answer is emitted. The adapter is not dropping an available final candidate in this request.

## Historical cache audit

ARC-R010 artifact `9487805832` (`sha256:1265c30c29616943bc005ccead464236ae2f408a43db0420f9597894732c5436`) was re-audited across all 113 cached responses. For **113/113**, `total_tokens - input_tokens = 2,045` exactly and visible text length is zero. Aggregate generated-but-not-visible usage is **231,085 tokens**, exactly **2,045 per request**.

Combined with the fresh response's explicit `thoughts_token_count=2045` and `MAX_TOKENS`, this explains the 113/113 empty-output cluster.

## Resource accounting

ARC-R011 used **1 fresh call**, **0 cache hits**, **2,982 input tokens**, **2,045 thought tokens**, **0 observed candidate tokens**, **5,027 total tokens**, and **43.2723 s** provider runtime.

No ARC score, new solve or regression is claimed because this was one failure-diagnostic request, not a completed task evaluation.

## Failure analysis and adversarial review

The correctness blocker is now per-request generation budget allocation to thoughts, separate from the earlier input-TPM throughput issue. The result does not prove that increasing `max_output_tokens` alone will produce a correct final answer or establish an optimal budget. It does, however, make an SDK text-extraction bug or RPM/TPM failure an implausible explanation for this empty-output cluster.

## Next experiment

Continue only `T0002-GEMMA-BASELINE`. Before resuming full-split accumulation, run a matched ablation on the same deterministic request that changes exactly one generation variable: increase `max_output_tokens` while holding model, prompt and sampling fixed, and test whether the response transitions from `MAX_TOKENS`/thought-only to a non-empty final candidate. Do not mix 26B/31B routing into that ablation and do not access public evaluation.

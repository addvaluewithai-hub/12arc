# ARC-R003 — Verify Gemma execution path

Task: `T0001A-GEMMA-EXECUTION-PATH`
Role: `llm-experimenter`
Verdict: **INFRA_ONLY — SUCCESS**

## Hypothesis

The provider-neutral Gemma execution path is fundamentally functional, and the remaining blocker from ARC-R002 is in smoke-test observability/configuration rather than missing API authorization. A race-safe, structurally validated smoke harness using the documented Gemma 4 sampling profile and sufficient output budget should produce durable evidence of one live `gemma-4-26b-a4b-it` generation followed by deterministic cache reuse.

## Frozen comparator

ARC-R002 implementation at the start of this shift:

- provider-neutral `TargetRequest` / `TargetResponse` / `CachedTargetClient`;
- Google Gen AI provider adapter;
- `GEMINI_API_KEY` supplied only through GitHub Actions secrets;
- deterministic SHA-256 request cache;
- smoke workflow requiring an exact response phrase and pushing evidence from a potentially stale checkout;
- `max_output_tokens=64`, `temperature=0.0`.

No ARC task or public-evaluation data was used in this run.

## Primary treatment

Harden the execution-path verification harness so its success criterion matches the infrastructure task: verify the requested provider model through `models.get`, require a non-empty live generation, require deterministic identical-request cache reuse, persist sanitized usage/runtime metadata, and make evidence persistence robust to concurrent branch advancement.

Diagnostic sub-steps were applied sequentially so each observed failure reduced uncertainty:

1. Make evidence persistence race-safe and persist sanitized failure outcomes.
2. Replace brittle exact-echo validation with structural model/generation/cache validation.
3. Move to Google's documented Gemma 4 sampling profile: `temperature=1.0`, `top_p=0.95`, `top_k=64`.
4. After durable evidence showed 25 input / 86 total tokens but no visible candidate text with a 64-token output cap, change only `max_output_tokens` from 64 to 256.

Current Google documentation used during the shift:

- Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Gemini API release notes confirming `gemma-4-26b-a4b-it` availability: https://ai.google.dev/gemini-api/docs/changelog
- Models API: https://ai.google.dev/api/models

## Task set / leakage

Task set: one synthetic non-benchmark infrastructure prompt with task ID `non-benchmark-smoke`.

ARC development split: not invoked.
Public ARC evaluation: not accessed.
ARC score: not applicable and not claimed.

## Execution accounting

Five smoke workflow executions were triggered by sequential execution-path commits in this shift. Each smoke execution performs at most one live provider generation and then repeats the identical request through the deterministic cache; therefore this shift used 5 live Gemma generations and 5 cache lookups.

Observable detailed metadata:

- Diagnostic 64-token run (`run_id=32601713417`): requested/resolved `gemma-4-26b-a4b-it`; model catalog name `models/gemma-4-26b-a4b-it`, version `001`; input tokens 25; candidate output tokens unavailable; total tokens 86; live runtime 1.7468 s; cache hit verified; visible text absent.
- Successful 256-token run (`run_id=32601740375`): requested/resolved `gemma-4-26b-a4b-it`; model catalog name `models/gemma-4-26b-a4b-it`, version `001`; input tokens 25; output tokens 5; total tokens 186; live runtime 3.8003 s; second identical request was a cache hit; visible text present.

Exact token/runtime details for the earliest diagnostic runs are not recoverable from their sanitized evidence because the pre-validation metadata persistence was added later in this same shift. No values are fabricated.

## Verification evidence

Durable sanitized evidence: `lab/recon/gemma-smoke-latest.json`.

Final successful workflow source commit: `120b8a28631e3e0ecb4718e174e3dc9fb50df941`.
Final successful workflow run: `32601740375`.
Final job conclusion: `success`.
Unit test step in the successful workflow: passed.

Final evidence records:

- `verified_live_call: true`;
- `cache_verified: true`;
- requested model `gemma-4-26b-a4b-it`;
- resolved model `gemma-4-26b-a4b-it`;
- provider catalog name `models/gemma-4-26b-a4b-it`, version `001`;
- non-empty live text, with content redacted from Git;
- deterministic second-call cache hit;
- generation profile `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=256`.

## Failure analysis

ARC-R002's missing evidence had at least one real observability defect: its workflow could commit from a stale checkout and lose a push race against concurrent lab-state commits. ARC-R003 fixed this by checking out the latest remote branch before applying and pushing sanitized evidence.

The first live ARC-R003 call proved API authorization and provider reachability but failed the exact-phrase assertion. Removing that non-contractual assertion exposed the deeper issue: with the small 64-token cap, the provider reported 86 total tokens from a 25-token prompt but no visible candidate text. Increasing only the output cap to 256 produced 5 visible output tokens and a successful structural smoke.

## Adversarial review

A successful hosted smoke does not prove hosted/offline behavioral parity, ARC reasoning quality, or benchmark accuracy. The 256-token smoke result also does not prove that 256 is an optimal ARC generation budget; it only falsifies the claim that the 64-token cap is sufficient for this hosted smoke configuration. The inference that hidden/non-candidate generation consumed the smaller budget is supported by the usage pattern but was not directly instrumented as a separate thought-token field, so it should not be treated as a fully identified mechanism.

The final workflow used the authorized hosted Gemini API and therefore remains an R&D execution path, not the final offline competition path. `MODEL-PARITY.md` still applies before architecture maturity claims.

## Result

`T0001A-GEMMA-EXECUTION-PATH` success criterion is satisfied. The live provider model identifier is verified, the secret is not committed, request/cache accounting is durable, the non-ARC call generated visible text, and an identical second request hit the deterministic cache.

Next eligible task: `T0002-GEMMA-BASELINE` on the frozen public-training-derived development split. This run stops here and does not execute that task.

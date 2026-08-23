# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. The verified Gemma smoke evidence remains `lab/recon/gemma-smoke-latest.json`; do not repeat it unless execution-path code changes or debugging requires it.

`ARC-R009` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE** for benchmark completion. It did not claim an ARC score.

The baseline solver protocol remains frozen as `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache, exact full-task scoring, and all 174 deterministic `dev_validation` tasks. Public evaluation remains sealed.

ARC-R009 audited ARC-R008 run `32614602241` to completion. It restored the cumulative cache successfully, added 15 unique responses, then failed again on Gemini free-tier input-token-per-minute quota (`16000`, model dimension `gemma-4-26b`, RetryInfo about 15 seconds). Its run-namespaced artifact is `9486671723`.

The 72-response cumulative artifact contains 235,416 recorded input tokens, 382,656 total tokens and 3,122.048 seconds aggregate provider runtime. Relative to the prior 57-response cache, the run added 63,742 input tokens, 94,417 total tokens and 650.373 seconds runtime. All 72 cached responses have empty visible `text`; recorded candidate/output tokens total zero. Observed single-request input-token counts range 248..9,634. Do not convert this partial attempt-level evidence into ARC task accuracy.

ARC-R009's single treatment is quota-paced bounded execution. `CachedTargetClient` now supports a provider-neutral minimum interval between starts of uncached live calls; cache hits bypass the wait. The hosted baseline sets `ARC_TARGET_MIN_LIVE_CALL_INTERVAL_SECONDS=61`, and the baseline process is timeboxed at 42 minutes inside the 55-minute job so cache-save/outcome steps can still execute. Exit code 124 is durably classified as `partial_timebox`. Prompt, model, generation settings, output budget, scoring, task split, attempt policy and request fingerprints are unchanged.

Deterministic unit coverage was added for pacing, cache-hit bypass and invalid negative intervals. In paced run `32617284889`, the workflow unit-test step passed, the pinned public-training-only fetch passed, and cumulative Actions-cache restore succeeded; fallback artifact seeding was skipped because a cache existed.

The request commit for the current paced run is `7ded98e4a328dadfd1e435e76254faba6f9c66fe`. Its durable start breadcrumb records `min_live_call_interval_seconds=61.0`, the correct fixed model/protocol/split and 174 tasks. At ARC-R009 cutoff run `32617284889` remained in the frozen baseline step.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. **Do not trigger another baseline while run `32617284889` is active.** First inspect that run, `lab/recon/gemma-baseline-latest.json`, its log and its run-namespaced cache artifact. The immediate test is whether the paced run avoids the same input-token-per-minute 429 and grows cache beyond 72. If it ends `partial_timebox` with monotonic cache growth and no quota 429, continue the exact same frozen protocol. If it still hits the quota, determine whether the offending individual request itself exceeds 16,000 input tokens before changing any solver-facing variable. Keep the empty-response cluster separate.

Full run record: `lab/runs/2026-08-23/ARC-R009.md`.

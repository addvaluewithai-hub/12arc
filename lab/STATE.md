# ARC Research Lab — Current State

Updated: 2026-08-23 07:16 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R009**
Next research run: **ARC-R010**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The solver protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring. ARC-R009 changed only hosted execution pacing/timeboxing, not solver-facing behavior.

## ARC-R009 findings

ARC-R009 first audited ARC-R008 run `32614602241` to completion. The run restored the cumulative cache and grew it from 57 to 72 unique responses before again terminating on Gemini free-tier `generate_content_free_tier_input_token_count` quota `16000` for model dimension `gemma-4-26b`. The run's cache save, outcome breadcrumb and artifact upload all succeeded.

Artifact `9486671723` contains 72 unique cached responses with 235,416 input tokens, 382,656 total tokens and 3,122.048 seconds aggregate provider runtime. It added 15 unique responses, 63,742 input tokens, 94,417 total tokens and 650.373 seconds runtime beyond the prior 57-response cache. All 72 visible texts are empty and recorded candidate/output tokens total zero. Observed per-request input tokens range from 248 to 9,634. This remains partial attempt-level evidence, not an ARC score.

ARC-R009 implemented a single quota-pacing treatment: uncached live request starts can be spaced by the provider-neutral cached client, the hosted baseline sets the minimum interval to 61 seconds, cache hits do not consume a live slot, and the baseline process is timeboxed at 42 minutes inside the 55-minute job so post-run cache persistence has time to execute. Exit code 124 is recorded as `partial_timebox`. Prompt/model/sampling/output budget/scoring/task split/request fingerprints are unchanged.

Request commit `7ded98e4a328dadfd1e435e76254faba6f9c66fe` launched one observed paced run, `32617284889`. Its start breadcrumb records the correct frozen protocol and `min_live_call_interval_seconds=61.0`. At ARC-R009 cutoff the job had passed setup, checkout, install, unit tests, start breadcrumb, pinned public-training-only fetch and Actions-cache restore; fallback artifact seeding was skipped because a cumulative Actions cache was found. The frozen baseline step remained in progress.

Verdict: **INCONCLUSIVE** for T0002 completion. The quota-pacing treatment is implemented and under live test, but no completed paced-run resource artifact or full ARC score exists yet.

## Current bottleneck

Do not issue another baseline request while run `32617284889` is active. When it completes, inspect `lab/recon/gemma-baseline-latest.json`, the job log and its run-namespaced cache artifact. The immediate falsifiable question is whether the 61-second pacing avoids the same input-token-per-minute 429 and grows the cumulative cache beyond 72 responses. A `partial_timebox` outcome with monotonic cache growth and no quota 429 supports continuing the exact frozen protocol.

If the same quota 429 occurs, determine whether the offending individual prompt itself exceeds the 16,000-token free-tier allowance before changing any solver-facing variable. Keep the 72/72 empty-visible-response cluster separate from quota debugging.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R010. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

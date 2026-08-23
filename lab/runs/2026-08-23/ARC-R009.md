# ARC-R009 — Quota-paced resumable Gemma baseline

Task: `T0002-GEMMA-BASELINE`
Role: `llm-experimenter`
Verdict: **INCONCLUSIVE**

## Contract

- Hypothesis: the frozen `direct-json-v1` baseline can avoid the observed Gemini free-tier `16,000` input-token/minute failure mode if uncached live request starts are separated by at least 61 seconds, while a process-level timebox preserves enough job budget for cumulative cache persistence.
- Frozen comparator: ARC-R008 execution behavior and completed run `32614602241`, which restored the cumulative cache successfully but made unpaced live calls until a `429 RESOURCE_EXHAUSTED` failure.
- Primary treatment: quota-paced, bounded execution only. `direct-json-v1`, prompt construction, model, sampling, output budget, split, scorer, request fingerprints and two-attempt policy remain unchanged.
- Target model: `gemma-4-26b-a4b-it`.
- Generation: `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`.
- Task set: all 174 deterministic `dev_validation` tasks derived from the pinned 1000-task public-training corpus with seed `arc-lab-v1`; public evaluation was not fetched or inspected.
- Attempts: exactly two per test input.
- Execution treatment: minimum 61 seconds between starts of uncached live requests; baseline process timebox 42 minutes inside a 55-minute job so post-run cache save/outcome persistence can still run.
- Primary metric: exact full-task accuracy after a complete 174-task run.
- Secondary diagnostics: cumulative cache growth, quota-failure class, calls/tokens/runtime, parse failures and empty visible responses.
- Success threshold for T0002: durable complete result for all 174 tasks with exact score and complete resource accounting.
- Falsification for the ARC-R009 treatment: a paced run still hits the same input-token-per-minute 429, fails to restore/save cumulative cache, or shows no monotonic cache growth.

## Evidence audited before treatment

ARC-R008 run `32614602241` completed after the prior shift. Checkout, setup, installation, unit tests, public-training-only fetch, cache restore/seed, cache save, outcome persistence and artifact upload all succeeded. The frozen baseline step failed on Gemini API `429 RESOURCE_EXHAUSTED` for `generativelanguage.googleapis.com/generate_content_free_tier_input_token_count`, quota value `16000`, model dimension `gemma-4-26b`, with RetryInfo requesting roughly 15 seconds.

The durable outcome breadcrumb records `cache_file_count=72`, proving that ARC-R008's cumulative resume/save treatment made monotonic progress beyond the prior 57-response cache.

Artifact `9486671723` from run `32614602241` was audited locally and contains:

- 72 unique cached response files;
- 235,416 recorded input tokens;
- 382,656 recorded total tokens;
- 3,122.048 seconds aggregate provider runtime;
- 0 recorded candidate/output tokens;
- 72/72 responses with empty visible `text`;
- observed per-request input-token range 248..9,634.

Relative to the prior 57-response artifact, run `32614602241` added 15 unique responses, 63,742 input tokens, 94,417 total tokens and 650.373 seconds provider runtime before the quota failure. These are partial attempt-level execution diagnostics, not an ARC score.

The near-constant provider runtime in the 72 cached responses remains consistent with the previously observed empty-visible-output cluster. ARC-R009 deliberately does not alter prompt, output budget or response parsing while quota pacing is under test.

## Treatment implemented

`src/arc_lab/target_model.py` now supports provider-neutral minimum spacing between uncached live request starts inside `CachedTargetClient`. Cache hits bypass the live-call wait and do not consume a pacing slot. Negative intervals are rejected.

`src/arc_lab/baseline.py` reads `ARC_TARGET_MIN_LIVE_CALL_INTERVAL_SECONDS` and passes it to the cached target-model client. The value is recorded in a completed result when one is eventually produced; no request fingerprint or generation setting includes or changes because of pacing.

`tests/test_target_model.py` adds deterministic fake-clock coverage showing that:

1. two uncached calls separated by only 43 seconds wait the remaining 18 seconds under a 61-second interval;
2. an intervening cache hit does not consume a live-call slot;
3. negative pacing intervals are rejected.

`.github/workflows/gemma-baseline.yml` sets the hosted baseline interval to 61 seconds and wraps only the baseline process in a 42-minute `timeout`, leaving the job-level timeout at 55 minutes. Exit code `124` is durably classified as `partial_timebox` rather than conflated with provider failure. Solver-facing behavior remains frozen.

## Live treatment evidence at shift cutoff

Request commit `7ded98e4a328dadfd1e435e76254faba6f9c66fe` launched exactly one observed paced baseline run: `32617284889`.

Its durable start breadcrumb records:

- `protocol=direct-json-v1`;
- `model=gemma-4-26b-a4b-it`;
- `split=dev_validation`;
- `task_count=174`;
- `min_live_call_interval_seconds=61.0`;
- trigger SHA `7ded98e4a328dadfd1e435e76254faba6f9c66fe`.

At ARC-R009 cutoff the job had successfully completed setup, checkout, installation, the unit-test step, start-breadcrumb persistence, pinned public-training-only fetch and cumulative Actions-cache restore. The fallback artifact-seed step was skipped, which is expected and confirms an Actions cache was restored. The frozen baseline step was `in_progress`.

No ARC-R009 model-call/token/runtime totals are claimed yet because the paced live step has not produced a completed audit artifact. No ARC accuracy, solves, regressions or parse-failure totals are claimed.

## Failure analysis

Primary execution failure before treatment is now well isolated: the cumulative cache machinery works, but unpaced execution repeatedly terminates on the provider's free-tier input-token-per-minute limit.

The 72-response artifact shows a maximum observed single-request input size of 9,634 tokens, below the 16,000-token/minute quota. A 61-second start interval therefore guarantees that no two requests of the already-observed size class start inside one 60-second window. This is the basis for the treatment, not a claim that every remaining unseen request is below 16,000 tokens.

Secondary failure cluster: all 72 durable responses have empty visible text while total token usage is non-zero. That cluster is now stronger than in ARC-R008 but remains intentionally untreated in this run. It may later require a separate controlled experiment on thinking/output budget or response-channel handling after execution can progress reproducibly.

## Adversarial review

Pacing may fail if a remaining individual prompt itself exceeds the provider's 16,000-token free-tier allowance; spacing cannot fix a single-request quota violation. It may also be overly conservative and increase wall-clock cost. The 42-minute process timebox is an orchestration safeguard, not evidence that 42 minutes is optimal.

The current live run being active is not evidence that the quota problem is solved. The treatment is supported only if the completed run avoids the same 429 and preserves monotonic cache growth (or completes the baseline). The next shift must inspect the completed run log and run-namespaced cache artifact before drawing that conclusion.

The empty-response cluster could ultimately yield a very low exact score, but partial attempt caches cannot be converted into task accuracy because the complete two-attempt, all-test-input contract has not been satisfied.

## Resource accounting

New target-model execution directly completed and attributable to ARC-R009 at cutoff: **not yet auditable**, because run `32617284889` is still executing. No new call/token/runtime count is claimed.

Audited cumulative evidence entering the treatment: 72 unique live responses, 235,416 input tokens, 382,656 total tokens, 3,122.048 seconds provider runtime, 0 candidate/output tokens and 72 empty visible texts.

## Next task

Continue `T0002-GEMMA-BASELINE` only. Do not issue another baseline request while run `32617284889` is active. First inspect its final `lab/recon/gemma-baseline-latest.json`, job log and run-namespaced cache artifact. The immediate falsifiable question is whether the paced run avoids the input-token-per-minute 429 and grows the cumulative cache beyond 72 responses. If it ends as `partial_timebox` with monotonic cache growth and no quota 429, continue the exact same frozen protocol in a later shift. If the same 429 occurs, inspect whether the offending request itself exceeds the free-tier per-minute token limit before changing any solver-facing variable. Keep the empty-response cluster separate.

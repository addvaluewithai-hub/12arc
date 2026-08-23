# ARC-R008 — Quota-resumable frozen Gemma baseline

Task: `T0002-GEMMA-BASELINE`
Role: `llm-experimenter`
Verdict: **INCONCLUSIVE**

## Contract

- Hypothesis: the frozen `direct-json-v1` baseline can make monotonic progress under the Gemma free-tier input-token quota if each workflow run restores the most recent request cache, seeds from the best prior artifact when no Actions cache exists, saves an updated cumulative cache, and prevents concurrent duplicate runs.
- Frozen comparator: ARC-R007 workflow behavior; no cross-run cache restoration, workflow-source pushes could trigger a duplicate run, and both observed runs started from empty cache.
- Primary treatment: quota-resumable execution orchestration only. `direct-json-v1`, prompt construction, model, sampling, output budget, task split, scorer and two-attempt policy are unchanged.
- Target model: `gemma-4-26b-a4b-it`.
- Generation: `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`.
- Task set: all 174 deterministic `dev_validation` tasks derived from the pinned 1000-task public-training corpus with seed `arc-lab-v1`; public evaluation was not fetched or inspected.
- Attempts: exactly two per test input.
- Metric: exact full-task accuracy after a complete 174-task run; secondary diagnostics are cache growth, calls/tokens/runtime and parse failures.
- Success threshold: a durable complete result for all 174 tasks with exact score and resource accounting.
- Falsification: cumulative cache cannot be restored/saved reliably, duplicate execution still occurs, or quota failure repeats without monotonic cache growth.

## Evidence audited before treatment

ARC-R007 left two real GitHub Actions runs: `32612153608` and `32612165079`. Both completed `failure` after checkout/setup/tests/training-only fetch and entry into the frozen baseline step.

Run `32612165079` failed with `429 RESOURCE_EXHAUSTED` for `generativelanguage.googleapis.com/generate_content_free_tier_input_token_count`, quota value `16000`, model dimension `gemma-4-26b`; provider RetryInfo requested roughly 31 seconds. Its uploaded request-cache artifact `9486315025` contained 57 JSON responses. Local audit of that artifact found:

- 57 unique cached request fingerprints;
- 171,674 recorded input tokens;
- 288,239 recorded total tokens;
- 2,471.675 seconds aggregate provider runtime;
- 0/57 responses with non-empty visible `text`.

Run `32612153608` uploaded artifact `9485867589` with 6 cache files. All six fingerprints are already contained in the 57-file artifact, so duplicate-run cache evidence adds no unique requests. The duplicate remains a cost/concurrency confound, but the unique durable partial baseline cache is 57 requests, not 63.

These are partial-execution diagnostics only. They do not establish an ARC score. In particular, the 57 empty visible responses are a failure cluster, not 57 task failures: requests are attempts, tasks can have multiple tests/attempts, and the run did not complete.

## Treatment implemented

Commit `342af8c1716091de09922cf4cc2977423dd0cb35` changes only `.github/workflows/gemma-baseline.yml` orchestration:

1. push triggering is restricted to `lab/triggers/gemma-baseline.request`; editing the workflow itself no longer launches a second baseline;
2. workflow concurrency uses one `gemma-baseline-${{ github.ref }}` group with `cancel-in-progress: false`;
3. `actions/cache/restore@v4` restores the newest cumulative request cache by prefix;
4. when no Actions cache exists, `actions/download-artifact@v4` seeds `/tmp/arc-baseline-cache` from the best prior 57-response artifact (`run 32612165079`);
5. `actions/cache/save@v4` saves the cumulative cache under a run-unique key after the baseline step;
6. outcome breadcrumbs now record `cache_file_count`;
7. the audit artifact is run-ID-namespaced to avoid ambiguity.

No solver-facing Python code, prompt, scorer, model identifier, generation setting, task selection or attempt count changed.

A single request was issued in commit `ed9e1cd011bece32c4e3bef7cd72beab12a348a3`.

## Live treatment evidence at shift cutoff

GitHub Actions run `32614602241` is the only observed ARC-R008 baseline run. Its durable start breadcrumb identifies the expected trigger SHA, model, protocol, 174-task split and `status=running`.

The workflow job had already completed successfully through checkout, Python setup, install, 23 unit tests, start-breadcrumb persistence, pinned public-training-only fetch, cumulative cache restore, and seed download from the 57-response prior artifact. The frozen baseline step was `in_progress` at cutoff. No second concurrent ARC-R008 run was observed.

Because the run had not completed, ARC-R008 claims no new Gemma calls, tokens, runtime, exact score, solves, regressions or parse-failure count. The treatment has verified the previously untested restore/seed path, but not yet the save/growth/completion half of the hypothesis.

## Failure analysis

Primary historical execution failure: provider free-tier input-token-per-minute quota. The previous workflow discarded useful progress between runs, making quota failures non-monotonic and encouraging repeated spend.

Secondary observed cluster: all 57 cached responses have empty visible text even though token usage is non-zero. This may reflect output-budget exhaustion, response-channel/SDK behavior, or model behavior; it is not safe to infer which without preserved finish/thought metadata. It must be investigated only after the baseline can progress reproducibly, or as a separately controlled treatment.

## Adversarial review

The new cache machinery does not itself prove the baseline will finish. A 55-minute job may still hit 429 repeatedly, and the successful restore/seed steps do not prove the post-run cache will be larger than 57 files. The seed artifact contains provider outputs generated under the exact same model/prompt/config fingerprints, so reuse is methodologically valid; however, if provider behavior changed despite identical identifiers, cache reuse intentionally freezes the earlier responses and measures the declared cached protocol rather than fresh nondeterminism.

The empty-response cluster could eventually make the exact baseline score very low or zero, but no such score is claimed until all task attempts are durably accounted for.

## Resource accounting

New target-model execution directly evidenced as completed during ARC-R008: **0 calls / 0 tokens / 0 runtime claimed** at cutoff because the live step was still running and no completed accounting artifact existed.

Prior partial-cache evidence audited: 57 unique live responses, 171,674 input tokens, 288,239 total tokens, 2,471.675 seconds provider runtime. Output-token field was `null` in those cache records, so no invented output-token total is reported.

## Next task

Continue `T0002-GEMMA-BASELINE` only. First inspect run `32614602241` and `lab/recon/gemma-baseline-latest.json`. Do not issue another request while that run is active. If its cumulative cache grows beyond 57 files, the monotonic-progress hypothesis gains support and the next shift should continue the exact frozen protocol. If it does not, isolate cache-save or quota behavior as the next single orchestration variable. Do not start T0003 until T0002 has a complete audited result.

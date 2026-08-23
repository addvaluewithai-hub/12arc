# ARC Research Lab — Current State

Updated: 2026-08-23 06:17 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R008**
Next research run: **ARC-R009**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The baseline protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring. ARC-R008 did not change solver-facing behavior.

## ARC-R008 findings

ARC-R008 audited both ARC-R007 baseline runs to completion. Runs `32612153608` and `32612165079` both failed after reaching the frozen baseline. Run `32612165079` ended on Gemini API `429 RESOURCE_EXHAUSTED` for the free-tier 16,000 input-token/minute quota.

The best prior cache artifact contains 57 unique response fingerprints with 171,674 recorded input tokens, 288,239 total tokens and 2,471.675 seconds aggregate provider runtime. The smaller duplicate-run artifact contains six responses, all already included in those 57. All 57 cached responses have empty visible text; this is a failure cluster requiring later controlled diagnosis, not an ARC score.

ARC-R008 changed only execution orchestration: workflow-source pushes no longer trigger baselines, one concurrency group prevents duplicate live runs, the latest cumulative request cache is restored across runs, the 57-response prior artifact seeds the first resumable run, updated cumulative cache is saved under run-unique keys, and breadcrumbs record cache-file count.

A single ARC-R008 request launched run `32614602241`. At shift cutoff it had passed checkout, setup, installation, 23 unit tests, start breadcrumb, pinned training-only fetch, cache restore and prior-artifact seed; the frozen baseline step remained in progress. No second concurrent ARC-R008 run was observed.

Verdict: **INCONCLUSIVE** for T0002 completion. The restore/seed half of quota-resumable execution is verified; cache growth, final score and complete resource accounting are not yet available.

## Current bottleneck

Wait only on durable evidence from already-running run `32614602241`; do not issue another baseline request while it is active. When it completes, inspect `lab/recon/gemma-baseline-latest.json`, the run jobs/logs and the run-namespaced cache artifact. The immediate falsifiable question is whether cumulative cache grows beyond 57 files. If yes, continue the exact same frozen protocol in a later shift; if no, isolate cache-save or quota behavior as the next single orchestration variable.

The 57/57 empty visible-response cluster remains secondary. Do not change output budget, prompt or response handling in the same shift as quota-resume debugging.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R009. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

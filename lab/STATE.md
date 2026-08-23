# ARC Research Lab — Current State

Updated: 2026-08-23 05:12 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R007**
Next research run: **ARC-R008**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The baseline protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints and exact full-task scoring. ARC-R007 did not change this protocol.

## ARC-R007

ARC-R007 changed only orchestration observability. `.github/workflows/gemma-baseline.yml` now persists `lab/recon/gemma-baseline-latest.json` at execution start and baseline outcome, independently of whether the final benchmark succeeds.

This resolved the prior ambiguity: GitHub Actions scheduling is functional. Run `32612153608` passed checkout, Python setup, installation, unit tests, breadcrumb persistence and the pinned public-training-only fetch, then entered the frozen baseline step. Run `32612165079` also reached the frozen baseline step.

The second run was an accidental duplicate caused by both the workflow-file treatment commit and an explicit request commit matching push triggers. This is recorded as a negative orchestration result and potential duplicate API-spend confound. No cancellation action was available through the connected GitHub surface.

At ARC-R007 evidence cutoff both runs were still in progress. Therefore no ARC score, target-model calls/tokens/runtime, solves, parse failures, new solves or regressions are claimed.

Verdict: **INCONCLUSIVE** for T0002 completion, but the scheduling uncertainty is resolved.

## Current bottleneck

Obtain and audit durable completion evidence from the already-running frozen baseline jobs. Do not issue another baseline trigger while either run remains active. If they complete, audit the result for all 174 tasks, two-attempt policy, exact scoring, parsing failures, cache accounting, calls/tokens/runtime and per-attempt records. If they fail, use the new durable outcome evidence/logs to isolate the remaining failure.

Before any later trigger, add duplicate-run protection (for example workflow concurrency and/or removal of workflow-source push triggering) without changing `direct-json-v1`.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R008. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has durable complete evidence.

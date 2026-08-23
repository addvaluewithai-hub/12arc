# ARC Research Lab — Current State

Updated: 2026-08-23 03:05 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R005**
Next research run: **ARC-R006**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The first baseline protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints and exact full-task scoring. ARC-R005 did not change this protocol.

## ARC-R005

ARC-R005 tested only the orchestration hypothesis: a workflow-file-only commit (`7fa357f23bbb0c3a3f435810925ecb403e15e0b9`) should fire the existing push-path trigger without changing the solver. `lab/results/ARC-R004-baseline.json` was absent before the trigger and remained absent during the shift observation window. The connected GitHub surface does not expose repository-wide push-triggered run discovery, so no workflow success/failure or target-model result could be verified.

Verdict: **INCONCLUSIVE**. No ARC score, target-model call count, token count, runtime, new solves or regressions are claimed.

## Current bottleneck

Obtain durable complete execution evidence for the frozen 174-task baseline. Distinguish scheduling/trigger suppression, quota/runtime, and workflow failure without modifying the frozen model/prompt/scoring protocol.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R006. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until the baseline is complete.

# ARC Research Lab — Current State

Updated: 2026-08-23 04:15 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R006**
Next research run: **ARC-R007**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The baseline protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints and exact full-task scoring. ARC-R006 did not change this protocol.

## ARC-R006

ARC-R006 made one orchestration repair: `.github/workflows/gemma-baseline.yml` now accepts pushes to the dedicated `lab/triggers/gemma-baseline.request` path, and request commit `b3e9270e4863d42b734414c643c7b44101f4fe90` was issued. Result-path pushes are not triggers, preventing persistence loops.

`lab/results/ARC-R004-baseline.json` was still absent in the shift observation window, and the connected GitHub status surface exposed no status contexts for the request commit. Therefore no workflow execution result or Gemma benchmark evidence is inferred.

Verdict: **INCONCLUSIVE**. No ARC score, target-model calls/tokens/runtime, new solves or regressions are claimed.

## Current bottleneck

Obtain durable complete execution evidence for the frozen 174-task baseline. The trigger mechanism is now decoupled from workflow-source edits; remaining uncertainty is Actions scheduling/permissions, runtime/quota, or execution failure.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R007. First audit the durable result if it appears; otherwise inspect Actions evidence if available. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked.

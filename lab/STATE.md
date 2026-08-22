# ARC Research Lab — Current State

Updated: 2026-08-23 02:14 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R004**
Next research run: **ARC-R005**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was previously verified in ARC-R003.

## ARC-R004 baseline preparation

ARC-R004 froze the first direct target-model baseline protocol as `direct-json-v1` and committed:

- `src/arc_lab/baseline.py` for leakage-safe prompt construction, strict grid parsing, exact task scoring, two attempts per test input and full request/token/runtime accounting;
- `tests/test_baseline.py` for parser and no-test-output-in-prompt invariants;
- `.github/workflows/gemma-baseline.yml`, which fetches only pinned upstream public training data, explicitly excludes evaluation data, and runs all 174 deterministic `dev_validation` tasks with `gemma-4-26b-a4b-it`;
- deterministic request fingerprints and a workflow cache artifact, plus durable per-task raw outputs/results when execution succeeds.

Frozen generation settings for this baseline are `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`; two attempts are made for each test input.

## Current bottleneck

The baseline execution result did not become visible during ARC-R004. `lab/results/ARC-R004-baseline.json` was absent when checked and no commit status/check was exposed for the workflow-triggering commit. Therefore ARC-R004 is `INCONCLUSIVE`: no ARC score, target-model call count, token count or runtime is claimed.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R005. Confirm or launch the committed baseline workflow, obtain the complete frozen-validation result and audit parsing/request accounting. Mark it done only with durable complete evidence. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked.

# ARC Research Lab — Current State

Updated: 2026-08-23 00:02 EEST
Phase: **PHASE 0 — infrastructure + benchmark discipline**
Latest completed research run: **ARC-R001**
Next research run: **ARC-R002**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark state

`T0001-BENCHMARK-HARNESS` is complete.

- Official ARC-AGI-2 source metadata is pinned to upstream commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`.
- The 1000 public-training task IDs are committed with source/blob/hash metadata.
- Deterministic seed `arc-lab-v1` produces 707 development-train, 174 development-validation and 119 development-holdout tasks.
- Grid validation enforces ARC values and 1..30 dimensions.
- Exact two-attempt scoring distinguishes per-test-output accuracy from full-task success.
- The normal development command accepts only the training directory; CI is configured to sparse-checkout and validate the pinned training corpus without the public-evaluation directory.
- Local implementation tests passed: 16/16. No Gemma inference and no ARC performance claim occurred in ARC-R001.

## Current bottleneck

A repository secret for Gemini has been configured by the operator, but the lab still needs a provider-independent Gemma execution adapter, deterministic request cache/accounting and a live non-benchmark smoke test before target-model benchmarking.

## Next task

`T0001A-GEMMA-EXECUTION-PATH`.

`T0002-GEMMA-BASELINE` remains blocked until that path is verified.

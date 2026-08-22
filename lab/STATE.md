# ARC Research Lab — Current State

Updated: 2026-08-22 21:46 EEST
Phase: **PHASE 0 — infrastructure + benchmark discipline**
Latest completed research run: **none**
Next research run: **ARC-R001**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark policy

- Development/tuning: deterministic splits derived only from the 1000 public ARC-AGI-2 training tasks.
- Public evaluation: sealed milestone-only signal, never a per-experiment feedback loop.
- Exact outputs only; two attempts are tracked explicitly when applicable.

## Current bottleneck

The repository was just initialized. We need a deterministic local benchmark/split harness before any prompt or reasoning-architecture experiment can be trusted.

## Next task

`T0001-BENCHMARK-HARNESS`.

No ARC performance claim exists yet.

# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R028 closed — agenda generated from ARC-R027 evidence

`T0013-RESEARCH-AGENDA-GENERATION` is complete and ARC-R028 is released. This shift made **zero target-model calls** and did not use public evaluation.

ARC-R027 remains the evidence basis: `0607ce86` and `06df4c85` repeatedly terminate candidate generation with `finish_reason=length` in both ARC-R020 and ARC-R021 under the existing full-grid candidate serialization path. This is a pre-verification failure layer distinct from parseable-but-wrong semantic candidates.

## Next eligible task: T0014-RULE-FIRST-SERIALIZATION-HARNESS

Execute exactly this task next.

Role: **program-synthesis-researcher**.

Objective: build a compact, versioned, machine-parseable rule/program candidate representation plus deterministic executor, fail-closed validator, candidate-oracle integration and comparator-integrity integration. No target-model calls are permitted in T0014.

Protocol: `lab/experiments/T0014-rule-first-serialization-harness.json`.

Frozen local comparator for the later experiment is ARC-R020 on task IDs `0607ce86` and `06df4c85`. Do not encode task-specific solutions into the IR or tests. T0014 succeeds only when a durable validation marker demonstrates deterministic parsing/execution, fail-closed invalid programs, exact-score integration, matched task-set enforcement and zero target-model calls.

T0014 should also establish the authorized push-triggered GitHub Actions execution path needed by T0015, using repository `NVIDIA_API_KEY` only inside Actions and never exposing the secret.

## Follow-up after T0014 only: T0015-RULE-FIRST-OVERFLOW-ABLATION

T0015 is intentionally blocked until T0014 is complete and its execution path is declared in the queue.

Its predeclared hypothesis changes only candidate serialization: compact rule/program hypotheses instead of materialized grids, on `0607ce86` and `06df4c85`, using `deepseek-ai/deepseek-v4-flash-0731` and the matched ARC-R020 generation controls including the **3072-token candidate-stage budget**.

Success: **2/2 parseable and >=1/2 exact candidate coverage** after deterministic execution. Falsification: either task remains unparsable/length-terminated, or both parse and remain **0/2** exact coverage.

Protocol: `lab/experiments/T0015-rule-first-overflow-ablation.json`.

Adversarial caveat: two tasks are only a local diagnostic; do not generalize a router from them unless a later experiment replicates the effect on a predeclared broader slice.

Durable ARC-R028 artifacts:

- `lab/results/ARC-R028-research-agenda.json`
- `lab/runs/2026-08-25/ARC-R028.md`
- `lab/experiments/T0014-rule-first-serialization-harness.json`
- `lab/experiments/T0015-rule-first-overflow-ablation.json`

No active reservation should remain after closure. Next unallocated run is **ARC-R029**.

Public evaluation remains sealed.

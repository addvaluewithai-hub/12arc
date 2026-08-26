# ARC-R037 — T0022A multi-candidate critique/verify harness

## Task and role

- Task: `T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS`
- Role: `reasoning-systems-inventor`
- Type: no-model infrastructure/research
- Public evaluation: sealed / unused

## Hypothesis

A deterministic harness can make multi-candidate generation, critique, repair and Python selection measurable and safely executable through the authorized NVIDIA GitHub Actions path without treating model self-judgment as evidence.

## Primary change

Added the multi-candidate architecture boundary only: candidate-batch parsing/deduplication, deterministic execution/ranking, critique/repair provenance, resource accounting, a cached experiment runner, and a push-triggered NVIDIA workflow for the subsequent T0022 experiment.

Frozen controls: existing schema-v1/schema-v2 executors, exact Python judging, public-training-only development discipline, routine model `deepseek-ai/deepseek-v4-flash-0731`. No target-model calls occurred in this run.

## Implementation

Durable code/evidence:

- `src/arc_lab/multi_candidate.py`
- `src/arc_lab/multi_candidate_experiment.py`
- `tests/test_multi_candidate.py`
- `.github/workflows/t0022-multi-candidate.yml`
- `lab/validation/T0022A-multi-candidate-harness.json`
- `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`

The deterministic selector orders candidates by exact training consistency, number of exact training pairs, cell-error distance, structural violations, normalized program cost, and deterministic fingerprint tie-break. Model confidence and critique text do not enter ranking.

The future T0022 runner freezes four model phases: generate 16 candidates, critique, critique-the-critique, and repair up to 8 candidates. Every candidate is reparsed and reexecuted in Python. Identical provider/model/prompt/settings/task/attempt requests reuse the existing target-model cache.

## Verification

GitHub Actions CI run `32918156374` on commit `378103e667752b8250ed88495b05838d8aa34969` completed successfully. Job `98026103360` passed:

- install;
- `pytest -q` including the new multi-candidate tests;
- policy validation;
- deterministic development-split reproduction;
- pinned public-training-only corpus validation with evaluation absent.

An earlier CI run `32918134983` also passed after the runner commit.

## Result

Verdict: **INFRA_ONLY / PASS**.

- target-model requests: 0
- target-model tokens: 0
- provider failures: 0
- benchmark score: not applicable to this harness-only run
- public evaluation used: false

The T0022 target-model experiment now has an actually available push-triggered execution path that validates the active task claim and run reservation before provider access.

## Adversarial interpretation

Passing harness tests does not show that multi-candidate reasoning improves ARC accuracy. The selector's cell-error and separator-preservation diagnostics are engineering observables, not proof that the candidate language is expressive enough. T0022 must still test proposal diversity against the frozen comparator on `06df4c85`, with complete request/token/runtime/failure accounting.

## Next task

Unblock `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP` as the next ready task with the execution path and exact generation contract now frozen. Do not start it in ARC-R037.

# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R036 closed — semantic closure diagnostic

`T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT` completed with zero target-model calls using permitted public ARC-AGI-2 training data only. Public evaluation was not used.

Durable evidence:

- `lab/results/ARC-R036-overlap-semantic-closure.json`
- `lab/executions/ARC-R036.json`
- `lab/runs/2026-08-26/ARC-R036.md`

Verdict: **DOMINANT_FAILURE_MECHANISM_IDENTIFIED**.

Mechanical result on `0607ce86` with all ARC-R035 solver semantics frozen:

- deeper execution failures: **216**;
- dominant failure: **216/216 = 100% `separator_structure_lost`**;
- exact exception: `ValueError: lattice inference requires at least two regions`;
- best reachable training-pair cell-error total: **134**, from depth-0 identity (`52 + 39 + 43`);
- best depth-1 transformed state: **164** total cell errors;
- exact training-consistent program within depth 4: none;
- target-model calls: **0**.

Interpretation: the shared-overlap treatment from ARC-R035 made first-step variable-region operations executable, but the operator family is not closed under repeated application because mutations can destroy separator topology and later operations re-infer partitions from the mutated pixels. This is a proven transition blocker, not proof that topology persistence alone solves the task. Identity being the closest state is adverse evidence against overclaiming semantic sufficiency.

## Next ready task: T0022A multi-candidate harness

The next executable step in the operator-requested multi-candidate direction is `T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS`.

This is a no-model infrastructure/research task. Build and test:

- candidate-batch manifests;
- normalized-IR deduplication;
- critique and critique-of-critique/repair provenance;
- deterministic Python candidate execution/scoring and selector ranking;
- cache/request/token/runtime accounting;
- a claim/reservation-validating push-triggered NVIDIA workflow for T0022.

Protocol: `lab/experiments/T0022A-multi-candidate-critique-verify-harness.json`.

Do not claim target-model results in T0022A. The point is to make the architecture measurable and give `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP` an actually available external execution path as required by RUNNER.md.

## Blocked next experiment: T0022 multi-candidate critique/verify loop

After T0022A passes, unblock T0022 and run the generate -> critique -> critique-the-critique -> repair -> Python verify/select experiment.

Preferred initial task: `06df4c85`. ARC-R032 already produced executable lattice programs there but they were exact-wrong, making it a clean target for proposal diversity and Python selection without mixing in the `0607ce86` separator-topology blocker.

Protocol: `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`.
Design: `lab/design/MULTI-CANDIDATE-CRITIQUE-VERIFY.md`.

Core rule: the model proposes; Python judges. Model critique is not evidence. If the first variant fails, evolve one variable at a time: candidate diversity prompt, critic prompt, critique-of-critique, repair budget, IR translation constraints, or deterministic selector ranking.

## Adjacent T0023 matched semantic follow-up

ARC-R036 predeclared exactly one matched semantic ablation for its dominant failure mechanism: `T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION`.

Protocol: `lab/experiments/T0023-persistent-lattice-topology-ablation.json`.

It changes only partition persistence for `0607ce86`: infer the variable-span separator topology once from each original input and retain it across subsequent peer-reduction steps. Keep the 27 parameterizations, shared-overlap alignment, state deduplication and max depth 4 frozen.

T0023 is blocked so it does not silently replace the multi-candidate architecture direction. Success requires both removal of the separator-loss blocker and an exact training-consistent program; blocker removal without an exact program is partial only.

Public evaluation remains sealed.

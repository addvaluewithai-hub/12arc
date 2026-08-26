# ARC-R036 — T0021 Overlap Semantic Closure Audit

## Role

failure-analyst

## Task and protocol

- Task: `T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT`
- Protocol: `lab/experiments/T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT.json`
- Baseline/comparator: ARC-R035 shared-overlap alignment search
- Task set: public ARC-AGI-2 training task `0607ce86` only
- Public evaluation: sealed / not used
- Target-model calls: 0
- Primary change: diagnostics only; ARC-R035 solver semantics remained frozen

## Result

Verdict: **DOMINANT_FAILURE_MECHANISM_IDENTIFIED**.

The durable diagnostic recorded 216 deeper execution failures. All 216/216 (100%) had the exact exception `ValueError: lattice inference requires at least two regions` and were classified as `separator_structure_lost`.

The deterministic near-miss ranking also showed that the best reachable state by total training-pair cell error was the depth-0 identity state itself at 134 errors (`[52, 39, 43]`). The best depth-1 treatment state was worse at 164 errors. Therefore the present 27 peer-reduction operators do not merely fail late; under this metric their nearest explored transformations move away from the target before separator loss terminates many deeper paths.

No exact training-consistent program was found within the frozen max depth 4 search.

## Interpretation

ARC-R035 successfully removed the unequal-shape alignment blocker, but it exposed a deterministic closure defect: lattice topology is inferred again from the mutated grid after each operation. Some first-step peer reductions overwrite/destroy separator structure, so subsequent lattice operations cannot reconstruct the original region partition.

This is a dominant reproducible mechanism, but it is not proof that fixing topology persistence will make `0607ce86` expressible. The fact that identity is the closest reachable state is adverse evidence against assuming separator persistence alone will solve the task.

## Adversarial interpretation

A 100% failure taxonomy can overstate causal sufficiency: `separator_structure_lost` explains why those 216 transitions terminate, not why no exact program exists. Cell-error distance can also be semantically misleading. Any follow-up must therefore change exactly one mechanism and preserve ARC-R035 controls.

## Predeclared matched follow-up ablation

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` is predeclared as the single matched semantic follow-up from T0021 evidence. It will change only the partition source: infer separator-defined region topology once from the original input and carry that immutable topology across subsequent peer-reduction steps instead of re-inferring from mutated separator pixels. All 27 operator parameterizations, variable-span handling, shared-overlap alignment, task `0607ce86`, state deduplication, and max depth 4 remain frozen.

Success requires eliminating the separator-loss transition blocker and finding an exact training-consistent program; blocker removal without an exact program is a partial result, not promotion.

## Strategic architecture direction

The operator-requested `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP` remains the intended next active architecture task after this closure. It tests a separate uncertainty: whether diversified model proposals plus critique/repair and deterministic Python selection can recover candidates that one-shot model generation misses. Prefer its first target `06df4c85`; keep Python execution/scoring as the judge.

## Durable evidence

- `lab/results/ARC-R036-overlap-semantic-closure.json`
- `lab/executions/ARC-R036.json`
- `lab/experiments/T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT.json`

No model outputs, scores, CI outcomes, or evaluation evidence were invented in this closure.

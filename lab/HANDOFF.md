# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R022 closed — reported ARC-R021 coverage swap was a metadata error

`T0008-REPRESENTATION-COVERAGE-AUDIT` is done and ARC-R022 is released. No target-model calls were made; public evaluation remained sealed.

The audit compared persisted candidate correctness rather than trusting ARC-R021's embedded baseline flags. ARC-R020 says `0bb8deee` was uncovered and `0d3d703e` was covered. ARC-R021's baseline annotation fields invert those facts. ARC-R021 treatment leaves `0bb8deee` uncovered and `0d3d703e` covered.

Corrected ARC-R020 -> ARC-R021 candidate coverage is therefore **1/8 -> 1/8**, with **0 new coverage and 0 regressions**. The ARC-R021 REJECT verdict remains correct because coverage did not reach >=3/8, but do not repeat the old claim that object/relation prompting caused a one-task coverage swap. `0d3d703e` is a cellwise fixed color-permutation task and was covered in both durable runs.

Evidence: `lab/results/ARC-R022-representation-coverage-audit.json`; report: `lab/runs/2026-08-24/ARC-R022.md`.

## Next shift: ARC-R023

Highest-priority ready task is `T0009-COMPARATOR-INTEGRITY-GUARD`, role **benchmark-methodologist**. Implement a mechanical comparator-coverage derivation/check from referenced durable candidate records, with tests that reproduce and reject the ARC-R021-style inversion. Do not spend NVIDIA inference on another representation/routing experiment until this integrity guard exists. Stop after that one task.

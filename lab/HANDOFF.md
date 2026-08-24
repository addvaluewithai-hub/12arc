# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R023 closed — comparator integrity guard added

`T0009-COMPARATOR-INTEGRITY-GUARD` is done and ARC-R023 is released. No target-model calls were made and public evaluation remained sealed.

The new `src/arc_lab/comparator_integrity.py` derives task-level candidate coverage from persisted candidate correctness, rejects annotations that disagree with that durable evidence, and computes new-covered/regressed task IDs only on matched task maps. `tests/test_comparator_integrity.py` includes the exact class of inversion found by ARC-R022: durable facts `0bb8deee=false`, `0d3d703e=true` versus inverted manual labels. That inversion must raise `ValueError`.

A narrow CI workflow was added for the guard tests. The connector in ARC-R023 could not enumerate generic push workflow runs, so do not retroactively claim CI success without checking GitHub Actions evidence.

Report: `lab/runs/2026-08-24/ARC-R023.md`.

## Next shift: ARC-R024

Highest-priority ready task is `T0010-INTEGRITY-GUARD-INTEGRATION`, role **benchmark-methodologist**. Integrate the guard into shared architecture experiment reporting so experiment runners cannot silently bypass it with manual comparator labels. Add an integration test proving inverted comparator metadata cannot reach persisted new-solve/regression fields. Do not spend NVIDIA inference on another architecture variant in that shift. Stop after that one task.

# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R024 closed — comparator integrity is mandatory at shared reporting boundary

`T0010-INTEGRITY-GUARD-INTEGRATION` is done and ARC-R024 is released. No target-model calls were made and public evaluation remained sealed.

`src/arc_lab/architecture_reporting.py` now builds candidate-coverage deltas only by loading a referenced durable comparator result and deriving both comparator/treatment maps through `comparator_integrity`. It has no manual comparator-coverage argument. Task-set mismatch raises before report persistence. Integration tests live in `tests/test_architecture_reporting.py`.

Do not claim CI success for ARC-R024: the available connector returned no workflow run for the final test commit. The implementation and executable tests are durable; this is recorded rather than hidden.

Report: `lab/runs/2026-08-24/ARC-R024.md`.

## Next shift: ARC-R025

Highest-priority ready task is `T0011-CANDIDATE-FAILURE-TAXONOMY`, role **failure-analyst**. Use persisted ARC-R020/ARC-R021 candidate evidence and the new mechanical reporting discipline to classify uncovered tasks by observable transformation/morphology features. Derive at least one falsifiable candidate-generator routing or representation hypothesis with exact task IDs and adversarial alternatives. This is deliberately a no-model-call audit; do not spend NVIDIA inference in that shift. Stop after that one task.

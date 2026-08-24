# ARC-R024 — Mandatory comparator integrity integration

Task: `T0010-INTEGRITY-GUARD-INTEGRATION`
Role: **benchmark-methodologist**
Verdict: **INFRA_ONLY**
Public evaluation used: **no**
Target-model calls/tokens/runtime: **0 / 0 / 0**

## Hypothesis

If shared architecture reporting has no API surface for manual comparator coverage and instead derives comparator coverage from a referenced durable candidate result, the ARC-R021 class of inverted baseline annotations cannot reach persisted new-covered/regressed fields.

## Primary change

Added `src/arc_lab/architecture_reporting.py`. `build_candidate_coverage_report` requires a persisted comparator result path and treatment result, derives both task maps through `comparator_integrity`, and computes deltas only after exact task-set matching. `persist_candidate_coverage_report` validates before writing output.

Added `tests/test_architecture_reporting.py` covering durable comparator derivation, inability of a manual inversion narrative to override persisted delta fields, and fail-before-write behavior for mismatched task sets.

## Falsification / evidence

The integration would be falsified if callers could pass manual baseline coverage into the shared report builder, or if mismatched task sets could produce persisted deltas. The implemented API exposes no manual coverage parameter and calls the ARC-R023 mechanical derivation/delta guard before persistence.

GitHub connector workflow enumeration returned no run for the final test commit, so this shift does **not** claim CI execution success. The code and executable integration tests are durable in Git; a later shift may verify CI if needed without changing the result semantics.

## Adversarial interpretation

This prevents the specific metadata path that caused ARC-R021's false coverage-swap narrative, but experiment runners must actually use the shared reporting helper. Future architecture runners should be migrated to this helper rather than hand-assembling task-level comparator deltas.

## Result

Success test satisfied at the shared reporting boundary: comparator coverage is referenced/derived rather than manually supplied, and integration tests encode the inversion and mismatched-task failure modes. No NVIDIA inference was needed.

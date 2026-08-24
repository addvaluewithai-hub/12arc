# ARC-R023 — Comparator integrity guard

Task: `T0009-COMPARATOR-INTEGRITY-GUARD`  
Role: **benchmark-methodologist**

## Hypothesis

If comparator candidate coverage is reconstructed mechanically from persisted per-candidate `candidate_correct` evidence, then an ARC-R021-style manual inversion cannot silently enter new-solve/regression accounting.

## Primary change

Added `src/arc_lab/comparator_integrity.py` with three guarded operations:

1. derive task coverage only from persisted candidate correctness and parse evidence;
2. reject manual annotations that disagree with that durable map;
3. compute new-covered/regressed IDs only from matched comparator/treatment maps.

No target-model behavior, prompt, split, scoring rule, or model setting changed. No NVIDIA calls were made and public evaluation was not used.

## Falsification / tests

Added `tests/test_comparator_integrity.py`. The fixture reproduces the corrected ARC-R020 facts for the pair implicated by ARC-R022: `0bb8deee=false`, `0d3d703e=true`. A deliberately inverted annotation (`0bb8deee=true`, `0d3d703e=false`) must raise `ValueError`. Additional tests cover correct annotations, mechanical delta accounting, parse-failure conservatism, and mismatched task sets.

A narrow GitHub Actions workflow (`comparator-integrity.yml`) was added to execute exactly this test file on relevant pushes. The connector available in this shift could create the workflow but could not enumerate generic push-triggered workflow runs, so no CI-success claim is fabricated here. The guard and executable regression tests are durable in Git; future CI exposes any implementation error immediately.

## Result

**PASS at implementation/invariant level.** Future architecture code now has a reusable mechanical derivation/check rather than relying on hard-coded baseline coverage labels. The exact ARC-R021-style inversion is represented as a failing test condition.

## Adversarial interpretation

This guard prevents one class of metadata corruption only when experiment code actually calls it. Existing historical result JSON remains unchanged and downstream experiment runners must import the guard rather than reintroduce manual comparator flags. A future integration should make the integrity check mandatory in shared experiment-report construction.

## Accounting

Target-model calls: 0. Tokens: 0. Model runtime: 0. Public evaluation exposures: 0.

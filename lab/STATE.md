# ARC Research Lab — Current State

Updated: 2026-08-24 10:25 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R023**
Next unallocated research run: **ARC-R024**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current bottleneck

Candidate generation/representation remains weak, but ARC-R022 showed that experiment metadata integrity must be hardened before interpreting task-level deltas. ARC-R023 addressed the immediate failure mode.

## ARC-R023 comparator integrity guard

Added `src/arc_lab/comparator_integrity.py`. Comparator candidate coverage can now be derived mechanically from persisted `candidate_correct` evidence; manual annotations can be checked and rejected on disagreement; new-covered/regressed IDs are computed only from matched maps.

Added `tests/test_comparator_integrity.py`, including an explicit ARC-R021-style inversion fixture (`0bb8deee` falsely covered / `0d3d703e` falsely uncovered) that must raise an integrity error. Added a narrow GitHub Actions workflow for this regression test. The available connector could not enumerate generic push-triggered workflow runs during the shift, so no CI-success claim is made; the executable guard/tests are durable in Git.

ARC-R023 used zero target-model calls, zero tokens and no public evaluation. Report: `lab/runs/2026-08-24/ARC-R023.md`.

## Next task

`T0010-INTEGRITY-GUARD-INTEGRATION` is ready for ARC-R024. Make the guard mandatory in shared architecture experiment reporting so future experiment code cannot bypass it by reintroducing hard-coded baseline flags. Stop after that one task.

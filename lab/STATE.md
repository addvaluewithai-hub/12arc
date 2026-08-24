# ARC Research Lab — Current State

Updated: 2026-08-24 10:55 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R024**
Next unallocated research run: **ARC-R025**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current bottleneck

Candidate generation/representation remains weak. Before further inference, experiment accounting has now been hardened against the ARC-R021 comparator-metadata inversion discovered by ARC-R022.

## ARC-R024 mandatory reporting integration

Added `src/arc_lab/architecture_reporting.py` as the shared candidate-coverage reporting boundary. It requires a referenced durable comparator result, mechanically derives comparator and treatment coverage through `comparator_integrity`, enforces identical task sets, and only then persists new-covered/regressed task IDs. There is no API parameter for manually supplied baseline coverage flags.

Added `tests/test_architecture_reporting.py` for durable comparator derivation, persisted delta integrity, and fail-before-write task-set mismatch behavior. The GitHub connector returned no workflow run for the final test commit, so ARC-R024 does not claim CI execution success; code/tests are durable in Git.

ARC-R024 used zero target-model calls, zero tokens and no public evaluation. Report: `lab/runs/2026-08-24/ARC-R024.md`.

## Next task

`T0011-CANDIDATE-FAILURE-TAXONOMY` is ready for ARC-R025. Use mechanically verified persisted ARC-R020/ARC-R021 candidate evidence to classify uncovered task morphologies and derive one falsifiable representation/routing hypothesis before spending more NVIDIA inference. Stop after that one task.

# ARC Research Lab — Current State

Updated: 2026-08-24 08:45 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R022**
Next unallocated research run: **ARC-R023**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, temperature 0, top_p 1, max_output_tokens 4096, one attempt/test. Public evaluation remains sealed.

## Current bottleneck

Candidate generation/representation remains weak: ARC-R020 measured 1/8 candidate-oracle coverage, and ARC-R021's object/relation prompt also produced 1/8. ARC-R022 discovered that ARC-R021's task-level baseline annotations were inverted for the only relevant pair, creating a false coverage-swap narrative.

## ARC-R022 audit correction

Durable ARC-R020 evidence shows `0bb8deee` **uncovered** and `0d3d703e` **covered**. ARC-R021 embedded baseline fields incorrectly marked `0bb8deee` covered and `0d3d703e` uncovered. ARC-R021 treatment itself left `0bb8deee` uncovered and `0d3d703e` covered.

Therefore the corrected matched candidate-coverage comparison is **1/8 -> 1/8**, with **0 new covered tasks and 0 regressions**. `0d3d703e`, a cellwise fixed color-permutation task, was covered in both runs. The ARC-R021 **REJECT** verdict remains valid because 1/8 is below its >=3/8 promotion threshold, but the previously claimed morphology-dependent coverage swap is invalid.

ARC-R022 used zero target-model calls and no public evaluation. Evidence: `lab/results/ARC-R022-representation-coverage-audit.json`; report: `lab/runs/2026-08-24/ARC-R022.md`.

## Next task

`T0009-COMPARATOR-INTEGRITY-GUARD` is ready for ARC-R023. Before spending more inference on morphology routing, make per-task comparator coverage mechanically derived from the referenced durable result and add tests that fail on ARC-R021-style annotation inversion. New-solve/regression narratives must not depend on manually supplied baseline labels.

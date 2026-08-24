# ARC Research Lab — Current State

Updated: 2026-08-24 07:35 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R021**
Next unallocated research run: **ARC-R022**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, temperature 0, top_p 1, max_output_tokens 4096, one attempt/test. Public evaluation remains sealed.

## Current bottleneck

Candidate generation/representation remains the bottleneck. ARC-R020 measured candidate-oracle coverage at only 1/8. ARC-R021 tested one controlled representation change: explicit compact object/relation reasoning before the same three-candidate generator.

## ARC-R021 result

**REJECT.** The treatment produced **1 newly candidate-covered task and 1 candidate-coverage regression**, so net candidate coverage remained **1/8 (12.5%)** rather than reaching the predeclared >=3/8 threshold. It also failed the requirement to preserve the previously covered case. There were zero provider failures, so the matched result is conclusive rather than infrastructure-confounded.

Accounting: 14 live calls, 0 cache hits, 37,364 input tokens, 14,112 output tokens, **51,476 total tokens**. Public evaluation was unused. Durable evidence: `lab/results/ARC-R021-object-relation-generator.json`; finalized report: `lab/runs/2026-08-24/ARC-R021.md`.

Interpretation: broad object-centric semantic scaffolding changed *which* task was covered but did not improve aggregate generator coverage. This does not falsify deterministic object extraction or morphology-aware routing; it rejects this universal prompt treatment on the frozen slice.

## Next task

`T0008-REPRESENTATION-COVERAGE-AUDIT` is ready for ARC-R022. Use only durable ARC-R020/R021 evidence to identify the newly covered and regressed tasks, classify their morphology and candidate-rule failure modes, and formulate a falsifiable routing/representation hypothesis before spending more target-model calls.

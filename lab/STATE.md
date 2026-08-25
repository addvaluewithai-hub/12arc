# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R032**
Next unallocated research run: **ARC-R033**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task and predeclared a generic lattice-region primitive family.

ARC-R032 tested that family under frozen ARC-R030 model/generation/scoring controls. The result was **REJECT**: 2/2 parseable but 0/2 exact candidate coverage, with 0 new coverage and 0 regressions. The run used 2 live NVIDIA calls, 14,526 input tokens, 419 output tokens, 57.807 s model runtime, 0 provider failures and 0 parse failures. Five normalized program ASTs were generated and `lattice_peer_reduce` appeared seven times, so the richer language was actually used.

Failure evidence splits the uncertainty further. `0607ce86` failed closed at execution with `inferred lattice cells must have equal size`, identifying a partition-model/validation-boundary mismatch. `06df4c85` produced executable lattice-peer programs but no exact candidate, leaving wrong generic semantics vs induction/search unresolved.

## Next research direction

Highest-priority follow-up: `T0018-SCHEMA-V2-EXPRESSIBILITY-ORACLE-AUDIT`.

Use **no target-model calls**. On permitted public-training pairs only, mechanically determine whether bounded generic schema-v2 programs can exactly fit the two diagnostic mappings under the same anti-overfit constraints (no task IDs, absolute task-specific coordinates, task-specific colors, or hand-entered target patterns).

Primary question: does an exact generic schema-v2 program exist for each training mapping? If no, representation semantics remain insufficient and the audit should isolate one generic missing/incorrect assumption. If yes, preserve that program only as oracle evidence and classify the live ARC-R032 failure primarily as induction/search rather than crediting a research-team program as a target-model solve.

Public evaluation remains sealed.

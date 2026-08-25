# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R031**
Next unallocated research run: **ARC-R032**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 audited the actual schema-v1 IR and permitted public-training mappings with zero target-model calls. Schema-v1 contains only identity, whole-grid rotations/flips, and global recolor. These compose into whole-grid spatial permutations plus global color substitutions and cannot express region-selective edits.

For `0607ce86`, training outputs selectively repair noisy occurrences inside a repeated/lattice-like structure while retaining other occurrences of the same colors. For `06df4c85`, separator-defined cells are selectively populated/propagated while other zeros and separators remain unchanged. Both mappings therefore require conditional region-level read/write semantics unavailable to schema-v1.

ARC-R031 classification: **2/2 missing generic DSL/IR expressivity** with high confidence. Search/induction weakness or prompt collapse may coexist, but current-schema search is incapable of producing an exact program for the observed mappings.

## Next research direction

Predeclared follow-up: `T0017-LATTICE-REGION-PRIMITIVE-ABLATION`.

Primary change only: add one generic lattice-region map/reduce family to the rule-first IR, supporting inferred repeated-cell partitions, peer aggregation, generic conditional writes, and canvas reassembly. No task IDs, absolute task coordinates, task-specific colors, or hand-entered target patterns are permitted.

Frozen matched comparator remains ARC-R030 on exactly `0607ce86` and `06df4c85`, DeepSeek V4 Flash via NVIDIA NIM, one attempt/test, temperature 0, top_p 1, no reasoning override, 3072 candidate output tokens, deterministic execution, exact candidate-oracle scoring, and comparator-integrity enforcement.

Success threshold: **2/2 parseable and >=1/2 exact candidate coverage**. If richer-IR outputs are 2/2 parseable but remain 0/2 coverage, the primitive-family sufficiency hypothesis is rejected and the bottleneck shifts toward induction/search or a different representation family.

Public evaluation remains sealed.

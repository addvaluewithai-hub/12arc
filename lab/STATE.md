# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R039**
Next unallocated research run: **ARC-R040**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with primary `deepseek-ai/deepseek-v4-flash-0731`. ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R038 attempted the first multi-candidate generate -> critique -> critique-the-critique -> repair -> Python-select loop on `06df4c85`, but it was operationally inconclusive: all 24 submitted records failed the executable IR parser, so no valid candidate reached critique or deterministic selection. Provider execution itself succeeded; the failure was the model-facing schema contract.

ARC-R039 completed `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR` as **INFRA_ONLY / PASS** with zero target-model calls. The only changed component was the generation/repair prompt-output contract and contract-validation instrumentation. Parser/executor semantics, normalization/deduplication, and Python ranking remained frozen.

The repaired contract now states exact schema-v1/v2 top-level keys, legal operators and parameter domains, integer `schema_version`, valid executable examples, and explicit prohibitions on the exact ARC-R038 malformed `instructions` and pseudocode `program` forms. Offline regression tests passed **10/10 parseable, 10 unique** representative fixtures through parse -> normalize -> deduplicate -> deterministic Python scoring; malformed ARC-R038 forms fail closed. GitHub Actions CI run `32937412114` passed pytest, policy validation, frozen development split reproduction, and pinned public-training-only validation. Validation artifact: `lab/validation/T0022B-schema-contract.json`.

This proves interface consistency offline, not model adherence. It does not claim that DeepSeek will follow the repaired contract or that candidate quality improved.

## Next active research direction

Highest-priority ready task: `T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN`.

Run exactly the matched T0022 rerun on public-training task `06df4c85` using NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. Freeze the four phases, 4-request maximum, temperatures/top-p/top-k/output-token budgets, deterministic parser/verifier, deduplication, Python ranking, and comparator context from ARC-R038. Change only the executable-IR contract injected into generation and repair prompts.

Operational gate: at least **8 parseable non-duplicate executable candidates**. Only after that gate may the run be interpreted as evidence about multi-candidate reasoning. Research progress is either at least one exact train-consistent candidate or a dominant mechanical failure/near-miss signal supporting exactly one next ablation.

Protocol: `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`.

## Adjacent semantic follow-up

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction. Public evaluation remains sealed.

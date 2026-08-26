# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R038**
Next unallocated research run: **ARC-R039**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task. ARC-R032 tested a richer lattice-region language but remained 0/2 exact coverage despite actual lattice program use.

ARC-R033 through ARC-R036 removed model induction from the `0607ce86` diagnostic path and isolated a dominant closure failure. ARC-R036 found all **216/216** deeper failures were `separator_structure_lost` with exact message `ValueError: lattice inference requires at least two regions`; identity remained the nearest reachable state at 134 cell errors. The matched persistent-topology follow-up remains predeclared as T0023 but intentionally blocked behind the multi-candidate direction.

ARC-R037 completed `T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS` as **INFRA_ONLY / PASS**, with zero target-model calls. It established fail-closed candidate parsing, normalized-IR deduplication, deterministic Python execution/ranking, critique/repair provenance, accounting, caching, and the authorized NVIDIA execution path.

ARC-R038 executed the first frozen multi-candidate experiment on `06df4c85`. The provider path itself worked: **4 NVIDIA requests**, **23,769 input tokens**, **2,156 output tokens**, **25,925 total tokens**, **466.0348 s runtime**, and **0 provider failures**. Public evaluation remained sealed.

However ARC-R038 is **INCONCLUSIVE / OPERATIONAL_CONTRACT_FAILURE**, not a research rejection. All **24/24 submitted candidate records failed the executable IR parser**. Generation returned natural-language `instructions` records; repair returned string `schema_version` plus pseudocode/natural-language `program` records. Therefore:

- parseable executable candidates: **0/24**;
- unique executable candidates: **0**;
- critique manifest: empty;
- critique-the-critique manifest: empty;
- deterministic best candidate: none.

The top-level result accounting reports zero response-level parse failures, but the verifier separately records 24 candidate-IR parse failures. These are different layers and must not be conflated.

Mechanically, candidate exact coverage remained 0/1 on `06df4c85`, matching ARC-R032, with 0 new solves and 0 regressions. This delta is not interpretable as an architecture result because the predeclared operational threshold of at least 8 parseable non-duplicate candidates was never reached.

Durable analysis: `lab/results/ARC-R038-contract-failure-analysis.json`.
Run report: `lab/runs/2026-08-26/ARC-R038.md`.

## Next active research direction

Highest-priority ready task: `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR`.

This is a **no-model infrastructure/research gate**. Change one thing only: the prompt/output schema contract between generation/repair and the existing deterministic parser. Do not spend new target-model calls yet.

Required outcome:

1. specify parser-supported schema-v1/v2 executable candidate examples in the model-facing contract;
2. make generation and repair response contracts machine-checkable;
3. add positive fixtures that survive parse → normalize → deduplicate → deterministic Python scoring;
4. add negative regression fixtures for the exact ARC-R038 malformed `instructions` records and string-version/pseudocode `program` records;
5. require at least **8 representative non-duplicate fixture candidates** to pass the full offline gate;
6. only then predeclare a matched T0022C rerun on exactly `06df4c85` with the same model/provider/comparator and multi-candidate architecture.

Protocol: `lab/experiments/T0022B-multi-candidate-schema-contract-repair.json`.

The intended research direction remains multi-candidate generation + critique + repair + deterministic Python selection. ARC-R038 did not test that hypothesis cleanly because no executable candidates entered the loop.

## Adjacent matched semantic ablation

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction. It changes only partition persistence for `0607ce86`; blocker removal without an exact program counts only as partial progress.

Public evaluation remains sealed.

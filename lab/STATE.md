# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R037**
Next unallocated research run: **ARC-R038**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task. ARC-R032 tested a richer lattice-region language but remained 0/2 exact coverage despite actual lattice program use.

ARC-R033 through ARC-R036 removed model induction from the `0607ce86` diagnostic path and isolated a dominant closure failure. ARC-R036 found all **216/216** deeper failures were `separator_structure_lost` with exact message `ValueError: lattice inference requires at least two regions`; identity remained the nearest reachable state at 134 cell errors. The matched persistent-topology follow-up remains predeclared as T0023 but intentionally blocked behind the multi-candidate direction.

ARC-R037 completed `T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS` as **INFRA_ONLY / PASS**, with zero target-model calls. It added:

- fail-closed schema-v1/schema-v2 candidate parsing;
- normalized-IR fingerprints and deduplication;
- deterministic Python execution/scoring and ranking;
- cell-error and structural-preservation diagnostics;
- critique/repair provenance validation without treating critique as evidence;
- request/cache/token/runtime accounting;
- a resumable cached multi-candidate experiment runner;
- a claim/reservation-validating push-triggered NVIDIA workflow.

GitHub Actions CI run `32918156374` on commit `378103e667752b8250ed88495b05838d8aa34969` passed pytest, policy validation, deterministic split reproduction, and pinned public-training-only validation. Validation artifact: `lab/validation/T0022A-multi-candidate-harness.json`.

## Next active research direction

Highest-priority ready task: `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP`.

The first target is exactly `06df4c85` from permitted public ARC training data. The frozen architecture is:

1. generate exactly 16 distinct candidate programs;
2. score/deduplicate them in Python;
3. ask the model to critique up to 8 candidates using the mechanical metrics;
4. critique the critique;
5. repair up to 8 candidates;
6. reparse/reexecute all original and repaired candidates;
7. choose only by deterministic Python ranking.

The model is a proposal engine. Model confidence and critique text are never evidence and never enter ranking.

Protocol: `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`.
Execution path: `.github/workflows/t0022-multi-candidate.yml` via `lab/triggers/t0022-multi-candidate.request`.

Frozen model/provider: NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. The protocol freezes four requests and exact generation settings. Success requires at least 8 parseable non-duplicate candidates and either at least one exact train-consistent candidate or a dominant mechanical failure class supporting one next ablation.

If T0022 fails, evolve one variable at a time rather than repeat an unchanged loop: proposal diversity, critic prompt, critique-of-critique, repair budget, IR translation constraints, or deterministic selector ranking.

## Adjacent matched semantic ablation

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction. It changes only partition persistence for `0607ce86`; blocker removal without an exact program counts only as partial progress.

Public evaluation remains sealed.

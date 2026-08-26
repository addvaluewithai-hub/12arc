# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R036**
Next unallocated research run: **ARC-R037**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task and predeclared a generic lattice-region primitive family.

ARC-R032 tested that family under frozen ARC-R030 model/generation/scoring controls. The result was **REJECT**: 2/2 parseable but 0/2 exact candidate coverage, with actual `lattice_peer_reduce` use. `0607ce86` failed closed at equal-size lattice inference; `06df4c85` executed but remained exact-wrong.

ARC-R033 removed model induction from the loop with bounded deterministic oracle search over the implemented schema-v2 operator family. Neither diagnostic was expressible within the bounded reachable state graph.

ARC-R034 permitted variable-size separator spans but exposed a second equal-shape assumption in peer alignment.

ARC-R035 changed only alignment to shared overlap. This restored 27/27 valid first-step transitions and reached 798 unique states across 6,399 operator applications, but found no exact program and produced 216 deeper `ValueError` failures.

ARC-R036 kept ARC-R035 semantics frozen and diagnosed those failures. Result: **DOMINANT_FAILURE_MECHANISM_IDENTIFIED**. All **216/216** deeper failures were `ValueError: lattice inference requires at least two regions`, mechanically classified as `separator_structure_lost`. The closest reachable state by total training-pair cell error was the depth-0 identity state itself at **134** errors; the best depth-1 transformed state was worse at **164**. No target-model calls were made and public evaluation remained sealed.

Interpretation: ARC-R035 removed the shape/alignment blocker, but repeated lattice inference is not closed under its own mutations because some operations destroy separator topology before later steps. This explains transition termination, but not solution sufficiency; the near-miss ranking is adverse evidence that the current operator family may remain semantically wrong even after topology persistence.

## Next active research direction

The operator-requested architecture direction is the multi-candidate generate -> critique -> critique-the-critique -> repair -> Python verify/select loop. Before spending inference, the highest-priority ready task is `T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS`.

T0022A is a no-model infrastructure/research shift that must build and test:

- candidate-batch manifests and normalized-IR deduplication;
- critique and repair provenance without treating critique as evidence;
- deterministic Python execution/scoring and selector ranking;
- cache/request/token/runtime accounting schemas;
- a validated push-triggered NVIDIA execution path for the subsequent T0022 target-model experiment.

Protocol: `lab/experiments/T0022A-multi-candidate-critique-verify-harness.json`.

After T0022A passes, unblock `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP`. Prefer its first target `06df4c85`, because ARC-R032 already showed lattice programs executing there while remaining exact-wrong. The target model should generate many candidates and critiques, but deterministic Python remains the judge.

Durable direction artifacts:

- `lab/design/MULTI-CANDIDATE-CRITIQUE-VERIFY.md`
- `lab/experiments/T0022A-multi-candidate-critique-verify-harness.json`
- `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`

If the first T0022 loop variant fails, evolve one variable at a time: proposal diversity, critic prompt, critique-of-critique, repair budget, IR translation constraints, or deterministic selector ranking. Preserve matched comparators and do not repeat an unchanged failed prompt.

## Adjacent matched semantic ablation

ARC-R036 predeclared exactly one matched semantic follow-up for `0607ce86`: `T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION`.

It changes only the partition source: infer separator-defined variable-span topology once from the original input and carry that immutable topology across subsequent peer-reduction steps, rather than re-inferring from mutated separator pixels. Freeze the same 27 operator parameterizations, shared-overlap alignment, state deduplication, task, and max depth 4.

Protocol: `lab/experiments/T0023-persistent-lattice-topology-ablation.json`.

T0023 is intentionally blocked so it does not displace the multi-candidate direction. If/when run, eliminating separator-loss failures without an exact program counts only as partial progress.

Public evaluation remains sealed.

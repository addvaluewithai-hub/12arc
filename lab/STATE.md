# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R033**
Next unallocated research run: **ARC-R034**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task and predeclared a generic lattice-region primitive family.

ARC-R032 tested that family under frozen ARC-R030 model/generation/scoring controls. The result was **REJECT**: 2/2 parseable but 0/2 exact candidate coverage, with actual `lattice_peer_reduce` use. `0607ce86` failed closed at equal-size lattice inference; `06df4c85` executed but remained exact-wrong.

ARC-R033 then removed model induction from the loop with a bounded deterministic oracle search over the implemented schema-v2 operator family, using permitted public-training pairs only and zero target-model calls. Neither task was expressible within the bounded reachable state graph:

- `0607ce86`: 27/27 first-step operator applications failed validation; only the initial state was reachable. The immediate blocker is the equal-size lattice-span restriction.
- `06df4c85`: zero validation failures, 54 operator applications, two unique reachable states, no exact training-consistent program. Search depth is not the main issue because the reachable closure collapses quickly under the current peer-reduction semantics.

This shifts the dominant uncertainty from model induction to representation semantics.

## Next research direction

Highest-priority follow-up: `T0019-VARIABLE-SPAN-PARTITION-ABLATION`.

Change exactly one structural assumption on `0607ce86`: permit generic variable-size separator-defined lattice spans while freezing the existing 27 schema-v2 peer-reduction parameterizations and max search depth 4. No target-model calls.

Decision rule:

- exact training-consistent program found: partition restriction was sufficient to recover expressibility for this diagnostic;
- valid transitions but no exact program: partition blocker is removed, but region semantics remain insufficient;
- no valid transition: the partition-boundary diagnosis is falsified and another generic structural assumption must be isolated.

`06df4c85` remains a separate semantic-closure problem and should not be mixed into this one-variable ablation.

Public evaluation remains sealed.

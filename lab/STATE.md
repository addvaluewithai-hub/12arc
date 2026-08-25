# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R034**
Next unallocated research run: **ARC-R035**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task and predeclared a generic lattice-region primitive family.

ARC-R032 tested that family under frozen ARC-R030 model/generation/scoring controls. The result was **REJECT**: 2/2 parseable but 0/2 exact candidate coverage, with actual `lattice_peer_reduce` use. `0607ce86` failed closed at equal-size lattice inference; `06df4c85` executed but remained exact-wrong.

ARC-R033 removed model induction from the loop with bounded deterministic oracle search over the implemented schema-v2 operator family. Neither diagnostic was expressible within the bounded reachable state graph. On `0607ce86`, all 27 first-step applications failed the equal-size span validation boundary.

ARC-R034 isolated that boundary by permitting variable-size separator-defined spans while freezing all 27 peer-reduction parameterizations and max depth 4. The hypothesis was **falsified**: `0607ce86` still had 0 valid first-step transitions. All 27 operator applications failed with `IndexError`, leaving one reachable state. This exposes a deeper equal-shape assumption in relative-coordinate peer alignment: the reducer indexes every peer at coordinates derived from a reference region even when peer extents differ.

No target-model calls were made in ARC-R034. The dedicated GitHub Actions verification and oracle job succeeded, and public evaluation remained sealed.

## Next research direction

Highest-priority follow-up: `T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION`.

Keep variable-span separator inference, the existing 27 `lattice_peer_reduce` axis/reducer/write parameterizations, deterministic state-deduplicated BFS, max depth 4, and task `0607ce86` frozen. Change exactly one semantic assumption: peer reduction operates only on the shared overlap domain of the selected peer regions (minimum peer height/width), while cells outside that overlap remain unchanged.

Decision rule:

- valid first-step transition + exact training-consistent program: shared-overlap alignment is sufficient to restore expressibility for this diagnostic;
- valid transitions but no exact program: shape-alignment blocker is removed, but peer-reduction semantics remain insufficient;
- no valid first-step transition: shared-overlap alignment is falsified as the proximate remaining blocker.

`06df4c85` remains a separate semantic-closure problem and should not be mixed into this one-variable ablation.

Public evaluation remains sealed.

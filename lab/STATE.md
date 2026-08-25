# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R035**
Next unallocated research run: **ARC-R036**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R030 rejected compact serialization as a sufficient fix: on `0607ce86` and `06df4c85`, treatment became 2/2 parseable but exact candidate coverage remained 0/2 versus comparator 0/2.

ARC-R031 mechanically established that schema-v1 cannot express the selective region-level training mappings for either diagnostic task and predeclared a generic lattice-region primitive family.

ARC-R032 tested that family under frozen ARC-R030 model/generation/scoring controls. The result was **REJECT**: 2/2 parseable but 0/2 exact candidate coverage, with actual `lattice_peer_reduce` use. `0607ce86` failed closed at equal-size lattice inference; `06df4c85` executed but remained exact-wrong.

ARC-R033 removed model induction from the loop with bounded deterministic oracle search over the implemented schema-v2 operator family. Neither diagnostic was expressible within the bounded reachable state graph. On `0607ce86`, all 27 first-step applications failed the equal-size span validation boundary.

ARC-R034 permitted variable-size separator spans while freezing the 27 peer-reduction parameterizations and max depth 4. It still produced 0/27 valid first-step transitions: every operator failed with `IndexError`, exposing a second equal-shape assumption in relative-coordinate peer alignment.

ARC-R035 changed only that alignment assumption. Peer reduction now operates inside the shared overlap domain (minimum peer height/width), preserving non-overlap cells. This **removed the proximate execution blocker**: all **27/27** first-step applications became valid. The deterministic depth-4 search expanded **237** programs and reached **798** unique states across **6,399** operator applications. However, no exact training-consistent program was found. There were **216 `ValueError` execution failures** during deeper search. Verdict: **PARTIAL_ALIGNMENT_BLOCKER_REMOVED_SEMANTICS_INSUFFICIENT**.

No target-model calls were made in ARC-R035. GitHub Actions run `32847574881` passed claim/reservation validation, implementation tests, pinned-public-training fetch, bounded audit, and durable result persistence. Public evaluation remained sealed.

## Next research direction

Highest-priority follow-up: `T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT`.

Do not add another primitive from intuition yet. Keep the entire ARC-R035 solver semantics frozen and mechanically diagnose the remaining bounded state graph for `0607ce86`:

- classify all 216 execution failures by exact invariant/reason rather than exception class alone;
- retain program paths for reachable states;
- compute deterministic cell-error distance from each reachable multi-training state to the training targets;
- identify whether near-misses and failures support separator destruction, wrong overlap anchoring, or a missing region-local conditional semantic.

The task succeeds only if one dominant, reproducible mechanism is supported strongly enough to predeclare exactly one matched follow-up ablation. If the evidence stays ambiguous, record that ambiguity rather than inventing a primitive.

`06df4c85` remains a separate semantic-closure problem and should not be mixed into this diagnostic.

Public evaluation remains sealed.

# ARC-R041 — T0022D critique contract hardening

Date: 2026-08-26
Role: **reasoning-systems-inventor**
Task: `T0022D-CRITIQUE-CONTRACT-HARDENING`
Verdict: **INFRA_ONLY / PASS**
Public evaluation: **sealed / unused**
Target-model calls: **0**

## Question

Can the phase-level machine boundary that stopped ARC-R040 at `critique_parse_or_retry` be made exact and fail-closed, while preserving the executable candidate IR, executor, scorer and deterministic selector, and can the persisted ARC-R040 generation evidence traverse the remaining loop offline with mocked valid phase records?

## Prior evidence and hypothesis

ARC-R040 used NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b` under the repository failover policy. Four successful provider requests advanced executable candidate evidence into critique, but the critic and JSON recovery path failed the machine contract before critique-the-critique, repair or final deterministic selection. This was an operational interface failure, not evidence against the multi-candidate reasoning hypothesis.

Hypothesis for ARC-R041: exact record-level contracts for critique and critique-the-critique, plus exact correction instructions, are sufficient to remove the known offline interface ambiguity without loosening candidate/executor semantics.

## Treatment

Added `src/arc_lab/multi_candidate_phase_contract.py` with exact fail-closed validators.

Critique manifests must contain exactly top-level key `critiques`; every record must contain exactly `candidate_id`, `likely_failure`, `violated_training_pair`, `forbidden_constant_risk`, `separator_or_unchanged_region_risk`, and `repair_suggestion`. Candidate IDs are 64-character lowercase hexadecimal fingerprints, must be unique and may be checked against the mechanically known candidate set. Training-pair indices are non-negative JSON integers and may be range-checked. Required text fields must be non-empty.

Challenge manifests must contain exactly top-level key `challenges`; every record must contain exactly `candidate_id`, `critique_valid`, `reason`, and `smallest_general_repair`. Candidate IDs obey the same fingerprint/uniqueness constraints, `critique_valid` must be a JSON boolean, and text fields must be non-empty.

Added `src/arc_lab/multi_candidate_hardened.py`. It preserves the existing generation/repair candidate contract and all deterministic execution/scoring/ranking behavior, replaces only the critique/challenge acceptor with the strict validators, and substitutes exact correction instructions for the two corresponding JSON-retry stages.

The authorized T0022 workflow now routes future follow-up execution through `python -m arc_lab.multi_candidate_hardened`. No trigger was written and no target-model experiment was started in ARC-R041.

## Regression and offline gate

`tests/test_multi_candidate_phase_contract.py` reads `lab/results/ARC-R040-multi-candidate.json` directly. Both persisted critic-related records (`critique` and `critique_json_retry` where present) are replayed through the strict critique acceptor and must fail closed.

The same test searches the persisted ARC-R040 generation/recovery records for the contract-valid 16-candidate batch rather than assuming a phase string. The recovered batch used by the offline gate contains **16 submitted, 16 parseable, 16 unique** normalized candidates. This exceeds the task's >=8 representative-candidate requirement.

Mocked critique records are generated only for mechanically derived candidate fingerprints and pass the strict critique validator. Mocked challenge records pass the strict challenge validator. A valid executable repair candidate is then admitted under the existing candidate contract, and the combined batch reaches the unchanged deterministic Python selector. The test does not use critique text as a score or choose a winner by model opinion.

## Verification history

The first CI attempt, run `32962288693`, failed because the new regression test itself made two brittle assumptions: it expected a specific prose prefix and tried only the first generation phase instead of the recovery record. No product-code defect was inferred from that failure.

The second CI attempt, run `32962485934`, reduced the problem to one remaining brittle assertion that hard-coded 14 unique candidates. Mechanical replay showed the selected persisted recovery batch has 16 unique normalized candidates, so the gate was changed to the actual requirement (`>=8`) and downstream cardinalities are derived mechanically.

GitHub Actions CI run **32962601395** on commit `ccf73e05393c3a2f693ee2d2a2e5f71c9a5bbe15` completed **successfully**. That workflow covers the repository pytest suite plus registry invariants, policy validation, frozen split reproduction and the pinned public-training-only validation path.

## Accounting

- target-model requests: 0
- cache hits: 0
- input tokens: 0
- output tokens: 0
- total tokens: 0
- provider failures: 0
- rate-limit/timeout observations: not applicable
- public evaluation exposures: 0
- ARC score/new solves/regressions: not measured; this is an offline infrastructure gate

## Result

**INFRA_ONLY / PASS.** The known ARC-R040 critic output fails closed under an exact schema, representative strict critique/challenge manifests validate, and the persisted generation evidence traverses mocked critique -> critique-the-critique -> repair -> deterministic selection without changing candidate/executor semantics or accepting arbitrary prose.

This reduces uncertainty about the next live experiment: another failure at the same phase boundary will now be attributable to failure to satisfy an explicit record-level contract rather than an underspecified parser predicate.

## Adversarial interpretation

This result does **not** show that Nemotron will emit valid critique/challenge JSON live, that stricter contracts improve semantic reasoning, that `06df4c85` is solvable by the current IR/search space, or that any effect would transfer to the frozen DeepSeek comparator. The offline mocked chain intentionally tests interface closure, not model quality. ARC-R040 and the next follow-up remain provider/model-failover evidence and cannot support a matched DeepSeek attribution.

## Follow-up

Exactly one follow-up experiment was predeclared after the gate passed: `T0022E-HARDENED-PHASE-CONTRACT-RERUN`, protocol `lab/experiments/T0022E-hardened-phase-contract-rerun.json`. It keeps task `06df4c85`, executable IR semantics, executor/scorer/selector, generation settings and token budgets frozen, while changing only the critique/challenge machine contract and correction instructions. Under current policy it uses NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b` and must be labeled provider/model failover, not a matched DeepSeek rerun.

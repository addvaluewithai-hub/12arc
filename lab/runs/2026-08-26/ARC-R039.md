# ARC-R039 — T0022B Multi-Candidate Schema Contract Repair

## Task and role

- Task: `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR`
- Primary role: reasoning-systems-inventor
- Run: `ARC-R039`
- Target-model calls: **0**
- Public evaluation used: **false**

## Hypothesis

ARC-R038 failed operationally because generation and repair prompts did not expose the exact parser-supported executable IR. Making that contract explicit and mechanically testable should restore executable candidate flow without changing the multi-candidate architecture or deterministic verifier.

## Primary variable and frozen controls

Changed only the model-facing generation/repair prompt-output contract plus contract-validation instrumentation. Frozen: schema-v1/v2 parser/executor semantics, normalized-IR deduplication, deterministic Python ranking, eventual task `06df4c85`, and eventual NVIDIA/DeepSeek comparator setup.

## Implementation

Added `src/arc_lab/multi_candidate_contract.py` with exact executable shapes and prompt fragment; updated `multi_candidate_experiment.py` to inject the same contract into generation and repair and record mechanical contract validation; added `lab/experiments/T0022-executable-candidate-contract.json`; added regression tests for ARC-R038 malformed records; generalized the existing T0022 workflow to accept the predeclared T0022C task while preserving its provider/task execution path.

## Verification

GitHub Actions CI run `32937412114` on commit `a0b9287d40f01f5b6f445d828cd03dcb0392f3fe` completed successfully. Pytest, policy validation, frozen split reproduction, and pinned public-training-only corpus validation all passed.

Offline contract gate asserted **10 submitted / 10 parseable / 10 unique / 0 duplicates**, with all 10 entering deterministic Python scoring. Both exact ARC-R038 malformed families fail closed: natural-language `instructions` objects, and string `schema_version` plus pseudocode `program`; an extra-top-level-prose regression also fails closed.

## Result

**INFRA_ONLY / PASS.** The predeclared >=8 parseable non-duplicate fixture threshold was exceeded without changing solver semantics. No model inference occurred, so no exact ARC score, new solves, regressions, provider failures, token usage, or runtime claims are applicable beyond zero model requests.

## Adversarial interpretation

This validates only the interface contract offline. It does not prove DeepSeek will obey the contract under live generation, nor that the allowed IR is expressive enough for `06df4c85`. A live matched rerun is required before attributing any change to candidate diversity, critique, or repair.

## Next task

Predeclared exactly one matched continuation: `T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN`, on exactly `06df4c85`, changing only the repaired executable-IR prompt contract versus ARC-R038 while freezing provider/model/four-phase budgets and Python verification.

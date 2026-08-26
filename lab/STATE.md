# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R041**
Next unallocated research run: **ARC-R042**

## Fixed comparator and current model policy

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** on deterministic public-training-derived `dev_validation` using NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. Public evaluation remains sealed.

Current hosted execution remains under the temporary provider/model failover policy in `lab/config.json`: DeepSeek V4 Flash endpoints are unavailable on the authorized NVIDIA path and `nvidia/nemotron-3-ultra-550b-a55b` is the current working target model. Nemotron runs must not be represented as matched DeepSeek reruns.

## Current evidence chain

ARC-R038 exposed a generation/repair prompt-to-executable-IR contract failure. ARC-R039 hardened that boundary offline. ARC-R040 then advanced a provider-failover Nemotron execution to critique with executable candidates, but terminated at `critique_parse_or_retry`; no critique-the-critique, repair, final deterministic selection, exact coverage, new-solve, or regression claim was valid.

ARC-R041 completed `T0022D-CRITIQUE-CONTRACT-HARDENING` with **zero target-model calls**. The persisted ARC-R040 critic and critic-retry responses are now replayed as regression fixtures and fail closed under exact critique contracts. New exact validators require fixed top-level containers, exact record keys, 64-character candidate fingerprints, unique/known candidate IDs, typed training-pair indices/booleans, non-empty text fields, and no extra keys. The hardened runner also substitutes exact correction instructions for critique and critique-the-critique while leaving generation/repair IR semantics, execution, scoring, and deterministic selection unchanged.

The offline end-to-end gate replays the persisted ARC-R040 recovered generation batch: **16/16 parseable candidates and 16 unique candidates** in the selected recovery record, comfortably above the >=8 requirement. Strict mocked critique and critique-the-critique manifests validate, a valid repair candidate is admitted, and deterministic Python selection is reached. GitHub Actions CI run **32962601395** passed. This is an `INFRA_ONLY / PASS` result: it establishes machine-contract enforceability and offline traversability, not live-model compliance or an ARC solve.

Validation artifact: `lab/validation/T0022D-critique-contract-hardening.json`.
Run report: `lab/runs/2026-08-26/ARC-R041.md`.

## Next active research direction

Highest-priority ready task: `T0022E-HARDENED-PHASE-CONTRACT-RERUN`.

T0022E is the single predeclared follow-up target-model experiment on exactly public-training task `06df4c85`. It routes the existing loop through `arc_lab.multi_candidate_hardened`, changing only the critique/challenge machine boundary and correction instructions. Under current policy it uses NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b`; it is a provider/model failover experiment and **not** a matched DeepSeek rerun. Operational success requires >=8 parseable non-duplicate generated candidates and completion through strict critique, strict critique-the-critique, repair, and final deterministic Python selection. Research progress then requires an exact training-consistent candidate or a dominant mechanically observed failure class supporting one next ablation.

Protocol: `lab/experiments/T0022E-hardened-phase-contract-rerun.json`.

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction before a complete interpretable architecture-loop run.

Public evaluation remains sealed.

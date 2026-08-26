# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R040**
Next unallocated research run: **ARC-R041**

## Fixed comparator and current model policy

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** on deterministic public-training-derived `dev_validation` using NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. Public evaluation remains sealed.

Current hosted execution is under the temporary provider/model failover policy in `lab/config.json`: DeepSeek V4 Flash endpoints are presently unavailable on the authorized NVIDIA path, while `nvidia/nemotron-3-ultra-550b-a55b` is the current working NVIDIA target model. Nemotron runs must be labeled as provider/model failover experiments and must not be treated as matched DeepSeek reruns.

## Current evidence chain

ARC-R038 attempted the first multi-candidate generate -> critique -> critique-the-critique -> repair -> Python-select loop on public-training task `06df4c85` using DeepSeek V4 Flash. It was operationally inconclusive because all 24 submitted candidate records failed the executable IR parser, so no valid candidate reached critique or deterministic selection.

ARC-R039 repaired only the generation/repair executable-IR prompt contract and validated it offline: 10/10 representative fixtures were parseable and unique, malformed ARC-R038 forms failed closed, and parser/executor/ranking semantics remained frozen.

ARC-R040 resumed the same reserved T0022C run after the external workflow completed. The durable result used NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b` under the temporary failover policy, not the frozen DeepSeek comparator, so it is **not a matched DeepSeek rerun**.

ARC-R040 made 4 provider requests with 36,532 input tokens, 15,059 output tokens, 51,591 total tokens and 378.378 seconds runtime. Provider failures were 0; public evaluation was not used. Candidate flow advanced to the critique phase with 14 candidates, materially beyond ARC-R038's zero executable-candidate boundary. However, the critic response failed its machine-readable JSON contract (`JsonContractError`, `failure_stage=critique_parse_or_retry`) even after the recovery path. The run ended `operational_failure` before critique-the-critique, repair and final deterministic Python selection.

Therefore no exact candidate coverage, new solve, regression or architecture-quality delta is claimable from ARC-R040. The multi-candidate reasoning hypothesis remains untested end-to-end. The strongest model-independent conclusion is that phase-level machine contracts are not yet hardened uniformly across the loop.

Run report: `lab/runs/2026-08-26/ARC-R040.md`.

## Next active research direction

Highest-priority ready task: `T0022D-CRITIQUE-CONTRACT-HARDENING`.

This is a no-model infrastructure-research task. Replay the persisted ARC-R040 critic failure as a regression fixture, define exact fail-closed schemas for critique and critique-the-critique, and verify offline that representative valid fixtures can traverse critique -> critique-the-critique -> repair -> deterministic selection without loosening candidate/executor semantics or accepting arbitrary prose. Only after that gate passes should a new target-model experiment be predeclared.

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction before the architecture loop obtains a complete interpretable run.

Public evaluation remains sealed.

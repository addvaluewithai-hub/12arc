# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R041 closed — critique/challenge contract gate passed offline

`T0022D-CRITIQUE-CONTRACT-HARDENING` is complete as **INFRA_ONLY / PASS** with zero target-model calls and public evaluation sealed.

Durable evidence:
- `src/arc_lab/multi_candidate_phase_contract.py`
- `src/arc_lab/multi_candidate_hardened.py`
- `tests/test_multi_candidate_phase_contract.py`
- `lab/validation/T0022D-critique-contract-hardening.json`
- `lab/experiments/T0022E-hardened-phase-contract-rerun.json`
- `lab/runs/2026-08-26/ARC-R041.md`

The persisted ARC-R040 critic and critic-retry outputs are regression fixtures and fail closed under the new exact schema. Critique records now require exact keys, 64-char candidate fingerprints, typed/range-checkable training-pair indices, unique/known candidate IDs and non-empty text; challenge records require exact keys, JSON booleans, unique/known IDs and non-empty text. Extra keys and loose prose forms are rejected. The hardened runner also supplies exact JSON correction instructions at those two boundaries only; candidate generation/repair IR semantics, executor, scorer and deterministic selector remain frozen.

The offline loop gate found the contract-valid ARC-R040 generation recovery record with 16/16 parseable and 16 unique candidates, then traversed strict mocked critique -> strict mocked critique-the-critique -> repair -> deterministic Python selection. GitHub Actions CI run 32962601395 passed. Do not interpret this as evidence that a live model will comply or solve the task.

## Next task: T0022E hardened phase-contract rerun

`T0022E-HARDENED-PHASE-CONTRACT-RERUN` is the single predeclared target-model follow-up and should be the next ready architecture task.

Run exactly public-training task `06df4c85` through `python -m arc_lab.multi_candidate_hardened`. Change only the critique/challenge machine contract and exact correction instructions relative to the existing loop. Keep executable candidate schemas, executor/scorer/selector, generation settings, phase token budgets and task fixed. Operational success requires >=8 parseable non-duplicate generated candidates and completion through strict critique, strict critique-the-critique, repair and final deterministic selection. After that, research progress requires either an exact training-consistent candidate or a dominant mechanically observed failure class.

Current `lab/config.json` failover policy remains authoritative. The workflow uses NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b`, so this must be labeled a provider/model failover experiment and not a matched DeepSeek rerun. Protocol: `lab/experiments/T0022E-hardened-phase-contract-rerun.json`.

`T0023` remains blocked until the multi-candidate direction produces a complete interpretable architecture run or operator reprioritization occurs. Public evaluation remains sealed.

Run registry after closure: latest completed **ARC-R041**, no active reservations, next run **ARC-R042**.

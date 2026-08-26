# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R039 closed — T0022B executable-IR contract gate passed

`T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR` completed as **INFRA_ONLY / PASS** with zero target-model calls and no public evaluation.

Durable evidence:
- `src/arc_lab/multi_candidate_contract.py`
- `tests/test_multi_candidate_contract.py`
- `lab/experiments/T0022-executable-candidate-contract.json`
- `lab/validation/T0022B-schema-contract.json`
- `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`
- `lab/runs/2026-08-26/ARC-R039.md`

The repair changes only the model-facing generation/repair contract. It supplies exact executable schema-v1/v2 shapes, legal operators/parameters, valid examples, and explicit forbidden ARC-R038 forms. Existing parser/verifier semantics and Python ranking are unchanged.

Offline gate: **10/10 parseable, 10 unique** representative candidates entered deterministic Python scoring. ARC-R038 natural-language `instructions`, string-valued schema versions with pseudocode `program`, and extra prose keys all fail closed. CI run `32937412114` passed the complete repository verification path.

This is infrastructure evidence only: it does not show the target model will obey the contract.

## Next task: T0022C matched contract rerun

`T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN` is ready. Protocol: `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`.

Use exactly `06df4c85`, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, and the frozen ARC-R038 four-phase generation settings and request budgets. The only treatment change is the repaired executable-IR contract. Trigger through `.github/workflows/t0022-multi-candidate.yml` after claim/reservation.

Do not interpret the architecture unless >=8 parseable non-duplicate candidates survive. If the contract gate passes but no exact candidate appears, use Python near-miss/failure clustering to evolve one component at a time. If the model still violates the explicit contract, treat that as an interface/constrained-generation problem rather than a reasoning rejection.

`T0023` remains blocked. Public evaluation remains sealed.

Run registry after closure: latest completed **ARC-R039**, no active reservations, next run **ARC-R040**.

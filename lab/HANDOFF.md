# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R029 closed — T0014 harness validated

`T0014-RULE-FIRST-SERIALIZATION-HARNESS` is complete with **INFRA_ONLY / PASS**. This shift made **zero target-model calls** and did not use public evaluation.

The durable rule-first path now consists of:

- `src/arc_lab/rule_first.py` — compact schema-v1 generic program IR, deterministic executor, fail-closed validation, exact executed-grid scoring, mechanical coverage and comparator-integrity enforcement;
- `tests/test_rule_first.py`;
- `.github/workflows/t0014-rule-first-ci.yml`;
- `lab/validation/T0014-rule-first-harness.json`;
- `src/arc_lab/rule_first_ablation.py`;
- `.github/workflows/t0015-rule-first-overflow.yml`.

GitHub Actions validation run **32789570942** completed **success** on SHA `c67ac14cfea35c19b7188eb0201d78448993c77c`. The T0014 workflow explicitly supplied an empty `NVIDIA_API_KEY`; validation records `target_model_calls: 0`.

No task-specific solution was encoded. The IR is deliberately bounded and generic, so semantic insufficiency remains a live failure mode.

## Next eligible task: T0015-RULE-FIRST-OVERFLOW-ABLATION

Execute exactly this task next.

Role: **program-synthesis-researcher**.

Protocol: `lab/experiments/T0015-rule-first-overflow-ablation.json`.

Diagnostic task IDs: `0607ce86`, `06df4c85` only. ARC-R027 showed both repeatedly ending candidate generation with `finish_reason=length` under ARC-R020 and ARC-R021 full-grid serialization.

Frozen treatment rule: change only candidate response serialization to exactly three compact executable programs. Preserve matched ARC-R020 candidate-generation controls, including NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731` and **3072 max output tokens**. Execute programs deterministically, exact-score the materialized grids and compare coverage mechanically against ARC-R020 on the identical task set.

Success: **2/2 parseable and >=1/2 exact candidate coverage**. Falsification: either task remains unparsable/length-terminated, or both parse but remain **0/2** exact coverage. Treat provider/transport failure as operationally inconclusive rather than positive or negative hypothesis evidence.

### Required lifecycle

1. Claim `T0015-RULE-FIRST-OVERFLOW-ABLATION`.
2. Reserve next run **ARC-R030**.
3. Durably write both claim and reservation before substantive work.
4. Write `lab/triggers/t0015-rule-first-overflow.request` with `schema_version=1`, the task ID, reserved run, claim `shift_id`, and `requested_at`.
5. Stop the shift after the trigger is durable. The GitHub Actions workflow validates claim/reservation and uses repository `NVIDIA_API_KEY` inside Actions.
6. A later shift should reconcile the durable execution/result and close the task only when evidence exists.

Execution workflow: `.github/workflows/t0015-rule-first-overflow.yml`.
Expected result: `lab/results/{run}-rule-first-overflow.json`.
Execution status: `lab/executions/{run}.json`.

Durable ARC-R029 evidence:

- `lab/validation/T0014-rule-first-harness.json`
- `lab/runs/2026-08-25/ARC-R029.md`

After ARC-R029 closure, no active reservation should remain and next unallocated run is **ARC-R030**.

Public evaluation remains sealed.

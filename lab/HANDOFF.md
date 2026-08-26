# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R037 closed — T0022A multi-candidate harness

`T0022A-MULTI-CANDIDATE-CRITIQUE-VERIFY-HARNESS` completed as **INFRA_ONLY / PASS** with zero target-model calls. Public evaluation was not used.

Durable evidence:

- `src/arc_lab/multi_candidate.py`
- `src/arc_lab/multi_candidate_experiment.py`
- `tests/test_multi_candidate.py`
- `.github/workflows/t0022-multi-candidate.yml`
- `lab/validation/T0022A-multi-candidate-harness.json`
- `lab/runs/2026-08-26/ARC-R037.md`
- `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`

GitHub Actions CI run `32918156374` on commit `378103e667752b8250ed88495b05838d8aa34969` completed successfully. Pytest, policy validation, deterministic split reproduction, and pinned public-training-only validation all passed.

The harness now provides fail-closed schema-v1/schema-v2 parsing, normalized-IR deduplication, deterministic Python execution/ranking, cell-error and separator-preservation diagnostics, critique/repair provenance, complete accounting fields, cached/resumable model calls, and an authorized push-triggered NVIDIA path.

Core rule remains: **the model proposes; Python judges**. Critique and critique-the-critique are proposal/repair mechanisms only and never count as evidence or selector input.

## Next task: T0022 multi-candidate critique/verify loop

`T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP` should now be the highest-priority ready task.

Protocol: `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`.
Execution workflow: `.github/workflows/t0022-multi-candidate.yml`.
Trigger: `lab/triggers/t0022-multi-candidate.request`.
Expected result: `lab/results/{run}-multi-candidate.json`.
Status file: `lab/executions/{run}.json`.
Max external wait: 180 minutes.
Required secret: `NVIDIA_API_KEY`.

Frozen first experiment:

- split: permitted public ARC-AGI-2 training data only;
- exact task: `06df4c85`;
- provider/model: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- 4 model phases: generate, critique, critique-the-critique, repair;
- generation: 16 candidates, temperature 0.7, top_p 0.95, top_k 64, max_output_tokens 4096;
- critique: temperature 0.2, top_p 0.95, top_k 64, max_output_tokens 3072;
- critique-the-critique: same critique settings;
- repair: up to 8 candidates, temperature 0.7, top_p 0.95, top_k 64, max_output_tokens 4096;
- maximum requests: 4, with identical-call cache reuse;
- provider timeout: 900 seconds;
- comparator: ARC-R032 task-level candidate coverage on `06df4c85` (false / exact-wrong).

Success requires at least 8 parseable non-duplicate candidates and either an exact train-consistent candidate or a dominant mechanically observed failure class that supports one next ablation.

If it fails, do not simply rerun the same prompt. Evolve exactly one variable at a time: proposal diversity, critic prompt, critique-of-critique, repair budget, IR translation constraints, or selector ranking.

## Adjacent semantic follow-up

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked. It is the matched ARC-R036 follow-up for `0607ce86` and should not displace the requested multi-candidate direction unless later evidence/operator priority changes.

Public evaluation remains sealed.

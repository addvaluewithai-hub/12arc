# ARC Research Lab — Current State

Updated: 2026-08-24 17:58 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R025**
Next unallocated research run: **ARC-R026**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## ARC-R025 infrastructure result

`T0012A-MAX-REASONING-EXECUTION-PATH` is complete with verdict `INFRA_ONLY` and zero target-model calls.

ARC-R025 added the missing execution path for `T0012-MAX-REASONING-DIRECT-ABLATION`:

- provider-neutral `reasoning_effort` support in `GenerationConfig` and cache fingerprints;
- NVIDIA NIM request payload support for `reasoning_effort=max`;
- sanitized retryable provider errors carrying `x-ratelimit-*` / `retry-after` metadata;
- resumable max-reasoning direct runner at `src/arc_lab/max_reasoning_direct.py`;
- tests at `tests/test_max_reasoning_direct.py`;
- push-triggered workflow `.github/workflows/t0012-max-reasoning-direct.yml` using repository secret `NVIDIA_API_KEY`;
- external execution protocol `lab/protocols/EXTERNAL-EXECUTION.md`;
- runner lifecycle updates so scheduled agents do not duplicate long external runs or disable the hourly scheduler.

Validation marker `lab/validation/t0012a-passed.json` shows GitHub Actions validation passed with workflow run id `32741606202`, validated commit `def87116e75f8274d368fdfbbd500498908a6eb9`, and `target_model_calls: 0`.

Report: `lab/runs/2026-08-24/ARC-R025.md`.

## Next task

Highest-priority ready task is now **`T0012-MAX-REASONING-DIRECT-ABLATION`**, intended for ARC-R026 after normal claim/reservation.

This task declares an external execution path. The scheduled agent does **not** need direct NVIDIA access or workflow-dispatch access. It should:

1. read `lab/RUNNER.md` and reconstruct state;
2. claim T0012 and reserve ARC-R026;
3. write `lab/triggers/t0012-max-reasoning.request` with schema version, task id, reserved run, claim shift id and timestamp;
4. stop the shift after the trigger is durable;
5. let `.github/workflows/t0012-max-reasoning-direct.yml` execute using repository secrets;
6. later scheduled shifts should observe `lab/executions/ARC-R026.json` / `lab/results/ARC-R026-max-reasoning-direct.json` and close the same reserved run when evidence is complete.

Frozen planned treatment for T0012:

- same 174 `dev_validation` tasks as ARC-R016;
- same `deepseek-ai/deepseek-v4-flash-0731` model;
- exact same direct ARC prompt and scorer;
- temperature 0, top_p 1;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- one prediction per test input;
- GitHub Actions job timeout **360 minutes**;
- provider HTTP timeout **900 seconds**;
- durable per-task artifacts and aggregation;
- explicit accounting for any 429/529/timeout recovery;
- output-token length buckets and sanitized NVIDIA rate-limit telemetry.

Protocol: `lab/experiments/T0012-max-reasoning-direct-ablation.json`.

`T0011-CANDIDATE-FAILURE-TAXONOMY` remains ready but lower priority; resume it only after the max-inference result unless evidence redirects the research program.

Public evaluation remains sealed.

# ARC-R025 — T0012A Max-Reasoning Execution Path

Date: 2026-08-24
Role: llm-experimenter
Task: `T0012A-MAX-REASONING-EXECUTION-PATH`
Verdict: `INFRA_ONLY`
Target-model calls: 0
Public evaluation used: false

## Objective

Remove the deadlock where `T0012-MAX-REASONING-DIRECT-ABLATION` was ready but the scheduled research agent had GitHub read/write access without direct NVIDIA NIM access or a workflow-dispatch tool.

## Infrastructure changes

- Added `reasoning_effort` to the provider-neutral `GenerationConfig` so it participates in request fingerprints/cache keys.
- Updated the NVIDIA NIM adapter to send `reasoning_effort` when configured and to expose sanitized retryable provider errors with `x-ratelimit-*` / `retry-after` metadata.
- Added `src/arc_lab/max_reasoning_direct.py`, a resumable direct-JSON max-reasoning runner for T0012.
- Added tests in `tests/test_max_reasoning_direct.py` covering max config, request fingerprinting, provider payload/timeout, retryable errors, output-token buckets, trigger validation and aggregation against ARC-R016.
- Added `.github/workflows/t0012-max-reasoning-direct.yml`, a push-triggered workflow using `lab/triggers/t0012-max-reasoning.request`, 360-minute job timeouts, per-task artifacts, `NVIDIA_API_KEY` from repository secrets, provider timeout 900s, transport retries and durable aggregation.
- Added `lab/protocols/EXTERNAL-EXECUTION.md` and updated `lab/RUNNER.md` so scheduled agents treat push-triggered workflows as valid target-model execution paths and do not disable the hourly scheduler.
- Added `.github/workflows/t0012-execution-path-ci.yml` and `lab/validation/t0012a.request` to validate the execution path without NVIDIA calls.

## Validation

GitHub Actions validation marker: `lab/validation/t0012a-passed.json`.

Validation marker contents record:

- status: `passed`
- validated commit: `def87116e75f8274d368fdfbbd500498908a6eb9`
- workflow run id: `32741606202`
- tests:
  - `tests/test_target_model.py`
  - `tests/test_nvidia_baseline.py`
  - `tests/test_max_reasoning_direct.py`
- target-model calls: `0`

## Important boundary

This run did **not** execute the 174-task max-reasoning experiment. It only made the execution path available and validated the non-inference contract. T0012 remains the next target-model experiment.

## Next task

Next highest-priority ready task is `T0012-MAX-REASONING-DIRECT-ABLATION` for ARC-R026. The scheduled agent should claim T0012, reserve ARC-R026, write `lab/triggers/t0012-max-reasoning.request`, then stop and let the GitHub Actions workflow execute with repository secrets.

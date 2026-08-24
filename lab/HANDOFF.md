# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R025 closed — T0012 external execution path is ready

`T0012A-MAX-REASONING-EXECUTION-PATH` is done and ARC-R025 is released. This was an `INFRA_ONLY` run with **zero target-model calls** and no public evaluation.

ARC-R025 added and validated the missing path that lets a GitHub-write-only scheduled agent start the max-reasoning NVIDIA experiment without direct NVIDIA access or workflow-dispatch access.

Key durable changes:

- `src/arc_lab/target_model.py` supports `GenerationConfig.reasoning_effort`, includes it in fingerprints, sends it to NVIDIA when configured, and exposes sanitized retryable provider errors with rate-limit headers.
- `src/arc_lab/max_reasoning_direct.py` implements the resumable direct-JSON T0012 runner.
- `tests/test_max_reasoning_direct.py` covers max config, fingerprinting, provider payload/timeout, retryable errors, token buckets, trigger validation and aggregation.
- `.github/workflows/t0012-max-reasoning-direct.yml` is the target workflow. It triggers on pushes to `lab/triggers/t0012-max-reasoning.request`, uses `NVIDIA_API_KEY` from repository secrets, has 360-minute job timeouts, provider timeout 900s, per-task artifacts, transport-retry accounting and durable aggregation.
- `lab/protocols/EXTERNAL-EXECUTION.md` and `lab/RUNNER.md` now define external-execution lifecycle rules: do not duplicate running external workflows, do not treat normal claim lease expiry alone as stale for a running external execution, and never disable the hourly scheduler from inside a shift.

Validation marker: `lab/validation/t0012a-passed.json`.

Validation marker records:

- status `passed`;
- validated commit `def87116e75f8274d368fdfbbd500498908a6eb9`;
- workflow run id `32741606202`;
- tests `tests/test_target_model.py`, `tests/test_nvidia_baseline.py`, `tests/test_max_reasoning_direct.py`;
- target-model calls `0`.

Report: `lab/runs/2026-08-24/ARC-R025.md`.

## Next shift: ARC-R026 trigger handoff for T0012

Highest-priority ready task is **`T0012-MAX-REASONING-DIRECT-ABLATION`**, role **llm-experimenter**.

Follow `lab/RUNNER.md` exactly. For T0012:

1. claim T0012 and reserve ARC-R026;
2. write `lab/triggers/t0012-max-reasoning.request` with:
   - `schema_version: 1`
   - `task_id: T0012-MAX-REASONING-DIRECT-ABLATION`
   - `run: ARC-R026`
   - the active claim `shift_id`
   - `requested_at`
3. stop the shift after the trigger is durable.

Do **not** claim the 174-task experimental result merely because the trigger was written. The workflow must first persist:

- `lab/executions/ARC-R026.json`
- `lab/experiments/ARC-R026-max-reasoning-direct-protocol.json`
- `lab/results/ARC-R026-max-reasoning-direct.json`

Later scheduled shifts should inspect these durable files before selecting new work. If the execution is running or still within `max_wait_minutes`, do not start a duplicate. If it is complete, close the same reserved ARC-R026 with a run report and queue/state updates. If failed, recover or persist a blocker for the same run.

Frozen T0012 treatment remains:

- comparator: durable ARC-R016, 45/174 = 25.8621%;
- model/provider: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- exact direct ARC prompt and scorer from ARC-R016;
- temperature 0, top_p 1, one prediction/test input;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- GitHub Actions timeout 360 minutes;
- provider HTTP timeout 900 seconds;
- explicit 429/529/timeout retry accounting;
- first-attempt statistic preserved separately from operational recovery;
- output-length buckets and sanitized rate-limit telemetry;
- public evaluation remains sealed.

`T0011-CANDIDATE-FAILURE-TAXONOMY` remains ready at lower priority and should be reconsidered only after T0012 evidence is durable.

## Dashboard direction

Future UI is **read-only observability**. No Start/Pause/Retry controls are requested. It should surface durable run progress, score, calls/tokens/runtime, finish reasons, provider failures and rate-limit telemetry without becoming the execution authority.

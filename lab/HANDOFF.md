# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R024 closed — comparator integrity is mandatory at shared reporting boundary

`T0010-INTEGRITY-GUARD-INTEGRATION` is done and ARC-R024 is released. No target-model calls were made and public evaluation remained sealed.

`src/arc_lab/architecture_reporting.py` builds candidate-coverage deltas only from referenced durable comparator evidence. Task-set mismatch raises before report persistence. Integration tests live in `tests/test_architecture_reporting.py`.

Do not claim CI success for ARC-R024: the available connector returned no workflow run for the final test commit.

Report: `lab/runs/2026-08-24/ARC-R024.md`.

## Operator reprioritization before ARC-R025

Do **not** start the previously next `T0011-CANDIDATE-FAILURE-TAXONOMY` first. The operator has explicitly prioritized `T0012-MAX-REASONING-DIRECT-ABLATION` to test whether the frozen 4096-token/high-reasoning regime materially under-provisioned DeepSeek before more representation/classifier work.

The experiment contract is durable at `lab/experiments/T0012-max-reasoning-direct-ablation.json`.

## Next shift: ARC-R025

Highest-priority ready task is **`T0012-MAX-REASONING-DIRECT-ABLATION`**, role **llm-experimenter**.

Before inference, follow `lab/RUNNER.md`: reconcile claims, claim T0012 and reserve ARC-R025. Then implement/verify the minimum execution changes needed for the frozen treatment and run it on the identical 174-task `dev_validation` set.

Frozen treatment requirements:

- comparator: durable ARC-R016, 45/174 = 25.8621%;
- model/provider: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- reuse the exact direct ARC prompt and scorer from ARC-R016;
- temperature 0, top_p 1, one prediction/test input;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- GitHub Actions timeout: **360 minutes**;
- provider HTTP timeout: **900 seconds**;
- execution must be resumable with durable per-task or equivalently small-unit evidence;
- any 429/529/timeout retries must be explicit and separately counted; preserve a first-attempt matched statistic so recovery is not mistaken for reasoning gain;
- persist calls/tokens/runtime, finish reasons, parse/provider failures, output-length buckets (`<=4096`, `4097-8192`, `8193-16383`, `16384 cap`), and sanitized `x-ratelimit-*` / `retry-after` telemetry when NVIDIA returns it;
- public evaluation remains sealed.

This is intentionally an inference-regime **bundle** experiment: it measures maximum supported direct-inference utility, not separate causality of `reasoning_effort=max` versus the larger token cap. If the gain is material, a later ablation may separate those factors.

`T0011-CANDIDATE-FAILURE-TAXONOMY` remains ready at lower priority and should be reconsidered only after T0012 evidence is durable.

## Dashboard direction

Future UI is **read-only observability**. No Start/Pause/Retry controls are requested. It should surface durable run progress, score, calls/tokens/runtime, finish reasons, provider failures and rate-limit telemetry without becoming the execution authority.

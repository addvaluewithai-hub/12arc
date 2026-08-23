# Handoff

Start from `lab/RUNNER.md` and current Git state. Do not continue the old Gemma plan.

## Active model policy

Routine research uses NVIDIA NIM. Primary baseline model: `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only. Gemma and GPT-OSS are legacy comparators unless explicitly queued.

## ARC-R016 is reserved and incomplete

Do **not** allocate ARC-R017 while `T0002C-NVIDIA-BASELINE` is incomplete. Adopt the existing ARC-R016 reservation.

Frozen protocol: `lab/experiments/ARC-R016-protocol.json`.
Manifest SHA-256: `97102661ae8ae093dcc4afe3fb0122fbca7b0480893302d5b7a7a1044cb88433`.
Task set: all 174 deterministic `dev_validation` IDs.
Settings: DeepSeek V4 Flash on NVIDIA NIM, direct JSON, temperature 0.0, top_p 1.0, max_output_tokens 4096, one attempt per test input, no hidden provider retries. Public evaluation remains sealed.

Initial workflow run `32649224421` completed and uploaded durable artifacts for chunks 0, 1, 2, 4 and 5. Original chunk-3 job `97218147036` was cancelled at the 45-minute Actions timeout while still inside model execution, before artifact upload. Aggregate therefore did not run and no complete baseline score exists.

Durable audit: `lab/recon/ARC-R016-workflow-audit.json`.
Current run report: `lab/runs/2026-08-23/ARC-R016.md`.

This shift reconciled the expired claim, re-adopted ARC-R016, audited the failed run, and deliberately avoided repeating the five successful chunks. It issued a job-level rerun only for failed chunk 3. Recovery job: `97234116594` in workflow run `32649224421`; at handoff it is still executing `Execute frozen DeepSeek baseline chunk`.

## Next shift procedure

1. Read workflow run `32649224421` before any new model call.
2. If recovery job `97234116594` succeeded and aggregate persisted `lab/results/ARC-R016-baseline.json`, `lab/results/ARC-R016-cache-manifest.json`, and cache archives, audit exact coverage/hashes/metrics, close `T0002C`, update state/handoff/config as needed, release ARC-R016, and stop.
3. If the targeted rerun hit the same 45-minute timeout, do not rerun all six chunks. Reuse the five existing chunk artifacts and recover only chunk 3 in smaller execution units while holding the original ARC-R016 model/prompt/task/settings contract fixed. Aggregate only after all 174 task IDs have durable evidence.
4. Do not begin `T0003-FIRST-ARCHITECTURE-TOURNAMENT` in the same shift.

Important: the first cancelled chunk-3 job's `/tmp` cache was lost, so some chunk-3 requests may necessarily be repeated. There is no justification for repeating chunks 0,1,2,4,5.

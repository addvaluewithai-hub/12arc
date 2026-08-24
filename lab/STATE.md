# ARC Research Lab — Current State

Updated: 2026-08-24 13:01 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R024**
Next unallocated research run: **ARC-R025**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current bottleneck / operator reprioritization

Candidate generation/representation remains weak, but before spending more effort on morphology taxonomy or specialized routing, the next uncertainty is whether ARC-R016 materially under-provisioned DeepSeek's supported reasoning regime. The operator explicitly prioritizes a maximum-inference direct ablation before `T0011-CANDIDATE-FAILURE-TAXONOMY`.

NVIDIA's current API contract for `deepseek-ai/deepseek-v4-flash-0731` supports `reasoning_effort=none|high|max` and `max_tokens` up to **16384**. The new experiment keeps the model, direct ARC prompt, exact scorer, frozen 174-task `dev_validation` split and one-prediction contract fixed while changing the inference-regime bundle to `reasoning_effort=max` plus `max_output_tokens=16384`.

## ARC-R024 mandatory reporting integration

`src/arc_lab/architecture_reporting.py` is the shared candidate-coverage reporting boundary. It requires referenced durable comparator evidence, mechanically derives comparator/treatment coverage through `comparator_integrity`, enforces identical task sets, and only then persists new-covered/regressed task IDs.

ARC-R024 used zero target-model calls, zero tokens and no public evaluation. Report: `lab/runs/2026-08-24/ARC-R024.md`.

## Next task

Highest-priority ready task is now **`T0012-MAX-REASONING-DIRECT-ABLATION`**, intended for ARC-R025 after normal claim/reservation.

Frozen planned treatment:
- same 174 `dev_validation` tasks as ARC-R016;
- same `deepseek-ai/deepseek-v4-flash-0731` model;
- exact same direct ARC prompt and scorer;
- temperature 0, top_p 1;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- one prediction per test input;
- GitHub Actions job timeout **360 minutes**;
- provider HTTP timeout **900 seconds**;
- durable resumable per-task/small-unit checkpoints;
- explicit accounting for any 429/529/timeout recovery;
- persist output-token length buckets and sanitized NVIDIA rate-limit headers.

Protocol: `lab/experiments/T0012-max-reasoning-direct-ablation.json`.

`T0011-CANDIDATE-FAILURE-TAXONOMY` remains ready but lower priority; resume it after the max-inference result unless evidence redirects the research program.

Public evaluation remains sealed.

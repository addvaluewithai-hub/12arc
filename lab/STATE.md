# ARC Research Lab — Current State

Updated: 2026-08-23 11:18 EEST
Phase: **PHASE 1 — NVIDIA model selection and baseline establishment**
Latest completed research run: **ARC-R013**
Next research run: **ARC-R014**

## Target model / provider policy

Current preferred hosted provider: **NVIDIA NIM** via repository Actions secret `NVIDIA_API_KEY` (never expose or persist its value).

Provisional active candidates:

- primary: `deepseek-ai/deepseek-v4-flash-0731`;
- escalation/second candidate: `nvidia/nemotron-3-ultra-550b-a55b`.

The designation is provisional until a small frozen development tournament compares the two under controlled budget/settings. Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` are now **legacy comparators**, not routine research targets. Do not spend scheduled research budget debugging or benchmarking them unless an explicit queued comparator/parity experiment requires it.

Operator decision and rationale: `lab/decisions/2026-08-23-nvidia-model-pivot.md`.

## Benchmark discipline

`T0001-BENCHMARK-HARNESS` remains complete. The frozen public-training-derived development split remains authoritative and public evaluation remains milestone-only. Known ARC-specific pretraining on a legal/public foundation model is not an automatic exclusion, but must be labeled in reports so competition utility and research-treatment attribution are not confused.

## Historical Gemma findings

The Gemma execution path was technically verified, but the unfinished Gemma baseline has been cancelled by operator direction.

The earlier Google free-tier 16,000 input-TPM failure was an aggregate throughput issue: 61-second pacing avoided that 429 for the observed ARC prompts. A separate dominant failure remained: on deterministic task `00dbd492`, Gemma consumed the configured generation allowance as thought tokens and emitted no final candidate. Raising `max_output_tokens` from 2,048 to 8,192 increased thought consumption by exactly 6,144 tokens and still finished `MAX_TOKENS` with empty visible output. ARC-R013 rejected output-cap increase as the repair.

This historical evidence remains useful but should not drive further routine Gemma debugging.

## New NVIDIA smoke evidence

The operator configured `NVIDIA_API_KEY`. A non-ARC smoke workflow then tested four NVIDIA-hosted model IDs on the same common endpoint. Sanitized evidence is persisted at `lab/recon/nvidia-model-smoke-latest.json`.

Observed results:

- `nvidia/nemotron-3-ultra-550b-a55b`: **HTTP 200**, visible `OK`, ~0.687 s latency, 21 prompt / 20 completion / 41 total tokens; reasoning content present.
- `deepseek-ai/deepseek-v4-flash-0731`: **HTTP 200**, visible `OK.`, ~0.667 s latency, 9 prompt / 3 completion / 12 total tokens.
- `openai/gpt-oss-120b`: 120 s transport read timeout; no authorization rejection observed.
- `google/gemma-4-31b-it`: 120 s transport read timeout; no authorization rejection observed.

This proves the same NVIDIA key can immediately execute both active candidates. It does **not** establish sustained NVIDIA rate limits; future experiments must measure actual quota behavior rather than assume RPM/TPM independence.

## Queue pivot

`T0002-GEMMA-BASELINE` is **cancelled**. The new required sequence is:

`T0001B-NVIDIA-EXECUTION-PATH` -> `T0002B-NVIDIA-MODEL-TOURNAMENT` -> `T0002C-NVIDIA-BASELINE` -> `T0003-FIRST-ARCHITECTURE-TOURNAMENT`.

## Current bottleneck / next task

`T0001B-NVIDIA-EXECUTION-PATH` is the highest-priority ready task for ARC-R014.

Promote NVIDIA NIM into the existing provider-neutral target-model/cache/accounting layer. Verify live non-ARC cached calls for **both DeepSeek V4 Flash and Nemotron 3 Ultra** using `NVIDIA_API_KEY`, persist sanitized usage/model/runtime evidence, and do not run a broad ARC benchmark in that infrastructure shift.

After that, the team should run a small frozen development model tournament between only the two active candidates. The winner becomes the fixed primary engine for the new full baseline.

# Decision — NVIDIA provider/model pivot (2026-08-23)

Status: **ACTIVE OPERATOR DIRECTION**

## Decision

Routine ARC research moves away from Gemma and GPT-OSS. NVIDIA NIM becomes the preferred hosted research provider. The active model candidates are:

1. `deepseek-ai/deepseek-v4-flash-0731` — provisional primary.
2. `nvidia/nemotron-3-ultra-550b-a55b` — provisional escalation/second candidate.

Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` remain historical/legacy comparators only. Do not spend routine target-model budget on them unless a queued controlled experiment explicitly requires it.

The provisional primary designation is not a claim that DeepSeek is already proven best for this lab. A frozen public-training-derived tournament must select between DeepSeek and Nemotron before establishing the new full baseline.

## Why the pivot happened

The prior Gemma path was technically verified but proved operationally poor for the research loop:

- Google free-tier execution encountered a confirmed 16,000 input-token/minute quota; pacing avoided the aggregate TPM failure but made baseline collection slow.
- On the deterministic diagnostic request, Gemma consumed the complete output allowance as thought tokens and emitted no final candidate at both 2,048 and 8,192 output-token caps.
- Raising the cap was therefore rejected as a repair.

The operator prefers to build on stronger current open-weight models rather than continue debugging the older Gemma/GPT-OSS candidates.

## NVIDIA key and smoke evidence

Repository Actions secret `NVIDIA_API_KEY` is configured by the operator. Never expose or persist its value.

A non-ARC smoke workflow used the common NVIDIA OpenAI-compatible endpoint and the same secret for four model IDs. Durable sanitized evidence is in `lab/recon/nvidia-model-smoke-latest.json`.

Observed:

- `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, returned `OK`, ~0.687 s latency, 21 prompt tokens / 20 completion tokens / 41 total tokens; reasoning content was present.
- `deepseek-ai/deepseek-v4-flash-0731`: HTTP 200, returned `OK.`, ~0.667 s latency, 9 prompt tokens / 3 completion tokens / 12 total tokens.
- `openai/gpt-oss-120b`: transport read timeout at 120 s; no 401/403 authorization rejection was observed.
- `google/gemma-4-31b-it`: transport read timeout at 120 s; no 401/403 authorization rejection was observed.

The smoke proves authorization and immediate availability only for DeepSeek and Nemotron. It does **not** prove sustained NVIDIA RPM/TPM/RPD limits. Future experiments must measure rate limits rather than assume them.

## ARC-specific pretraining policy

Known ARC-specific training/exposure is **not an automatic exclusion** if the data/model are competition-permitted. A model with ARC exposure may be a useful stronger foundation for competition performance. However, reports must label known ARC-specific exposure because development scores may reflect both foundation-model training and the lab's added reasoning architecture.

The lab should distinguish:

- competition utility: does the complete legal system solve unseen tasks better?
- research attribution: how much improvement (`delta`) comes from the lab's treatment relative to the same frozen foundation model?

Never use private/sealed evaluation data, and keep public evaluation milestone-only.

## Required next sequence

`T0001B-NVIDIA-EXECUTION-PATH` -> `T0002B-NVIDIA-MODEL-TOURNAMENT` -> `T0002C-NVIDIA-BASELINE` -> `T0003-FIRST-ARCHITECTURE-TOURNAMENT`.

The first scheduled shift after this decision should implement the NVIDIA adapter through the existing provider-neutral cache/accounting interface and verify both active candidates without running a broad ARC benchmark.

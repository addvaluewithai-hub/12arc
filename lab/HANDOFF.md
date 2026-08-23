# Handoff

Start from `lab/RUNNER.md` and current Git state. Do not continue the old Gemma plan from historical reports.

## Active operator direction

Routine research has pivoted to **NVIDIA NIM**. Repository Actions secret `NVIDIA_API_KEY` is configured; never expose or persist its value.

Active provisional target models:

- `deepseek-ai/deepseek-v4-flash-0731` — provisional primary;
- `nvidia/nemotron-3-ultra-550b-a55b` — provisional escalation/second candidate.

Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` are legacy comparators only. Do not spend routine scheduled calls on them unless a future queue item explicitly requires a controlled comparator/parity study.

Full decision memo: `lab/decisions/2026-08-23-nvidia-model-pivot.md`.

## Fresh operational evidence

A sanitized non-ARC NVIDIA multi-model smoke result is persisted at `lab/recon/nvidia-model-smoke-latest.json`.

Using the same `NVIDIA_API_KEY` and common NVIDIA endpoint:

- Nemotron 3 Ultra returned HTTP 200 / `OK` in ~0.687 s with 21 prompt, 20 completion and 41 total tokens; reasoning content was present.
- DeepSeek V4 Flash returned HTTP 200 / `OK.` in ~0.667 s with 9 prompt, 3 completion and 12 total tokens.
- GPT-OSS-120B timed out after 120 s.
- Gemma 4 31B timed out after 120 s.

The two timeouts were not 401/403 responses, but they are irrelevant to routine research after the operator pivot. The smoke establishes authorization/availability for DeepSeek and Nemotron only; it does not establish sustained NVIDIA RPM/TPM/RPD limits.

## Historical Gemma work

ARC-R013 was the last Gemma-focused research run. It rejected the 8192-output-token repair: on deterministic task `00dbd492`, changing only `max_output_tokens` 2048 -> 8192 caused thought tokens 2,045 -> 8,189 while visible/final output remained empty and finish reason remained `MAX_TOKENS`. The prior 16k Google input-TPM issue was separately manageable through pacing. Preserve these results as history; do not continue debugging Gemma by default.

`T0002-GEMMA-BASELINE` is now **cancelled** by operator direction.

## Next scheduled shift: ARC-R014

Execute exactly one task: `T0001B-NVIDIA-EXECUTION-PATH`.

Promote NVIDIA NIM into the existing provider-neutral target-model layer. Required outcome:

- adapter reads only `NVIDIA_API_KEY` from environment/Actions secret;
- model-facing interface remains provider-neutral;
- request fingerprint/cache includes provider/model/settings and reuses identical calls;
- usage/runtime/error metadata are persisted without secrets;
- live non-ARC smoke through the adapter succeeds for both DeepSeek V4 Flash and Nemotron 3 Ultra;
- tests verify deterministic caching/accounting;
- do not run a broad ARC benchmark in this infrastructure shift.

Then release the claim and stop. Do not chain into the tournament.

## After ARC-R014

`T0002B-NVIDIA-MODEL-TOURNAMENT`: compare **DeepSeek V4 Flash vs Nemotron 3 Ultra only** on a small frozen public-training-derived development slice with controlled prompt/settings/budget. Record exact solves, parseability, reasoning/output tokens, latency, failures, cache behavior and known ARC-specific model exposure. Select the primary model by evidence, not reputation.

Then `T0002C-NVIDIA-BASELINE` establishes the winner's full frozen development baseline. Only after that does `T0003-FIRST-ARCHITECTURE-TOURNAMENT` begin.

Public evaluation remains sealed/milestone-only throughout.

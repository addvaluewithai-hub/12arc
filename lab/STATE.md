# ARC Research Lab — Current State

Updated: 2026-08-23 11:40 EEST
Phase: **PHASE 1 — NVIDIA model selection and baseline establishment**
Latest completed research run: **ARC-R014**
Next research run: **ARC-R015**

## Target model / provider policy

Current preferred hosted provider: **NVIDIA NIM** via repository Actions secret `NVIDIA_API_KEY` (never expose or persist its value).

Provisional active candidates:

- primary: `deepseek-ai/deepseek-v4-flash-0731`;
- escalation/second candidate: `nvidia/nemotron-3-ultra-550b-a55b`.

The designation remains provisional until a small frozen development tournament compares the two under controlled budget/settings. Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` are legacy comparators, not routine research targets.

Operator decision and rationale: `lab/decisions/2026-08-23-nvidia-model-pivot.md`.

## Benchmark discipline

`T0001-BENCHMARK-HARNESS` remains complete. Development feedback uses deterministic public-training-derived splits only; public evaluation remains sealed/milestone-only. Known ARC-specific pretraining on competition-permitted public data is an interpretation/provenance label, not an automatic exclusion.

## ARC-R014 — NVIDIA execution path complete

`T0001B-NVIDIA-EXECUTION-PATH` is **done**.

The provider-neutral target-model layer now includes `NvidiaNIMProvider` using `NVIDIA_API_KEY` only from environment/Actions secret. Cache fingerprints now include provider identity in addition to model/prompt/generation/solver/task/attempt inputs, preventing cross-provider cache collisions. Sanitized accounting records model ID, prompt/completion/total token usage, runtime, finish reason, reasoning-character count, safe usage detail and rate-limit headers when available; reasoning text and secrets are not persisted.

GitHub Actions run `32628504884` completed successfully and ran **31 passing tests** before live verification. Durable evidence is `lab/recon/nvidia-adapter-smoke-latest.json` with `verified=true`, exactly two live provider requests and two deterministic cache hits.

Observed non-ARC adapter results:

- DeepSeek V4 Flash: resolved exact requested model, visible `OK`, 19 input / 2 output / 21 total tokens, 7.423069927 s live runtime, then identical request served from cache.
- Nemotron 3 Ultra: resolved exact requested model, visible `OK`, 31 input / 36 output / 67 total tokens, 2.2212853519999953 s live runtime, 146 reasoning characters observed without storing reasoning text, then identical request served from cache.

Total ARC-R014 live usage: **2 requests, 50 input tokens, 38 output tokens, 88 total tokens, 9.644355279 s aggregate provider runtime**. No ARC benchmark task was executed and no ARC score was claimed.

Successful responses exposed no rate-limit headers, so sustained NVIDIA RPM/TPM/RPD capacity remains unmeasured. Tiny smoke authorization must not be interpreted as throughput evidence.

## Historical Gemma findings

The unfinished Gemma baseline remains cancelled by operator direction. Historical Google findings are preserved for reproducibility but should not consume routine research budget.

## Queue / current bottleneck

`T0002B-NVIDIA-MODEL-TOURNAMENT` is now the highest-priority **ready** task for ARC-R015.

Run a small frozen public-training-derived development comparison between only DeepSeek V4 Flash and Nemotron 3 Ultra through the verified NVIDIA provider-neutral cache/accounting path. Freeze task IDs, prompt/protocol, generation settings and attempts before calls. Record exact solves, parseability, reasoning/output usage, latency, failures, cache behavior, resource-normalized result and known ARC-specific foundation-model exposure. Select the fixed primary engine by evidence rather than reputation.

Do not run the full NVIDIA baseline until the tournament winner is selected. Do not use public evaluation.

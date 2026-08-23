# ARC Research Lab — Current State

Updated: 2026-08-23 15:09 EEST
Phase: **PHASE 1 — NVIDIA baseline establishment**
Latest completed research run: **ARC-R015**
Next research run: **ARC-R016**

## Target model / provider policy

Current hosted provider: **NVIDIA NIM** via repository Actions secret `NVIDIA_API_KEY` (never expose or persist its value).

ARC-R015 selected **`deepseek-ai/deepseek-v4-flash-0731`** as the fixed primary target model for the next baseline. `nvidia/nemotron-3-ultra-550b-a55b` remains an escalation/research candidate. Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` remain legacy comparators and should not receive routine research budget.

The selection is evidence for competition utility under the frozen direct-JSON protocol, not a broad claim of intrinsic model superiority or clean de-novo ARC reasoning. Foundation-model ARC-specific pretraining/exposure was not independently established by ARC-R015.

## Benchmark / leakage discipline

Development feedback uses deterministic public-training-derived splits only. ARC-R015 used exactly three `dev_validation` tasks: `00dbd492`, `05f2a901`, `0607ce86`. Public evaluation remained sealed and unused.

## ARC-R015 — NVIDIA model tournament complete

Frozen protocol: `lab/experiments/ARC-R015-protocol.json`, manifest SHA-256 `d159e7209e785fa0879d249ffc989dc6092eab996d3c6c1468131f5dce0154d0`.

Provider/model/settings were held fixed except for model ID: NVIDIA NIM; temperature 0.0; top_p 1.0; max_output_tokens 4096; one attempt per test input; direct-JSON solver version `nvidia-direct-json-tournament-v1`.

Result:

- DeepSeek V4 Flash: **1/3 exact tasks (33.3333%)**, 0 parse failures among successful responses, 1 provider timeout, 11,819 successful-response tokens, 51.018667405 s observable successful-response runtime.
- Nemotron 3 Ultra: **0/3 exact tasks**, 3/3 parse failures, all three responses ended `length` at exactly 4096 output tokens, 23,869 tokens, 202.81418594 s runtime.
- Delta: **+1 solve / +33.3333 percentage points** for DeepSeek; new solve `0607ce86`; regressions 0.
- Total: 6 request attempts, 5 successful provider responses, 1 provider failure, 35,688 successful-response tokens, 253.832853345 s observable successful-response runtime.

Adversarial interpretation: the slice is very small; Nemotron's result is primarily a reasoning-budget/answer-emission failure under this protocol, while DeepSeek also exhibited one transport timeout. The comparison therefore selects the baseline engine but does not establish general model superiority.

The Actions cache lived under `/tmp` and was not durable after the job. No repeated identical inference occurred. `lab/results/ARC-R015-cache-manifest.json` preserves request fingerprints and explicitly records that response cache hashes are unavailable rather than fabricating them. Future baseline execution should persist a sanitized durable cache/cache manifest.

Full report: `lab/runs/2026-08-23/ARC-R015.md`. Sanitized raw result: `lab/results/ARC-R015-tournament.json`.

## Queue / current bottleneck

`T0002B-NVIDIA-MODEL-TOURNAMENT` is complete.

Highest-priority eligible next task is `T0002C-NVIDIA-BASELINE`: establish a fully cached reproducible baseline for `deepseek-ai/deepseek-v4-flash-0731` on the frozen development split, with exact task accounting, durable cache evidence, failures, calls/tokens/runtime and no public-evaluation feedback.

`T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until the DeepSeek baseline is established.

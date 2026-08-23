# Handoff

Start from `lab/RUNNER.md` and current Git state. Do not continue the old Gemma plan from historical reports.

## Active operator direction

Routine research uses **NVIDIA NIM** through repository Actions secret `NVIDIA_API_KEY`; never expose or persist its value.

Active provisional candidates:

- `deepseek-ai/deepseek-v4-flash-0731` — provisional primary;
- `nvidia/nemotron-3-ultra-550b-a55b` — provisional second/escalation candidate.

Gemma and GPT-OSS are legacy comparators only unless an explicit future task requires them.

## ARC-R014 completed

`T0001B-NVIDIA-EXECUTION-PATH` is complete. The repository now has a provider-neutral `NvidiaNIMProvider`, provider-aware deterministic cache keys, sanitized usage/runtime/finish/error metadata, and an Actions smoke workflow.

GitHub Actions run `32628504884` completed successfully with **31 passing tests** and live non-ARC verification for both active models. Durable evidence: `lab/recon/nvidia-adapter-smoke-latest.json`.

DeepSeek V4 Flash:
- exact model resolved;
- visible `OK`;
- 19 input / 2 output / 21 total tokens;
- 7.423069927 s live runtime;
- identical second request was a deterministic cache hit.

Nemotron 3 Ultra:
- exact model resolved;
- visible `OK`;
- 31 input / 36 output / 67 total tokens;
- 2.2212853519999953 s live runtime;
- 146 reasoning characters observed but reasoning text was not persisted;
- identical second request was a deterministic cache hit.

ARC-R014 total live budget: 2 provider requests, 50 input tokens, 38 output tokens, 88 total tokens, 9.644355279 s aggregate runtime, plus 2 cache hits. No ARC task/public evaluation task was executed and no ARC score exists for this run.

Successful responses returned no rate-limit headers, so do not assume NVIDIA RPM/TPM/RPD capacity from this smoke.

Full report: `lab/runs/2026-08-23/ARC-R014.md`.

## Next scheduled shift: ARC-R015

Execute exactly one task: `T0002B-NVIDIA-MODEL-TOURNAMENT`.

Design and execute a **small frozen public-training-derived development slice** comparing only DeepSeek V4 Flash and Nemotron 3 Ultra. Before any target-model calls, freeze and persist the task IDs/manifest hash, exact prompt/protocol, generation settings, attempts and per-model call/token budget. Use the verified provider-neutral NVIDIA adapter/cache path.

Measure exact full-task solves, parseability, output/reasoning usage where observable, runtime, provider failures, cache behavior and resource-normalized performance. Explicitly record known ARC-specific foundation-model exposure/provenance so competition utility is not confused with de-novo reasoning attribution.

Select a fixed primary engine only if evidence justifies it. If the result is inconclusive, persist that honestly. Do not chain into the full baseline in the same shift.

## After ARC-R015

`T0002C-NVIDIA-BASELINE` remains blocked until the model tournament selects the engine. Then establish a fully cached frozen development baseline. Only after that should `T0003-FIRST-ARCHITECTURE-TOURNAMENT` begin.

Public evaluation remains sealed/milestone-only throughout.

# ARC Research Lab — Current State

Updated: 2026-08-23 09:24 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R011**
Next research run: **ARC-R012**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only.

## Frozen baseline

The comparator remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring.

## ARC-R011 finding

ARC-R011 isolated the dominant empty-output failure without changing the frozen generation settings. Response telemetry was added to the provider adapter and one fresh deterministic `dev_validation` request was executed on task `00dbd492`, test index 0.

The request used 2,982 input tokens and **2,045 thought tokens**, emitted no candidate/output tokens, had zero visible text, and stopped with **`MAX_TOKENS`** under `max_output_tokens=2048`. Runtime was 43.2723 seconds and total usage was 5,027 tokens. The only candidate part was marked `thought=true`; no final candidate was available for the adapter to extract. Durable evidence: `lab/recon/gemma-empty-output-latest.json`.

A matched re-audit of ARC-R010 artifact `9487805832` found `total_tokens - input_tokens = 2,045` exactly for **113/113** cached responses, with zero visible text throughout. Aggregate generated-but-not-visible usage is 231,085 tokens. Combined with the fresh explicit `thoughts_token_count=2045` and `MAX_TOKENS`, this explains the entire observed empty-output cluster as per-request generation-budget exhaustion by thoughts.

This is separate from quota throughput. ARC-R010 already showed 61-second pacing avoids the prior aggregate 16k input-TPM failure for observed prompts. ARC-R011 shows the current correctness blocker is the frozen 2048 output budget, not RPM, TPM, or a `response.text` extraction defect.

No ARC score is claimed because the full two-attempt/all-test-input baseline remains incomplete.

## Current bottleneck

Before resuming full-split accumulation, run a small matched ablation on the same deterministic request changing exactly one variable: increase `max_output_tokens` while holding model, prompt and sampling fixed. The immediate falsifiable question is whether a larger budget changes the finish mode from `MAX_TOKENS`/thought-only to a non-empty final candidate.

Do not mix in 31B routing yet, do not change multiple generation variables simultaneously, and keep public evaluation sealed.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R012. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

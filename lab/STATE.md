# ARC Research Lab — Current State

Updated: 2026-08-23 20:48 EEST
Phase: **PHASE 1 — NVIDIA baseline establishment / ARC-R016 recovery**
Latest completed research run: **ARC-R015**
Active reserved research run: **ARC-R016**

## Target model / provider policy

Current hosted provider: **NVIDIA NIM** via repository Actions secret `NVIDIA_API_KEY` (never expose or persist its value).

ARC-R015 selected **`deepseek-ai/deepseek-v4-flash-0731`** as the fixed primary target model for baseline establishment. `nvidia/nemotron-3-ultra-550b-a55b` remains an escalation/research candidate. Gemma and GPT-OSS remain legacy comparators and should not receive routine research budget.

## Leakage discipline

ARC-R016 uses only the deterministic public-training-derived `dev_validation` split. Public evaluation remains sealed and unused.

## ARC-R016 frozen baseline contract

Protocol: `lab/experiments/ARC-R016-protocol.json`.
Manifest SHA-256: `97102661ae8ae093dcc4afe3fb0122fbca7b0480893302d5b7a7a1044cb88433`.
Task set: all 174 deterministic `dev_validation` task IDs.
Model/settings: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`; direct JSON; temperature 0.0; top_p 1.0; max_output_tokens 4096; one attempt per test input; no hidden provider retries.

## Execution recovery finding

Initial workflow run `32649224421` completed chunks 0, 1, 2, 4 and 5 successfully and uploaded durable artifacts. Chunk 3 was cancelled at the GitHub Actions 45-minute job timeout while still executing model requests, before its artifact/cache archive could be uploaded. Aggregate therefore did not run and **no complete baseline score exists yet**.

Durable audit: `lab/recon/ARC-R016-workflow-audit.json`.
Run report: `lab/runs/2026-08-23/ARC-R016.md`.

This shift reconciled the stale claim and re-adopted the existing ARC-R016 reservation. It did not allocate ARC-R017. To avoid duplicating the five successful chunks, only failed chunk job `97218147036` was re-run. Recovery job `97234116594` is currently executing the frozen chunk-3 workload in the same workflow run.

Because the first chunk-3 job timed out before upload, its ephemeral cache is unrecoverable; some chunk-3 requests may necessarily be repeated. There is no justification for repeating the five successful chunks.

## Current bottleneck

`T0002C-NVIDIA-BASELINE` remains **ready/incomplete**. The next shift must adopt the existing ARC-R016 reservation and inspect workflow run `32649224421` before issuing any new inference.

If recovery job `97234116594` completed and aggregate persisted `lab/results/ARC-R016-baseline.json`, `lab/results/ARC-R016-cache-manifest.json`, and cache archives, audit those artifacts and close T0002C. If the targeted rerun hits the same timeout, split only chunk 3 into smaller execution units while holding the frozen ARC-R016 task set/model/prompt/settings fixed, reuse the five retained artifacts, and aggregate only when all 174 IDs have durable evidence.

`T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until this baseline is complete.

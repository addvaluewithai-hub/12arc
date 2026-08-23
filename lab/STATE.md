# ARC Research Lab — Current State

Updated: 2026-08-23 21:47 EEST
Phase: **PHASE 2 — first architecture tournament ready**
Latest completed research run: **ARC-R016**
Next research run: **ARC-R017**

## Target model / provider policy

Current hosted provider: **NVIDIA NIM** via repository Actions secret `NVIDIA_API_KEY` (never expose or persist its value).

ARC-R015 selected **`deepseek-ai/deepseek-v4-flash-0731`** as the fixed primary target model. ARC-R016 has now established its frozen direct-JSON baseline. `nvidia/nemotron-3-ultra-550b-a55b` remains an escalation/research candidate. Gemma and GPT-OSS remain legacy comparators and should not receive routine research budget.

## Leakage discipline

ARC-R016 used only the deterministic public-training-derived `dev_validation` split. Public evaluation remained sealed and unused.

## Frozen ARC-R016 baseline comparator

Protocol: `lab/experiments/ARC-R016-protocol.json`.
Manifest SHA-256: `97102661ae8ae093dcc4afe3fb0122fbca7b0480893302d5b7a7a1044cb88433`.
Task set: all 174 deterministic `dev_validation` task IDs.
Model/settings: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`; `nvidia-direct-json-baseline-v1`; temperature 0.0; top_p 1.0; top_k null; max_output_tokens 4096; one attempt per test input; no hidden provider retries.

Final retained baseline metrics:

- exact solved tasks: **45 / 174**;
- exact task accuracy: **25.8621%**;
- 179 provider calls/request records;
- 458,626 input tokens;
- 175,994 output tokens;
- 634,620 total tokens;
- 4,625.097828976 seconds summed model runtime;
- 13 parse failures recorded;
- 10 provider failures recorded;
- 108 wrong-but-parseable tasks recorded;
- zero cache hits during the retained baseline execution;
- 179 durable cache records across six hashed archives.

Evidence: `lab/results/ARC-R016-baseline.json`, `lab/results/ARC-R016-cache-manifest.json`, `lab/results/ARC-R016-cache-archives/`, and `lab/runs/2026-08-23/ARC-R016.md`.

## ARC-R016 recovery note

Initial workflow run `32649224421` completed chunks 0, 1, 2, 4 and 5, while original chunk-3 job `97218147036` hit the GitHub Actions 45-minute job limit before artifact upload. Recovery job `97234116594` succeeded for chunk 3. Aggregate job `97237369824` then downloaded the five original successful artifacts plus the recovered chunk-3 artifact, validated complete frozen coverage, and persisted the final baseline at commit `8143324`.

The unrecoverable ephemeral work from the first cancelled chunk-3 job is execution overhead and is not counted as durable baseline cache evidence. Public evaluation was not used.

## Interpretation

ARC-R016 is a frozen comparator, not a claim that direct JSON is optimal. The 25.86% score reflects model reasoning, prompt/protocol quality, parsing behavior, and provider reliability together. Known ARC-specific foundation-model exposure was not independently established, so this is competition-utility evidence rather than a clean measure of de-novo ARC reasoning.

## Current bottleneck / next task

`T0003-FIRST-ARCHITECTURE-TOURNAMENT` is now **ready** for ARC-R017.

The next shift should compare the frozen ARC-R016 direct-JSON comparator against one structured hypothesis-generation + exact-verification treatment under a matched, controlled development experiment. Do not change multiple unrelated variables. Record exact new solves, regressions, parse/provider effects and resource deltas. Public evaluation remains milestone-only and sealed.

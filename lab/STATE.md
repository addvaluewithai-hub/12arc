# ARC Research Lab — Current State

Updated: 2026-08-23 08:06 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R010**
Next research run: **ARC-R011**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only. The live Gemma execution path was verified in ARC-R003.

## Frozen baseline

The solver protocol remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring. ARC-R010 changed no solver-facing behavior.

## ARC-R010 findings

ARC-R010 audited paced run `32617284889` to completion. With a minimum 61 seconds between uncached live-call starts, the baseline process ran for the full deliberate 42-minute timebox without the previously observed `generate_content_free_tier_input_token_count=16000` 429. It then exited `124` solely because of the process timebox; cumulative cache save, outcome persistence and artifact upload succeeded.

Artifact `9487805832` (`sha256:1265c30c29616943bc005ccead464236ae2f408a43db0420f9597894732c5436`) contains 113 unique cached responses: 313,622 input tokens, 544,707 total tokens and 4,938.450 seconds aggregate provider runtime. Relative to the prior 72-response cache, the paced run added 41 responses, 78,206 input tokens, 162,051 total tokens and 1,816.402 seconds runtime.

Observed single-request input-token counts remain 248..9,634; zero of 113 observed requests is >=16,000 input tokens. This strongly supports that the prior 16k failure was aggregate input-TPM pressure, not an intrinsically oversized observed ARC request. No evidence points to RPM as the blocker in this run. The 16k TPM limit is therefore a throughput constraint that conservative pacing/resume can avoid for the observed request distribution.

However, all 113/113 cached responses still have empty visible text while total token usage is non-zero; recorded output/candidate token fields are null. This is now the dominant correctness blocker. Continuing to spend full-split calls before isolating this response-generation/extraction failure would be wasteful.

No ARC score is claimed because the complete frozen two-attempt/all-test-input baseline has not finished.

## Current bottleneck

The immediate research question is no longer TPM-vs-RPM. It is why `gemma-4-26b-a4b-it` produces/records empty visible responses under the frozen baseline despite substantial total token usage. The next shift should perform a small controlled cached diagnostic on the empty-output cluster, changing one response-generation or extraction variable at a time, before resuming large-scale baseline accumulation.

Do not interpret the partial 113-response cache as ARC accuracy. Keep public evaluation sealed and preserve the fixed baseline comparator.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R011. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

# ARC Research Lab — Current State

Updated: 2026-08-23 01:13 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R003**
Next research run: **ARC-R004**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark state

`T0001-BENCHMARK-HARNESS` is complete. The frozen public-training-derived development split remains authoritative; public evaluation remains milestone-only.

## Gemma execution path

`T0001A-GEMMA-EXECUTION-PATH` is complete as of `ARC-R003`.

The repository now has:

- a provider-neutral target-model request/response interface;
- deterministic SHA-256 request fingerprinting and filesystem caching;
- Google Gen AI provider integration using `GEMINI_API_KEY` only from the environment;
- usage/runtime metadata capture;
- structural smoke validation of provider catalog identity, visible generation and cache reuse;
- race-safe GitHub Actions persistence of sanitized success/failure evidence;
- smoke triggers on execution-path source/test/workflow changes.

Durable live evidence: `lab/recon/gemma-smoke-latest.json`.

Verified workflow run `32601740375` used source commit `120b8a28631e3e0ecb4718e174e3dc9fb50df941` and completed successfully. It resolved `gemma-4-26b-a4b-it` / provider catalog version `001`, produced non-empty text, recorded 25 input tokens, 5 output tokens, 186 total tokens and 3.8003 s live runtime, then reused the identical response from deterministic cache on the second request.

The successful smoke profile is `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=256`. The sampling profile follows Google's current Gemma 4 model-card recommendation; the larger output cap was required because a 64-token diagnostic run consumed 86 total tokens from a 25-token prompt without yielding visible candidate text.

## Current bottleneck

There is not yet a fixed Gemma baseline score on the frozen ARC development split. No ARC performance claim has been made from the infrastructure smoke work.

## Next task

`T0002-GEMMA-BASELINE` is now `ready`.

Establish the fully cached baseline on the frozen public-training-derived development split with exact two-attempt task scoring, fixed generation settings, per-task outputs, calls/tokens/runtime accounting and failure taxonomy. Do not use public evaluation as iterative feedback.

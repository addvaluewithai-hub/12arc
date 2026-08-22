# ARC Research Lab — Current State

Updated: 2026-08-23 00:21 EEST
Phase: **PHASE 0 — infrastructure + benchmark discipline**
Latest completed research run: **ARC-R002**
Next research run: **ARC-R003**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark state

`T0001-BENCHMARK-HARNESS` is complete. The frozen public-training-derived development split remains authoritative; public evaluation remains milestone-only.

## Gemma execution path

`ARC-R002` implemented:

- a provider-neutral target-model request/response interface;
- deterministic SHA-256 request fingerprinting and filesystem caching;
- request usage/runtime metadata capture;
- a Google Gen AI provider adapter;
- a non-ARC smoke command that requires the second identical request to hit cache;
- unit tests for request fingerprints and cache reuse;
- a GitHub Actions smoke workflow using `GEMINI_API_KEY` without committing or printing the secret.

Current Google AI documentation lists `gemma-4-26b-a4b-it` and `gemma-4-31b-it` as live API model options. Isolated local verification of the new cache/fingerprint layer passed 2/2 tests.

## Current bottleneck

The live hosted smoke call has not yet been verified by durable evidence. The workflow was committed, but the connected GitHub surface available to ARC-R002 could not list or dispatch push-triggered runs, and `lab/recon/gemma-smoke-latest.json` was not visible before shift close. Do not claim a successful Gemma API call from ARC-R002.

## Next task

`T0001A-GEMMA-EXECUTION-PATH` remains `ready`: inspect or rerun the GitHub Actions smoke workflow, repair it if needed, and only mark it done after sanitized live evidence exists in Git.

`T0002-GEMMA-BASELINE` remains blocked until T0001A is verified.

# T0001A — Gemma Execution Path

Status: READY

## Mission

Create the authorized target-model execution surface required before the first Gemma benchmark run.

## Deliverables

- provider-independent target-model client interface;
- Google/Gemini-backed Gemma adapter that reads `GEMINI_API_KEY` from the environment/Actions secret only;
- verification of the provider's current live model identifier rather than blindly trusting the repo label;
- deterministic request fingerprinting and cache reuse for identical calls;
- request count, available token usage, latency/runtime and model metadata recording;
- one GitHub Actions smoke workflow using a non-ARC prompt so infrastructure validation cannot be confused with benchmark performance;
- tests proving cache keys change when meaningful request/model/generation inputs change and that secrets are never persisted in cache artifacts.

## Success test

A live authorized non-benchmark smoke call completes through the adapter, is represented by a reproducible cache record/manifest with no secret material, and a repeated identical call can be served from cache without another provider request.

Do not run ARC benchmark tasks in this infrastructure task. Do not report a Gemma ARC score here.

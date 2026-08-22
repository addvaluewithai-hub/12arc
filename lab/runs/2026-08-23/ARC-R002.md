# ARC-R002 — Gemma execution path

Task: `T0001A-GEMMA-EXECUTION-PATH`
Role: `llm-experimenter`
Verdict: **INCONCLUSIVE**

## Hypothesis

A provider-neutral target-model client can call the approved fixed Gemma model through the Gemini API, deterministically cache identical requests, record usage/runtime metadata, and verify a live non-ARC smoke call without exposing the repository secret.

## Frozen inputs

- Primary model label: `gemma-4-26b-a4b-it`
- No ARC task input or public-evaluation data used.
- Smoke prompt is explicitly non-benchmark and requests a fixed marker string.
- One live provider call maximum for an identical request; the second identical request must be served from local cache.

## Work performed

- Added `src/arc_lab/target_model.py` with provider-neutral request/response types, deterministic SHA-256 request fingerprinting, filesystem cache, usage/runtime accounting, and a Google Gen AI provider adapter.
- Added `src/arc_lab/gemma_smoke.py` for a non-ARC smoke call and same-process cache verification.
- Added `tests/test_target_model.py` covering fingerprint sensitivity and one-call cache reuse.
- Added `.github/workflows/gemma-smoke.yml` using `GEMINI_API_KEY` only as an Actions secret, running unit tests, invoking the smoke command, and persisting only redacted metadata.
- Current Google AI developer documentation was checked on 2026-08-23 and lists `gemma-4-26b-a4b-it` and `gemma-4-31b-it` as live model options. The Generate Content API documentation confirms the `models.generate_content` SDK surface used by the adapter.

## Verification

- Isolated local unit verification of the new deterministic request fingerprint/cache behavior: **2/2 passed**.
- No local live provider call was possible because repository secrets are intentionally unavailable outside GitHub Actions.
- The workflow was committed with a push trigger limited to changes of the smoke workflow itself, but the connected GitHub tooling available to this shift could not list/inspect push-triggered workflow runs or dispatch a workflow manually.
- No `lab/recon/gemma-smoke-latest.json` evidence file was visible before shift close, therefore a successful live provider call is **not claimed**.

## Cost / benchmark accounting

- ARC benchmark tasks queried: 0
- Public evaluation exposures: 0
- Verified Gemma API calls observed by this shift: 0
- ARC score claim: none

## Failure / adversarial analysis

The implementation may still fail in hosted execution due to SDK/API differences, repository Actions permissions, secret scope, provider quota, or model availability. A passing local fake-provider cache test cannot establish live API correctness. The absence of persisted smoke evidence is therefore treated as a blocker rather than silently interpreted as success.

## Result

The execution-path implementation is substantially complete, but the task success criterion requires a verified live non-benchmark smoke call. `T0001A` remains `ready` for the next shift to inspect Actions evidence or rerun/repair the smoke path. `T0002-GEMMA-BASELINE` remains blocked.

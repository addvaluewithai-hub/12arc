# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` is complete and remains authoritative for benchmark/split discipline.

`ARC-R002` substantially implemented `T0001A-GEMMA-EXECUTION-PATH` but did **not** satisfy its live-smoke success criterion. Durable work now includes:

- `src/arc_lab/target_model.py` — provider-neutral request/response interface, deterministic request fingerprints, filesystem cache, usage/runtime accounting, and Google Gen AI provider adapter;
- `src/arc_lab/gemma_smoke.py` — non-ARC smoke call with required cache reuse on an identical second request;
- `tests/test_target_model.py` — fingerprint/cache unit coverage;
- `.github/workflows/gemma-smoke.yml` — secret-backed hosted smoke workflow with redacted metadata persistence.

Current Google AI developer documentation lists `gemma-4-26b-a4b-it` and `gemma-4-31b-it` as current API model options. Local isolated verification of the new cache/fingerprint behavior passed 2/2 tests.

However, no successful live Gemma call is claimed. The connected GitHub tooling available during ARC-R002 could not list or manually dispatch push-triggered Actions runs, and `lab/recon/gemma-smoke-latest.json` was not visible before shift close. This could mean the workflow had not completed, failed, or could not push evidence.

Next execute the same highest-priority task `T0001A-GEMMA-EXECUTION-PATH`: first look for `lab/recon/gemma-smoke-latest.json` or inspect the smoke workflow run if the connector exposes it. If evidence is absent, rerun/repair the workflow. Only mark T0001A done after a live non-ARC call is verified with sanitized model/usage/runtime metadata and cache verification. Never expose the secret.

Keep `T0002-GEMMA-BASELINE` blocked until T0001A is complete. Do not use public evaluation as iterative feedback.

# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. The verified Gemma smoke evidence remains `lab/recon/gemma-smoke-latest.json`; do not repeat it unless execution-path code changes or debugging requires it.

`ARC-R008` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE** for benchmark completion. It did not claim an ARC score.

The baseline protocol remains frozen as `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache, exact full-task scoring, and all 174 deterministic `dev_validation` tasks. Public evaluation remains sealed.

ARC-R008 audited the two ARC-R007 runs. Both completed failure. Run `32612165079` failed on Gemini free-tier input-token-per-minute quota (`16000`, model dimension `gemma-4-26b`). Its cache artifact `9486315025` has 57 unique response files, 171,674 input tokens, 288,239 total tokens and 2,471.675 seconds aggregate provider runtime. The six-file artifact from run `32612153608` is a strict fingerprint subset of those 57 files. All 57 cached responses have empty visible `text`; do not convert that partial attempt-level observation into an ARC task score.

ARC-R008 made one primary treatment: quota-resumable orchestration in `.github/workflows/gemma-baseline.yml`. Workflow-file edits no longer trigger baselines; only `lab/triggers/gemma-baseline.request` does. A concurrency group prevents duplicate live runs. The workflow restores the latest cumulative Actions cache, seeds from prior artifact `9486315025` when no Actions cache exists, saves the updated cache under a run-unique key, names audit artifacts by run ID, and records cache-file count in the durable outcome breadcrumb. Solver-facing code and generation settings did not change.

A single request commit `ed9e1cd011bece32c4e3bef7cd72beab12a348a3` launched run `32614602241`. At ARC-R008 cutoff that run had succeeded through checkout, Python setup, install, 23 unit tests, execution-start breadcrumb, pinned public-training-only fetch, cumulative cache restore and seed download. The frozen baseline step was still in progress. No second concurrent ARC-R008 run was observed.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. **Do not trigger another baseline while run `32614602241` is active.** First inspect that run, `lab/recon/gemma-baseline-latest.json`, and its run-namespaced cache artifact. The immediate test is whether the durable cumulative cache grows beyond 57 files. If it grows, continue the exact frozen protocol in a later run; if it does not, isolate cache-save or quota behavior as the next single orchestration variable. Keep the empty-response cluster separate; do not simultaneously change prompt/output budget/response handling.

Full run record: `lab/runs/2026-08-23/ARC-R008.md`.

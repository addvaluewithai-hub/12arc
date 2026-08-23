# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. The verified Gemma smoke evidence remains `lab/recon/gemma-smoke-latest.json`; do not repeat it unless execution-path code changes or debugging requires it.

`ARC-R007` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE** for benchmark completion. It did not claim an ARC score.

The baseline protocol remains frozen as `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache, exact full-task scoring, and all 174 deterministic `dev_validation` tasks. Public evaluation remains sealed.

ARC-R007 made one primary change: durable execution breadcrumbs in `.github/workflows/gemma-baseline.yml`. The workflow now persists `lab/recon/gemma-baseline-latest.json` at run start and at baseline outcome, so absence of `lab/results/ARC-R004-baseline.json` no longer conflates scheduling with target-model execution failure.

This proved Actions scheduling/setup is functional. Run `32612153608` (trigger SHA `95c0d1939a5688c212c9f032f3547096d24d9f78`) passed checkout, setup, install, unit tests, breadcrumb persistence and pinned training-only fetch, then entered the frozen baseline step. Run `32612165079` (trigger SHA `c7900869ab1d46626a6db1342c3554bbdf4eda14`) also reached the same baseline step.

The second run was an accidental duplicate trigger: the workflow-file observability commit itself matched `push.paths`, and ARC-R007 also wrote the dedicated request file. Record this as a negative orchestration/cost result; do not hide or silently ignore duplicate API spend if usage later becomes visible. No cancellation action was available through the connected GitHub surface.

At ARC-R007 cutoff both runs were still `in_progress`. No score, calls, tokens, runtime total, parse failures, new solves or regressions are claimed yet.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. **Do not trigger another baseline while either run is active.** First inspect `lab/recon/gemma-baseline-latest.json` and `lab/results/ARC-R004-baseline.json`; inspect runs `32612153608` and `32612165079` if needed. If a complete result exists, audit all 174 task IDs, two-attempt policy, exact score, parser failures, cache accounting, calls/tokens/runtime and raw per-attempt records before marking T0002 done. If the runs fail, use the durable outcome/log evidence to make one minimal orchestration repair. Before any later trigger, add duplicate-run protection without changing `direct-json-v1`.

Full run record: `lab/runs/2026-08-23/ARC-R007.md`.

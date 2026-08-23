# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. The verified Gemma smoke evidence remains `lab/recon/gemma-smoke-latest.json`; do not repeat it unless execution-path code changes or debugging requires it.

`ARC-R006` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE**. It did not claim an ARC score.

The baseline protocol remains frozen as `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache, exact full-task scoring, and all 174 deterministic `dev_validation` tasks. Public evaluation remains sealed.

ARC-R006 diagnosed a trigger-design weakness and made one orchestration-only repair. `.github/workflows/gemma-baseline.yml` now includes `lab/triggers/gemma-baseline.request` in `push.paths`; request commit `b3e9270e4863d42b734414c643c7b44101f4fe90` was then issued. This allows an execution request without editing workflow source, while result persistence does not retrigger the workflow. No prompt/model/parser/scorer/task/budget setting changed.

The result `lab/results/ARC-R004-baseline.json` was still absent during the observation window, and no commit status context was visible for the request commit. Do not infer workflow failure, success, or Gemma accuracy from that absence.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. First check whether `lab/results/ARC-R004-baseline.json` has appeared. If so, audit completeness, exact score, parsing failures, calls/tokens/runtime and cache accounting before marking done. If not, inspect any available Actions run/log/artifact evidence. Preserve `direct-json-v1`; do not begin architecture experiments until T0002 has durable complete evidence.

Full run record: `lab/runs/2026-08-23/ARC-R006.md`.

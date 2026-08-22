# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. The verified Gemma smoke evidence remains `lab/recon/gemma-smoke-latest.json`; do not repeat it unless execution-path code changes or debugging requires it.

`ARC-R004` worked only on `T0002-GEMMA-BASELINE` and is complete with verdict **INCONCLUSIVE**. It did not claim an ARC score.

The first baseline protocol is now frozen in Git as `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache, and exact full-task scoring. The prompt includes every training input/output pair and one test input and requests only the output JSON grid. Tests explicitly assert that the test output is absent from the prompt.

`.github/workflows/gemma-baseline.yml` fetches only the pinned ARC-AGI-2 public-training directory at `f3283f727488ad98fe575ea6a5ac981e4a188e49`, asserts evaluation data is absent, and targets the complete deterministic `dev_validation` split (174 tasks). On success it persists `lab/results/ARC-R004-baseline.json` with per-task raw target-model text, parsed grids, fingerprints, exact solves and request/token/runtime accounting, and uploads the request cache artifact.

During ARC-R004 the expected result file never became visible and the connected GitHub status surface showed no status/check for the workflow-triggering commit. This may be connector-authored push trigger suppression, scheduling delay, or an early workflow failure. Do not infer anything about Gemma accuracy from this orchestration failure.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. First determine whether the committed workflow ran and inspect its result/logs if available. If it did not run, launch it through an authorized Actions path or make the smallest necessary workflow-trigger repair. Preserve the frozen baseline protocol unless a separately documented correctness repair is necessary. Only mark T0002 done after the full 174-task result is durable and request accounting is complete. Public evaluation remains sealed.

Full run record: `lab/runs/2026-08-23/ARC-R004.md`.

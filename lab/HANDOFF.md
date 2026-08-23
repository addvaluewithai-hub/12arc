# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R017 is complete: REJECT

`hypothesis-train-replay-v1` failed its frozen matched test. DeepSeek direct JSON comparator solved 4/8; treatment solved 1/8, with zero new solves and three regressions. Exact training replay was not sufficient to resolve rule ambiguity, and full-grid replay created output-token failures.

Evidence: `lab/results/ARC-R017-architecture-tournament.json`; finalized report: `lab/runs/2026-08-23/ARC-R017.md`.

## ARC-R018 is active — do not allocate ARC-R019 yet

The stale ARC-R017 reservation was reconciled before this run. `T0004-COMPACT-HYPOTHESIS-SEARCH` is claimed and ARC-R018 is reserved.

Role: **reasoning-systems-inventor**.

Frozen hypothesis: three compact competing rules plus a separate training-only discriminator can recover accuracy without ARC-R017's full-grid replay serialization burden.

Matched treatment `compact-hypothesis-select-v1` uses the same eight deterministic `dev_validation` IDs and fixed NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, temperature 0/top_p 1. Stage 1 max output 3072 tokens; stage 2 max output 512; total configured output allowance 3584/test. The discriminator sees training pairs and rule texts only, never the test input or candidate test grids.

Durable inputs already committed:

- `src/arc_lab/compact_hypothesis_search.py`
- `tests/test_compact_hypothesis_search.py`
- `.github/workflows/r018-compact-hypothesis-search.yml`
- `lab/runs/2026-08-24/ARC-R018.md`
- trigger `lab/triggers/r018-compact-hypothesis-search.request` at commit `cf1c1d4f2164923b2393aff37441145de0a1dd19`

At handoff time, `lab/results/ARC-R018-compact-hypothesis-search.json` had not yet landed. Do **not** invent a score. First look for that durable result/Actions outcome. If it exists, audit exact solves/new solves/regressions/parse failures/provider failures/tokens/runtime, finalize ARC-R018 report/state/queue/run-counter, release the claim/reservation, and stop. If the workflow failed, inspect the actual job evidence and fix only this experiment; do not start a second architecture idea.

Public evaluation remains sealed/milestone-only. Model policy remains DeepSeek primary, Nemotron escalation/research only, Gemma/GPT-OSS legacy comparators.

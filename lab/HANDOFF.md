# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R017 is active; do not allocate ARC-R018 yet

`T0003-FIRST-ARCHITECTURE-TOURNAMENT` is claimed and ARC-R017 is reserved. The first architecture experiment has been implemented and triggered, but its durable result had not landed at the prior shift boundary.

Check first for `lab/results/ARC-R017-architecture-tournament.json` and recent workflow/commit evidence. If the result exists, adopt ARC-R017, analyze exact matched outcome, persist final report/state/queue, release claim/reservation, and stop. If workflow failed, diagnose/recover the same ARC-R017 experiment without changing its frozen contract. Do not silently redesign the treatment while retaining the run ID.

## Frozen experiment

Comparator: ARC-R016 `nvidia-direct-json-baseline-v1`. Treatment: `hypothesis-train-replay-v1`. Fixed model: NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`; temperature 0; top_p 1; top_k null; max_output_tokens 4096; one attempt/test.

Treatment asks for JSON `rule`, `train_predictions`, `test_output`; deterministic code accepts test output only if every train prediction exactly equals its known training output. This is the sole primary architecture change.

Matched slice: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`, all from deterministic public-training-derived dev_validation. Public evaluation is sealed and unused.

Promotion requires >=1 new solve and strictly more treatment solves than comparator on these same IDs. Otherwise a complete matched run is REJECT. Provider failure that prevents matched coverage can make the result INCONCLUSIVE and justify recovery, not invented scores.

Files: `lab/experiments/ARC-R017-protocol.json`, `src/arc_lab/architecture_tournament.py`, `.github/workflows/r017-architecture-tournament.yml`, `lab/runs/2026-08-23/ARC-R017.md`.

Model policy remains DeepSeek primary, Nemotron escalation/research only, Gemma/GPT-OSS legacy comparators.

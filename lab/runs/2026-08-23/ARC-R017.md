# ARC-R017 — First architecture tournament

Task: `T0003-FIRST-ARCHITECTURE-TOURNAMENT`  
Role: **reasoning-systems-inventor**  
Status: **execution launched; result pending**

## Falsifiable hypothesis

Requiring fixed DeepSeek V4 Flash to state one transformation hypothesis and replay that same rule on every training input, then accepting its test grid only when those replay grids exactly equal every known training output, will strictly improve exact task accuracy over the frozen ARC-R016 direct-JSON comparator on the same eight deterministic `dev_validation` tasks.

## Primary treatment

Only the solver protocol changes. Comparator remains ARC-R016 `nvidia-direct-json-baseline-v1`. Treatment is `hypothesis-train-replay-v1`: one model call per test input asks for JSON containing `rule`, `train_predictions`, and `test_output`; deterministic code checks `train_predictions` against every training output and rejects the test candidate unless all replay grids match exactly.

Model and generation remain fixed: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`, temperature 0, top_p 1, top_k null, max_output_tokens 4096, one attempt/test, no public evaluation.

Task slice is the first eight lexicographically ordered IDs from the frozen ARC-R016 `dev_validation` manifest: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

Promotion requires at least one new solve and strictly more solved tasks than the matched ARC-R016 comparator. A completed matched run that does not strictly beat comparator is `REJECT`.

## Durable implementation

Added `src/arc_lab/architecture_tournament.py`, frozen contract `lab/experiments/ARC-R017-protocol.json`, and `.github/workflows/r017-architecture-tournament.yml`. Trigger commit requests execution using repository `NVIDIA_API_KEY`. Workflow fetches only pinned public training data and asserts evaluation data is absent, runs repository tests, executes the eight-task treatment, and persists sanitized result to `lab/results/ARC-R017-architecture-tournament.json`.

## Current evidence

At this shift boundary the result file has not yet appeared on the default branch, so no score, token count, runtime, new solve, or regression is claimed. The ARC-R017 reservation and task claim remain active so a later shift must adopt/reconcile this run rather than allocate ARC-R018 prematurely.

## Adversarial interpretation

This gate may suppress otherwise-correct test guesses if the model cannot serialize exact training replays, so a negative result would reject this particular strict verifier architecture, not structured reasoning in general. Eight tasks are directional evidence only; promotion would require a larger matched confirmation in a later queued task.

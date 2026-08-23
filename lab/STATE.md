# ARC Research Lab — Current State

Updated: 2026-08-23 22:49 EEST
Phase: **PHASE 2 — first architecture tournament executing**
Latest completed research run: **ARC-R016**
Active research run: **ARC-R017**
Next unallocated research run: **ARC-R018**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## ARC-R017 active experiment

`T0003-FIRST-ARCHITECTURE-TOURNAMENT` is claimed and ARC-R017 reserved. Role: **reasoning-systems-inventor**.

Treatment `hypothesis-train-replay-v1` changes one architecture variable: instead of direct test-grid JSON, DeepSeek must emit a concise rule, replay predictions for every training input, and a test output. Deterministic code accepts the test output only when all replay predictions exactly equal the known training outputs. Model, generation budget, attempts, split and scorer remain fixed.

Frozen slice: first eight lexicographic ARC-R016 dev_validation IDs: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

Promotion threshold: at least one new solve and strictly more exact solves than ARC-R016 on those same IDs. Completed matched non-improvement => REJECT.

Implementation and frozen contract are committed; a GitHub Actions execution was triggered using only pinned public training data and repository `NVIDIA_API_KEY`. At the current boundary `lab/results/ARC-R017-architecture-tournament.json` has not yet appeared, so no result is claimed. Keep the claim/reservation until durable evidence lands, then finalize ARC-R017 rather than allocating a new run.

Evidence: `lab/experiments/ARC-R017-protocol.json`, `src/arc_lab/architecture_tournament.py`, `.github/workflows/r017-architecture-tournament.yml`, `lab/runs/2026-08-23/ARC-R017.md`.

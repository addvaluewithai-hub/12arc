# ARC Research Lab — Current State

Updated: 2026-08-24
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R026**
Next unallocated research run: **ARC-R027**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## ARC-R026 max-reasoning direct ablation

`T0012-MAX-REASONING-DIRECT-ABLATION` is complete with verdict **REJECT**.

Frozen treatment versus ARC-R016:

- same 174-task `dev_validation` split;
- same DeepSeek V4 Flash model;
- same direct ARC prompt and exact scorer;
- temperature 0, top_p 1;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- one prediction/test input, with transport recovery accounted separately.

Results:

- primary first attempt: **37/174 = 21.2644%**;
- operational after explicit transport recovery: **41/174 = 23.5632%**;
- frozen comparator: **45/174 = 25.8621%**;
- six new solves versus ARC-R016;
- fourteen first-attempt regressions; ten regressions after transport recovery;
- 234 live calls;
- 458,220 input tokens;
- 146,054 output tokens;
- 604,274 total tokens;
- 57 transport failure events;
- 12 terminal provider failures;
- 1 parse failure;
- successful-output token buckets: 173 `<=4096`, 3 `4097-8192`, 1 `8193-16383`, 0 at the 16384 cap.

The workflow completed under external execution run id `32743684588`. Transport instability materially affected the first-attempt score, but even recovered execution remained four solves below the comparator. The 16K cap was never reached and was rarely relevant. This rejects the bundled maximum direct-inference regime as the main explanation for the current gap; it does not separately identify reasoning effort versus output cap causality.

Report: `lab/runs/2026-08-24/ARC-R026.md`.
Result: `lab/results/ARC-R026-max-reasoning-direct.json`.
Execution status: `lab/executions/ARC-R026.json`.

## Next task

The next highest-priority eligible ready task is **`T0011-CANDIDATE-FAILURE-TAXONOMY`**.

Its purpose is to use persisted ARC-R020/ARC-R021 mechanically verified candidate evidence, with **no new target-model calls**, to classify uncovered tasks by observable transformation/morphology features and derive at least one falsifiable candidate-generator routing or representation hypothesis with exact task IDs and adversarial alternatives.

The next shift should reconstruct Git truth, claim T0011, reserve **ARC-R027**, choose the `failure-analyst` role, and perform exactly one substantive taxonomy/hypothesis task. Do not start additional work in the same shift.

Public evaluation remains sealed.

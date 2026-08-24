# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R026 closed — max-reasoning direct regime rejected

`T0012-MAX-REASONING-DIRECT-ABLATION` is done and ARC-R026 is released.

The external GitHub Actions execution completed and persisted durable evidence. The frozen ARC-R016 comparator remains **45/174 = 25.8621%** on the identical deterministic `dev_validation` split.

ARC-R026 treatment:

- NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- unchanged direct ARC JSON prompt and scorer;
- temperature 0, top_p 1;
- `reasoning_effort=max`;
- `max_output_tokens=16384`;
- one prediction per test input;
- public evaluation sealed.

Observed result:

- first attempt: **37/174 = 21.2644%**;
- after explicit transport recovery: **41/174 = 23.5632%**;
- six new solves versus ARC-R016;
- ten operational regressions versus ARC-R016;
- 234 live calls and 604,274 total tokens;
- 57 transport failure events;
- 12 terminal provider failures;
- 1 parse failure;
- 173 successful outputs used at most 4096 output tokens, only four exceeded 4096, and none hit the 16384 cap.

Verdict: **REJECT** the bundled maximum direct-inference regime as the main explanation for the current direct-baseline gap. Transport failures depressed the first-attempt result, but recovery still finished four solves below ARC-R016, so provider instability does not reverse the decision. Because reasoning effort and output cap changed together, do not infer separate causality from this run.

Durable artifacts:

- `lab/runs/2026-08-24/ARC-R026.md`
- `lab/experiments/ARC-R026-max-reasoning-direct-protocol.json`
- `lab/results/ARC-R026-max-reasoning-direct.json`
- `lab/executions/ARC-R026.json`

No active reservation remains. The next unallocated research run is **ARC-R027**.

## Next shift

Highest-priority eligible ready task is **`T0011-CANDIDATE-FAILURE-TAXONOMY`**, recommended role **failure-analyst**.

Follow `lab/RUNNER.md` exactly. Reconstruct current Git truth, reconcile claims, then if T0011 remains the highest-priority eligible task:

1. claim T0011;
2. reserve ARC-R027;
3. use the persisted ARC-R020/ARC-R021 candidate evidence and comparator-integrity corrections;
4. make no new target-model calls;
5. classify uncovered tasks using observable transformation/morphology features;
6. identify at least one falsifiable candidate-generator routing or representation hypothesis;
7. persist exact task IDs and adversarial alternatives;
8. write the run report and update queue/state/handoff before releasing the claim;
9. stop after that single substantive task.

Do not rely on the corrected-away manual ARC-R021 coverage annotation. Use mechanically verified candidate evidence only.

Public evaluation remains sealed.

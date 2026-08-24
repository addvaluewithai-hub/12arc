# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R021 closed — object/relation prompt rejected

`T0007-OBJECT-RELATION-CANDIDATE-GENERATOR` is done and ARC-R021 is released.

ARC-R020 established the generator/representation bottleneck with candidate coverage 1/8. ARC-R021 changed only candidate-generation representation guidance: explicit object/relation reasoning before emitting the same three hypotheses, with DeepSeek V4 Flash, selector, task slice and budgets frozen.

Result: **REJECT**. One task became newly candidate-covered but one previously covered task regressed, leaving net coverage **1/8**, below the >=3/8 promotion threshold and violating the no-regression condition. Provider failures were 0. Accounting: 14 calls, 37,364 input + 14,112 output = 51,476 total tokens; 0 cache hits. Public evaluation was unused. See `lab/results/ARC-R021-object-relation-generator.json` and `lab/runs/2026-08-24/ARC-R021.md`.

The result is a coverage swap, not a gain. Do not promote the universal object/relation prompt. It does not rule out deterministic object extraction or routing object-centric reasoning only to compatible task morphologies.

## Next shift: ARC-R022

Highest-priority ready task is `T0008-REPRESENTATION-COVERAGE-AUDIT`, role **failure-analyst**. This is deliberately a no-model-call audit. Compare durable ARC-R020 and ARC-R021 candidate evidence to identify the newly covered and regressed task IDs, inspect their candidate rules and public-training task morphology, and formulate a falsifiable criterion for when object-centric representation should be routed versus avoided. Persist the audit and queue the resulting matched experiment. Do not start that experiment in the same shift.

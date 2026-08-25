# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R030 closed — T0015 rule-first overflow ablation rejected

`T0015-RULE-FIRST-OVERFLOW-ABLATION` is complete with verdict **REJECT**. Public evaluation was not used.

Final durable external execution:

- status: `lab/executions/ARC-R030.json` = `complete`;
- result: `lab/results/ARC-R030-rule-first-overflow.json`;
- GitHub Actions run: **32800687395**, conclusion `success`;
- model/provider: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- diagnostic task IDs: `0607ce86`, `06df4c85`;
- candidate-stage output budget: **3072 tokens**;
- attempts: one per test input;
- live calls: **1**;
- cache hits: **1**;
- tokens: **14,366 input / 186 output**;
- provider failures: **0**;
- parse failures: **0**;
- program validation failures: **0**.

Matched result: comparator coverage **0/2**, treatment coverage **0/2**, new coverage **0**, regressions **0**. Both treatment candidate stages were parseable (**2/2**), so the previous length/serialization symptom was removed, but no exact candidate emerged after deterministic execution.

This falsifies the strong local hypothesis that compact serialization alone would recover candidate coverage. Do not repeat the same experiment with a larger token budget: the persisted outputs were tiny relative to the 3072-token cap and parseability is already solved.

Adversarially, this does not falsify every rule-first architecture. The generic schema-v1 IR may be too weak, available primitives may be composable but poorly induced, or the prompt may collapse semantic diversity.

## Next eligible task: T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT

Execute exactly this task next.

Role: **failure-analyst**.

Purpose: use only persisted ARC-R030 programs/results and permitted public-training examples for `0607ce86` and `06df4c85` to determine which bottleneck best explains 2/2 parseability with 0/2 coverage:

1. missing generic DSL/IR expressivity;
2. compositional search/induction failure despite adequate expressivity;
3. prompt-induced candidate collapse/diversity failure.

Constraints:

- no target-model calls are required;
- public evaluation remains sealed;
- do not encode task-specific solutions or hints into the solver;
- distinguish generic primitive insufficiency from search failure mechanically where possible;
- inspect the actual persisted candidate programs, not just aggregate scores;
- produce a failure/primitive audit artifact;
- propose only generic reusable primitive families or representation changes;
- predeclare exactly one matched follow-up ablation with frozen comparator, exact task IDs, one primary change, success threshold, failure diagnostics and resource requirements.

Required lifecycle for next shift:

1. Reconstruct truth from `lab/RUNNER.md`.
2. Claim `T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT`.
3. Reserve **ARC-R031**.
4. Durably write claim and reservation before substantive audit work.
5. Perform only T0016, persist its evidence/report/state/queue/handoff, release claim/reservation, then stop.

Durable ARC-R030 report: `lab/runs/2026-08-25/ARC-R030.md`.

After ARC-R030 closure, there are no active reservations and next unallocated run is **ARC-R031**.

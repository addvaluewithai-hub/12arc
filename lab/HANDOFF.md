# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R033 closed — schema-v2 expressibility audit

`T0018-SCHEMA-V2-EXPRESSIBILITY-ORACLE-AUDIT` completed with zero target-model calls using permitted public ARC-AGI-2 training data only. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R033-schema-v2-expressibility.json` and `lab/runs/2026-08-25/ARC-R033.md`.

Result: **RESEARCH_DIRECTION / REPRESENTATION_INSUFFICIENT**.

The bounded deterministic search enumerated the implemented 27 `lattice_peer_reduce` parameterizations to max depth 4 with state deduplication.

- `0607ce86`: not expressible under current schema-v2. All 27 first-step applications fail at the same generic validation boundary because inferred separator-defined lattice cells are required to have equal size. No deeper program can be reached under the current semantics.
- `06df4c85`: not expressible under current schema-v2. There were zero validation failures, but only two unique reachable states after 54 operator applications and no exact training-consistent program. The current peer-reduction semantics therefore have an extremely small closure for this task; increasing BFS depth alone is not a credible fix.

Do not credit any oracle/research-team program as a target-model solve. No such program was found here anyway.

## Next task: T0019-VARIABLE-SPAN-PARTITION-ABLATION

This is a no-model, one-variable ablation focused only on `0607ce86`.

Change only `infer_lattice` partition validation to permit variable-size separator-defined spans. Freeze the existing 27 `lattice_peer_reduce` parameterizations and max search depth 4. Keep all anti-overfit constraints: no task IDs in DSL semantics, no absolute task-specific coordinates, no task-specific colors, no hand-entered target patterns.

Protocol: `lab/experiments/T0019-variable-span-partition-ablation.json`.

Decision rule:

- valid first-step transition + exact training-consistent program: partition restriction was sufficient for expressibility;
- valid first-step transition but no exact fit: partition blocker is real but region semantics are still insufficient;
- no valid first-step transition: falsify the equal-size restriction as the proximate blocker.

Keep `06df4c85` out of T0019. Its failure mechanism is different and should get a later isolated semantic/operator ablation rather than contaminating this partition test.

Public evaluation remains sealed.

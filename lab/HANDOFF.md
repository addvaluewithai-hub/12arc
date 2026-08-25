# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R032 closed — lattice-region primitive sufficiency rejected

`T0017-LATTICE-REGION-PRIMITIVE-ABLATION` completed under the frozen ARC-R030 comparator controls. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R032-lattice-region.json`, `lab/executions/ARC-R032.json`, and `lab/runs/2026-08-25/ARC-R032.md`.

Result: **REJECT**. The treatment was 2/2 parseable but 0/2 exact candidate coverage, identical to comparator 0/2, so the predeclared success threshold was missed and the explicit falsification condition was met. There were 2 live NVIDIA calls, 0 cache hits, 14,526 input tokens, 419 output tokens, 57.807 s model runtime, 0 provider failures and 0 parse failures.

The new representation was actually used: five normalized program ASTs were generated and `lattice_peer_reduce` appeared seven times. This rules out the trivial explanation that DeepSeek never emitted the new operator.

Per-task evidence differs:

- `0607ce86`: response parsed, then executor failed closed with `inferred lattice cells must have equal size`. Treat this as a partition-model / validation-boundary signal.
- `06df4c85`: response parsed and executed lattice-peer reductions, but all candidates were exact-wrong. Treat this as unresolved generic semantics vs induction/search.

## Next task: T0018-SCHEMA-V2-EXPRESSIBILITY-ORACLE-AUDIT

No model calls. On permitted public-training pairs only, use bounded deterministic enumeration/search to test whether generic schema-v2 can represent exact training-consistent programs for `0607ce86` and `06df4c85` under the existing anti-overfit constraints.

Do not credit any research-team/oracle program as a target-model solve. The audit is diagnostic only.

Decision rule:

- If no exact generic schema-v2 program exists for a task, classify representation/partition semantics as insufficient and isolate one generic missing or incorrect assumption before proposing another matched ablation.
- If an exact generic schema-v2 program does exist, preserve it only as oracle evidence and classify ARC-R032 primarily as induction/search failure for that task; then predeclare a search/prompt intervention that leaves the DSL frozen.

Keep public evaluation sealed and do not increase token budget as a substitute for resolving this distinction.

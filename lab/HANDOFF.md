# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R035 closed — shared-overlap alignment ablation

`T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION` completed with zero target-model calls using permitted public ARC-AGI-2 training data only. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R035-variable-span-overlap.json` and `lab/runs/2026-08-25/ARC-R035.md`.

Result: **PARTIAL_ALIGNMENT_BLOCKER_REMOVED_SEMANTICS_INSUFFICIENT**.

T0020 kept ARC-R034 variable-span separator inference, all 27 `lattice_peer_reduce` parameterizations, task `0607ce86`, deterministic state-deduplicated BFS, and max depth 4 frozen. The only semantic change was peer-coordinate alignment: reduce inside the shared minimum-height/minimum-width overlap and preserve non-overlap cells.

Mechanical result:

- valid first-step transitions: **27/27**, versus 0/27 in ARC-R034;
- exact training-consistent program: none;
- unique reachable states: **798**;
- programs expanded: **237**;
- operator applications: **6,399**;
- execution failures: **216**, all surfaced as `ValueError`;
- target-model calls: **0**.

Thus shared-overlap alignment removes the specific unequal-shape `IndexError` blocker but is not sufficient for bounded expressibility. Do not revert this to a claim that variable spans failed; the representation now executes broadly and the remaining problem is semantic/invariant closure.

GitHub Actions run `32847574881` completed successfully and persisted the result. An earlier attempt `32847394781` failed before tests because the task-claim write had left `queue.json` malformed; that registry syntax was repaired on the same ARC-R035 reservation without changing experimental semantics.

## Next task: T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT

This is a no-model diagnostic on `0607ce86`. Keep all ARC-R035 semantics frozen.

Protocol: `lab/experiments/T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT.json`.

Required work:

- classify each of the 216 deeper-search failures by exact cause/invariant;
- retain program paths for all reachable states;
- rank reachable multi-training states by deterministic cell-error distance to the training outputs;
- determine whether evidence isolates separator destruction, wrong overlap anchoring, or missing region-local conditional semantics;
- predeclare exactly one matched ablation only if one mechanism dominates reproducibly.

If the evidence remains mixed, report ambiguity rather than inventing a semantic primitive.

Keep `06df4c85` separate. Public evaluation remains sealed.

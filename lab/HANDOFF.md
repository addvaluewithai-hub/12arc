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

## Active task: T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT

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

## Post-T0021 direction: T0022 multi-candidate critique/verify loop

The operator has explicitly requested that the lab stop relying on one single answer from the model and explore multiple reasoning/generation paths, critique, critique-of-critique, repair, and Python-based selection. This is now documented as a predeclared direction, not a completed result.

New durable planning artifacts:

- `lab/design/MULTI-CANDIDATE-CRITIQUE-VERIFY.md`
- `lab/experiments/T0022-multi-candidate-critique-verify-loop.json`
- `lab/registry/proposed-tasks/T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP.json`

After T0021 is resolved and the queue is safe to update, convert the proposed task into the active queue unless T0021 produces stronger contrary evidence. The experiment should test a generate -> critique -> critique-the-critique -> repair -> Python verify/select loop.

Core rule: the model proposes; Python judges. Model critique is not evidence. Selection must be based on deterministic parsing, execution, exact training-pair scoring, cell-error distance, structural preservation, normalized-IR deduplication, and matched comparator deltas.

Preferred first target: `06df4c85`, because ARC-R032 already showed lattice programs executing there while remaining exact-wrong. Use `0607ce86` only after T0021 produces durable failure taxonomy or freezes a compatible mechanism.

If the first loop variant fails, keep evolving the same area one variable at a time: candidate diversity prompt, critic prompt, repair budget, IR translation constraints, or deterministic selector ranking. Do not repeat the same prompt and do not invent outputs, scores, CI success, provider behavior, or public-evaluation feedback.

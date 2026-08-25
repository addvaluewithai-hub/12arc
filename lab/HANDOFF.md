# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R034 closed — variable-span partition ablation

`T0019-VARIABLE-SPAN-PARTITION-ABLATION` completed with zero target-model calls using permitted public ARC-AGI-2 training data only. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R034-variable-span-partition.json` and `lab/runs/2026-08-25/ARC-R034.md`.

Result: **REJECT / FALSIFIED_NO_VALID_FIRST_STEP**.

T0019 changed only lattice partition inference to permit variable-size separator-defined spans while freezing the existing 27 `lattice_peer_reduce` parameterizations and max search depth 4 on `0607ce86`.

The equal-size validation error disappeared, but no valid transition became reachable:

- valid first-step transitions: 0;
- operator applications: 27;
- execution failures: 27/27, all `IndexError`;
- unique reachable states: 1;
- exact training-consistent program: none.

This reveals a deeper generic structural assumption in the frozen peer reducer: it indexes every peer region with common relative coordinates derived from one region, which is invalid when separator-defined regions have unequal extents. Do not interpret ARC-R034 as evidence against variable-span partitioning in every richer representation; it rejects the claim that relaxing the partition check alone is sufficient.

Dedicated GitHub Actions run `32841175739` / job `97780790181` completed successfully, including claim/reservation validation, implementation tests, pinned-public-training fetch, bounded audit, and durable result persistence.

## Next task: T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION

This is a no-model one-variable ablation focused only on `0607ce86`.

Keep the ARC-R034 variable-span partition inference, all 27 peer-reduction axis/reducer/write parameterizations, deterministic BFS/state deduplication, and max depth 4 frozen. Change only coordinate alignment: for each peer set, reduce over the shared overlap domain defined by minimum peer height/width, and preserve cells outside that overlap unchanged.

Protocol: `lab/experiments/T0020-variable-span-overlap-alignment-ablation.json`.

Decision rule:

- valid first-step transition + exact training-consistent program: overlap alignment is sufficient for bounded expressibility;
- valid first-step transition but no exact fit: alignment blocker is removed but semantics remain insufficient;
- no valid first-step transition: falsify shared-overlap alignment as the proximate remaining blocker.

Keep `06df4c85` out of T0020. Its failure mechanism remains the separate semantic-closure problem established by ARC-R033.

Public evaluation remains sealed.

# ARC-R034 — T0019 Variable-Span Partition Ablation

Date: 2026-08-25
Role: program-synthesis-researcher
Verdict: **REJECT / FALSIFIED_NO_VALID_FIRST_STEP**

## Question

Does the equal-size separator-span restriction explain the schema-v2 reachability failure on public-training diagnostic `0607ce86`?

## Predeclared hypothesis and comparator

Protocol: `lab/experiments/T0019-variable-span-partition-ablation.json`.

- Baseline: ARC-R033 schema-v2 bounded oracle audit.
- Primary change: remove only the requirement that separator-defined row/column spans have equal sizes.
- Frozen controls: the existing 27 `lattice_peer_reduce` axis/reducer/write parameterizations, deterministic BFS with state deduplication, and maximum depth 4.
- Task set: exactly `0607ce86`, using permitted public ARC-AGI-2 training data from pinned source commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`.
- Target model: none.
- Target-model calls/tokens/runtime: 0 / 0 / 0.
- Public evaluation: not used.

## Implementation

`src/arc_lab/lattice_region.py` now permits unequal separator-defined spans in lattice inference while leaving peer-reduction semantics unchanged. `src/arc_lab/variable_span_partition_audit.py` reuses the same 27 operators and depth-4 BFS and records first-step validity plus execution-failure type. Tests cover variable-span inference/reassembly and audit classification.

A dedicated no-model GitHub Actions workflow validated the active claim/reservation, ran the implementation tests, fetched only the pinned public training corpus, executed the bounded oracle audit, and persisted the result. GitHub Actions run `32841175739`, job `97780790181`, completed successfully.

## Result

Durable result: `lab/results/ARC-R034-variable-span-partition.json`.

- Exact training-consistent program: **none**.
- Valid first-step transitions: **0**.
- Operator applications: **27**.
- Execution failures: **27/27**.
- Failure type: **27 IndexError**.
- Programs expanded: **1**.
- Unique reachable states: **1**.
- Search depth reached beyond initial state: **none**.
- Target-model calls: **0**.

The predeclared success and partial-success conditions both fail. By the protocol's decision rule, the equal-size validation restriction is not sufficient as the proximate blocker when the rest of the schema-v2 peer semantics are frozen.

## Failure analysis

ARC-R033 stopped all 27 first steps at explicit equal-size validation. ARC-R034 removes that check, but the same 27 first steps now fail at a deeper invariant: `lattice_peer_reduce` indexes each peer region at a common relative `(r,c)` derived from one reference region. Variable-size regions therefore produce out-of-bounds accesses before any valid transformed state is reached.

Failure cluster: **variable-region shape alignment / shared-coordinate semantics**.

## Adversarial interpretation

This result does **not** show that variable-span partitioning is useless in a richer DSL. It shows that changing partition validation alone is insufficient because frozen peer-reduction semantics contain a second equal-shape assumption. Expanding both partitioning and alignment at once in T0019 would have violated the one-variable ablation contract.

## Next falsifiable task

Predeclared `T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION`: keep variable-span partitioning and all 27 operator parameterizations frozen, and change only peer coordinate alignment to operate on the shared overlap domain of selected peer regions while preserving non-overlap cells. Re-run the same bounded depth-4 oracle on `0607ce86`.

No second substantive task was executed in ARC-R034.

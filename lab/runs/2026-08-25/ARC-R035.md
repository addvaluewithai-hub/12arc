# ARC-R035 — T0020 Variable-Span Overlap Alignment Ablation

- Date: 2026-08-25
- Role: `program-synthesis-researcher`
- Task: `T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION`
- Benchmark task: `0607ce86`
- Data: permitted public ARC-AGI-2 training data only, pinned commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`
- Public evaluation used: **no**
- Target-model calls: **0**
- Comparator: ARC-R034 variable-span partition semantics

## Hypothesis

After variable-size separator spans are permitted, the remaining `0607ce86` blocker is the frozen peer reducer's assumption that every region shares identical relative-coordinate extents. Restricting peer reduction to the generic shared overlap domain while preserving non-overlap cells will yield valid transitions and may recover an exact training-consistent program.

## Primary treatment

Changed only peer coordinate alignment: each peer set reduces within the minimum shared peer height/width. Cells outside that overlap remain unchanged. Variable-span inference, the 27 axis/reducer/write parameterizations, deterministic state-deduplicated BFS, task ID, and max depth 4 stayed frozen.

## Verification

GitHub Actions run `32847574881` completed successfully after a registry-syntax recovery on the same reserved run. The successful attempt passed claim/reservation validation, implementation tests, pinned public-training fetch, bounded oracle execution, and durable result persistence. The initial attempt `32847394781` stopped before tests because `lab/registry/queue.json` was malformed during the claim write; that operational defect was repaired without changing experimental semantics.

## Result

Verdict: **PARTIAL_ALIGNMENT_BLOCKER_REMOVED_SEMANTICS_INSUFFICIENT**.

- valid first-step transitions: **27/27**
- exact training-consistent program within depth 4: **none**
- unique reachable states: **798**
- programs expanded: **237**
- operator applications: **6,399**
- execution failures: **216**, all `ValueError`
- depth-state counts: depth 0 = 1, depth 1 = 12, depth 2 = 45, depth 3 = 179, depth 4 = 561
- target-model calls: **0**

Compared with ARC-R034, where 0/27 first-step applications survived and all failed with `IndexError`, shared-overlap alignment mechanically removes the proximate unequal-shape indexing blocker. It is not sufficient for expressibility: exhaustive bounded search still found no exact program.

## Failure analysis

The treatment produces a much larger reachable state graph, so the previous inability to execute a first step is resolved. The remaining uncertainty is semantic closure: either the 27 peer reducers cannot express the required selective transformation, the top-left overlap anchor is the wrong generic relation, or later transformations destroy invariants needed for lattice inference. The 216 `ValueError` failures require exact reason classification before another semantic primitive is justified.

## Adversarial interpretation

Restoring executable transitions is weaker than restoring the target mapping. The large state-space increase could simply explore many irrelevant states. An exact miss at depth 4 does not prove impossibility at every depth, but under the frozen bounded protocol it rejects sufficiency of shared-overlap alignment plus the existing operator family. We should not attribute the remaining failure to one specific missing primitive without mechanical diagnostics.

## Next task

Predeclared `T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT`: a no-model diagnostic that classifies the 216 failures by exact reason and ranks all reachable states by deterministic cell-error distance to the training targets, preserving program paths. It must isolate a reproducible dominant mechanism before proposing one matched semantic ablation.

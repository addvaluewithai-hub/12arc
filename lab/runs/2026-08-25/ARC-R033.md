# ARC-R033 — T0018 Schema-v2 Expressibility Oracle Audit

Date: 2026-08-25
Role: program-synthesis-researcher
Verdict: RESEARCH_DIRECTION / REPRESENTATION_INSUFFICIENT
Target-model calls: 0
Public evaluation used: no

## Hypothesis

The ARC-R032 failures can be separated mechanically: if a bounded generic schema-v2 program fits all permitted public-training pairs for a diagnostic task, the live failure is primarily induction/search; if no program exists in the bounded language, representation/partition semantics remain insufficient.

## Frozen scope

Tasks: `0607ce86`, `06df4c85` from permitted public ARC-AGI-2 training data only.

Search: deterministic BFS to depth 4 over the 27 `lattice_peer_reduce` parameterizations implemented by schema-v2. Anti-overfit constraints remained: no task IDs in DSL semantics, no absolute task-specific coordinates, no task-specific color constants, no hand-entered target patterns.

## Durable result

`lab/results/ARC-R033-schema-v2-expressibility.json` was persisted by the GitHub Actions audit. It records zero target-model calls and no public-evaluation use.

- `0607ce86`: not expressible in the bounded schema-v2 search. The initial state was the only reachable state; all 27 first-step operator applications failed validation because current lattice inference requires equal-size separator-defined cells.
- `06df4c85`: not expressible in the bounded schema-v2 search. Search expanded two states, made 54 operator applications, encountered zero validation failures, but reached only two unique states and no exact training-consistent program.

## Interpretation

This rejects the strongest remaining explanation that ARC-R032 failed only because DeepSeek could not induce an already-sufficient schema-v2 program. For both diagnostics, the bounded implemented language itself lacks an exact training-consistent program.

The mechanisms differ:

1. `0607ce86` is blocked at the partition/validation boundary before any region semantics can operate. Equal-size lattice cells are an unjustified structural restriction for this task family.
2. `06df4c85` passes partition validation, but the peer-reduction operator family collapses quickly to a tiny reachable-state closure and cannot realize the mapping. This points to missing region-selection / relational transfer semantics rather than search depth alone.

The audit is diagnostic only; no oracle program is credited as a target-model solve.

## Adversarial interpretation

The result is bounded, not a theorem about every conceivable schema-v2 extension. The search enumerated exactly the implemented 27 `lattice_peer_reduce` parameterizations, with identity implicit as the initial state, to depth 4. A deeper search cannot rescue `0607ce86` because no first step is valid under current partition inference. For `06df4c85`, the reachable-state graph had only two unique states under the implemented operator family, so additional depth would revisit already-seen states rather than discover a new output.

Thus the actionable uncertainty is semantic/representational, not token budget or generic BFS depth.

## Next falsifiable task

Predeclare `T0019-VARIABLE-SPAN-PARTITION-ABLATION`: change only lattice partition inference to permit variable-size separator-defined spans while freezing the existing 27 peer-reduction semantics. Run the same deterministic oracle search on `0607ce86` only. Success: at least one valid first-step transition and an exact training-consistent program within depth 4. Partial success: valid transitions but no exact program, which isolates remaining semantic insufficiency. Failure: partition relaxation still yields no valid transition, falsifying the current partition-boundary diagnosis.

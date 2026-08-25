# ARC-R031 — Rule-first semantic primitive audit

- Task: `T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT`
- Role: failure-analyst
- Date: 2026-08-25
- Target-model calls: 0
- Public evaluation: sealed / unused
- Source evidence: `lab/results/ARC-R030-rule-first-overflow.json`, `src/arc_lab/rule_first.py`, and pinned public ARC-AGI-2 training examples for `0607ce86` and `06df4c85`.

## Hypothesis

ARC-R030's 2/2 parseability with 0/2 coverage is primarily explained by missing generic IR expressivity rather than output serialization, and this can be established mechanically from invariants of schema-v1 against the public-training input/output mappings.

## Frozen comparator

ARC-R030: same two task IDs, DeepSeek V4 Flash, NVIDIA NIM, one attempt per test input, temperature 0, top_p 1, no reasoning-effort override, 3072 candidate tokens, deterministic execution and exact candidate-oracle scoring. Comparator coverage was 0/2.

## Audit

Schema-v1 supports only `identity`, whole-grid rotations, whole-grid flips, and global `recolor`. These operations compose into whole-grid spatial permutations plus global substitutions. They have no region selection, local predicate, repeated-cell abstraction, conditional write, peer comparison, or local copy/reconstruction semantics.

For `0607ce86`, permitted training pairs preserve a repeated/lattice-like macrostructure while selectively correcting noisy cells. The same colors are retained at some locations while occurrences at other locations are altered. A global recolor cannot make such occurrence-selective changes, and a whole-grid dihedral transform cannot repair local corruption while preserving the surrounding aligned template. Therefore the observed mapping is outside schema-v1.

For `06df4c85`, the canvas is explicitly divided by repeated separator lines into regular cells. The outputs selectively fill/propagate payloads into some previously empty cell interiors while leaving other zeros and separators unchanged. Any schema-v1 recolor that changes zero would change all zeros globally; rotations/flips only permute existing content. Therefore the demonstrated region-conditional propagation is outside schema-v1.

Classification: both tasks => `missing_generic_dsl_expressivity` with high confidence. Search weakness or prompt candidate collapse may coexist, but they are not needed to explain failure because the current representation has no exact program for the observed mappings.

## Generic primitive-family proposal

Introduce one reusable **lattice-region map/reduce** family: infer regular separator/periodic cell partitions; extract cell payloads; aggregate aligned peer cells with generic equality/majority operations; conditionally write derived payloads using generic predicates such as empty/nonempty/equality-to-peer; and reassemble while preserving separators. No task IDs, absolute task coordinates, fixed task colors, or hand-entered target patterns are allowed.

## Predeclared follow-up

`lab/experiments/T0017-lattice-region-primitive-ablation.json` freezes the ARC-R030 comparator, model, task IDs, 3072-token candidate budget, one attempt, temperature/top_p, scorer and public-eval seal. The sole treatment is adding the lattice-region primitive family. Success requires 2/2 parseable and >=1/2 mechanically verified candidate coverage. 2/2 parseable with 0/2 coverage falsifies the sufficiency hypothesis.

## Failure analysis and adversarial interpretation

This audit establishes insufficiency of schema-v1, not sufficiency of the proposed primitive family. A richer IR could remain unused, model induction could still fail, or the proposed abstraction could be too broad. The follow-up therefore keeps model-generation controls frozen and measures program usage/diversity plus exact coverage.

## Verdict

`RESEARCH_DIRECTION`: missing generic expressivity is a necessary bottleneck on both ARC-R030 diagnostic tasks. Queue exactly one next experiment family, T0017, rather than increasing output budget or repeating serialization work.

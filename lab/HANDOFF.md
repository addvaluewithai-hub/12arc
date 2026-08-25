# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R031 closed — schema-v1 expressivity is insufficient

`T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT` completed as a no-model failure audit. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R031-semantic-primitive-audit.json` and `lab/runs/2026-08-25/ARC-R031.md`.

The decisive mechanical fact is that `src/arc_lab/rule_first.py` schema-v1 supports only identity, whole-grid rotations/flips, and global recolor. Those operations cannot condition edits on region/cell membership or change only selected occurrences of a color while retaining other occurrences unchanged.

On permitted public-training examples:

- `0607ce86` requires selective local repair inside repeated/lattice-like structure; same colors survive in some locations while noisy occurrences are corrected elsewhere.
- `06df4c85` uses a separator-defined lattice and selectively fills/propagates payloads into some cells while preserving other zeros and separators.

Classification: **2/2 missing generic DSL/IR expressivity**, high confidence. Search/induction or prompt diversity may still be weak, but no search over schema-v1 can represent the observed mappings.

## Next task: T0017-LATTICE-REGION-PRIMITIVE-ABLATION

Protocol: `lab/experiments/T0017-lattice-region-primitive-ablation.json`.

Primary change only: add a reusable lattice-region map/reduce primitive family with inferred regular cell partitions, region extraction/reassembly, peer equality/majority aggregation, and generic conditional writes. Strictly forbid task IDs, absolute task coordinates, task-specific color constants, or hand-entered target patterns.

Before target-model calls, implement and test the primitive generically and fail closed. Then run the matched two-task ablation against ARC-R030 using exactly `0607ce86` and `06df4c85`, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, one attempt/test, temperature 0, top_p 1, no reasoning override, and 3072 candidate output tokens.

Success: 2/2 parseable and >=1/2 mechanically verified exact candidate coverage. If 2/2 parseable remains 0/2 coverage, reject primitive-family sufficiency and shift attention toward induction/search or a different representation.

Do not increase token budget as a substitute; ARC-R030 already removed the serialization/length failure. Keep public evaluation sealed.

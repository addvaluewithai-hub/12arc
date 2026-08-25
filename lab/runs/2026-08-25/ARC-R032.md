# ARC-R032 — Lattice-region primitive ablation

- Task: `T0017-LATTICE-REGION-PRIMITIVE-ABLATION`
- Role: program-synthesis-researcher / falsifier
- Date: 2026-08-25
- Provider/model: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`
- Split/task IDs: deterministic public-training-derived `dev_validation`; exactly `0607ce86`, `06df4c85`
- Comparator: ARC-R030 rule-first treatment, exact candidate coverage 0/2
- Attempts/search budget: 1 model attempt per test input
- Generation: temperature 0.0, top_p 1.0, no reasoning override, max_output_tokens 3072
- Requests: 2 live calls, 0 cache hits
- Tokens: 14,526 input + 419 output = 14,945 total
- Runtime: 57.807374738 s model runtime
- Parse failures: 0
- Provider failures: 0
- Public evaluation: sealed / unused

## Hypothesis

Adding one generic lattice-region map/reduce primitive family to the validated rule-first IR will recover exact candidate coverage on at least one of the two ARC-R030 diagnostic tasks without changing model, prompt budget, attempts, scorer, or unrelated solver behavior.

## Primary change

Schema-v2 adds generic inferred lattice-region peer map/reduce semantics with anti-overfit constraints: no task IDs, task-specific coordinates, task-specific colors, or hand-entered target patterns. Model, task set, budget, sampling, deterministic execution, exact candidate-oracle scoring, and comparator-integrity boundary remain frozen.

## Result

**REJECT.** Treatment was 2/2 parseable but 0/2 exact candidate coverage, identical to comparator 0/2. New coverage: 0. Regressions: 0. The predeclared success threshold (2/2 parseable and >=1/2 exact coverage) was not met, and the predeclared falsification condition (2/2 parseable with 0/2 coverage) was met.

The model did use the richer representation: five normalized program ASTs were produced and `lattice_peer_reduce` appeared seven times. This is therefore not a simple case where the new primitive family was absent from the candidate language or never selected syntactically.

Per-task failure evidence:

- `0607ce86`: model response parsed successfully, but execution failed closed with `inferred lattice cells must have equal size`. This isolates a representation/inference-boundary problem: the candidate selected the lattice abstraction but the executor's inferred partition constraints could not validate the task geometry.
- `06df4c85`: model response parsed and executed, including generic `lattice_peer_reduce`, but no candidate matched the exact output. This is compatible with wrong reducer/write semantics, insufficient primitive expressivity, or induction/search selecting the wrong composition.

## Failure clusters

1. **Partition-model mismatch / validation boundary** — 0607ce86. The current lattice inference assumes equal-sized inferred cells; that assumption can reject a candidate before semantic scoring.
2. **Semantic composition / induction failure** — 06df4c85. Primitive usage occurred, yet executed candidates remained wrong.
3. **Unresolved schema-v2 sufficiency** — the experiment shows the proposed primitive family is not sufficient under the frozen model-generation protocol, but does not yet tell us whether an exact generic schema-v2 program exists for the permitted training mappings.

## Adversarial interpretation

A 0/2 result does not prove that lattice-region abstractions are irrelevant. It can arise because the DSL still lacks a necessary generic operation, because lattice inference is too restrictive, or because DeepSeek failed to induce a valid composition despite the representation being expressive enough. Conversely, simply adding more primitives risks post-hoc DSL overfitting. The next uncertainty-reducing step should therefore separate **representation expressibility** from **model induction/search** without spending new model calls.

## Next task

Queue `T0018-SCHEMA-V2-EXPRESSIBILITY-ORACLE-AUDIT`: on permitted public-training pairs only, mechanically test whether generic schema-v2 programs can fit the two diagnostic mappings using bounded deterministic enumeration/search and anti-overfit constraints. If no exact training-consistent program exists, classify missing/incorrect representation semantics and propose one generic change. If an exact program exists for a task, preserve it only as oracle evidence and classify the live failure primarily as induction/search; do not credit research-team programs as model solves.

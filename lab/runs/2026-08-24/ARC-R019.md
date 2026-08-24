# ARC-R019 — ARC-R018 candidate-coverage vs selector audit

Task: `T0005-R018-FAILURE-AUDIT`  
Role: **failure-analyst**  
Status: **complete — INCONCLUSIVE on requested attribution; measurement blind spot identified**

## Falsifiable hypothesis

Durable ARC-R018 evidence is sufficient to determine whether selector error or candidate-set omission is the dominant cause of parseable treatment failures.

No target-model calls were required or made. This shift changes no solver behavior and uses no public evaluation.

## Evidence audited

Primary durable result: `lab/results/ARC-R018-compact-hypothesis-search.json`. Implementation contract: `src/arc_lab/compact_hypothesis_search.py`.

ARC-R018 had eight tasks. Six reached parseable candidate generation and selector output; two candidate generations hit the 3072-token cap and were unparseable (`0607ce86`, `06df4c85`). Of the six parseable tasks, two solved (`0bb8deee`, `0d3d703e`) and four failed (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`).

Among the three comparator regressions, `0607ce86` is attributable to candidate serialization/parse failure. The other two regressions, `00dbd492` and `05f2a901`, parsed both stages and selected indices 0 and 1 respectively, but remained wrong.

## Key finding: attribution is not identifiable from persisted evidence

The ARC-R018 runner parses three objects containing `rule` and `test_output`, then sends only their rule texts to the selector. However, the durable result persists only candidate-stage metadata (`parsed`, tokens, runtime, finish reason) and selector metadata including `selected_index`. It does **not** persist the three candidate grids/rules or an oracle vector indicating which candidate grids match the known public-training-derived test output.

Therefore a parseable wrong selected output has two observationally equivalent explanations:

1. a correct candidate existed among the two unselected candidates and the selector chose wrongly; or
2. all three candidates were wrong, so no selector could recover the task.

The current artifact cannot distinguish these cases. Claiming either mechanism retrospectively would fabricate evidence.

## Quantification

Across all eight tasks:

- candidate parse failures: **2/8**;
- parseable but unsolved: **4/8**;
- parseable and solved: **2/8**.

Across the three regressions:

- candidate serialization/parse failure: **1/3** (`0607ce86`);
- parseable but candidate-coverage vs selection attribution unidentifiable: **2/3** (`00dbd492`, `05f2a901`);
- selector error proven from durable evidence: **0/3**;
- candidate omission proven from durable evidence: **0/3**.

This rejects the shift hypothesis that existing durable evidence is sufficient for the requested classification.

## Adversarial review

It would be tempting to call the two parseable regressions selector failures because a selector index exists. That is invalid: selected-index metadata proves only that ranking completed, not that a correct alternative was present. Conversely, the treatment's low aggregate accuracy does not prove poor candidate coverage because unselected candidates were never scored or persisted.

The audit itself uses known outputs only from the permitted public-training-derived development task records already used for ARC-R018; public evaluation remains sealed.

## Falsifiable successor experiment

Queue `candidate-oracle-instrumentation-v1` before another architecture redesign. On the same frozen eight `dev_validation` IDs, keep DeepSeek V4 Flash, prompts, temperature/top_p, candidate count, selector and token budgets unchanged. Change only instrumentation: exact-score all three parsed candidate grids against the known development output and persist `candidate_correct` for each candidate alongside `selected_index`/`selected_correct`.

Predeclared decision rule on the four parseable ARC-R018 failures: if candidate-set coverage is **<50%**, prioritize candidate generator/representation research; if coverage is **>=50%** but the selected candidate remains wrong, prioritize selector/ranking research. Reuse deterministic cache where available and do not touch public evaluation.

## Verdict

**INCONCLUSIVE on candidate omission versus selector mistakes, because ARC-R018 did not persist the evidence needed to identify that distinction.** The useful result is the measurement diagnosis and a minimal matched instrumentation experiment that can resolve it without changing the architecture.

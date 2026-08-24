# ARC-R022 — Representation coverage audit

Task: `T0008-REPRESENTATION-COVERAGE-AUDIT`  
Role: **failure-analyst**  
Status: **complete — audit correction**

## Falsifiable question

Did ARC-R021 really create one newly candidate-covered task and regress one previously covered task relative to durable ARC-R020 candidate-oracle evidence?

Primary variable: none; this is a no-model-call evidence audit. Comparator evidence is frozen to `lab/results/ARC-R020-candidate-oracle.json`; treatment evidence is `lab/results/ARC-R021-object-relation-generator.json`. Public evaluation was not used.

## Result

The reported coverage swap is not supported by the durable candidate records.

ARC-R020 exact candidate evidence says:

- `0bb8deee`: candidate set **did not** contain a correct candidate.
- `0d3d703e`: candidate set **did** contain a correct candidate.

ARC-R021's embedded baseline annotations invert those two facts: it marks `0bb8deee` baseline-covered and `0d3d703e` baseline-uncovered. ARC-R021 treatment evidence itself says `0bb8deee` remains uncovered and `0d3d703e` is covered.

Corrected matched comparison therefore is **1/8 -> 1/8**, with **0 new covered tasks and 0 coverage regressions**. The one covered task, `0d3d703e`, is preserved.

This does not change ARC-R021's promotion verdict: **REJECT** remains correct because treatment coverage 1/8 is below the predeclared >=3/8 threshold. It does change the mechanism: there is no evidence for a morphology-dependent coverage swap.

## Morphology / failure interpretation

`0d3d703e` is a simple cellwise fixed color-permutation task. ARC-R020 generated an exact fixed color mapping candidate, and ARC-R021 again generated exact correct mapping candidates. Its coverage therefore cannot be attributed as a new benefit of object-centric representation.

`0bb8deee` is uncovered in both durable runs, so calling it an object-prompt regression was a metadata error rather than a solver regression.

The strongest uncertainty-reducing conclusion is methodological: per-task comparator coverage must be mechanically derived from the referenced persisted candidate records. Manual/hard-coded baseline labels can create false new-solve/regression narratives even when aggregate coverage is unchanged.

## Adversarial review

Temperature-zero hosted serving can still vary, but that cannot explain this discrepancy: the audit compares persisted exact candidate correctness against ARC-R021's own baseline annotation fields. The contradiction is internal and directly falsifiable.

## Next falsifiable direction

Before another routing/representation experiment spends inference, add a comparator-integrity check that reconstructs task-level coverage from the referenced baseline result and fails if experiment annotations disagree. Then re-open morphology-aware routing only when trustworthy per-task deltas exist. No target-model calls were spent in ARC-R022.

Durable audit: `lab/results/ARC-R022-representation-coverage-audit.json`.

# ARC-R020 — Candidate Oracle Instrumentation

Task: `T0006-CANDIDATE-ORACLE-INSTRUMENTATION`
Role: **benchmark-methodologist**
Status: **COMPLETE**

## Hypothesis / diagnostic

ARC-R018's unresolved parseable failures can be localized by exact-scoring every generated candidate before selection. On the four prior parseable failures (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`), candidate-set coverage below 50% diagnoses generator/representation as the dominant bottleneck; coverage at least 50% with wrong selections diagnoses selector/ranking as the dominant bottleneck.

## Frozen comparator and primary variable

The model-facing protocol was frozen to ARC-R018 `compact-hypothesis-select-v1`: NVIDIA NIM, `deepseek-ai/deepseek-v4-flash-0731`, candidate prompt, selector prompt, temperature 0, top_p 1, three candidates, 3072 candidate output tokens, 512 selector output tokens, same eight deterministic `dev_validation` task IDs.

Primary variable: **instrumentation only**. After candidate parsing, each candidate rule/grid was persisted and exact-scored, together with `selected_index` and `selected_correct`. Development ground truth was used only by the scorer after generation and was not exposed to either model stage.

## Result

Durable result: `lab/results/ARC-R020-candidate-oracle.json`.

- diagnostic prior-failure set: 4/4 parseable;
- diagnostic candidate-set coverage: **0/4 = 0%**;
- predeclared boundary: **<50% => generator/representation bottleneck**;
- all eight tasks: 6/8 candidate stages parseable, 1/8 had any correct candidate, 1/8 selected correct;
- live calls: 13; cache hits: 0;
- input tokens: 35,719; output tokens: 14,570; total: **50,289**;
- summed model runtime: **434.5213 s**;
- provider failures: 1 transient NVIDIA HTTP 529 overload;
- public evaluation: **not used**.

The one provider failure does not invalidate the predeclared diagnostic because all four diagnostic task IDs were parseable and exact-scored. The result file's conservative `bottleneck` string says provider failures confound the diagnostic globally, but the declared decision statistic is computed entirely on the four prior parseable failures and has complete observations there. Applying the experiment contract therefore diagnoses **generator/representation bottleneck**.

## Interpretation

The compact selector is not the immediate bottleneck on the previously parseable ARC-R018 failures: none of the three generated candidates was correct on any of those four tasks. Improving ranking cannot recover an answer that is absent from the candidate set. The next architecture treatment should therefore change candidate representation/generation rather than selector sophistication.

## Adversarial interpretation

Even with temperature 0, a fresh hosted rerun can differ from ARC-R018 serving. ARC-R020 measures candidate coverage under the frozen protocol now; it cannot reconstruct the historically unpersisted ARC-R018 candidate set. Also, one non-diagnostic task experienced transient provider overload. Neither caveat changes the observed 0/4 candidate coverage on the fully observed diagnostic set, but the small four-task diagnostic should be treated as directional rather than a population estimate.

## Next falsifiable direction

Queue a generator-focused treatment that introduces a compact object/relation representation before hypothesis generation while leaving the selector and model budget controlled. Success should require materially higher candidate-oracle coverage on a frozen slice without increasing selector complexity first.

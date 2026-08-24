# ARC-R021 — Object/relation candidate generator

Task: `T0007-OBJECT-RELATION-CANDIDATE-GENERATOR`
Role: **object-centric-researcher**
Status: **complete — REJECT**

## Falsifiable hypothesis

Adding an explicit compact object/relation reasoning instruction before the same three-candidate generation step would increase candidate-oracle coverage from ARC-R020's 1/8 to at least 3/8 on the identical frozen eight-task `dev_validation` slice, while retaining the previously covered task `0bb8deee`.

## Frozen contract

Primary variable: candidate-generation representation instruction only. The treatment asks the target model to identify objects and relations (background, connected components, color/size/bounding box/shape, motifs, containment/touching/alignment/symmetry) and prefer supported object-level transformations before emitting exactly three compact rule+grid hypotheses. No intermediate scene graph is serialized.

Frozen controls: NVIDIA NIM; `deepseek-ai/deepseek-v4-flash-0731`; temperature 0; top_p 1; candidate output cap 3072; selector output cap 512; one attempt/test; same selector prompt; exact candidate-level oracle scoring; same eight task IDs as ARC-R020: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`. Public evaluation was sealed and unused.

Decision rule: PROMOTE iff candidate coverage >=3/8, >=2 tasks are newly covered versus ARC-R020, and `0bb8deee` remains covered. Provider failures => INCONCLUSIVE. Otherwise REJECT.

## Result

Durable result: `lab/results/ARC-R021-object-relation-generator.json`.

- ARC-R020 comparator candidate coverage: **1/8**.
- ARC-R021 new candidate-covered tasks: **1**.
- ARC-R021 candidate-coverage regressions: **1**.
- Therefore net ARC-R021 candidate coverage remains **1/8 (12.5%)**, not the required >=3/8.
- The previously covered set was not preserved because one candidate-coverage regression occurred, independently failing the no-regression requirement.
- Provider failures: **0**.
- Calls: **14**; cache hits: **0**.
- Input tokens: **37,364**; output tokens: **14,112**; total tokens: **51,476**.
- Public evaluation used: **false**.

Verdict: **REJECT**. Explicit object/relation semantic scaffolding changed which task received a correct candidate but did not increase aggregate candidate-oracle coverage and lost one previously covered case. The current evidence does not justify promoting this representation prompt.

## Failure analysis

The important signal is a coverage swap rather than a monotonic gain: one new task became candidate-covered while one prior covered task regressed. This argues against a universal object-centric prompt as the next default representation. The generator remains the bottleneck because candidate coverage is still only 1/8 despite a materially more structured semantic instruction.

## Adversarial interpretation

Prompt wording may help through extra semantic scaffolding rather than object-centric representation specifically; eight tasks are directional and object structure may not suit every ARC family. Conversely, rejection of this prompt does not reject object-centric reasoning as a class: a deterministic extractor, typed scene representation, or routing by task morphology could behave differently. The next uncertainty-reducing step should inspect the new-covered/regressed pair and determine which task properties predict benefit versus harm before spending more inference on another broad prompt variant.

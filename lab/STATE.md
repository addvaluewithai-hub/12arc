# ARC Research Lab — Current State

Updated: 2026-08-24 06:46 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R020**
Active research run: **ARC-R021**
Next unallocated research run: **ARC-R022**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## Current bottleneck

ARC-R020 instrumented the ARC-R018 compact three-candidate protocol and found the predeclared four-task diagnostic fully observed but **0/4 candidate sets contained a correct answer**. Across all eight frozen tasks only 1/8 had any correct candidate. This diagnoses candidate generation/representation, not selector ranking, as the current bottleneck.

## ARC-R021 in flight

`T0007-OBJECT-RELATION-CANDIDATE-GENERATOR` is claimed under ARC-R021 with role **object-centric-researcher**. The falsifiable treatment changes only candidate-generation representation guidance: before emitting the same three compact rule+grid hypotheses, the target model is instructed to reason over objects and relations (background, connected objects, color/size/bounding box/shape, motifs, containment/touching/alignment/symmetry) and prefer supported object-level transformations. It does not serialize an intermediate scene graph.

Frozen controls: same eight ARC-R020 `dev_validation` task IDs, DeepSeek V4 Flash on NVIDIA NIM, temperature 0, top_p 1, candidate cap 3072, selector cap 512, one attempt/test, same selector prompt, candidate-level exact oracle scoring, no public evaluation.

Predeclared success: candidate coverage must rise from ARC-R020's 1/8 to >=3/8, with >=2 newly covered tasks and no loss of previously covered `0bb8deee`; provider failures make the matched result INCONCLUSIVE. Otherwise REJECT.

Implementation, test, workflow and run report are committed. Authorized GitHub Actions execution was triggered via `lab/triggers/r021-object-relation-generator.request`. At this state update `lab/results/ARC-R021-object-relation-generator.json` had not yet landed, so no score, token/runtime accounting or verdict is claimed.

## Next action

Reconcile ARC-R021 first. If its durable result has landed, analyze candidate coverage/new coverage/regressions/cost against the predeclared contract, finalize the report, queue the evidence-driven next task, release the claim/reservation, and stop. Do not allocate ARC-R022 while ARC-R021 remains active.

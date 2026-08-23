# ARC-R018 — Compact multi-hypothesis discriminative search

Task: `T0004-COMPACT-HYPOTHESIS-SEARCH`  
Role: **reasoning-systems-inventor**  
Status: **running / awaiting durable workflow result**

## Falsifiable hypothesis

On the same eight deterministic `dev_validation` tasks used by ARC-R017, fixed DeepSeek V4 Flash will improve exact task accuracy over the frozen ARC-R016 direct-JSON comparator if it first generates three compact competing transformation rules with candidate test grids, then a separate training-only discriminator selects the rule that best explains the training transformations.

This treatment targets the two mechanisms exposed by ARC-R017: rule ambiguity despite exact training replay, and excessive output serialization from replaying complete training grids.

## Frozen matched design

Comparator: ARC-R016 `nvidia-direct-json-baseline-v1` on the same task IDs.  
Treatment: `compact-hypothesis-select-v1`.

Fixed model/provider: NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`.

Fixed deterministic sampling: temperature 0, top_p 1, top_k null. The treatment divides generation budget across two stages: candidate generation max 3072 output tokens; selector max 512 output tokens; total configured output allowance is 3584/test, below the comparator's single-call 4096-token cap. The second stage receives training pairs and candidate rule text only; it does not receive the test input or candidate test-output grids.

Frozen task IDs: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

Public evaluation is not used. Training data is fetched from pinned ARC-AGI-2 commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`, sparse-checkout training only.

## Metrics and threshold

Primary metric: exact task accuracy versus ARC-R016 on identical IDs.

Secondary diagnostics: new solves, regressions, candidate/selector parse failures, provider failures, calls, cache hits, input/output/total tokens and summed model runtime.

PROMOTE only if treatment has at least one new solve and strictly more solved tasks than comparator. REJECT if it fails to strictly beat comparator. INCONCLUSIVE only if provider failure prevents matched comparison.

## Adversarial check declared in advance

The selector is the same foundation model and may merely prefer its own wording rather than truly discriminate causal rules. Repeating training pairs in stage two also increases input-token cost. Even a positive eight-task result would be directional and require confirmation before scaling.

Implementation: `src/arc_lab/compact_hypothesis_search.py`. Workflow: `.github/workflows/r018-compact-hypothesis-search.yml`.

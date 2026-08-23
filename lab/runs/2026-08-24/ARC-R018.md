# ARC-R018 — Compact multi-hypothesis discriminative search

Task: `T0004-COMPACT-HYPOTHESIS-SEARCH`  
Role: **reasoning-systems-inventor**  
Status: **complete — REJECT**

## Falsifiable hypothesis

On the same eight deterministic `dev_validation` tasks used by ARC-R017, fixed DeepSeek V4 Flash will improve exact task accuracy over the frozen ARC-R016 direct-JSON comparator if it first generates three compact competing transformation rules with candidate test grids, then a separate training-only discriminator selects the rule that best explains the training transformations.

This treatment targeted the two mechanisms exposed by ARC-R017: rule ambiguity despite exact training replay, and excessive output serialization from replaying complete training grids.

## Frozen matched design

Comparator: ARC-R016 `nvidia-direct-json-baseline-v1` on the same task IDs.  
Treatment: `compact-hypothesis-select-v1`.

Fixed model/provider: NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`.

Fixed deterministic sampling: temperature 0, top_p 1, top_k null. Candidate generation max output 3072 tokens; selector max output 512 tokens; total configured treatment output allowance 3584/test, below the comparator's single-call 4096-token cap. The selector receives training pairs and the three candidate rule texts only; it does not receive the test input or candidate test-output grids.

Frozen task IDs: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

Public evaluation was not used. Training data was fetched from pinned ARC-AGI-2 commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`, sparse-checkout training only.

## Predeclared threshold

Primary metric: exact task accuracy versus ARC-R016 on identical IDs.

PROMOTE only if treatment has at least one new solve and strictly more solved tasks than comparator. REJECT if it fails to strictly beat comparator. INCONCLUSIVE only if provider failure prevents matched comparison.

## Provider-recovery audit

The initial execution was INCONCLUSIVE because NVIDIA NIM returned transient HTTP 529 overloads for `00dbd492` and `05f2a901`, both comparator-solved tasks. A targeted recovery reran only those two IDs under the exact same solver version, prompts, model, sampling and generation budgets. The six unaffected tasks were not repeated.

Recovery succeeded with zero provider failures. It added four live calls, 12,348 tokens and 105.299 s summed model runtime. Both recovered tasks parsed successfully through both stages but remained treatment failures, so they are genuine matched regressions rather than provider confounds.

Durable recovery evidence: `lab/results/ARC-R018-provider-recovery.json`. Merged final evidence: `lab/results/ARC-R018-compact-hypothesis-search.json`.

## Final result

Frozen comparator: **4/8 = 50%**.  
Treatment: **2/8 = 25%**.  
Verdict: **REJECT**.

Final accounting after targeted recovery:

- treatment solved: **2/8**;
- new solves: **1** — `0bb8deee`;
- regressions: **3** — `00dbd492`, `05f2a901`, `0607ce86`;
- candidate parse failures: **2** — `0607ce86`, `06df4c85`;
- selector parse failures: **0**;
- unresolved provider failures: **0**;
- live calls: **15**;
- input tokens: **39,778**;
- output tokens: **16,948**;
- total tokens: **56,726**;
- summed model runtime: **380.112 s**;
- cache hits: **0**.

The treatment therefore misses the frozen promotion threshold by two tasks despite producing one genuine new solve.

## Failure analysis

The experiment separates two failure mechanisms.

First, compact multi-hypothesis generation contains useful signal: `0bb8deee` was a genuine new solve, and `0d3d703e` remained solved. So generating several compact rules is not uniformly harmful.

Second, the discriminator does not protect already-solvable cases. After transient-provider recovery, `00dbd492` and `05f2a901` produced parseable candidate/selector outputs but still regressed. This means their failures cannot be explained by provider availability or JSON parsing. The treatment can confidently select a wrong hypothesis even when the frozen direct baseline solved the task.

Third, output pressure remains on large tasks even after removing full training-grid replay. Candidate generation hit the 3072-token cap and failed parsing on `0607ce86` and `06df4c85`. `0607ce86` is a comparator-solved task, so one of the three regressions is directly attributable to candidate-stage serialization failure.

## Adversarial interpretation

This is only an eight-task directional slice, so it does not estimate full-split performance precisely. The selector uses the same foundation model and may merely prefer its own natural-language phrasing instead of discriminating transformation causality. Repeating training pairs in stage two also raises input cost. Conversely, the one new solve shows that rejecting this exact architecture should not be interpreted as evidence that multi-hypothesis search itself is useless.

The cleanest next uncertainty is whether the regressions come from **candidate-set omission** (the correct/direct solution is absent) or **selection error** (a correct candidate exists but the discriminator chooses another). That distinction should be established from durable candidate evidence before another model-facing architecture variant is justified.

## Verdict

**REJECT `compact-hypothesis-select-v1`.**

Do not promote it to the full 174-task baseline. Preserve the `0bb8deee` new solve as evidence that candidate diversity can help, but diagnose candidate coverage versus selector error before spending calls on a successor architecture.

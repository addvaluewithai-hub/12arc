# ARC-R018 — Compact multi-hypothesis discriminative search

Task: `T0004-COMPACT-HYPOTHESIS-SEARCH`  
Role: **reasoning-systems-inventor**  
Status: **running — targeted transient-provider recovery in flight**

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

## Initial durable result

The first complete workflow result landed at `lab/results/ARC-R018-compact-hypothesis-search.json` and is **INCONCLUSIVE under the predeclared contract**, because two transient provider errors prevent a matched eight-task comparison.

Observed initial totals:

- comparator: **4/8 (50%)**;
- treatment as observed: **2/8 (25%)**;
- new solves: **1** (`0bb8deee`);
- apparent regressions: **3**;
- candidate parse failures: **2**;
- selector parse failures: **0**;
- provider failures: **2**;
- calls: **11**;
- total tokens: **44,378**;
- summed model runtime: **274.813 s**.

Both provider failures were NVIDIA NIM HTTP 529 `Service temporarily overloaded`. They affected `00dbd492` and `05f2a901`, both of which are comparator-solved tasks. Therefore counting them as treatment regressions would confound architecture quality with transient provider availability.

## Targeted recovery

Recovery changes **no experimental variable**. The code now supports scoping execution to an explicit frozen task-ID subset while retaining the same solver version, prompts, model, sampling and generation budgets. A dedicated workflow reruns **only** `00dbd492` and `05f2a901`, then merges those records into the original eight-task result and recomputes the verdict. The six unaffected task IDs are not re-inferred.

Recovery trigger commit: `61a842e0b33df5be3accfe665904085b6dc57224`. Audit: `lab/recon/ARC-R018-provider-recovery-audit.json`.

Until the recovered durable result lands, do not promote or reject the architecture and do not allocate ARC-R019.

## Adversarial interpretation

Even if recovery improves the score, the selector is the same foundation model and may merely prefer its own wording rather than genuinely discriminate causal rules. Repeating training pairs in stage two increases input-token cost. Eight tasks remain directional rather than a full-split estimate. Conversely, if the recovered result still fails to strictly beat 4/8, the treatment should be rejected under the frozen threshold rather than rescued by post-hoc interpretation.

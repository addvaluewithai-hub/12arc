# ARC Research Lab — Current State

Updated: 2026-08-24 01:44 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R017**
Active research run: **ARC-R018**
Next unallocated research run: **ARC-R019**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## ARC-R017 result

The first architecture tournament is complete and **REJECTED**. On the frozen eight-task matched slice, ARC-R016 direct JSON solved **4/8 (50%)** while `hypothesis-train-replay-v1` solved **1/8 (12.5%)**, with **0 new solves and 3 regressions**. Execution used 8 calls, 41,344 total tokens and 383.978 s summed model runtime; there were 2 parse failures and no provider failures.

The strict training-replay gate passed 6/8 tests but still regressed previously solved tasks, showing that exact training consistency does not resolve rule ambiguity. Two tasks also exhausted the 4096-token output cap while serializing full replay.

## ARC-R018 active experiment

`T0004-COMPACT-HYPOTHESIS-SEARCH` remains claimed/reserved for ARC-R018 under role **reasoning-systems-inventor**.

Treatment `compact-hypothesis-select-v1` is a matched follow-up on the same eight deterministic `dev_validation` task IDs. Stage 1 asks fixed DeepSeek V4 Flash for exactly three compact distinct rules plus one candidate test grid per rule, with no full training-grid replay. Stage 2 receives the training pairs plus only the three rule texts — not the test input or candidate test grids — and discriminates the best-supported rule. Configured output allowance is 3072 + 512 = 3584 tokens/test, below the frozen comparator's 4096-token cap.

### Initial durable result: INCONCLUSIVE

The first durable result landed at `lab/results/ARC-R018-compact-hypothesis-search.json`:

- comparator: **4/8 (50%)**;
- observed treatment: **2/8 (25%)**;
- new solves: **1**;
- apparent regressions: **3**;
- candidate parse failures: **2**;
- selector parse failures: **0**;
- provider failures: **2**;
- calls: **11**;
- total tokens: **44,378**;
- summed model runtime: **274.813 s**;
- verdict: **INCONCLUSIVE**.

The two provider failures were transient NVIDIA NIM HTTP 529 overloads on `00dbd492` and `05f2a901`, both comparator-solved tasks. Under the predeclared contract, these prevent a clean matched rejection because provider unavailability is confounded with architecture regression.

### Targeted provider recovery in flight

A recovery path was implemented that changes no model-facing experimental variable and reruns only the two HTTP-529 task IDs. The six unaffected tasks are not re-inferred. The recovery keeps the same solver version, prompts, model, temperature/top_p, output budgets and scoring; it only scopes execution to the failed IDs and merges them back into the original result.

Recovery workflow: `.github/workflows/r018-recover-provider-failures.yml`. Trigger commit: `61a842e0b33df5be3accfe665904085b6dc57224`. Audit: `lab/recon/ARC-R018-provider-recovery-audit.json`.

Do **not** allocate ARC-R019 or issue a final ARC-R018 verdict until the recovered durable result lands. If recovery has no unresolved provider failures, apply the frozen threshold mechanically: PROMOTE only if treatment strictly exceeds 4/8 with at least one new solve; otherwise REJECT. If provider failures remain, retain INCONCLUSIVE and continue only transient-failure resolution within ARC-R018.

Public evaluation has not been used.

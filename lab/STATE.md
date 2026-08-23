# ARC Research Lab — Current State

Updated: 2026-08-24 00:47 EEST
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

`T0004-COMPACT-HYPOTHESIS-SEARCH` is claimed for ARC-R018 under role **reasoning-systems-inventor**.

Treatment `compact-hypothesis-select-v1` is a matched follow-up on the same eight deterministic `dev_validation` task IDs. Stage 1 asks fixed DeepSeek V4 Flash for exactly three compact distinct rules plus one candidate test grid per rule, with no full training-grid replay. Stage 2 receives the training pairs plus only the three rule texts — not the test input or candidate test grids — and discriminates the best-supported rule. Configured output allowance is 3072 + 512 = 3584 tokens/test, below the frozen comparator's 4096-token cap.

The experiment contract and implementation are persisted at `lab/runs/2026-08-24/ARC-R018.md` and `src/arc_lab/compact_hypothesis_search.py`; tests are in `tests/test_compact_hypothesis_search.py`; workflow is `.github/workflows/r018-compact-hypothesis-search.yml`; trigger commit is `cf1c1d4f2164923b2393aff37441145de0a1dd19`.

At this state update, `lab/results/ARC-R018-compact-hypothesis-search.json` has **not yet landed**. Do not claim a score or verdict until that durable result exists. Keep the ARC-R018 claim/reservation and reconcile the workflow/result next shift rather than allocating ARC-R019.

Public evaluation has not been used.

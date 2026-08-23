# ARC Research Lab — Current State

Updated: 2026-08-24 02:36 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R018**
Next unallocated research run: **ARC-R019**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## ARC-R017 result

The first architecture tournament was **REJECTED**. On the frozen eight-task matched slice, ARC-R016 direct JSON solved **4/8 (50%)** while `hypothesis-train-replay-v1` solved **1/8 (12.5%)**, with 0 new solves and 3 regressions. Exact training replay was therefore not sufficient to disambiguate rules, and full-grid replay created heavy output serialization cost.

## ARC-R018 final result

`T0004-COMPACT-HYPOTHESIS-SEARCH` is complete with verdict **REJECT**.

Treatment `compact-hypothesis-select-v1` generated three compact rule/candidate pairs and used a separate training-only selector. It was tested on the same eight deterministic `dev_validation` task IDs as ARC-R017 under fixed NVIDIA NIM DeepSeek V4 Flash, temperature 0/top_p 1, with candidate max output 3072 and selector max output 512.

The initial run was INCONCLUSIVE because NVIDIA returned transient HTTP 529 overloads for `00dbd492` and `05f2a901`. A targeted recovery reran only those two IDs without changing the model-facing protocol. Both recovered successfully, eliminating the provider confound.

Final merged result at `lab/results/ARC-R018-compact-hypothesis-search.json`:

- frozen comparator: **4/8 (50%)**;
- treatment: **2/8 (25%)**;
- new solves: **1** (`0bb8deee`);
- regressions: **3** (`00dbd492`, `05f2a901`, `0607ce86`);
- candidate parse failures: **2** (`0607ce86`, `06df4c85`);
- selector parse failures: **0**;
- unresolved provider failures: **0**;
- live calls: **15**;
- input tokens: **39,778**;
- output tokens: **16,948**;
- total tokens: **56,726**;
- summed model runtime: **380.112 s**.

The frozen promotion threshold required a strict improvement over 4/8 plus at least one new solve. Although one new solve appeared, the treatment remained two tasks below comparator, so rejection is mechanical rather than interpretive.

## Mechanistic takeaway

Compact multi-hypothesis generation has some useful signal because it produced a genuine new solve on `0bb8deee`. However, the selector failed to preserve already-solvable cases: after provider recovery, `00dbd492` and `05f2a901` both produced parseable two-stage outputs but still regressed. A third regression, `0607ce86`, hit the 3072-token candidate cap and failed parsing. Thus the next uncertainty is whether parseable regressions are caused mainly by the correct candidate being absent from the generated set or by the selector choosing the wrong candidate.

## Next task

`T0005-R018-FAILURE-AUDIT` is the highest-priority ready task for ARC-R019, recommended role **failure-analyst**.

Audit durable ARC-R018 candidate evidence and classify parseable failures into candidate-set omission versus selector error. Quantify the mechanisms before designing another model-facing architecture treatment. Do not use public evaluation and do not start a new architecture variant until this ambiguity is reduced.

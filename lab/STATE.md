# ARC Research Lab — Current State

Updated: 2026-08-24 04:45 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R019**
Active research run: **ARC-R020**
Next unallocated research run: **ARC-R021**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## Architecture history

ARC-R017 `hypothesis-train-replay-v1` was rejected at **1/8** versus comparator **4/8**. ARC-R018 `compact-hypothesis-select-v1` was rejected after provider recovery at **2/8** versus comparator **4/8**, with one new solve and three regressions. ARC-R019 then established that ARC-R018 did not persist unselected candidate grids/correctness, making candidate omission versus selector error observationally unidentifiable from historical artifacts.

## ARC-R020 candidate-oracle instrumentation

`T0006-CANDIDATE-ORACLE-INSTRUMENTATION` is claimed/reserved as ARC-R020. Role: **benchmark-methodologist**.

The experiment keeps ARC-R018's model-facing protocol fixed on the same eight deterministic `dev_validation` IDs and changes instrumentation only: every parsed candidate rule/grid is persisted and exact-scored after generation, together with `selected_index` and `selected_correct`. Development ground truth is not exposed to candidate generation or selection.

Predeclared diagnostic boundary on the four prior parseable ARC-R018 failures (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`): candidate-set coverage **<50%** => generator/representation bottleneck; coverage **>=50%** with wrong selections => selector/ranking bottleneck.

Implementation, test, workflow and trigger are committed. The authorized NVIDIA workflow was triggered, using pinned public training only and explicitly excluding public evaluation. At this state update, `lab/results/ARC-R020-candidate-oracle.json` had not yet landed. Do not invent coverage, token/runtime accounting or a bottleneck verdict.

Run report: `lab/runs/2026-08-24/ARC-R020.md`.

## Next action

Reconcile ARC-R020 before allocating ARC-R021. If the durable result has landed, inspect candidate-level correctness, apply the predeclared diagnostic boundary, record calls/tokens/runtime/provider failures and adversarial interpretation, finalize queue/state/handoff, then release ARC-R020. If the workflow failed, persist the failure evidence and repair only this experiment; do not start a new architecture task in the same shift.

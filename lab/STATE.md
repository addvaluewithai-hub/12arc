# ARC Research Lab — Current State

Updated: 2026-08-23 23:37 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R017**
Next research run: **ARC-R018**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## ARC-R017 result

The first architecture tournament is complete and **REJECTED**. On the frozen eight-task matched slice, ARC-R016 direct JSON solved **4/8 (50%)** while `hypothesis-train-replay-v1` solved **1/8 (12.5%)**, with **0 new solves and 3 regressions**. Execution used 8 calls, 41,344 total tokens and 383.978 s summed model runtime; there were 2 parse failures and no provider failures.

The strict training-replay gate passed 6/8 tests but still regressed two previously solved tasks despite perfect replay, demonstrating that exact consistency on training examples does not resolve ARC rule ambiguity. Two other tasks exhausted the 4096-token output budget while serializing structured replay. This exact architecture should not be scaled.

Durable evidence: `lab/results/ARC-R017-architecture-tournament.json` and `lab/runs/2026-08-23/ARC-R017.md`.

## Next bottleneck

`T0004-COMPACT-HYPOTHESIS-SEARCH` is the next research direction: test multiple compact hypotheses with discriminative verification, specifically attacking the ambiguity and serialization-cost failures exposed by ARC-R017 while retaining the frozen comparator/model discipline.

Note: queue/report/state have been finalized. If `lab/registry/run-counter.json` still shows the ARC-R017 reservation, it is a stale bookkeeping record caused by a connector write guard; the completed result and released queue claim are authoritative and the next shift should reconcile that stale reservation before allocating ARC-R018.

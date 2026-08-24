# ARC Research Lab — Current State

Updated: 2026-08-24 03:35 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R019**
Next unallocated research run: **ARC-R020**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## Architecture history

ARC-R017 `hypothesis-train-replay-v1` was rejected at **1/8** versus comparator **4/8**. ARC-R018 `compact-hypothesis-select-v1` was rejected after provider recovery at **2/8** versus comparator **4/8**, with one new solve and three regressions.

ARC-R018 final accounting remains: 15 live calls, 56,726 tokens, 380.112 s summed runtime, two candidate parse failures, zero unresolved provider failures.

## ARC-R019 failure audit

`T0005-R018-FAILURE-AUDIT` is complete. Role: **failure-analyst**. No target-model calls were made and public evaluation was not used.

The audit tested whether existing durable ARC-R018 evidence can classify parseable failures as **candidate-set omission** versus **selector error**. Result: **INCONCLUSIVE because the distinction is not identifiable from the persisted artifacts**.

ARC-R018's implementation holds three candidate rules/test grids in memory, but the durable result persists only candidate-stage metadata and selector `selected_index`. It does not persist the three candidate grids/rules or exact `candidate_correct` flags. Therefore a wrong selected candidate is compatible with either a correct unselected candidate (selector error) or three wrong candidates (candidate omission).

Quantified ARC-R018 mechanisms:

- candidate parse failure: **2/8** (`0607ce86`, `06df4c85`);
- parseable but unsolved: **4/8** (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`);
- parseable and solved: **2/8** (`0bb8deee`, `0d3d703e`).

Among the three comparator regressions:

- **1/3** is attributable to candidate serialization/parse failure (`0607ce86`);
- **2/3** are parseable but coverage-vs-selection is unidentifiable (`00dbd492`, `05f2a901`);
- selector error proven: **0/3**;
- candidate omission proven: **0/3**.

Durable audit: `lab/results/ARC-R019-R018-failure-audit.json`; report: `lab/runs/2026-08-24/ARC-R019.md`.

## Next task

`T0006-CANDIDATE-ORACLE-INSTRUMENTATION` is the highest-priority ready task for ARC-R020.

Run a matched instrumentation-only experiment on the same frozen eight `dev_validation` IDs. Keep the ARC-R018 DeepSeek model, candidate/selector prompts, sampling and output budgets fixed; exact-score and persist all three parsed candidate grids plus `selected_index`/`selected_correct`. Reuse deterministic cache where available.

Predeclared diagnostic boundary on the four parseable ARC-R018 failures: candidate-set coverage **<50%** means generator/representation is the dominant bottleneck; coverage **>=50%** with wrong selection means selector/ranking is the dominant bottleneck. Do not redesign the architecture before this measurement exists.

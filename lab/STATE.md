# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R030**
Next unallocated research run: **ARC-R031**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R026 rejected max-reasoning direct inference as the main bottleneck: first-attempt 37/174 and transport-recovered 41/174 remained below the frozen 45/174 comparator, while successful outputs did not approach the 16K cap.

ARC-R027 mechanically verified ARC-R020 and ARC-R021 candidate coverage at **1/8**, with only `0d3d703e` covered. It isolated repeated candidate-serialization overflow on `0607ce86` and `06df4c85`: both candidate stages ended with `finish_reason=length` in R020 and R021 before candidate verification.

ARC-R028 converted that evidence into a falsifiable two-stage queue: T0014 infrastructure first, then a matched two-task T0015 serialization ablation.

ARC-R029 validated the rule-first infrastructure with zero target-model calls: compact generic program IR, deterministic fail-closed execution, exact candidate scoring, mechanical coverage and comparator-integrity enforcement.

## ARC-R030 rule-first overflow ablation

`T0015-RULE-FIRST-OVERFLOW-ABLATION` is complete with outcome **REJECT**.

The matched diagnostic used exactly `0607ce86` and `06df4c85`, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, one attempt per test input, `temperature=0.0`, `top_p=1.0`, no reasoning-effort override, and the frozen **3072-token** candidate-stage output budget. The only intended treatment was candidate serialization: compact executable programs instead of materialized full grids.

Durable result:

- comparator candidate coverage: **0/2**;
- treatment candidate coverage: **0/2**;
- parseability: **2/2**;
- new coverage: **0**;
- regressions: **0**;
- live provider calls: **1**;
- cache hits: **1**;
- input tokens: **14,366**;
- output tokens: **186**;
- provider failures: **0**;
- parse failures: **0**;
- program validation failures: **0**;
- public evaluation used: **false**.

Execution status `lab/executions/ARC-R030.json` is `complete` with verdict `REJECT`. GitHub Actions run **32800687395** completed successfully on head SHA `2cb4ad651c2f729816d4658f2fdb6db67e9f7e8a` and persisted `lab/results/ARC-R030-rule-first-overflow.json`.

Interpretation: compact serialization removed the repeated length/parse failure but did **not** create any exact candidate. Therefore response-length overflow was a real operational symptom but is not a sufficient explanation of the candidate-coverage bottleneck. The strongest remaining uncertainty is **semantic program induction versus generic IR expressivity**, not output budget.

Adversarially, the two-task diagnostic does not show that rule-first representations are globally useless. The schema-v1 IR is intentionally small, and failure could arise because required transformations are not expressible, because the model fails to compose available primitives, or because the prompt collapses candidate diversity. Parseability alone is not reasoning progress.

## Ready now: T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT

Highest-priority ready task: `T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT`.

Role: **failure-analyst**.

This is a no-model audit using persisted ARC-R030 evidence plus permitted public-training examples only. It must classify each diagnostic failure into one of three falsifiable buckets:

1. missing generic DSL/IR expressivity;
2. compositional search/induction failure despite adequate expressivity;
3. prompt-induced candidate collapse/diversity failure.

The audit must not encode task-specific solutions into the solver. It should produce a mechanically auditable generic primitive/representation gap report and predeclare exactly one matched follow-up ablation with frozen comparator/task IDs/success threshold.

No active run reservation remains. Next unallocated run is **ARC-R031**.

Public evaluation remains sealed.

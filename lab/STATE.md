# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R029**
Next unallocated research run: **ARC-R030**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R026 rejected max-reasoning direct inference as the main bottleneck: first-attempt 37/174 and transport-recovered 41/174 remained below the frozen 45/174 comparator, while successful outputs did not approach the 16K cap.

ARC-R027 mechanically verified ARC-R020 and ARC-R021 candidate coverage at **1/8**, with only `0d3d703e` covered. It isolated repeated candidate-serialization overflow on `0607ce86` and `06df4c85`: both candidate stages ended with `finish_reason=length` in R020 and R021 before candidate verification.

ARC-R028 converted that evidence into a falsifiable two-stage queue: T0014 infrastructure first, then a matched two-task T0015 serialization ablation.

## ARC-R029 rule-first serialization harness

`T0014-RULE-FIRST-SERIALIZATION-HARNESS` is complete with outcome **INFRA_ONLY / PASS** and made **zero target-model calls**.

Durable implementation:

- `src/arc_lab/rule_first.py`: versioned compact generic program IR, bounded fail-closed validation, deterministic executor, exact candidate scoring, mechanical coverage and matched comparator enforcement;
- `tests/test_rule_first.py`: deterministic execution/input immutability, invalid-program rejection, exact materialized-grid scoring, coverage semantics and comparator mismatch tests;
- `.github/workflows/t0014-rule-first-ci.yml`: zero-model-call CI path;
- `lab/validation/T0014-rule-first-harness.json`: passing validation marker;
- `src/arc_lab/rule_first_ablation.py` and `.github/workflows/t0015-rule-first-overflow.yml`: authorized external execution path for the follow-up experiment.

GitHub Actions run **32789570942** completed **success** on head SHA `c67ac14cfea35c19b7188eb0201d78448993c77c`. The rule-first, comparator-integrity and scoring test command passed. `NVIDIA_API_KEY` was explicitly empty in the T0014 validation workflow, and the validation marker records `target_model_calls: 0`.

T0014 does not claim any research improvement. The bounded generic IR may still be semantically too weak; that is what T0015 must test.

## Ready now: T0015-RULE-FIRST-OVERFLOW-ABLATION

Run the predeclared matched diagnostic on exactly `0607ce86` and `06df4c85` using the authorized push-trigger workflow.

Primary change: candidate response serialization only — exactly three compact executable rule/program hypotheses instead of materialized full grids.

Frozen controls from ARC-R020 candidate generation remain unchanged, including:

- provider/model: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`;
- candidate-stage `max_output_tokens`: **3072**;
- same deterministic public-training-derived task data;
- one candidate-generation attempt per test input;
- exact scoring only after deterministic execution;
- mechanical comparator-integrity reporting against ARC-R020 on the identical task IDs.

Success: **2/2 candidate stages parseable and >=1/2 exact candidate coverage** after deterministic execution. Failure/falsification: either task remains unparsable/length-terminated, or both parse but remain **0/2** exact coverage. Provider/transport failure should be reported separately rather than interpreted as hypothesis evidence.

Execution path:

- workflow: `.github/workflows/t0015-rule-first-overflow.yml`
- trigger: `lab/triggers/t0015-rule-first-overflow.request`
- expected result: `lab/results/{run}-rule-first-overflow.json`
- status: `lab/executions/{run}.json`
- repository secret: `NVIDIA_API_KEY` inside Actions only

The next shift must claim T0015 and reserve **ARC-R030** before writing the trigger. After the trigger is durably written, stop and let GitHub Actions execute; do not start another substantive task in that shift.

Public evaluation remains sealed.

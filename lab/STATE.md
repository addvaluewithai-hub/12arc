# ARC Research Lab — Current State

Updated: 2026-08-24 05:37 EEST
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R020**
Next research run: **ARC-R021**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline is frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`, with temperature 0, top_p 1, max_output_tokens 4096 and one attempt/test. Public evaluation remains sealed.

## Architecture history

ARC-R017 full training replay was rejected at 1/8 versus comparator 4/8. ARC-R018 compact multi-hypothesis selection was rejected at 2/8 versus 4/8, with one new solve and three regressions. ARC-R019 found that ARC-R018 had not persisted unselected candidate correctness, so omission versus selection error was not identifiable historically.

## ARC-R020 candidate-oracle diagnosis

ARC-R020 reran the frozen ARC-R018 model-facing protocol with instrumentation only, persisting and exact-scoring all generated candidates.

The predeclared diagnostic set was the four prior parseable ARC-R018 failures: `00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`. All 4/4 were parseable in ARC-R020, and **0/4 candidate sets contained a correct answer (0% coverage)**. The declared boundary was <50% candidate coverage => generator/representation bottleneck; >=50% with wrong selections => selector/ranking bottleneck. Therefore the current diagnosis is **generator/representation bottleneck**.

Across all eight tasks, 6/8 candidate stages were parseable, only 1/8 had any correct candidate, and 1/8 selected correctly. Accounting: 13 live calls, 35,719 input + 14,570 output = **50,289 tokens**, **434.5213 s** summed model runtime, zero cache hits, and one transient NVIDIA HTTP 529 overload outside the fully observed four-task diagnostic statistic. Public evaluation was not used.

Adversarial caveat: this fresh temperature-zero hosted rerun measures current frozen-protocol coverage, not the unknowable historical ARC-R018 candidate set. The four-task diagnostic is directional and small, but selector improvement cannot recover candidates that are absent.

## Next action

`T0007-OBJECT-RELATION-CANDIDATE-GENERATOR` is ready for ARC-R021. Attack candidate omission rather than selector sophistication: test whether a compact object/relation representation before hypothesis generation materially increases candidate-oracle coverage under controlled model and selector budget. Freeze a development slice and retain candidate-level oracle scoring so coverage, selected accuracy, regressions and cost are all observable.

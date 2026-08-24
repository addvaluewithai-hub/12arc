# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R020 complete — generator/representation is the diagnosed bottleneck

`T0006-CANDIDATE-ORACLE-INSTRUMENTATION` is complete and ARC-R020 is released. No active reservation remains; ARC-R021 is next.

ARC-R020 kept ARC-R018's model-facing protocol frozen and changed instrumentation only. On the four predeclared prior parseable failures (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`), all four candidate stages parsed and **0/4 candidate sets contained a correct answer**. This is below the predeclared 50% boundary, so the diagnosis is **generator/representation bottleneck**, not selector/ranking.

Overall: 6/8 candidate stages parseable, 1/8 tasks with any correct candidate, 1/8 selected correct; 13 calls, 50,289 tokens, 434.5213 s summed runtime, zero cache hits, one transient NVIDIA HTTP 529. The provider failure does not contaminate the declared four-task diagnostic because that statistic had complete observations. Public evaluation was not used.

Durable evidence: `lab/results/ARC-R020-candidate-oracle.json` and `lab/runs/2026-08-24/ARC-R020.md`.

## Next shift

Highest-priority ready task: `T0007-OBJECT-RELATION-CANDIDATE-GENERATOR` for ARC-R021. Recommended role: **object-centric-researcher**.

Design one falsifiable generator-focused treatment: insert a compact object/relation representation before hypothesis generation and retain candidate-level oracle scoring. Keep DeepSeek V4 Flash, deterministic public-training-derived development data, selector complexity and unrelated settings controlled. Primary success signal should be increased correct-candidate coverage, not merely selector output accuracy. Record exact calls/tokens/runtime, parse failures, provider failures, new solves/regressions and adversarial interpretation.

Do not spend the next shift making the selector more sophisticated before candidate coverage improves. Do not use public evaluation. Gemma/GPT-OSS remain legacy comparators only.

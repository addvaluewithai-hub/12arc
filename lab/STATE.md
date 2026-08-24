# ARC Research Lab — Current State

Updated: 2026-08-24
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R027**
Next unallocated research run: **ARC-R028**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with fixed primary `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only; Gemma and GPT-OSS are legacy comparators.

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** exact accuracy on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## ARC-R026 max-reasoning direct ablation

`T0012-MAX-REASONING-DIRECT-ABLATION` is complete with verdict **REJECT**. First-attempt score was 37/174; after transport recovery 41/174, still below the frozen 45/174 comparator. The 16K output cap was never reached and does not explain the gap.

## ARC-R027 candidate failure taxonomy

`T0011-CANDIDATE-FAILURE-TAXONOMY` is complete with verdict **RESEARCH_DIRECTION** and made **zero target-model calls**.

Mechanically verified ARC-R020 and ARC-R021 coverage is the same: **1/8**, with only `0d3d703e` covered. The seven uncovered IDs are `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, and `1190bc91`.

Key failure families:

- repeated candidate-serialization overflow: `0607ce86`, `06df4c85` both ended candidate generation with `finish_reason=length` in R020 and R021;
- parseable object-attribute binding near miss: `00dbd492`;
- parseable relational motion near miss: `05f2a901`;
- parseable connectivity/path near miss: `070dd51e`;
- parseable but still unresolved compositional failures: `0bb8deee`, `1190bc91`;
- control case `0d3d703e` remains a simple cellwise color permutation already covered by both generators.

The strongest falsifiable next direction is **rule-first serialization routing** on `0607ce86` and `06df4c85`: generate compact rule/program hypotheses without full predicted grids, execute them deterministically, and require 2/2 parseability plus at least 1/2 mechanically verified candidate coverage under a matched comparator.

Artifacts:

- `lab/results/ARC-R027-candidate-failure-taxonomy.json`
- `lab/runs/2026-08-24/ARC-R027.md`

## Next task

No follow-up task has been invented automatically. The queue should be extended deliberately from the ARC-R027 hypothesis before another substantive experiment begins. Public evaluation remains sealed.

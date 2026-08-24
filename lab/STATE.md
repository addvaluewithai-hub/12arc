# ARC Research Lab — Current State

Updated: 2026-08-25
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R028**
Next unallocated research run: **ARC-R029**

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

## ARC-R028 agenda generation

`T0013-RESEARCH-AGENDA-GENERATION` is complete with verdict **RESEARCH_DIRECTION** and made **zero target-model calls**. It converted the ARC-R027 bottleneck into a two-stage falsifiable queue rather than idling.

### Ready now: T0014-RULE-FIRST-SERIALIZATION-HARNESS

Build and validate a compact, versioned rule/program candidate IR with deterministic execution, fail-closed parsing, exact candidate-oracle integration, and comparator-integrity enforcement. This task is infrastructure/research only and must make zero target-model calls.

Frozen local comparator: ARC-R020 compact-hypothesis candidate generation on `0607ce86` and `06df4c85`. The next target-model ablation must preserve the original DeepSeek model/settings and 3072-token candidate-stage budget except for the candidate serialization format.

T0014 success requires a zero-model-call validation marker and a declared authorized external execution path for the later ablation.

### Blocked follow-up: T0015-RULE-FIRST-OVERFLOW-ABLATION

After T0014 passes, test rule-first candidate serialization on `0607ce86` and `06df4c85`. Success is **2/2 candidate stages parseable and at least 1/2 mechanically verified candidate coverage** after deterministic execution. If both parse but coverage stays 0/2, the stronger semantic-coverage hypothesis is falsified.

Artifacts:

- `lab/results/ARC-R028-research-agenda.json`
- `lab/experiments/T0014-rule-first-serialization-harness.json`
- `lab/experiments/T0015-rule-first-overflow-ablation.json`
- `lab/runs/2026-08-25/ARC-R028.md`

## Next task

Execute exactly `T0014-RULE-FIRST-SERIALIZATION-HARNESS`. Do not start T0015 in the same shift. Public evaluation remains sealed.

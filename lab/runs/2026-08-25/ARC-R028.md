# ARC-R028 — Research agenda generation

Task: `T0013-RESEARCH-AGENDA-GENERATION`  
Role: **reasoning-systems-inventor**  
Status: **COMPLETE**

## Objective

The queue contained no eligible `ready` task after ARC-R027. This shift converted the strongest durable ARC-R027 failure evidence into a bounded, falsifiable next research sequence rather than idling or fabricating experimental results.

No target-model calls were made. Public evaluation remained sealed.

## Evidence reconstructed

ARC-R027 mechanically verified that ARC-R020 and ARC-R021 both cover only `0d3d703e` out of the eight-task diagnostic set. The repeated, structurally distinct failure on `0607ce86` and `06df4c85` is candidate-stage `finish_reason=length` in both runs, before exact candidate verification can operate. The frozen local comparator for those two IDs is therefore ARC-R020 compact-hypothesis candidate generation under its original settings and 3072-token candidate-stage budget.

This supports a narrow local hypothesis, not a population-wide router claim: full-grid candidate serialization may be the first removable bottleneck on those two tasks.

## Agenda created

### T0014-RULE-FIRST-SERIALIZATION-HARNESS — READY

Primary role: **program-synthesis-researcher**.

Hypothesis: a compact, versioned, machine-parseable rule IR plus deterministic execution can remove full-grid model-output serialization while preserving exact candidate-oracle and comparator-integrity accounting.

Primary change: infrastructure/representation only; zero target-model calls.

Success requires parser/executor round-trip tests, fail-closed invalid programs, deterministic execution, exact scorer integration, matched task-set validation, and a durable zero-model-call validation marker. Task-specific solution encoding is forbidden.

Protocol: `lab/experiments/T0014-rule-first-serialization-harness.json`.

### T0015-RULE-FIRST-OVERFLOW-ABLATION — BLOCKED pending T0014

Hypothesis: on `0607ce86` and `06df4c85`, replacing materialized grid candidates with compact rule/program hypotheses under the matched DeepSeek/ARC-R020 candidate budget will make 2/2 candidate stages parseable and produce at least 1/2 exact candidate coverage after deterministic execution.

Primary variable: candidate response serialization only.

Frozen comparator: ARC-R020 on the same two task IDs with matched provider/model, candidate count, generation/reasoning settings, attempts and 3072-token candidate-stage budget, recovered from durable code/config at execution time.

Success: 2/2 parseable and >=1/2 mechanically verified candidate coverage. Falsification: continued parse/length failure, or 2/2 parseable but 0/2 exact coverage.

Protocol: `lab/experiments/T0015-rule-first-overflow-ablation.json`.

T0015 remains blocked until T0014 validates the harness and declares an authorized push-triggered execution path using repository secrets.

## Adversarial review

- The repeated length stops could be model verbosity rather than task morphology; therefore the planned ablation changes only serialization format and keeps the task set and candidate budget matched.
- Two tasks are insufficient for a broad routing claim; the experiment is deliberately local.
- A DSL can cheat by embedding task-specific solutions; T0014 explicitly forbids task-ID-specific hard coding and must fail closed on unsupported programs.
- Better parseability without exact candidate coverage would be useful infrastructure evidence but would falsify the stronger semantic-coverage hypothesis.

## Result

Verdict: **RESEARCH_DIRECTION**.

Durable agenda: `lab/results/ARC-R028-research-agenda.json`.

Next substantive task is exactly `T0014-RULE-FIRST-SERIALIZATION-HARNESS`. Do not start T0015 until T0014 is complete and the queue explicitly unblocks it.

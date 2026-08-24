# ARC-R029 — T0014 Rule-First Serialization Harness

Date: 2026-08-25
Role: **program-synthesis-researcher**
Task: `T0014-RULE-FIRST-SERIALIZATION-HARNESS`
Outcome: **INFRA_ONLY / PASS**
Target-model calls: **0**
Public evaluation used: **no**

## Selection and lifecycle

The shift reconstructed repository truth from `lab/RUNNER.md`, current config/charter/protocols, run counter, queue, `STATE.md`, `HANDOFF.md`, experiment protocols, results and recent reports. No stale reservation required reconciliation. `T0014-RULE-FIRST-SERIALIZATION-HARNESS` was the highest-priority eligible ready task.

Before substantive work, the task was durably claimed under shift `t0014-20260825T022016+0300` and `ARC-R029` was durably reserved.

## Bottleneck attacked

ARC-R027 mechanically isolated repeated candidate-generation `finish_reason=length` on `0607ce86` and `06df4c85` under both ARC-R020 and ARC-R021. The immediate uncertainty was whether a compact executable representation could remove full-grid serialization as a pre-verification bottleneck without weakening exact scoring or comparator integrity.

This shift built the infrastructure only. It did not execute the T0015 target-model ablation and did not make any NVIDIA/model call.

## Durable implementation

### Generic rule-first IR and deterministic executor

Added `src/arc_lab/rule_first.py` with schema version 1 and a deliberately small task-agnostic primitive set:

- `identity`
- `rotate90`, `rotate180`, `rotate270`
- `flip_h`, `flip_v`
- `recolor(from,to)`

Programs are bounded to eight steps. Parsing fails closed on malformed JSON, schema mismatches, unsupported operations, extraneous parameters, invalid recolor colors and empty/oversized step lists. Execution validates ARC grids after each operation and does not mutate the caller input.

The module materializes candidate grids deterministically before calling the existing exact scorer. Candidate coverage is derived mechanically: every test input for a task must have at least one exactly correct executed candidate. Matched comparator deltas delegate to the existing comparator-integrity guard, which rejects mismatched task sets.

No task-specific solution or primitive for `0607ce86` or `06df4c85` was encoded.

### Tests and verification

Added `tests/test_rule_first.py` covering:

- deterministic execution and input immutability;
- fail-closed malformed/unsupported programs;
- exact scoring only after deterministic materialization;
- per-task candidate coverage semantics;
- matched comparator task-set enforcement.

Added `.github/workflows/t0014-rule-first-ci.yml`, with `NVIDIA_API_KEY` explicitly empty, to run:

`python -m pytest -q tests/test_rule_first.py tests/test_comparator_integrity.py tests/test_scoring.py`

GitHub Actions workflow run **32789570942** completed with conclusion **success** on head SHA `c67ac14cfea35c19b7188eb0201d78448993c77c`. The test step completed successfully. Durable validation is recorded at `lab/validation/T0014-rule-first-harness.json` with `target_model_calls: 0`.

Workflow URL: https://github.com/addvaluewithai-hub/12arc/actions/runs/32789570942

## T0015 authorized external execution path

Added `src/arc_lab/rule_first_ablation.py` and `.github/workflows/t0015-rule-first-overflow.yml` for the already-predeclared follow-up experiment.

The workflow is push-triggered only by `lab/triggers/t0015-rule-first-overflow.request`. Before model execution it mechanically validates that the trigger task/run/shift matches a durable claimed queue entry and active run reservation, and requires the repository `NVIDIA_API_KEY` secret inside Actions.

It fetches only the pinned public ARC training data (`ARC-AGI-2` commit `f3283f727488ad98fe575ea6a5ac981e4a188e49`) with sparse checkout and asserts the evaluation directory is absent.

The T0015 runner preserves the ARC-R020 candidate generation model/settings and 3072-token candidate-stage budget while changing the response serialization to exactly three compact executable programs. Executed grids are exact-scored and treatment coverage is compared mechanically to the ARC-R020 evidence on the same two task IDs.

T0015 was **not triggered** in this shift.

## Falsifiability and adversarial interpretation

T0014 establishes only that the representation/execution/scoring path is deterministic, validated and operational. It does **not** establish that compact rules improve ARC reasoning or candidate coverage.

A likely failure mode is that compact syntax removes serialization overflow but the intentionally bounded generic IR lacks the semantic primitive needed by either diagnostic task. Therefore T0015 remains the actual test: success requires 2/2 parseable candidate stages and at least 1/2 exact candidate coverage; parseability without coverage is evidence against the stronger serialization-bottleneck hypothesis, not a win.

## Conclusion

`T0014-RULE-FIRST-SERIALIZATION-HARNESS` satisfies its infrastructure success criteria and can be closed. `T0015-RULE-FIRST-OVERFLOW-ABLATION` may now become eligible for the next shift using the declared push-trigger execution path. No second substantive task was started.

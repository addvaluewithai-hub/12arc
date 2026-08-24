# ARC-R020 — Candidate Oracle Instrumentation

Task: `T0006-CANDIDATE-ORACLE-INSTRUMENTATION`
Role: **benchmark-methodologist**
Status: **IN FLIGHT**

## Hypothesis / diagnostic

ARC-R018's unresolved parseable failures can be localized by exact-scoring every generated candidate before selection. On the four prior parseable failures (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`), candidate-set coverage below 50% diagnoses generator/representation as the dominant bottleneck; coverage at least 50% with wrong selections diagnoses selector/ranking as the dominant bottleneck.

## Frozen comparator and primary variable

The model-facing protocol is frozen to ARC-R018 `compact-hypothesis-select-v1`: NVIDIA NIM, `deepseek-ai/deepseek-v4-flash-0731`, candidate prompt, selector prompt, temperature 0, top_p 1, three candidates, 3072 candidate output tokens, 512 selector output tokens, same eight deterministic `dev_validation` task IDs.

Primary variable: **instrumentation only**. After candidate parsing, persist each candidate rule/grid and exact `candidate_correct`, plus `selected_index` and `selected_correct`. Development ground truth is used only by the scorer after generation; it is not exposed to either model stage.

## Execution

Implementation: `src/arc_lab/candidate_oracle.py`.
Test: `tests/test_candidate_oracle.py`.
Workflow: `.github/workflows/r020-candidate-oracle.yml`.
Trigger: `lab/triggers/r020-candidate-oracle.request`.
Public evaluation: **not used**; workflow sparse-checks out pinned public training only and asserts evaluation is absent.

The workflow was triggered during this shift. At shift close, `lab/results/ARC-R020-candidate-oracle.json` had not yet landed, so no coverage statistic, score, token count, runtime, or bottleneck verdict is claimed here. The ARC-R020 reservation/claim remains active for reconciliation by the next shift.

## Adversarial interpretation

Even with temperature 0, a fresh hosted rerun can differ from ARC-R018 serving. Therefore this experiment measures candidate coverage under the frozen protocol now; it cannot reconstruct the historically unpersisted ARC-R018 candidate set. That limitation must remain explicit in the final interpretation.

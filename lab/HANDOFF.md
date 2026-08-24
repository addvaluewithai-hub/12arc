# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R020 is active — candidate oracle instrumentation in flight

`T0006-CANDIDATE-ORACLE-INSTRUMENTATION` is claimed and ARC-R020 is reserved. Do **not** allocate ARC-R021 until this run is reconciled.

Role: **benchmark-methodologist**.

ARC-R019 showed that historical ARC-R018 artifacts cannot distinguish candidate omission from selector error because unselected candidate grids were never persisted. ARC-R020 fixes that measurement blind spot without changing the model-facing architecture.

Frozen protocol: same eight `dev_validation` IDs, NVIDIA NIM, `deepseek-ai/deepseek-v4-flash-0731`, ARC-R018 candidate and selector prompts, temperature 0, top_p 1, three candidates, 3072 candidate output tokens and 512 selector output tokens. Instrumentation only now persists each candidate rule/grid and exact `candidate_correct`, plus `selected_index`/`selected_correct`. Ground-truth scoring occurs after model generation and is never included in either prompt.

Predeclared diagnostic on the four prior parseable failures (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`): candidate-set coverage **<50%** => generator/representation bottleneck; coverage **>=50%** with wrong selection => selector/ranking bottleneck.

Committed artifacts:

- `src/arc_lab/candidate_oracle.py`
- `tests/test_candidate_oracle.py`
- `.github/workflows/r020-candidate-oracle.yml`
- `lab/triggers/r020-candidate-oracle.request`
- `lab/runs/2026-08-24/ARC-R020.md`

The workflow was triggered through the authorized NVIDIA secret path and fetches only pinned public training data. Public evaluation remains sealed. At handoff time `lab/results/ARC-R020-candidate-oracle.json` had not yet landed, so no result or resource accounting is claimed.

Next shift: reconcile this same ARC-R020. If the result exists, apply the frozen decision boundary, finalize the report and accounting, mark T0006 done, update state/handoff and release the reservation. If execution failed, persist the failure evidence and repair/retry ARC-R020 only. Do not redesign architecture before this measurement is complete.

Adversarial caveat: a fresh temperature-zero hosted rerun can still differ from ARC-R018 serving, so ARC-R020 measures the frozen protocol's current candidate coverage rather than reconstructing the unknowable historical candidate set.

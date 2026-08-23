# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R018 is complete — REJECT

`T0004-COMPACT-HYPOTHESIS-SEARCH` is closed and ARC-R018 is no longer reserved.

Role used: **reasoning-systems-inventor**.

Frozen treatment `compact-hypothesis-select-v1` was evaluated on the same eight deterministic `dev_validation` task IDs as ARC-R017 with fixed NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, temperature 0/top_p 1, candidate max output 3072 and selector max output 512. Public evaluation remained sealed.

The initial result had two NVIDIA HTTP 529 overloads on comparator-solved tasks. Targeted recovery reran only `00dbd492` and `05f2a901` under the identical protocol and resolved both provider failures.

Final merged result:

- comparator: **4/8 (50%)**;
- treatment: **2/8 (25%)**;
- new solve: **1** (`0bb8deee`);
- regressions: **3** (`00dbd492`, `05f2a901`, `0607ce86`);
- candidate parse failures: **2** (`0607ce86`, `06df4c85`);
- selector parse failures: **0**;
- unresolved provider failures: **0**;
- 15 live calls;
- 56,726 total tokens;
- 380.112 s summed model runtime.

The predeclared threshold required treatment to strictly exceed 4/8 and have at least one new solve. It did produce one new solve, but only reached 2/8, therefore **REJECT**.

Durable evidence: `lab/results/ARC-R018-compact-hypothesis-search.json`, `lab/results/ARC-R018-provider-recovery.json`, and `lab/runs/2026-08-24/ARC-R018.md`.

## Mechanistic lesson

The experiment does not justify abandoning candidate diversity: `0bb8deee` is a genuine new solve. But two recovered comparator-solved tasks (`00dbd492`, `05f2a901`) parsed cleanly through candidate generation and selection and still regressed. Another comparator-solved task (`0607ce86`) failed because candidate generation hit its output cap.

The next key distinction is **candidate coverage versus selector error**: for parseable failures, determine whether a correct candidate was generated but not selected, or whether no correct candidate was generated at all.

## Next scheduled shift: ARC-R019

Highest-priority ready task: `T0005-R018-FAILURE-AUDIT`.

Recommended role: **failure-analyst**.

Use durable ARC-R018 evidence to classify parseable failures by candidate-set omission versus selector mistake, quantify the failure modes, and nominate one falsifiable successor experiment. Avoid new model-facing architecture work until this audit establishes which subsystem is actually responsible. Public evaluation remains sealed; Gemma/GPT-OSS remain legacy comparators.

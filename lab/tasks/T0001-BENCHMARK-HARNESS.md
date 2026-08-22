# T0001 — Benchmark Harness

Status: READY

## Mission

Make future ARC claims trustworthy before spending model quota.

## Deliverables

- validate the official ARC-AGI-2 JSON task shape;
- exact grid equality and pass@2 scoring;
- deterministic split of public-training task IDs into development train/validation/holdout;
- dataset manifest with source/version/hash once the official data is vendored or fetched;
- tests for malformed grids and scoring edge cases;
- a development command path that does not require public-evaluation solutions.

## Success test

A clean checkout can run tests and deterministically reproduce the same split manifest from the same task-ID list. No Gemma score is claimed in this task.

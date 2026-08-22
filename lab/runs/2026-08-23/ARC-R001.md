# ARC-R001 — T0001 Benchmark Harness

Date: 2026-08-23 EEST
Role: benchmark-methodologist
Verdict: `INFRA_ONLY`

## Hypothesis

If ARC task validation, scoring semantics, public-training development splits and source provenance are frozen before model inference, later solver deltas can be attributed and reproduced without using public-evaluation feedback.

## Primary change

Replace the initial benchmark primitives with a reproducible ARC-AGI-2 benchmark harness and pinned public-training specification.

## Frozen source

- Repository: `arcprize/ARC-AGI-2`
- Commit: `f3283f727488ad98fe575ea6a5ac981e4a188e49`
- Public training tasks: 1000
- Public evaluation tasks: 120, sealed from ordinary development
- Training ID-list Git blob: `3c3f6f0384dfe22343f7a0e9fc7ad5480b5fb4db`
- Local training ID-list SHA-256: `9dc93bc68f658d9077f76b882c2e26aff6a91cea1eb5415355837f83e6db0b00`

## Split

Seed: `arc-lab-v1`

- dev_train: 707
- dev_validation: 174
- dev_holdout: 119
- deterministic reference manifest SHA-256: `9d1172858ce93f3ba47513fef3259bd9168f9d6aa7b200bedb8983087292fa70`

## Implementation

- Enforced rectangular ARC grids with dimensions 1..30 and cells 0..9.
- Added task/pair schema validation and deterministic task-directory validation.
- Kept exact two-attempt matching while separating per-output accuracy from whole-task success.
- Added deterministic split manifest generation and self-hashing.
- Added source/version/hash metadata for the official public-training task list.
- Added CLI commands to generate/verify splits and validate development data.
- Added tests proving the normal development path does not require an evaluation directory.
- Extended CI to reproduce the split and sparse-checkout only pinned training data for integration validation.

## Verification

Local candidate implementation: `16 passed`.
No target-model requests were made. Calls/tokens/runtime cost for Gemma: zero.
No ARC solver accuracy is reported by this run.

The available GitHub connector did not expose a push-triggered Actions run/check for the implementation commit, so hosted CI is not claimed as observed-green in this report.

## Failure / regression analysis

The initial scorer returned fractional accuracy for multi-test tasks under a generic `score_task` name, which could later be confused with ARC's whole-task success criterion. This run replaced the ambiguity with explicit `output_accuracy` and `task_solved`/`task_accuracy` semantics.

The initial loader did not enforce the official 30x30 maximum; this is now tested.

## Adversarial interpretation

Passing synthetic/local tests alone does not prove the entire official corpus is valid under the loader. To guard against that, CI is configured to fetch the pinned upstream training tree and validate all 1000 training files while excluding the public-evaluation directory. Hosted execution of that CI step still needs to be observed independently.

The 70/20/10 proportions are hash buckets, so exact realized counts are 707/174/119 rather than exactly 700/200/100. This is intentional and deterministic, not stratified sampling.

## Next task

`T0001A-GEMMA-EXECUTION-PATH`: implement and smoke-test the authorized provider adapter/cache before `T0002-GEMMA-BASELINE`.

# T0001 — Benchmark Harness

Status: DONE
Completed by: `ARC-R001`

## Mission

Make future ARC claims trustworthy before spending model quota.

## Delivered

- strict ARC-AGI-2 grid/task validation, including 1..30 dimensions and values 0..9;
- exact grid equality and two-attempt scoring;
- separate per-test-output accuracy and full-task success metrics;
- deterministic public-training split generation from seed `arc-lab-v1`;
- pinned official ARC-AGI-2 source metadata and the 1000 public-training task-ID list;
- reproducible split reference: 707 dev-train / 174 dev-validation / 119 dev-holdout, manifest SHA-256 `9d1172858ce93f3ba47513fef3259bd9168f9d6aa7b200bedb8983087292fa70`;
- malformed-grid, scoring, split and benchmark-policy tests;
- a default development validation path that takes a training directory only;
- CI steps that sparse-checkout the pinned public-training corpus without the public-evaluation directory and validate it.

## Verification

Local implementation test run: 16 passed.
No Gemma call, ARC score or public-evaluation tuning occurred.

Hosted push-triggered CI status was not observable through the available GitHub connector at completion; see `lab/HANDOFF.md` and the ARC-R001 report.

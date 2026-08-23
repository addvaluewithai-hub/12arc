# ARC-R016 — DeepSeek frozen dev_validation baseline

Status: **INCOMPLETE / RECOVERY IN PROGRESS**
Task: `T0002C-NVIDIA-BASELINE`
Role: `llm-experimenter`
Provider/model: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`
Public evaluation used: **no**

## Frozen experiment contract

Protocol: `lab/experiments/ARC-R016-protocol.json`
Manifest SHA-256: `97102661ae8ae093dcc4afe3fb0122fbca7b0480893302d5b7a7a1044cb88433`
Split: all 174 deterministic `dev_validation` IDs under `arc-lab-v1`.
Generation: temperature `0.0`, top_p `1.0`, top_k `null`, max_output_tokens `4096`, one attempt per test input.
Solver: `nvidia-direct-json-baseline-v1`.
Provider retry policy: no hidden retries; one provider request per uncached request fingerprint.

Hypothesis: the ARC-R015-selected DeepSeek engine can establish a reproducible direct-JSON baseline across the full frozen `dev_validation` split with exact task accounting and durable response-cache evidence.

Success threshold: all frozen task IDs attempted with durable sanitized result/cache evidence. Missing task IDs, duplicate task IDs, non-durable successful responses, or public-evaluation use falsifies baseline establishment.

## Initial execution and failure

Workflow run: `32649224421` (`nvidia-baseline`).
Trigger commit: `441d0ad154a358b95bd61a0525a419bfa4b856ec`.
Protocol freeze commit: `1c2500b3267d3254286166d38b0eff9b6062a051`.

The initial six-way chunk execution did **not** establish a complete baseline. Five chunks completed successfully and uploaded artifacts; chunk 3 was cancelled by the GitHub Actions 45-minute job timeout while still inside `Execute frozen DeepSeek baseline chunk`. Aggregate therefore did not run.

Successful original chunk artifacts retained by GitHub Actions:

- chunk 0 — artifact `9495866152`, digest `sha256:e5d356751d4797606f88f824e668660c4454fd8b62eb9453fa3c0eeb80ce63e0`;
- chunk 1 — artifact `9495936544`, digest `sha256:745470099520a37cf3f88578b867a2ea6889bc74d8019453aabdc681c596c680`;
- chunk 2 — artifact `9495889735`, digest `sha256:cad1d55cca56b6ee744779842678cd2c41345407e1ee7fed226fc4243c217e37`;
- chunk 4 — artifact `9495906567`, digest `sha256:3ecbc96ce1a1b33c3002bccd4892df1a28659163442f4ad6a43ee8958e6cc043`;
- chunk 5 — artifact `9495898843`, digest `sha256:a456888807035b596e478dbd3674696a340ef630de1faff1c47171bc63c90bde`.

Failed original job: `chunk (3)`, job `97218147036`. Its log shows setup, pinned public-training fetch, and execution start succeeded; at `2026-08-23T16:24:47Z` GitHub cancelled the operation at the 45-minute job limit before artifact upload. The ephemeral chunk-3 cache was therefore lost and cannot be claimed as durable evidence.

Durable workflow audit: `lab/recon/ARC-R016-workflow-audit.json`.

## Recovery action in this shift

The stale claim from the prior shift expired at 20:35 EEST. This shift reconciled and re-adopted the existing **ARC-R016** reservation instead of allocating ARC-R017.

To avoid blindly repeating all 174 tasks, a repository-side audit workflow was added and used to identify exactly which chunk failed. Based on that audit, only the cancelled chunk-3 job was re-run using GitHub's job-level rerun action. The five successful chunk artifacts were not intentionally reissued.

Targeted rerun job: `97234116594` in workflow run `32649224421`.
At handoff time the job is `in_progress` in `Execute frozen DeepSeek baseline chunk`; aggregate has not yet produced final baseline artifacts.

Because the original chunk-3 ephemeral cache was lost on timeout, any successfully completed requests from that cancelled job cannot be recovered and some chunk-3 inference may necessarily be repeated. No evidence supports repeating the five successful chunks.

## Current metrics

A complete baseline score is **not yet available** and must not be invented. Exact solved/total, parse failures, tokens, runtime and cache counts remain pending successful chunk-3 completion plus aggregate validation.

## Failure analysis

Primary execution failure: workflow wall-clock timeout, not a benchmark scoring failure. The provider client itself has a 120-second request timeout, but a chunk contains many sequential requests; enough slow/timeout responses can exceed the 45-minute job budget even when each individual request is bounded.

The six-way partition was therefore operationally imbalanced for the observed latency distribution. This does not change the frozen model/prompt/generation protocol; it only affects execution packaging.

## Adversarial interpretation

The existing five chunks cannot be treated as a baseline because the frozen contract requires all 174 task IDs and durable cache evidence. Conversely, re-running all six chunks would waste inference and introduce avoidable repeated requests. The defensible recovery is to preserve the five successful artifacts and recover only chunk 3, then aggregate against the original frozen manifest.

## Verdict

`INCONCLUSIVE` — baseline not established yet.

## Required continuation

Adopt the existing ARC-R016 reservation; do **not** allocate ARC-R017 while this baseline is incomplete. Inspect workflow run `32649224421` first. If targeted rerun job `97234116594` completed and aggregate persisted `lab/results/ARC-R016-baseline.json` plus cache manifest/archives, audit and close T0002C without duplicate inference. If it hits the same 45-minute timeout, recover chunk 3 in smaller execution units while holding the original ARC-R016 protocol/model/settings/task set fixed, reuse the five retained chunk artifacts, aggregate once all 174 IDs have durable evidence, then close the task.

# ARC-R016 — DeepSeek frozen dev_validation baseline

Status: **COMPLETE / PROMOTE AS FROZEN COMPARATOR**
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

## Execution and recovery

Workflow run: `32649224421` (`nvidia-baseline`).
Trigger commit: `441d0ad154a358b95bd61a0525a419bfa4b856ec`.
Protocol freeze commit: `1c2500b3267d3254286166d38b0eff9b6062a051`.
Durable result commit from aggregate: `8143324` (`ARC-R016: persist DeepSeek baseline evidence`).

The initial six-way execution completed chunks 0, 1, 2, 4 and 5 and uploaded durable artifacts. Original chunk 3 job `97218147036` was cancelled at the GitHub Actions 45-minute job timeout while still executing requests, before artifact upload. Its ephemeral cache was lost.

The prior recovery shift reconciled the stale claim, adopted the existing ARC-R016 reservation instead of allocating ARC-R017, audited the workflow, and invoked a job-level rerun for only the failed chunk-3 job. Recovery job `97234116594` succeeded. Aggregate job `97237369824` then succeeded.

The aggregate log proves it downloaded exactly six artifacts: the five original successful artifacts plus recovered chunk 3 (`arc-r016-chunk-3`, artifact `9497708518`, digest `sha256:99fc7e577dffef3c0a367bcadebe4bd36ecb17e21f8664951bb0c77e7c27dfde`). The original successful artifacts were reused rather than intentionally recomputed.

Durable evidence:

- `lab/results/ARC-R016-baseline.json`
- `lab/results/ARC-R016-cache-manifest.json`
- `lab/results/ARC-R016-cache-archives/cache-0.tar.gz` through `cache-5.tar.gz`
- `lab/recon/ARC-R016-workflow-audit.json`

The cache manifest contains 179 request records and six archive hashes. It explicitly records that cache JSON contains visible model output and sanitized provider metadata only; `NVIDIA_API_KEY` and reasoning text are not persisted.

## Final baseline metrics

- exact solved tasks: **45 / 174**
- exact task accuracy: **0.25862068965517243 (25.8621%)**
- provider requests/calls represented in the retained baseline: **179**
- input tokens: **458,626**
- output tokens: **175,994**
- total tokens: **634,620**
- model-runtime sum: **4,625.097828976 s**
- cache hits during retained baseline execution: **0**
- cache records persisted: **179**
- parse failures recorded: **13**
- provider failures recorded: **10**
- wrong-but-parseable tasks recorded: **108**

The aggregate validator returned `PROMOTE`, meaning the baseline is promoted as the frozen comparator for subsequent architecture experiments; it does **not** mean direct JSON is claimed to be an optimal solver.

## Failure analysis

Two distinct failure layers matter.

First, execution packaging: one 29-task-ish chunk exceeded a 45-minute GitHub job budget because sequential requests can accumulate long latency even when individual provider requests are bounded. The recovery preserved five durable chunks and recovered only the missing chunk. Future large experiments should avoid coupling evidence durability to a single long chunk and should prefer smaller resumable units or periodic durable checkpoints.

Second, solver/model failures: the final retained baseline records 13 parse failures and 10 provider failures, alongside 108 wrong-but-parseable task records. These are baseline failures, not grounds to silently retry or alter the frozen comparator. Subsequent architecture work should compare against these exact retained outcomes and account for whether gains come from better reasoning, better output validity, or merely fewer provider/parse failures.

## Adversarial interpretation

This is a baseline measurement, not evidence that direct JSON is optimal. The 25.86% score mixes model reasoning quality, prompt/protocol limitations, parseability, and provider reliability. Known ARC-specific pretraining/exposure for the foundation model was not independently established by this run, so the score should be interpreted as competition-utility evidence rather than a clean measure of de-novo ARC reasoning.

The recovery also necessarily repeated any chunk-3 requests that may have completed before the first cancelled job lost its ephemeral cache; those unrecoverable calls are execution overhead and must not be confused with the retained baseline's 179 durable request records. Public evaluation was never used.

## Verdict

`PROMOTE` — **baseline established and frozen as comparator**.

`T0002C-NVIDIA-BASELINE` is complete. Release ARC-R016 and unblock `T0003-FIRST-ARCHITECTURE-TOURNAMENT`, but do not begin that second substantive task in ARC-R016.

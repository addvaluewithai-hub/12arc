# ARC-R007 — T0002 Gemma baseline observability diagnosis

Date: 2026-08-23
Role: `llm-experimenter`
Verdict: **INCONCLUSIVE**

## Hypothesis

The missing durable baseline result is primarily an observability problem: if the frozen GitHub Actions baseline is instrumented to persist a start/outcome breadcrumb independently of final benchmark success, the lab can distinguish “workflow never scheduled” from “workflow scheduled and benchmark still running/failed” without changing solver behavior.

## Frozen comparator

No target-model or solver variable changed.

- solver: `direct-json-v1`
- model: `gemma-4-26b-a4b-it`
- split: deterministic `dev_validation`
- task count: 174
- temperature: 1.0
- top_p: 0.95
- top_k: 64
- max_output_tokens: 2048
- attempts: exactly 2 per test input
- scorer: exact full-task success
- public evaluation: not fetched or used

## Primary treatment

Changed only `.github/workflows/gemma-baseline.yml` to persist `lab/recon/gemma-baseline-latest.json` at workflow start and again at baseline outcome. The breadcrumb contains only sanitized orchestration metadata: protocol/model/split/task count, run ID/attempt, trigger SHA, status, and whether the result file exists. No secret, prompt, raw model output, benchmark answer, parser, scorer, model ID, generation setting, task set, or attempt budget changed.

Treatment commit: `95c0d1939a5688c212c9f032f3547096d24d9f78`.

An explicit request commit was also issued at `c7900869ab1d46626a6db1342c3554bbdf4eda14` to exercise the dedicated request path. This was an orchestration mistake because the workflow-file treatment commit itself also matched `push.paths`, causing duplicate executions. The duplication is recorded as a negative result and must not be hidden from cost accounting.

## Evidence

The treatment produced durable proof that Actions scheduling and pre-baseline setup work.

Run `32612153608`, triggered by treatment commit `95c0d1939a5688c212c9f032f3547096d24d9f78`:

- checkout: success
- Python setup: success
- package install: success
- unit tests: success
- execution-start breadcrumb: success
- pinned public-training-only fetch: success
- frozen baseline step: in progress at observation cutoff

A second run `32612165079`, triggered by request commit `c7900869ab1d46626a6db1342c3554bbdf4eda14`, reached the same state and was also in the frozen baseline step at observation cutoff.

The latest durable breadcrumb at observation cutoff reported:

- status: `running`
- run ID: `32612165079`
- attempt: `1`
- trigger SHA: `c7900869ab1d46626a6db1342c3554bbdf4eda14`
- model: `gemma-4-26b-a4b-it`
- protocol: `direct-json-v1`
- split: `dev_validation`
- task count: 174

`lab/results/ARC-R004-baseline.json` was still absent when checked before the treatment.

## Result

The hypothesis is supported with respect to scheduling observability: the workflow is not silently failing to schedule. GitHub Actions started and passed all setup/leakage-safety gates before entering target-model execution.

The benchmark itself had not completed at the evidence cutoff, so **no ARC score is claimed**. No solved-task count, accuracy, parse-failure count, target-model call count, token count, runtime total, new solves, or regressions are claimed in ARC-R007.

## Failure analysis

Previous runs conflated several failure classes because only a final result file was durable. ARC-R007 separates them:

1. Actions scheduling is functional.
2. Repository write permission is functional because the start breadcrumb persisted.
3. Checkout/install/unit-test stages are functional.
4. Leakage-safe pinned training fetch is functional.
5. Remaining uncertainty is inside or after the expensive baseline step: target-model runtime/quota/API failure, job timeout, result persistence after completion, or successful completion not yet observed.
6. The workflow currently permits duplicate expensive runs because both workflow-source changes and request-file changes are push triggers and there is no concurrency guard.

## Adversarial review

The running breadcrumb does not prove any Gemma call succeeded; it proves only that execution entered the baseline step. A later success result must still be audited for complete 174-task coverage, exact scoring, two-attempt policy, parsing failures, cache accounting, calls/tokens/runtime and raw per-attempt records.

The second concurrent run is a confound for cost accounting and could duplicate API spend. Because the connected GitHub tool surface exposed no cancellation action, ARC-R007 did not claim those unknown resources. Future orchestration should prevent duplicate execution before another manual trigger is issued.

## Next action

Continue `T0002-GEMMA-BASELINE` only. First inspect `lab/recon/gemma-baseline-latest.json` and `lab/results/ARC-R004-baseline.json`, then inspect run `32612153608` and run `32612165079` if needed. Do not trigger another baseline while either run is still active. If a complete result exists, audit and close T0002. If both runs fail or time out, use their durable outcome/log evidence to make one minimal orchestration repair. Before any subsequent trigger, add duplicate-run protection (for example a workflow concurrency policy and/or removal of workflow-source push triggering) without changing `direct-json-v1`.

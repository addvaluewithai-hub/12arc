# ARC-R006 — T0002 Gemma baseline orchestration repair

Verdict: **INCONCLUSIVE**
Role: **llm-experimenter**

## Hypothesis

A dedicated request-file push path will make the existing frozen baseline workflow eligible to run without modifying the target model, prompt, parser, scorer, task set, sampling settings, or inference budget.

## Frozen comparator / protocol

`direct-json-v1` remains unchanged: `gemma-4-26b-a4b-it`; `temperature=1.0`; `top_p=0.95`; `top_k=64`; `max_output_tokens=2048`; exactly two attempts per test input; all 174 deterministic `dev_validation` tasks; deterministic cache/fingerprints; exact full-task scoring. Public evaluation was not accessed.

## Primary treatment

Orchestration only. Added `lab/triggers/gemma-baseline.request` to the workflow's `push.paths`, then committed that request file. Result-path pushes are intentionally not triggers, avoiding a persistence loop.

Workflow repair commit: `acf07b6461b119d2ad6e5d3c9bb0abfc07519707`.
Request commit: `b3e9270e4863d42b734414c643c7b44101f4fe90`.

## Result

The expected durable result `lab/results/ARC-R004-baseline.json` was absent immediately before and after the request commit during this shift's observation window. The connected GitHub status surface returned no status contexts for the request commit and cannot establish whether a push-triggered Actions run was queued, running, suppressed, or failed.

No ARC score is claimed. No target-model calls, tokens, runtime, new solves, regressions, or failure clusters are claimed because no durable execution evidence was available.

## Failure analysis

The prior workflow could only be retriggered by editing its own YAML (or manual dispatch), which coupled execution requests to workflow-source changes. The dedicated request file removes that coupling while preserving the solver protocol. Remaining uncertainty is downstream of trigger eligibility: Actions scheduling/permissions, runtime/quota, or workflow execution.

## Adversarial review

The absence of a result during a short observation window does not falsify the trigger repair: a run may be queued or still executing, and the full baseline may take substantial time. Conversely, adding an eligible path does not prove GitHub actually launched the run. Only durable result evidence or Actions run/log evidence can resolve this.

## Next

Continue `T0002-GEMMA-BASELINE` only. First audit `lab/results/ARC-R004-baseline.json` if it appears. Otherwise inspect Actions evidence if available. Do not alter `direct-json-v1` while diagnosing orchestration, and do not begin T0003 until a complete baseline is durable.

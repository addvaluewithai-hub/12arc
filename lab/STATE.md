# ARC Research Lab — Current State

Updated: 2026-08-23 10:14 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R012**
Next research run: **ARC-R013**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only.

## Frozen baseline

The comparator remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring.

ARC-R012 did **not** change the full baseline. It created a one-request matched ablation only.

## ARC-R011 finding carried forward

ARC-R011 isolated the dominant empty-output failure. On deterministic `dev_validation` task `00dbd492`, test index 0, the frozen 2048-token request used 2,982 input tokens and 2,045 thought tokens, emitted no candidate/output tokens, returned zero visible text, and stopped `MAX_TOKENS`. Runtime was 43.2723 seconds and total usage was 5,027 tokens. Re-audit of 113 cached responses found `total_tokens - input_tokens = 2,045` for 113/113, all empty.

This correctness blocker is separate from the earlier 16k input-TPM throughput issue; 61-second pacing had already avoided that 429 during a 42-minute baseline chunk for observed prompts.

## ARC-R012 treatment

ARC-R012 selected `T0002-GEMMA-BASELINE` and role `llm-experimenter`. It committed a matched single-request ablation on the exact ARC-R011 deterministic request with one model-facing variable only:

- comparator: `max_output_tokens=2048`;
- treatment: `max_output_tokens=8192`;
- frozen: model `gemma-4-26b-a4b-it`, prompt construction and prompt SHA, task/test/attempt identity, `temperature=1.0`, `top_p=0.95`, `top_k=64`;
- public evaluation is not fetched;
- one treatment call maximum; no 31B routing.

The workflow explicitly verifies prompt/model/task/sampling identity against the ARC-R011 evidence before persisting a treatment result. Trigger commit: `5d3a05f5f0b96ce9fac4c2ae6a2409999a40e29b`.

At ARC-R012 cutoff, `lab/recon/gemma-output-budget-ablation-latest.json` was still absent and the connected GitHub status surface exposed no status context for the trigger commit. Therefore ARC-R012 claims **zero completed treatment calls and no treatment token/runtime/output result**. Verdict: **INCONCLUSIVE**.

## Current bottleneck

Do not issue a duplicate 8192-token treatment call until the existing ARC-R012 trigger has been audited. First inspect whether `lab/recon/gemma-output-budget-ablation-latest.json` or its workflow artifact/run appears.

If durable evidence appears, the immediate falsifiable question is whether the same request transitions from `MAX_TOKENS`/thought-only under 2048 to a non-empty final candidate under 8192. Record exact input/thought/candidate/total tokens, runtime, finish reason, visible text and parseability. A single-task success establishes the empty-output mechanism for this request but does not by itself justify that 8192 is globally sufficient or cost-optimal.

If no workflow execution occurred, repair only the orchestration path and then execute the already-frozen ablation once. Do not mix in 31B routing, thinking-control changes, prompt changes, or public evaluation.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R013. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

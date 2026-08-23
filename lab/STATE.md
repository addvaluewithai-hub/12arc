# ARC Research Lab — Current State

Updated: 2026-08-23 11:06 EEST
Phase: **PHASE 1 — fixed-model baseline establishment**
Latest completed research run: **ARC-R013**
Next research run: **ARC-R014**

## Target model policy

Primary fixed engine: `gemma-4-26b-a4b-it`.
Escalation candidate: `gemma-4-31b-it`.
The research team invents the solver; Gemma executes controlled target-model experiments.

## Benchmark and execution state

`T0001-BENCHMARK-HARNESS` and `T0001A-GEMMA-EXECUTION-PATH` are complete. The frozen public-training-derived split remains authoritative and public evaluation remains milestone-only.

## Frozen baseline

The comparator remains `direct-json-v1`: all 174 deterministic `dev_validation` tasks, `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic request fingerprints/cache and exact full-task scoring.

ARC-R013 did **not** change the full baseline. It audited and falsified ARC-R012's one-request 8192-token treatment.

## Empty-output mechanism

ARC-R011 isolated the dominant empty-output failure on deterministic `dev_validation` task `00dbd492`, test index 0. With the frozen 2048-token cap, the request used 2,982 input tokens and 2,045 thought tokens, emitted no candidate/output tokens, returned zero visible text, and stopped `MAX_TOKENS`. Runtime was 43.2723 seconds and total usage was 5,027 tokens. Re-audit of 113 cached responses found `total_tokens - input_tokens = 2,045` for 113/113, all empty.

The earlier 16k input-TPM throughput issue is separate; 61-second pacing had already avoided that 429 during a 42-minute baseline chunk for observed prompts.

## ARC-R013 finding

ARC-R013 selected `T0002-GEMMA-BASELINE` with role `llm-experimenter` and audited the durable evidence produced by the already-triggered ARC-R012 matched ablation. No duplicate model call was issued.

The one-variable treatment held model, prompt SHA, task/test/attempt identity and sampling fixed and changed only `max_output_tokens: 2048 -> 8192`. Durable evidence is at `lab/recon/gemma-output-budget-ablation-latest.json`, persisted by GitHub Actions bot commit `1d5de993efb38580d7dcce1e1869b9576eab36b5`.

Treatment result on task `00dbd492`, test index 0, attempt 0:

- input tokens: 2,982;
- thought tokens: 8,189;
- candidate/output tokens: none reported; no final candidate emitted;
- total tokens: 11,171;
- runtime: 172.106133682 s;
- visible text chars: 0;
- parsed grid: none;
- finish reason: `MAX_TOKENS`.

Relative to the 2048 comparator, the 8192 treatment added exactly 6,144 thought tokens and 6,144 total tokens, matching exactly the +6,144 increase in configured output allowance, while adding 128.833833682 seconds runtime and producing no final answer.

Verdict: **REJECT** the 8192-token treatment as a repair for the empty-output failure. Merely increasing the output cap caused the extra budget to be consumed entirely by additional thinking.

## Current bottleneck

`T0002-GEMMA-BASELINE` remains incomplete because the primary model still does not produce scoreable final candidates under the frozen baseline configuration.

Do not spend another full baseline chunk or simply increase the output cap again. The next falsifiable question is whether the authorized Gemma API exposes a reproducible thinking-control mechanism that can limit/disable thinking enough to reserve budget for a final answer while keeping the same model, prompt/task identity, sampling and bounded output cap.

If such a control exists, test it on the exact same deterministic request as a one-variable matched ablation before changing the full baseline. If no usable thinking control exists for this model/API path, durably establish that limitation before considering a prompt-protocol change or explicitly authorized routing/escalation experiment.

## Next task

`T0002-GEMMA-BASELINE` remains `ready` for ARC-R014. `T0003-FIRST-ARCHITECTURE-TOURNAMENT` remains blocked until T0002 has a durable complete result.

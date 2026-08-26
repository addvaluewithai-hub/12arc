# ARC-R040 — T0022C multi-candidate contract rerun closure

Date: 2026-08-26
Primary role: reasoning-systems-inventor with failure-analysis emphasis
Task: `T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN`
Status: **INCONCLUSIVE / OPERATIONAL PHASE-CONTRACT FAILURE**
Public evaluation: sealed / not used

## Hypothesis

The ARC-R039 executable-IR generation/repair contract repair would restore candidate flow through the frozen deterministic verifier so the four-phase multi-candidate generate -> critique -> critique-the-critique -> repair -> Python-selection hypothesis could be tested.

## Frozen protocol and comparator

Predeclared protocol: `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`.

Frozen comparator context was ARC-R038 on public-training task `06df4c85`, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, four-request maximum, generation temperature 0.7 / top_p 0.95 / top_k 64 / max_output_tokens 4096, critique temperature 0.2 / top_p 0.95 / top_k 64 / max_output_tokens 3072, candidate target 16, repair maximum 8, frozen parser/verifier, normalization/deduplication, deterministic Python ranking and exact scoring.

## Provider/model continuity

The durable ARC-R040 execution used NVIDIA NIM model `nvidia/nemotron-3-ultra-550b-a55b`, with `default_model` still recorded as `deepseek-ai/deepseek-v4-flash-0731` and `model_override_used=true`. This followed the repository's temporary provider/model failover state after the DeepSeek endpoint became unavailable.

Therefore ARC-R040 is **not a matched DeepSeek rerun** and no reasoning-quality delta may be attributed solely to the repaired executable-IR contract. It is a failover/model-portability execution of the same architecture path.

## Durable execution evidence

Execution status: `lab/executions/ARC-R040.json` = `complete`.
Result: `lab/results/ARC-R040-multi-candidate.json`.

Observed accounting:
- provider: NVIDIA NIM
- model: `nvidia/nemotron-3-ultra-550b-a55b`
- requests: 4
- cache hits: 0
- input tokens: 36,532
- output tokens: 15,059
- total tokens: 51,591
- runtime: 378.378206148 seconds
- provider failures: 0
- top-level parse failures accounting: 0
- public evaluation used: false

The durable result terminates with:
- `status = operational_failure`
- `failure_stage = critique_parse_or_retry`
- `error_type = JsonContractError`

The critique-stage evidence explicitly states that 14 candidates were presented to the critic. This is a material operational improvement over ARC-R038's zero executable candidates: the repaired generation contract moved candidate flow past generation into critique. However, the critique response itself failed the required JSON-object contract, including after the retry/recovery path, so critique-the-critique, repair, final deterministic selection and exact candidate coverage were not completed.

## Metrics and verdict

Operational generation boundary: **improved** relative to ARC-R038; 14 candidates reached the critique stage versus 0 executable candidates reaching critique in ARC-R038.

Full T0022C operational gate: **not established**, because the run failed before the final repaired batch and deterministic final selection were produced.

Exact task score / candidate coverage: **not available from a completed final batch**; do not invent or infer a solve.
New solves: **not established**.
Regressions: **not established**.
Architecture verdict: **INCONCLUSIVE**.

## Failure cluster

Dominant failure: **phase-level JSON contract brittleness outside generation/repair**.

ARC-R039 repaired the executable candidate contract specifically for generation and repair. ARC-R040 shows that the fail-closed architecture still has an analogous machine-contract dependency at the critique boundary: the target model produced substantive critique prose but not a parseable JSON object satisfying the critic schema. The system therefore spent all four requests without reaching repair/selection despite successfully generating candidate material.

This is not a provider transport failure: provider_failures=0 and the workflow completed durably. It is also not evidence that multi-candidate reasoning is ineffective, because the architecture did not execute through its full frozen loop.

## Adversarial interpretation

The apparent generation improvement cannot be cleanly credited to the ARC-R039 contract repair because the model changed from the frozen DeepSeek comparator to Nemotron under provider failover. Nemotron may independently be more compliant with executable candidate generation. Conversely, the critique JSON failure may be model-specific rather than a general architecture defect.

The strongest model-independent conclusion is narrower: **the loop's machine-readable contract is not uniformly enforced across all model-facing phases**. Generation/repair had an explicit executable-IR contract; critique remained sufficiently brittle that a valid candidate batch could still be stranded before repair. Fixing this boundary offline is uncertainty-reducing and does not require more inference.

## Next task

Queue `T0022D-CRITIQUE-CONTRACT-HARDENING` as the next ready no-model task. It should replay the persisted ARC-R040 critic failure as a regression fixture, specify exact critic and critique-the-critique schemas, validate fail-closed parsing/recovery offline, and ensure the existing 14-candidate generation boundary can traverse mocked critique/repair/selection without changing candidate semantics or loosening the parser to accept arbitrary prose.

Do not rerun target-model inference until that phase-contract gate is durable. Keep DeepSeek-vs-Nemotron labels explicit; any later Nemotron experiment is a provider/model failover experiment unless a new matched comparator is intentionally established.

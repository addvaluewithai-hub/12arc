# ARC-R042 — T0022E hardened phase-contract rerun

Date: 2026-08-26
Role: **reasoning-systems-inventor**
Task: `T0022E-HARDENED-PHASE-CONTRACT-RERUN`
Verdict: **INCONCLUSIVE / OPERATIONAL_PHASE_CONTRACT_FAILURE**
Public evaluation: **sealed / unused**

## Question

Do the exact fail-closed critique and critique-the-critique contracts from ARC-R041 let the existing multi-candidate loop on public-training task `06df4c85` complete through critique, challenge, repair, and deterministic Python selection under the current NVIDIA/Nemotron failover path?

## Frozen protocol

Protocol: `lab/experiments/T0022E-hardened-phase-contract-rerun.json`.

Task, public-training-only boundary, executable candidate IR, executor, exact scorer, deterministic selector, generation/repair contract, and phase generation settings/token budgets were frozen. The only treatment relative to ARC-R040 was the strict critique/challenge schema boundary and exact correction instructions introduced by ARC-R041.

Provider/model: NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b` under the temporary failover policy. This is not a matched DeepSeek rerun.

## Execution evidence

Durable execution status `lab/executions/ARC-R042.json` is `complete`, with result `lab/results/ARC-R042-multi-candidate.json`.

Accounting from the result:

- live provider requests: 1
- cache hits: 3
- input tokens: 36,627
- output tokens: 15,059
- total tokens: 51,686
- runtime: 363.979225434 seconds
- provider failures: 0
- recorded parse-failure counter: 0
- public evaluation exposures: 0

The run nevertheless terminated at `failure_stage=critique_parse_or_retry` with `JsonContractError`. The critic response contained a `critiques` JSON object but was not accepted as a complete strict contract; the persisted diagnostic reports an unterminated string at offset 0 and rejected candidate containers at later offsets. No strict critique manifest was durably accepted, so critique-the-critique, repair, final deterministic selection, exact training coverage, new solves, and regressions were not reached.

## Result

**INCONCLUSIVE / OPERATIONAL_PHASE_CONTRACT_FAILURE.** ARC-R041 proved the strict phase contracts are internally valid and offline-traversable, but the live Nemotron path still failed at the same critique boundary. The treatment therefore did not achieve the operational success threshold.

This is not a research rejection of multi-candidate reasoning. It isolates the remaining uncertainty more narrowly: live critic serialization/completion under the present payload and token contract is still unreliable even after schema specification was made exact. Because three phases were served from cache and only one provider request was live, the run also does not provide an independent fresh end-to-end sample of every phase.

## Exact-score accounting

No exact ARC solve/coverage score is claimable because deterministic final selection was not reached. New coverage and regressions versus ARC-R040 are therefore undefined rather than zero. Public evaluation remained sealed.

## Failure cluster

Dominant failure cluster: **critic response serialization/completion failure at strict contract boundary**.

Observed provider availability was healthy for the live call (0 provider failures). The persisted exception is a contract/serialization failure, not an HTTP provider-path failure. The result-level `parse_failures` counter remaining zero despite terminal `JsonContractError` indicates that accounting and terminal phase-contract diagnostics are not synonymous; future reporting should preserve both.

## Adversarial interpretation

The repeated failure could be caused by output truncation, response-length pressure from critiquing many candidates in one object, model noncompliance with the exact schema, or recovery logic that still asks for too much structured payload at once. The current evidence does not distinguish these mechanisms. It also cannot establish whether the current IR/search would solve `06df4c85` if the critic boundary completed. Nemotron failover behavior cannot be attributed to the frozen DeepSeek comparator.

## Follow-up

Queue one no-model diagnostic before spending another live inference run: `T0022F-CRITIC-PAYLOAD-BOUNDARY-DIAGNOSTIC`. It should replay ARC-R040/R042 persisted critic evidence, measure the structural/size failure mode, and test a deterministic bounded critique batching/chunking contract offline without changing candidate semantics, executor, scorer, or selector. Only after that gate should another target-model rerun be considered.

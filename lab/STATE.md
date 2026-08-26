# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R042**
Next unallocated research run: **ARC-R043**

## Fixed comparator and current model policy

ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** on deterministic public-training-derived `dev_validation` using NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. Public evaluation remains sealed.

Current hosted execution remains under the temporary provider/model failover policy in `lab/config.json`: DeepSeek V4 Flash endpoints are unavailable on the authorized NVIDIA path and `nvidia/nemotron-3-ultra-550b-a55b` is the current working target model. Nemotron runs must not be represented as matched DeepSeek reruns.

## Current evidence chain

ARC-R038 exposed a generation/repair prompt-to-executable-IR contract failure. ARC-R039 hardened that boundary offline. ARC-R040 advanced provider-failover Nemotron execution to critique with executable candidates but terminated at `critique_parse_or_retry`. ARC-R041 then hardened critique and critique-the-critique contracts offline and demonstrated mocked end-to-end traversability with a persisted 16-candidate recovery batch.

ARC-R042 executed the predeclared live hardened-phase rerun on exactly public-training task `06df4c85`. Durable status is `complete`, but the experiment is **INCONCLUSIVE / OPERATIONAL_PHASE_CONTRACT_FAILURE**: the run again terminated at `critique_parse_or_retry` with `JsonContractError` before strict critique acceptance, critique-the-critique, repair, or final deterministic Python selection.

ARC-R042 accounting: **1 live provider request + 3 cache hits**, **36,627 input tokens**, **15,059 output tokens**, **51,686 total tokens**, **363.979225434 s runtime**, **0 provider failures**, and public evaluation sealed. The result-level parse-failure counter is 0 even though the terminal exception is a JSON contract failure; preserve both facts rather than conflating the counters.

No exact training coverage, new-solve, regression, or final-selector score is valid for ARC-R042 because the deterministic selection boundary was never reached. The remaining bottleneck is now narrower than ARC-R040: the live critic serialization/completion boundary remains unreliable despite an exact offline-valid schema.

Run report: `lab/runs/2026-08-26/ARC-R042.md`.
Result: `lab/results/ARC-R042-multi-candidate.json`.
Execution status: `lab/executions/ARC-R042.json`.

## Next active research direction

Highest-priority follow-up should be a no-model diagnostic of the critic payload boundary before another live rerun: `T0022F-CRITIC-PAYLOAD-BOUNDARY-DIAGNOSTIC`.

The diagnostic should replay persisted ARC-R040 and ARC-R042 critic evidence, distinguish truncation/size pressure from schema noncompliance/recovery behavior, and test a deterministic bounded critique batching/chunking contract offline while freezing candidate semantics, executor, scorer, and selector. It should make zero target-model calls and leave public evaluation sealed.

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate architecture direction before the critic boundary is made operationally interpretable.

Public evaluation remains sealed.

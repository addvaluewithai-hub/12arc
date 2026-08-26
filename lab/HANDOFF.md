# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R038 closed — T0022 multi-candidate loop was operationally inconclusive

`T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP` is closed as **INCONCLUSIVE / OPERATIONAL_CONTRACT_FAILURE**. This is not a rejection of multi-candidate reasoning.

Durable evidence:

- `lab/results/ARC-R038-multi-candidate.json`
- `lab/results/ARC-R038-contract-failure-analysis.json`
- `lab/executions/ARC-R038.json`
- `lab/runs/2026-08-26/ARC-R038.md`

The authorized NVIDIA path completed on public-training task `06df4c85` using `deepseek-ai/deepseek-v4-flash-0731`:

- requests: **4**
- cache hits: **0**
- input tokens: **23,769**
- output tokens: **2,156**
- total tokens: **25,925**
- runtime: **466.0348 s**
- provider failures: **0**
- public evaluation used: **false**

But the executable candidate contract failed before the intended reasoning loop could operate:

- submitted candidate records: **24**
- executable IR parseable: **0/24**
- unique executable candidates: **0**
- best candidate: none
- valid-candidate critiques: **0**
- critique challenges: **0**

Generation returned JSON records containing `schema_version` plus natural-language `instructions`; repair returned string-valued `schema_version` and natural-language/pseudocode `program` fields. The T0022A parser correctly failed these closed because they are not supported executable schema-v1/v2 IR objects.

Important accounting distinction: ARC-R038 top-level `parse_failures=0` means the provider responses themselves were parseable JSON. The candidate verifier separately records **24 candidate-IR parse failures**. Do not report these as zero candidate parse failures.

Mechanically, exact candidate coverage is still 0/1 on `06df4c85` versus ARC-R032's 0/1, with no new solves or regressions. Do not treat that as evidence against the architecture because the predeclared minimum of 8 parseable non-duplicate candidates was never reached.

## Next task: T0022B schema-contract repair

Highest-priority ready task is `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR`.

Protocol: `lab/experiments/T0022B-multi-candidate-schema-contract-repair.json`.

This is a no-model gate. Change **only** the prompt/output contract between generation/repair and the existing deterministic parser. Keep parser/verifier semantics, candidate normalization/deduplication, Python ranking, and the eventual `06df4c85` comparator setup frozen.

Required work:

- specify parser-supported executable schema-v1/v2 examples in the model-facing contract;
- make generation/repair outputs machine-checkable against that contract;
- add positive fixtures that pass parse → normalize → deduplicate → Python score;
- add negative regression fixtures for the exact ARC-R038 `instructions` and pseudocode `program` failure forms;
- require at least **8 representative non-duplicate fixtures** to pass offline;
- then predeclare exactly one matched T0022C rerun on `06df4c85`.

Do not make target-model calls in T0022B. If the contract cannot express diverse candidates without changing solver semantics, record that interface limitation and redesign the translation layer instead of forcing another inference run.

## Adjacent semantic follow-up

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked. It is the matched ARC-R036 follow-up on `0607ce86` and should not displace the multi-candidate direction unless later evidence or operator priority changes.

Run registry after ARC-R038 closure: latest completed run **ARC-R038**, no active reservations, next run **ARC-R039**.

Public evaluation remains sealed.

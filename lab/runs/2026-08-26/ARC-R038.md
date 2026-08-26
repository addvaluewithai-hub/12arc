# ARC-R038 — T0022 multi-candidate critique/verify loop

## Verdict

**INCONCLUSIVE / OPERATIONAL_CONTRACT_FAILURE**

ARC-R038 does not falsify the multi-candidate generate → critique → critique-the-critique → repair → Python-select architecture. The authorized NVIDIA execution completed and persisted evidence, but the model-facing output contract did not match the deterministic candidate parser, so no executable candidate entered the intended reasoning/critique loop.

## Frozen experiment contract

- Task: `T0022-MULTI-CANDIDATE-CRITIQUE-VERIFY-LOOP`
- Split: permitted public ARC-AGI-2 training data only
- Exact task ID: `06df4c85`
- Provider: NVIDIA NIM
- Model: `deepseek-ai/deepseek-v4-flash-0731`
- Solver: `t0022-multi-candidate-v1`
- Comparator: ARC-R032 task-level candidate coverage for `06df4c85` = false/exact-wrong
- Requests: maximum 4, exactly generate / critique / critique-the-critique / repair
- Generate: temperature 0.7, top_p 0.95, top_k 64, max_output_tokens 4096, target 16 candidates
- Critique: temperature 0.2, top_p 0.95, top_k 64, max_output_tokens 3072
- Critique-the-critique: same critique settings
- Repair: temperature 0.7, top_p 0.95, top_k 64, max_output_tokens 4096, up to 8 repairs
- Provider timeout: 900 seconds
- Public evaluation: sealed / not used

External workflow: `t0022-multi-candidate.yml`, GitHub Actions run `32929087561`, workflow head `4b39e773f75809a79a7fcd454136a6876c9fcd17`.

## Durable result

Source result: `lab/results/ARC-R038-multi-candidate.json`.
Analysis artifact: `lab/results/ARC-R038-contract-failure-analysis.json`.
Execution status: `lab/executions/ARC-R038.json` = complete.

Observed accounting:

- request count: **4**
- cache hits: **0**
- input tokens: **23,769**
- output tokens: **2,156**
- total tokens: **25,925**
- runtime: **466.0348 s**
- provider failures: **0**
- response-level JSON parse failures: **0**
- submitted candidate records: **24**
- candidate-IR parseable: **0/24**
- unique executable candidates: **0**
- deterministic best candidate: **none**
- critiques produced for valid candidates: **0**
- critique challenges produced for valid candidates: **0**

The top-level result accounting field `parse_failures=0` refers to provider/response parsing, while the verifier records **24 candidate-IR parse failures**. These are distinct failure layers and must not be conflated.

## Failure analysis

The 16 generation candidates were syntactically valid JSON records, but they used fields such as `schema_version` plus natural-language `instructions`. They were not parser-supported executable schema-v1/v2 IR objects.

The 8 repair candidates likewise did not satisfy the IR contract: they used string-valued `schema_version` and natural-language/pseudocode `program` fields. All failed closed.

Because pre-repair verification had zero valid candidates, the critique and critique-the-critique phases returned empty manifests. Thus the experiment never exercised the intended feedback loop over executable candidate programs.

Primary failure cluster: **prompt_to_ir_schema_mismatch**.

## Exact score / comparator delta

Mechanically, treatment candidate exact coverage is 0/1 on `06df4c85`, matching ARC-R032's false coverage: new solves **0**, regressions **0**. This delta is **not interpretable as an architecture result**, because the operational success threshold of at least 8 parseable non-duplicate candidates was never reached.

## Adversarial interpretation

The natural-language proposals may contain semantically useful ideas, so declaring the architecture bad because the executable score is zero would over-attribute an interface failure to reasoning quality. The opposite error is also possible: manually translating those prose rules and crediting them as target-model candidates would violate the predeclared deterministic contract. The correct conclusion is that the test is inconclusive until the prompt/output schema and parser agree.

## Next task

`T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR` is ready. It changes one thing only: the generator/repair prompt-to-IR output contract. It is a no-model infrastructure/research gate. It must add positive parser-compatible fixtures and regression tests for the exact ARC-R038 malformed forms, and require at least 8 representative non-duplicate fixtures to pass parse → normalize → deduplicate → Python score before predeclaring a matched T0022C rerun.

No second substantive task was started in ARC-R038 closure.

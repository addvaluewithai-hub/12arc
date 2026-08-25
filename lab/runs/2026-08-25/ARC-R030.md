# ARC-R030 — T0015 Rule-First Overflow Ablation

Date: 2026-08-25
Role: **program-synthesis-researcher**
Task: `T0015-RULE-FIRST-OVERFLOW-ABLATION`
Outcome: **REJECT**
Public evaluation used: **no**

## Lifecycle and external execution

This shift reconstructed repository truth from `lab/RUNNER.md`, config, charter, applicable protocols, run counter, queue, `STATE.md`, `HANDOFF.md`, the T0015 experiment contract, durable result/status, role catalog, and the preceding run report.

T0015 was already durably claimed under shift `t0015-20260825T033032+0300` with `ARC-R030` reserved. Per `lab/protocols/EXTERNAL-EXECUTION.md`, the expired ordinary lease was not treated as stale because the same external task/run had durable execution state. No second run was reserved.

The final durable execution status `lab/executions/ARC-R030.json` is `complete` with verdict `REJECT`; GitHub Actions workflow run `32800687395` completed successfully and persisted `lab/results/ARC-R030-rule-first-overflow.json`.

## Falsifiable hypothesis

Replacing materialized full-grid candidate serialization with exactly three compact executable rule/program hypotheses on `0607ce86` and `06df4c85` would make both candidate stages parseable under the same 3072-token candidate budget and produce at least one mechanically verified exact candidate after deterministic execution.

Success threshold: **2/2 parseable and >=1/2 exact candidate coverage**.

Falsification: either task remains unparsable/length-terminated, or both parse but deterministic execution yields **0/2** exact coverage.

## Frozen comparator and controls

Comparator: ARC-R020 candidate-generation evidence on the identical task IDs `0607ce86` and `06df4c85`, mechanically derived coverage **0/2**.

Primary change only: candidate response serialization changed from materialized grids to compact schema-v1 executable programs.

Provider/model: NVIDIA NIM / `deepseek-ai/deepseek-v4-flash-0731`.

Candidate protocol: matched ARC-R020 candidate-stage controls with `temperature=0.0`, `top_p=1.0`, no reasoning-effort override, `max_output_tokens=3072`, one candidate-generation attempt per test input, and exactly three compact programs per response.

Task data: deterministic permitted public-training-derived ARC data only. Public evaluation remained sealed.

## Durable result

Exact candidate-oracle coverage: **0/2 = 0%**.

Parseability: **2/2** candidate stages parseable.

Comparator coverage: `0607ce86=false`, `06df4c85=false`.
Treatment coverage: **0/2**.
New coverage: **0** tasks.
Regressions: **0** tasks.
Parse failures: **0**.
Program validation failures: **0**.
Provider failures: **0**.

Target-model accounting recorded in the durable result:

- live provider calls: **1**;
- cache hits: **1**;
- input tokens: **14,366**;
- output tokens: **186**;
- attempts per test input: **1**;
- candidate output budget: **3,072 tokens**;
- visible live-call runtime in the result record: about **4.3211 s**;
- external workflow result window: `2026-08-25T02:15:13.310792Z` to `2026-08-25T02:15:20.779560Z` (about **7.47 s**).

No rate-limit, timeout, transport, or provider-failure observation affected the final persisted run. One of the two requests was satisfied from the experiment cache, avoiding an unnecessary repeated inference call.

GitHub Actions run: `32800687395`, conclusion `success`, head SHA `2cb4ad651c2f729816d4658f2fdb6db67e9f7e8a`.

## Failure analysis

The compact protocol successfully removed the previously observed serialization/length termination symptom: both diagnostic candidate stages were parseable and the persisted output-token count was far below the 3072-token ceiling. Therefore serialization overflow was a real operational failure mode, but removing it was not sufficient to recover candidate coverage.

The stronger hypothesis is falsified because deterministic execution produced no exact candidate on either task. This shifts the bottleneck downstream/upstream from response length toward **semantic program induction and representational expressivity**: the model can emit valid compact programs, but the bounded generic IR and/or prompt does not induce a transformation that matches the task.

This is not evidence that rule-first representations are globally useless. The experiment intentionally used a very small generic primitive set and only two tasks selected for repeated overflow. It establishes that compression alone, with the frozen generic IR and prompt, does not convert those failures into coverage.

## Adversarial interpretation

Alternative explanations remain:

1. **IR insufficiency:** the bounded schema-v1 primitive set may simply be incapable of expressing the required transformations.
2. **Induction failure despite expressivity:** required transformations may be expressible compositionally, but the model did not infer them from demonstrations.
3. **Prompt/interface mismatch:** compact JSON validity may have been optimized at the expense of semantic search diversity.
4. **Tiny diagnostic slice:** two overflow-selected tasks cannot establish broad architecture value; they only falsify the local success claim.

Because comparator and treatment both have 0/2 coverage, there is no positive score delta to attribute to the representation change. Parseability alone must not be promoted as reasoning improvement.

## Next research task

Queue `T0016-RULE-FIRST-SEMANTIC-PRIMITIVE-AUDIT` as the next no-model failure-analysis task. It should inspect the persisted ARC-R030 programs and the corresponding permitted public-training transformations to determine, without encoding task-specific answers, whether failure is best explained by missing generic DSL primitives, compositional search failure, or prompt-induced candidate collapse. The deliverable should be a small generic primitive-family proposal plus a predeclared matched ablation, not another unconstrained prompt change.

## Conclusion

`T0015-RULE-FIRST-OVERFLOW-ABLATION` is **REJECTED**. Compact serialization fixed parseability but did not improve mechanically verified candidate coverage: **0/2 -> 0/2**, with zero new coverage and zero regressions. The task can be closed and `ARC-R030` completed. No second substantive task was executed in this shift.

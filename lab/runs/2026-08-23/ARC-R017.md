# ARC-R017 — First architecture tournament

Task: `T0003-FIRST-ARCHITECTURE-TOURNAMENT`  
Role: **reasoning-systems-inventor**  
Status: **complete — REJECT**

## Falsifiable hypothesis

Requiring fixed DeepSeek V4 Flash to state one transformation hypothesis and replay that same rule on every training input, then accepting its test grid only when those replay grids exactly equal every known training output, will strictly improve exact task accuracy over the frozen ARC-R016 direct-JSON comparator on the same eight deterministic `dev_validation` tasks.

## Frozen matched design

Comparator: ARC-R016 `nvidia-direct-json-baseline-v1`. Treatment: `hypothesis-train-replay-v1`. Only the solver protocol changed: one model call per test input emitted JSON containing `rule`, `train_predictions`, and `test_output`; deterministic code accepted the test candidate only if every training replay exactly matched its known output.

Model/settings were fixed: NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, temperature 0, top_p 1, top_k null, max_output_tokens 4096, one attempt/test. Public evaluation was not used.

Frozen IDs: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

Promotion required >=1 new solve and strictly more treatment solves than comparator.

## Result

**REJECT.** Comparator solved **4/8 = 50%**; treatment solved **1/8 = 12.5%**. New solves: **0**. Regressions: **3** (`00dbd492`, `05f2a901`, `0607ce86`). The sole retained solve was `0d3d703e`, already solved by baseline.

The strict replay gate passed 6/8 tests, yet passing verification was not sufficient for correctness: verified candidates on `00dbd492` and `05f2a901` regressed despite exact training replay. Two tasks (`0607ce86`, `06df4c85`) hit the 4096 output cap and failed parsing. This distinguishes two failure modes: overlong structured serialization and hypothesis overfitting/ambiguity despite perfect training consistency.

Execution accounting: **8 calls**, **26,344 input tokens**, **15,000 output tokens**, **41,344 total tokens**, **383.978 s** summed model runtime, **2 parse failures**, **0 provider failures**, **0 cache hits**.

Per-task sanitized evidence and exact accounting are persisted in `lab/results/ARC-R017-architecture-tournament.json`.

## Failure analysis

The treatment imposed a large serialization burden and converted training consistency into a hard acceptance criterion. ARC transformations can be underdetermined by training examples: reproducing every training output does not prove the inferred rule generalizes to the test grid. The experiment therefore falsifies the strong claim that a single natural-language hypothesis plus exact full-grid replay is a useful general verifier for this model under the matched budget.

A better next research direction should separate compact executable invariants from verbose full-grid replay, or generate multiple competing hypotheses and use discriminative checks that can reject ambiguity without requiring thousands of output tokens.

## Adversarial interpretation

Eight tasks are directional rather than a full-split estimate. The comparator happened to solve 4/8, so regression opportunity was substantial. Nevertheless the result is decisively below the predeclared promotion threshold, has zero new solves, and includes three matched regressions; no larger confirmation is justified for this exact architecture. Known ARC-specific foundation-model exposure is not independently established, so scores are interpreted as competition utility rather than clean de-novo reasoning measurement.

# ARC-R015 — Frozen NVIDIA model tournament

Task: `T0002B-NVIDIA-MODEL-TOURNAMENT`  
Role: `llm-experimenter`  
Verdict: **PROMOTE `deepseek-ai/deepseek-v4-flash-0731` as the fixed primary engine for the next baseline**

## Reconciliation note

The original ARC-R015 claim expired before queue/report closure, but Git history proved the substantive experiment had already completed: the trigger commit was `485f7b51fa33c13d0e89607b24ced62019a123af`, the protocol was frozen by Actions at `dc23f96c1e2846bdf28cb36633969cbe4d17a033`, and the sanitized tournament result was persisted at `2d649cb3fbc4386b39d9cf1b01fd3c8d255306fd`. This shift adopted the existing ARC-R015 reservation and audited/closed the same task without repeating target-model inference.

## Experiment contract

- Hypothesis: under identical direct-JSON decoding and one attempt per test input, one NVIDIA candidate will solve more tasks on a frozen development slice; an exact-solve tie is `INCONCLUSIVE`.
- Primary variable: target model identifier only.
- Frozen comparator: the other NVIDIA candidate under the exact same solver/prompt/scorer/task slice/generation budget.
- Execution checkout: trigger commit `485f7b51fa33c13d0e89607b24ced62019a123af`; its only change from parent `4ae9c9ab70f25ec692aeb564013bb77d224c3bf5` was the tournament trigger file.
- Solver version: `nvidia-direct-json-tournament-v1`.
- Provider: `nvidia-nim` through the repository-authorized `NVIDIA_API_KEY` Actions secret.
- Models: `deepseek-ai/deepseek-v4-flash-0731` and `nvidia/nemotron-3-ultra-550b-a55b`.
- Split: deterministic public-training-derived `dev_validation`; public evaluation was not used.
- Selection rule: first 3 lexicographically sorted `dev_validation` task IDs under `arc-lab-v1`.
- Task IDs: `00dbd492`, `05f2a901`, `0607ce86`.
- Manifest SHA-256: `d159e7209e785fa0879d249ffc989dc6092eab996d3c6c1468131f5dce0154d0`.
- Generation: temperature `0.0`, top_p `1.0`, top_k `null`, max_output_tokens `4096`.
- Attempts: exactly 1 per test input.
- Primary metric: exact full-task solves.
- Secondary diagnostics: parseability, tokens, runtime, provider failures and cache behavior.
- Success threshold: strictly more exact full-task solves for one model.
- Falsification: equal exact solves => `INCONCLUSIVE`.
- ARC-specific exposure label: this run does not independently establish either foundation model's ARC-specific pretraining/exposure. Scores are competition-utility evidence, not clean de-novo reasoning attribution.

Frozen manifest: `lab/experiments/ARC-R015-protocol.json`.

## Exact results

### DeepSeek V4 Flash

- Exact solves: **1 / 3 = 33.3333%**.
- Solved task: `0607ce86`.
- Unsolved: `00dbd492` returned a parseable but incorrect grid; `05f2a901` ended in a provider read timeout.
- Parse failures among successful responses: **0**.
- Provider failures: **1**.
- Successful live responses: **2**; request attempts including the timeout: **3**.
- Cache hits: **0**.
- Successful-response input tokens: **9,932**.
- Successful-response output tokens: **1,887**.
- Successful-response total tokens: **11,819**.
- Observable successful-response runtime: **51.018667405 s**. The failed timeout duration was not captured by the result schema, so this is not total wall-clock spend.

### Nemotron 3 Ultra

- Exact solves: **0 / 3 = 0%**.
- All three tasks ended with `finish_reason=length` at exactly **4096 output tokens** and no parseable final grid.
- Parse failures: **3 / 3**.
- Provider failures: **0**.
- Successful live responses / request attempts: **3 / 3**.
- Cache hits: **0**.
- Input tokens: **11,581**.
- Output tokens: **12,288**.
- Total tokens: **23,869**.
- Observable runtime: **202.81418594 s**.
- Reasoning characters observed, without persisting reasoning text: `8,263`, `11,237`, and `8,554` on the three tasks respectively.

### Matched comparison

- Score delta, DeepSeek minus Nemotron: **+1 solve / +33.3333 percentage points**.
- New solves for DeepSeek versus Nemotron: **1** (`0607ce86`).
- Regressions for DeepSeek versus Nemotron: **0**.
- Shared failures: `00dbd492` and `05f2a901`, though with different failure modes.
- Successful-response token cost: Nemotron used **23,869 vs 11,819**, about **2.02x** DeepSeek's observed tokens.
- Observable successful-response runtime: Nemotron used **202.814 s vs 51.019 s**, about **3.98x** DeepSeek's observed runtime.
- Nemotron output tokens were **12,288 vs 1,887**, about **6.51x** DeepSeek's, driven by all three responses saturating the 4096-token cap.
- Across both models: **6 request attempts**, **5 successful provider responses**, **1 provider failure**, **21,513 input tokens**, **14,175 output tokens**, **35,688 total successful-response tokens**, and **253.832853345 s** observable successful-response runtime.

The predeclared selection rule therefore selects DeepSeek. Secondary metrics are consistent with that choice but were not used to break a tie.

## Failure clusters

1. **Nemotron reasoning-budget saturation / answer non-emission.** Every Nemotron response consumed the full 4096-token output budget, finished by length, and failed parsing. This is a systematic protocol-fit failure, not three independent wrong-grid errors. The direct-JSON protocol does not reliably force this model to emit the final grid within the frozen budget.
2. **DeepSeek semantic error with valid syntax.** `00dbd492` was parseable but not exact. This is an actual reasoning/solution failure rather than formatting failure.
3. **DeepSeek provider transport instability.** `05f2a901` timed out before a usable response. The frozen one-attempt contract correctly counted the task unsolved; retrying it now would change the declared attempt budget and contaminate the comparison.
4. **Durable-cache limitation.** The workflow used deterministic `CachedTargetClient` storage under `/tmp/arc-r015-cache` but did not persist that directory after the Actions job. No duplicate inference occurred in this run and request fingerprints survive, but response cache records/hashes are unavailable after job teardown. `lab/results/ARC-R015-cache-manifest.json` records this limitation without fabricating missing hashes. The next baseline workflow should persist a sanitized durable cache/cache manifest so identical requests can be reused across runs.

## Adversarial interpretation

This is only a three-task slice, so sampling variance and task-family composition are large. A 1-0 win does not establish broad intrinsic superiority. Foundation-model ARC-specific exposure is also unknown here, so the score must not be described as clean de-novo reasoning ability.

The treatment is model identity under a matched 4096-token cap. Nemotron's failure may therefore reflect a mismatch between its reasoning-output behavior and this direct-JSON budget rather than weaker latent reasoning. That distinction does not invalidate the declared competition-utility question: under the frozen protocol/budget, it failed to emit a scorable answer on every task. A future architecture experiment may explicitly change answer-extraction/reasoning control, but doing so inside this tournament would have introduced a second variable.

DeepSeek also had one provider timeout, so its true inference cost and reliability are understated by the successful-response accounting. The timeout cannot reverse the observed primary comparison because the affected task is already counted unsolved, but it lowers confidence in throughput/reliability claims. No sustained RPM/TPM/RPD conclusion is supported.

## Matched-ablation verdict

The comparison held task IDs, prompt builder, scorer, generation settings, attempts, provider, execution path and solver version fixed; only the model ID changed. On the declared primary metric DeepSeek wins **1-0**, so the hypothesis survives the matched comparison and meets the predeclared promotion threshold.

**Decision: PROMOTE `deepseek-ai/deepseek-v4-flash-0731` as the fixed primary target model for `T0002C-NVIDIA-BASELINE`.** Keep `nvidia/nemotron-3-ultra-550b-a55b` as an escalation/research candidate, not the routine baseline engine. This decision is provisional at the architecture level and should not be generalized beyond the frozen direct-JSON protocol without new evidence.

## Durable artifacts

- Frozen protocol: `lab/experiments/ARC-R015-protocol.json`.
- Sanitized result: `lab/results/ARC-R015-tournament.json`.
- Cache/request manifest and durability limitation: `lab/results/ARC-R015-cache-manifest.json`.
- Tournament implementation: `src/arc_lab/nvidia_tournament.py`.
- Execution workflow: `.github/workflows/nvidia-model-tournament.yml`.

## Next task

Unblock `T0002C-NVIDIA-BASELINE`: establish a fully cached reproducible DeepSeek V4 Flash baseline on the frozen development split. Preserve the exact target-model ID and do not spend routine budget on Gemma/GPT-OSS. Do not begin the baseline inside ARC-R015.

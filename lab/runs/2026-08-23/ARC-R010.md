# ARC-R010 — Falsify single-request / unresolved TPM blocker

Task: `T0002-GEMMA-BASELINE`
Role: `falsifier`
Verdict: **INCONCLUSIVE** for T0002 completion; **SUPPORTED** for the pacing hypothesis.

## Contract

- Hypothesis: if the prior blocker was aggregate input-token-per-minute pressure rather than an intrinsically oversized ARC request, the frozen baseline with 61-second live-call start spacing will avoid the prior `generate_content_free_tier_input_token_count=16000` 429 for a full bounded execution window and monotonically grow the cumulative cache.
- Frozen comparator: ARC-R008 completed run `32614602241`, which grew cache 57->72 and then failed on the 16k input-TPM quota.
- Primary variable: execution pacing already introduced in ARC-R009, audited to completed outcome here. No solver-facing variable changed in ARC-R010.
- Model: `gemma-4-26b-a4b-it` (resolved provider model version `001`).
- Generation: `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`.
- Protocol: `direct-json-v1`, exactly two attempts per test input.
- Split: all 174 deterministic `dev_validation` tasks from pinned public training; public evaluation not used.
- Execution budget: minimum 61 seconds between uncached live-call starts; 42-minute baseline process timebox inside 55-minute workflow job.
- Primary diagnostic: recurrence/non-recurrence of the same input-TPM 429.
- Secondary diagnostics: cache growth, individual input-token maximum, cumulative calls/tokens/runtime, visible-output cluster.
- Falsification: same TPM 429 despite pacing, or any observed individual request >=16,000 input tokens.

## Completed-run evidence

Audited GitHub Actions run `32617284889`, job `97139928594`, artifact `9487805832` (`sha256:1265c30c29616943bc005ccead464236ae2f408a43db0420f9597894732c5436`).

The baseline process ran from approximately 04:12:39Z until the deliberate 42-minute timeout at 04:54:39Z. The log contains no provider 429/RESOURCE_EXHAUSTED during this paced interval. Exit code was `124`, durably classified as `partial_timebox`; cache save, outcome persistence, and artifact upload all succeeded afterward. The final workflow gate failed only because the full 174-task baseline was not complete.

The audited artifact contains exactly 113 unique cached response JSON files. Aggregate accounting:

- unique cached responses: **113**;
- cumulative input tokens: **313,622**;
- cumulative total tokens: **544,707**;
- cumulative provider runtime: **4,938.450 s**;
- visible text empty: **113/113**;
- recorded output/candidate token field: null for all 113 cache records;
- observed per-request input-token range: **248..9,634**;
- observed requests >=16,000 input tokens: **0**.

Relative to the pre-treatment 72-response artifact, the paced run added:

- **41** unique live responses;
- **78,206** input tokens;
- **162,051** total tokens;
- **1,816.402 s** provider runtime.

No ARC accuracy is claimed because the frozen complete two-attempt/all-test-input contract has not finished.

## Result

The evidence strongly supports the narrow hypothesis: the previously observed 16k error was an **aggregate input-token-per-minute rate limit**, not evidence that ordinary observed ARC requests individually require more than 16k input tokens. A conservative 61-second spacing avoided the same quota failure for the full 42-minute bounded execution window while adding 41 requests. The largest request remains 9,634 input tokens.

Therefore the immediate blocker is no longer uncertainty about TPM versus RPM/single-request size. The 16k input-TPM quota is a throughput constraint that can be managed with pacing/resume for the observed request-size distribution. There is no evidence in this run for an RPM blocker.

## Failure analysis

The baseline still cannot complete efficiently under the current hosted workflow because conservative pacing plus long provider runtimes exceeds the 42-minute process timebox. More importantly, all 113 cached responses still have empty visible text despite non-zero total token usage. This empty-output cluster is now the dominant solver-execution correctness blocker and must be isolated before interpreting ARC capability or spending many more paced calls.

The cache artifact proves monotonic progress and durable resume behavior. The next experiment should not simply continue accumulating hundreds of empty responses without first determining why the provider returns/our adapter records no visible candidate text under the frozen 2048-token configuration.

## Adversarial review

- Remaining unseen prompts could theoretically exceed 16k, but none of 113 observed requests does; current maximum is 9,634.
- A 61-second interval is deliberately over-conservative and does not establish the optimal safe throughput.
- Absence of 429 over 42 minutes does not prove provider quotas can never vary, but it directly falsifies the claim that the current baseline necessarily exceeds the 16k allowance per request.
- The empty-text problem is orthogonal to quota pacing. It could arise from model thinking consuming the output budget, provider response-channel semantics, SDK parsing, or adapter extraction. No cause is claimed without a controlled test.

## Resource accounting

ARC-R010 itself made **0 new target-model calls**. It audited the completed paced run and its durable cache artifact. The treatment run added 41 unique live responses, 78,206 input tokens, 162,051 total tokens and 1,816.402 seconds provider runtime relative to the prior 72-response cache.

## Next task

Continue only `T0002-GEMMA-BASELINE`. The next highest-value uncertainty is the 113/113 empty-visible-output cluster. Run a small, controlled, cached diagnostic that changes one response-generation/extraction variable at a time before spending additional full-split calls. Keep the fixed baseline comparator and public evaluation sealed.

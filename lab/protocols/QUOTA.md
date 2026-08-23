# Target-Model Quota and Compute Discipline

Target-model calls are experimental resources.

## Cache key

Hash together provider, model ID, full prompt/messages, decoding settings, solver version, task ID and attempt index. Identical cache keys must reuse stored outputs unless an experiment explicitly studies nondeterminism.

## Current worker policy

Use `deepseek-ai/deepseek-v4-flash-0731` on NVIDIA NIM as the provisional default worker while the frozen model tournament is unresolved. Use `nvidia/nemotron-3-ultra-550b-a55b` as the provisional second/escalation candidate when the queue explicitly calls for model comparison or routing.

Gemma and GPT-OSS are legacy comparators. Do not spend routine quota on them unless an explicit experiment requires them.

## Provider limits

Do not infer quota from marketing pages alone. Measure actual behavior from sanitized live calls and persist HTTP errors, rate-limit information when exposed, request timing, token usage and model ID. A successful tiny smoke call proves authorization/model availability only; it does not establish sustained RPM/TPM/RPD capacity.

If multiple models share a provider/account, do not assume their limits are independent. Test that assumption before using inter-model switching as a throughput strategy.

## Accounting

Every model experiment should record provider, calls, input tokens, output/reasoning tokens when observable, wall time, cache hits and failures. Report score delta together with resource delta.

A +1 point improvement that costs 10x more inference is not automatically progress.

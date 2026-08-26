# Provider failure policy

This policy prevents scheduled shifts from spending repeated runs on the same unavailable hosted-model path.

## Failure classes

Provider errors must be reported with a stable `error_category` when possible.

- `rate_limited`: HTTP 429; retry only according to quota/backoff policy.
- `transient_provider`: HTTP 408/500/502/503/504/529; retry or transport recovery may be valid on the same reserved run.
- `auth_or_permission`: HTTP 401/403; terminal until credentials/permissions are fixed by the operator or provider policy task.
- `model_or_endpoint_unavailable`: HTTP 404 when NVIDIA reports a missing function/model/endpoint; terminal until the approved model/provider mapping is updated or the provider confirms restoration.
- `provider_resource_not_found`: other HTTP 404; treat as terminal unless a protocol proves it is a temporary propagation issue.
- `transport_or_client_failure`: no status code; retry only if the error is plausibly network/transient and evidence is preserved.

## Rules

1. Do not mark a target-model experiment as research-rejected if no target-model output was produced.
2. Do not retrigger a terminal provider failure on the same protocol without changing the provider/model availability precondition.
3. If `error_category=model_or_endpoint_unavailable`, close or pause the active experiment as a provider-path blocker and create or execute a no-model/provider-policy task that revalidates the approved model mapping.
4. If a retryable provider failure occurs, recovery may reuse the same reserved run only when all experimental controls remain frozen.
5. Never silently switch models. A fallback model is allowed only when the queued task explicitly names it as an approved comparator or escalation path.
6. Persist the raw sanitized provider failure, status code, retryability, rate-limit headers, request count, token usage if any, runtime if any, and whether public evaluation was used.

## Current known blocker

ARC-R040/T0022C produced a terminal NVIDIA NIM 404 indicating that the provider account could not find the requested function for `deepseek-ai/deepseek-v4-flash-0731`. That is a provider/model endpoint availability blocker, not evidence against the multi-candidate architecture.

# Target-Model Quota and Compute Discipline

Target-model calls are experimental resources.

## Cache key

Hash together model ID, full prompt/messages, decoding settings, solver version, task ID and attempt index. Identical cache keys must reuse stored outputs unless an experiment explicitly studies nondeterminism.

## Escalation

Use the 26B A4B model as the default worker. Do not spend 31B calls on tasks already solved by the primary path unless the experiment is explicitly measuring model differences. Future routing studies should escalate only uncertain/failed cases.

## Accounting

Every model experiment should record calls, input tokens, output tokens, wall time and cache hits where available. Report score delta together with resource delta.

A +1 point improvement that costs 10x more inference is not automatically progress.

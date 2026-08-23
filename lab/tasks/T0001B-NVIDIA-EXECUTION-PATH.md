# T0001B — NVIDIA execution path

Status: **DONE**
Completed run: **ARC-R014**
Role: `llm-experimenter`

## Mission

Promote NVIDIA NIM into the provider-neutral target-model execution layer without changing ARC solver behavior or touching public evaluation.

## Required evidence

- `NvidiaNIMProvider` reads `NVIDIA_API_KEY` only from constructor/environment and never persists it.
- Cache fingerprint includes provider identity in addition to model/prompt/settings/solver/task/attempt inputs.
- Sanitized usage/runtime/finish/reasoning-size/rate-limit metadata are recorded without chain-of-thought text.
- Deterministic identical requests reuse cache and do not issue a second live provider call.
- A non-ARC GitHub Actions smoke succeeds through the provider-neutral adapter for both active candidates:
  - `deepseek-ai/deepseek-v4-flash-0731`
  - `nvidia/nemotron-3-ultra-550b-a55b`
- Unit tests pass.

## Completion evidence

GitHub Actions run `32628504884` completed successfully with **31 passing tests**. Live adapter smoke used exactly one live request per active model and then verified the identical second request was a cache hit.

Durable sanitized evidence: `lab/recon/nvidia-adapter-smoke-latest.json`.

DeepSeek: 19 input / 2 output / 21 total tokens, 7.423069927 s, visible `OK`, deterministic repeat cache hit.

Nemotron: 31 input / 36 output / 67 total tokens, 2.2212853519999953 s, visible `OK`, 146 reasoning characters observed but reasoning text not persisted, deterministic repeat cache hit.

No ARC benchmark task or public evaluation task was executed in this infrastructure task.

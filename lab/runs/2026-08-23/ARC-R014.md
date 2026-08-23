# ARC-R014 — Provider-neutral NVIDIA NIM execution path

Task: `T0001B-NVIDIA-EXECUTION-PATH`
Role: `llm-experimenter`
Verdict: **INFRA_ONLY / PROMOTE execution path**

## Contract

- Hypothesis: NVIDIA NIM can be promoted into the existing provider-neutral target-model layer such that provider identity participates in deterministic cache keys, sanitized accounting is durable, and both active NVIDIA model candidates can make one authorized non-ARC live call followed by an identical cache hit without a second provider request.
- Frozen comparator: the pre-task raw NVIDIA operational probe plus the existing provider-neutral Google adapter/cache design. The ARC solver, benchmark split and scorer are not variables in this infrastructure run.
- Primary treatment: add an NVIDIA NIM implementation of the target-provider interface and make cache fingerprints provider-aware.
- Provider: `nvidia-nim`, endpoint `https://integrate.api.nvidia.com/v1/chat/completions`.
- Models: `deepseek-ai/deepseek-v4-flash-0731` and `nvidia/nemotron-3-ultra-550b-a55b`.
- Task set: **non-benchmark smoke only**. No ARC task IDs and no public evaluation data were used.
- Generation for live smoke: temperature 0.0, top_p 1.0, no top_k, max output 128 tokens.
- Request budget: at most one live request per active model plus one identical cache lookup per model.
- Primary success criterion: both models return non-empty visible output through the adapter and their identical second calls are served from deterministic cache.
- Falsification: authorization/model failure, empty visible response, model mismatch, duplicate live provider call for an identical request, secret persistence, or failing tests.

## Implementation

`src/arc_lab/target_model.py` now contains `NvidiaNIMProvider` with provider ID `nvidia-nim`. It reads `NVIDIA_API_KEY` from the environment unless explicitly injected for tests. It uses the common NVIDIA OpenAI-compatible chat-completions endpoint and records model ID, prompt/completion/total usage, runtime, finish reason, reasoning-character count, non-sensitive usage details and rate-limit headers when exposed. Reasoning text itself is not persisted.

`TargetRequest.fingerprint()` now accepts provider identity, and `CachedTargetClient` includes the provider ID in the cache key. This prevents an identical model/prompt/settings request served by different providers from colliding in the cache.

`tests/test_target_model.py` adds coverage for provider-separated cache keys, NVIDIA response parsing, secret requirements and non-persistence of reasoning text, while preserving pacing/cache tests.

`src/arc_lab/nvidia_smoke.py` runs the two active models through the same provider-neutral client, makes an identical second request for each, verifies cache reuse, and records request fingerprints plus SHA-256 hashes of the cache records.

`.github/workflows/nvidia-adapter-smoke.yml` reads only the repository `NVIDIA_API_KEY` Actions secret, runs tests, executes the non-ARC smoke, persists sanitized evidence and uploads the evidence artifact.

`.env.example` and the charter were aligned with the current provider-neutral/NVIDIA policy; no real secret value was written.

## Verification

GitHub Actions run `32628504884` completed successfully. The workflow log records **31 passed in 0.15s** before live execution. Secret output is masked in the workflow log.

Durable evidence: `lab/recon/nvidia-adapter-smoke-latest.json` with `verified=true`, `provider_requests_total=2`, `cache_hits_total=2`, and `secret_persisted=false`.

### DeepSeek V4 Flash

- model requested/resolved: `deepseek-ai/deepseek-v4-flash-0731` / same;
- first call: live (`cache_hit=false`);
- repeat: cache hit (`cache_hit=true`);
- visible output: `OK` (2 chars);
- input tokens: 19;
- output tokens: 2;
- total tokens: 21;
- runtime: 7.423069927 s;
- finish reason: `stop`;
- reasoning chars: 0;
- request fingerprint: `580afba15128fe28de3a4af5b36662ae2305ce99a925e16dbb105df8925e8871`;
- cache SHA-256: `ed7240aca1d4a4b0ce1b85075d88cf94eaf7f1dd8cc5910cd78db7fe2b7db6f1`.

### Nemotron 3 Ultra

- model requested/resolved: `nvidia/nemotron-3-ultra-550b-a55b` / same;
- first call: live (`cache_hit=false`);
- repeat: cache hit (`cache_hit=true`);
- visible output: `OK` (2 chars);
- input tokens: 31;
- output tokens: 36;
- total tokens: 67;
- runtime: 2.2212853519999953 s;
- finish reason: `stop`;
- reasoning chars observed: 146; reasoning text not persisted;
- request fingerprint: `05fed2bd9ee3c71ef0504a65446a9fed1b07230bbed6c49b8d1e6fdf5542676f`;
- cache SHA-256: `0a5fe6c5b218b10c57ace0774eb58e070083f27bba2eef60422ab07018443b15`.

No rate-limit headers were returned on these two successful calls, so this run makes **no claim** about sustained RPM/TPM/RPD capacity.

## Resource accounting

- live NVIDIA requests: **2 total** (1 DeepSeek, 1 Nemotron);
- deterministic cache hits: **2 total**;
- live input tokens: **50 total**;
- live output/completion tokens: **38 total**;
- live total tokens: **88 total**;
- aggregate provider runtime: **9.644355279 s**;
- ARC solves/score/new solves/regressions: **not applicable; no ARC benchmark executed**.

## Failure analysis

No active-model authorization, model-resolution, output or cache-reuse failure occurred. The earlier raw operational smoke had shown GPT-OSS and Gemma timeouts, but those models are legacy comparators and were deliberately outside ARC-R014's declared scope.

The only operational limitation observed here is absence of rate-limit headers on successful calls. Therefore quota capacity remains an empirical question for later controlled runs; this smoke proves execution-path correctness, not throughput.

## Adversarial interpretation

A two-call non-ARC smoke does not establish ARC competence, sustained NVIDIA reliability, rate limits, identical hosted/offline behavior, or that one active model is better than the other. DeepSeek's slower latency in this smoke than the earlier raw probe is not interpretable as a model regression because hosted queue/load conditions were uncontrolled. The only supported conclusion is that the provider-neutral adapter/cache/accounting path works for both currently approved candidates under tiny live requests.

## Decision / next task

**Promote the NVIDIA NIM execution path.** `T0001B-NVIDIA-EXECUTION-PATH` is complete.

Next eligible task: `T0002B-NVIDIA-MODEL-TOURNAMENT`. Run a small frozen public-training-derived development comparison between DeepSeek V4 Flash and Nemotron 3 Ultra only. Do not chain that experiment into ARC-R014.

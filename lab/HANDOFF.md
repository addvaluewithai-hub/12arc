# Handoff

Start from `lab/RUNNER.md` and current Git state. Do not continue the old Gemma plan from historical reports.

## Active operator direction

Routine research uses **NVIDIA NIM** through repository Actions secret `NVIDIA_API_KEY`; never expose or persist its value.

ARC-R015 selected:

- **primary:** `deepseek-ai/deepseek-v4-flash-0731`;
- escalation/research candidate: `nvidia/nemotron-3-ultra-550b-a55b`.

Gemma and GPT-OSS remain legacy comparators only unless an explicit future task requires them.

## ARC-R015 completed — frozen NVIDIA model tournament

The earlier ARC-R015 claim expired after the Actions experiment had already persisted durable results. Git showed:

- trigger commit: `485f7b51fa33c13d0e89607b24ced62019a123af`;
- frozen protocol commit: `dc23f96c1e2846bdf28cb36633969cbe4d17a033`;
- sanitized result commit: `2d649cb3fbc4386b39d9cf1b01fd3c8d255306fd`.

The current shift reconciled that stale claim, adopted the existing ARC-R015 reservation, audited the evidence and closed the same task without repeating inference.

Frozen public-training-derived `dev_validation` slice: `00dbd492`, `05f2a901`, `0607ce86`; public evaluation was not used. Both candidates used NVIDIA NIM, direct-JSON solver `nvidia-direct-json-tournament-v1`, temperature 0.0, top_p 1.0, max_output_tokens 4096, one attempt per test input.

Result:

- DeepSeek V4 Flash: **1/3 exact**; solved `0607ce86`; one parseable wrong answer on `00dbd492`; one provider timeout on `05f2a901`; 11,819 successful-response tokens; 51.018667405 s observable successful-response runtime.
- Nemotron 3 Ultra: **0/3 exact**; all three outputs hit the 4096-token cap with `finish_reason=length` and no parseable final grid; 23,869 tokens; 202.81418594 s runtime.
- DeepSeek delta: **+1 solve / +33.3333 percentage points**, one new solve, zero regressions.

Per the predeclared selection rule, DeepSeek is promoted as the fixed primary engine for baseline establishment. Treat this as protocol-specific competition-utility evidence only: the slice is tiny, known ARC-specific exposure was not established, Nemotron's failure was largely answer-emission/budget saturation, and DeepSeek had a transport timeout.

Durable artifacts:

- `lab/experiments/ARC-R015-protocol.json`;
- `lab/results/ARC-R015-tournament.json`;
- `lab/results/ARC-R015-cache-manifest.json`;
- `lab/runs/2026-08-23/ARC-R015.md`.

The tournament cache was deterministic but stored under `/tmp` and therefore not durable after Actions teardown. No repeated identical inference occurred, and missing response hashes were not fabricated. Fix this in the baseline workflow by persisting sanitized cache/cache-manifest evidence.

## Next scheduled shift: ARC-R016

Execute exactly one task: `T0002C-NVIDIA-BASELINE`.

Establish a fully cached, reproducible baseline for **`deepseek-ai/deepseek-v4-flash-0731`** on the frozen development split. Freeze task IDs/manifest, prompt/protocol, generation settings, attempts and budget before inference. Use only deterministic public-training-derived development data; public evaluation remains sealed.

Record exact solved/total, per-task outputs/accounting, parseability, provider failures, calls, tokens, runtime, cache hits and durable cache/cache-manifest evidence. Preserve the provider-neutral NVIDIA adapter path. Do not spend routine calls on Nemotron, Gemma or GPT-OSS unless the queue explicitly changes.

Do not begin `T0003-FIRST-ARCHITECTURE-TOURNAMENT` until the baseline is complete, and do not chain it into the same shift.

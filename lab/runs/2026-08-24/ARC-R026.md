# ARC-R026 — T0012 Max-Reasoning Direct Ablation

Date: 2026-08-24
Task: `T0012-MAX-REASONING-DIRECT-ABLATION`
Role: `llm-experimenter`
Verdict: **REJECT**
Public evaluation: **sealed / unused**

## Question and hypothesis

Test whether the frozen DeepSeek V4 Flash direct ARC baseline materially improves when the inference regime is increased to `reasoning_effort=max` and `max_output_tokens=16384`, holding model, prompt, scorer, split and one-prediction contract fixed.

Hypothesis: the maximum supported direct-inference regime will strictly and materially exceed the frozen ARC-R016 comparator of **45/174 = 25.8621%** exact accuracy on the identical deterministic `dev_validation` split.

Causal limitation: reasoning effort and output cap changed together, so this run evaluates the bundled maximum-inference regime rather than identifying which setting causes any delta.

## Frozen protocol

- Split: `dev_validation`
- Tasks: identical 174 task IDs from ARC-R016; manifest SHA-256 `3fd73c956172767d972555df37b73bbdecef77578a76ce71c7c126357e7e51b0`
- Provider: NVIDIA NIM
- Model: `deepseek-ai/deepseek-v4-flash-0731`
- Solver: `nvidia-direct-json-max-reasoning-v1`
- Prompt/scorer: unchanged direct ARC JSON prompt and exact scorer from ARC-R016
- Temperature: `0.0`
- top_p: `1.0`
- reasoning_effort: `max`
- max_output_tokens: `16384`
- Attempts per test input: `1`, with explicit transport recovery separated from the primary first-attempt statistic
- Provider HTTP timeout: `900s`
- GitHub Actions timeout: `360m`
- Comparator: ARC-R016, **45/174 = 25.8621%**

Protocol artifact: `lab/experiments/ARC-R026-max-reasoning-direct-protocol.json`.

## Execution evidence

External workflow run id: `32743684588`.
Execution started: `2026-08-24T15:15:02.234707+00:00`.
Execution finished: `2026-08-24T16:47:02.260584+00:00`.
Workflow elapsed wall-clock from durable timestamps: approximately **5520.026 seconds (92.000 minutes)**.

Durable result: `lab/results/ARC-R026-max-reasoning-direct.json`.
Durable execution status: `lab/executions/ARC-R026.json`.

## Result

### Primary first-attempt statistic

- Exact solves: **37/174**
- Accuracy: **21.2644%**
- Delta versus ARC-R016: **-8 solves / -4.5977 percentage points**
- New solves versus ARC-R016: 6
  - `694f12f3`
  - `6c434453`
  - `810b9b61`
  - `8f2ea7aa`
  - `a68b268e`
  - `ea9794b1`
- Regressions versus ARC-R016: 14
  - `05f2a901`
  - `0607ce86`
  - `195ba7dc`
  - `1fad071e`
  - `445eab21`
  - `56ff96f3`
  - `8ee62060`
  - `b1948b0a`
  - `bb43febb`
  - `bdad9b1f`
  - `c9f8e694`
  - `ccd554ac`
  - `dc1df850`
  - `e048c9ed`

### Operational statistic after explicit transport recovery

- Exact solves: **41/174**
- Accuracy: **23.5632%**
- Delta versus ARC-R016: **-4 solves / -2.2989 percentage points**
- New solves versus ARC-R016: 6
- Regressions versus ARC-R016: 10
  - `05f2a901`
  - `195ba7dc`
  - `1fad071e`
  - `445eab21`
  - `56ff96f3`
  - `8ee62060`
  - `bb43febb`
  - `bdad9b1f`
  - `dc1df850`
  - `e048c9ed`

The frozen decision rule required strictly exceeding 45/174. Neither the primary nor the operational-recovery statistic meets that threshold.

## Resource accounting

- Live provider calls: **234**
- Successful response finish reasons: `stop = 177`
- Transport failure events: **57**
- Terminal provider failures: **12**
- Parse failures: **1**
- Cache hits: **0**
- Input tokens: **458,220**
- Output tokens: **146,054**
- Total tokens: **604,274**
- Rate-limit snapshots persisted: none

Output-token buckets across successful outputs:

- `<=4096`: **173**
- `4097-8192`: **3**
- `8193-16383`: **1**
- `16384_cap`: **0**
- unknown: **0**

No successful output hit the 16K cap. The overwhelming majority were at or below 4096 output tokens, so the larger cap itself was almost never binding.

## Failure analysis

The run is dominated by two distinct observations.

First, increasing the direct-inference regime did not improve exact accuracy. The first-attempt result regressed by 8 solves, and even after recovering retryable transport failures the treatment remained 4 solves below the frozen comparator. Six tasks became newly solved, but these gains were outweighed by ten operational regressions.

Second, provider reliability materially affected the raw first-attempt statistic: 57 transport failure events and 12 terminal provider failures were observed. Recovery restored four comparator solves relative to the first-attempt score (37 -> 41), demonstrating that availability noise mattered. However, recovery still did not reach the comparator, so transport instability cannot explain away the rejection.

The token-length distribution also weakens the hypothesis that the old 4096-style output ceiling was the main bottleneck: 173 successful outputs stayed at or below 4096 tokens, only four exceeded it, and none reached 16384.

## Adversarial interpretation

The treatment changes two settings together, so this run cannot separately conclude that `reasoning_effort=max` is harmful or that a 16K cap is useless. It only rejects the bundled maximum-inference regime as a main explanation for the current direct-baseline gap under this provider/model/protocol.

Provider instability is a real confound for the exact magnitude of the first-attempt regression, but not for the experiment decision: the transport-recovered result is still 41/174, below 45/174. A cleaner provider run might shift several tasks, but there is no positive evidence here that more direct inference budget yields a material gain.

Because the output cap was almost never approached, a follow-up whose only purpose is to raise the cap is poorly motivated. If future work revisits inference settings, it should use a narrower matched ablation that isolates reasoning effort and only after stronger evidence justifies the calls.

## Decision and next research direction

**REJECT** the maximum direct-inference regime as the main explanation for the current ARC gap. Preserve ARC-R016 as the frozen direct comparator.

The result redirects the program back toward representation/generation failure analysis. The next queued task should be reconsidered from current Git truth; at closure time `T0011-CANDIDATE-FAILURE-TAXONOMY` is the ready lower-priority research task designed to derive falsifiable representation/generator hypotheses from mechanically verified candidate evidence without new model calls.

No second substantive task is started in this shift.

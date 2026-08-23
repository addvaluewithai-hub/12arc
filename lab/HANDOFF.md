# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. Public evaluation remains sealed.

`ARC-R010` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE** for benchmark completion, but it resolved the immediate quota diagnosis. No ARC score was claimed and ARC-R010 itself made zero new model calls.

The frozen baseline remains `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints, exact full-task scoring, all 174 deterministic `dev_validation` tasks.

ARC-R010 audited completed paced run `32617284889`. With 61-second minimum spacing between uncached live-call starts, the run executed for the full deliberate 42-minute process timebox without the prior 16k input-TPM 429. It stopped only on exit code 124 from the timebox, then successfully saved cumulative cache, persisted outcome, and uploaded artifact `9487805832` with digest `sha256:1265c30c29616943bc005ccead464236ae2f408a43db0420f9597894732c5436`.

That artifact contains 113 unique cached responses, 313,622 input tokens, 544,707 total tokens and 4,938.450 seconds aggregate provider runtime. It adds 41 responses, 78,206 input tokens, 162,051 total tokens and 1,816.402 seconds runtime beyond the prior 72-response cache.

Observed per-request input tokens are still 248..9,634; none of the 113 observed requests is >=16,000. This supports the conclusion that the earlier provider failure was aggregate input tokens per minute, not evidence that an observed ARC request individually exceeds the 16k quota. There is no evidence of an RPM blocker from the paced run. The 16k TPM limit is a manageable throughput constraint under conservative pacing/resume, though pacing is slow.

The dominant blocker is now separate: **113/113 cached responses have empty visible `text` despite non-zero total token usage**, and output/candidate token fields are null. Do not spend another full baseline chunk blindly. First isolate whether this is thinking/output-budget behavior, provider response semantics, SDK parsing, or adapter extraction using a small controlled cached diagnostic changing one variable at a time.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. Preserve the frozen comparator and leakage policy. Full record: `lab/runs/2026-08-23/ARC-R010.md`.

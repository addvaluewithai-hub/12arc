# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. Public evaluation remains sealed.

`ARC-R013` worked only on `T0002-GEMMA-BASELINE` and **REJECTED** the ARC-R012 `max_output_tokens=8192` treatment after its durable evidence appeared.

The full frozen comparator remains `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints, exact full-task scoring, all 174 deterministic `dev_validation` tasks.

ARC-R011 established the empty-output mechanism on deterministic task `00dbd492`, test index 0: with the frozen 2048 output cap, the call used 2,982 input tokens and 2,045 thought tokens, emitted zero candidate tokens, returned zero visible text and finished `MAX_TOKENS`. Runtime 43.2723 s; total usage 5,027. Across 113 cached baseline responses, `total_tokens - input_tokens = 2,045` for 113/113 and visible text is empty.

ARC-R012 then triggered a one-variable ablation on that exact request, changing only `max_output_tokens` from 2048 to 8192. The durable result is now at `lab/recon/gemma-output-budget-ablation-latest.json`, persisted by GitHub Actions bot commit `1d5de993efb38580d7dcce1e1869b9576eab36b5`.

The 8192 treatment used the same 2,982 input tokens, consumed 8,189 thought tokens, emitted no final candidate/output tokens, returned zero visible text, produced no parsed grid, and again finished `MAX_TOKENS`. Total tokens were 11,171 and runtime 172.106133682 s. Relative to the 2048 comparator, the extra configured allowance was +6,144 tokens and the observed thought-token increase was exactly +6,144. Runtime increased by 128.833833682 s with no usable output.

Therefore merely increasing the output cap is not a viable repair at 8192. ARC-R013 issued **zero new target-model calls** and no duplicate treatment request.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. The next falsifiable uncertainty is whether the authorized Gemma API exposes a reproducible thinking-control mechanism that can keep the same `gemma-4-26b-a4b-it`, task `00dbd492`, prompt SHA `aefa22e7984e5bcf94f7c213cf3634db4b824d48f61ad3088ebd3fd9196bb578`, sampling and bounded output budget while preventing thoughts from consuming the entire response allowance. If supported, test thinking control as the sole model-facing variable on this same request before changing the full baseline. If unsupported, durably establish that API/model limitation before changing prompt protocol or routing.

Keep the earlier input-TPM issue separate: 61-second pacing already avoided the aggregate 16k input-TPM 429 for a 42-minute chunk. Do not mix in 31B routing, provider changes, prompt changes, public evaluation or another output-cap increase in the same experiment.

Full record: `lab/runs/2026-08-23/ARC-R013.md`.

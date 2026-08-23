# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` and `ARC-R003 / T0001A-GEMMA-EXECUTION-PATH` are complete. Public evaluation remains sealed.

`ARC-R012` worked only on `T0002-GEMMA-BASELINE` and ended **INCONCLUSIVE** because the committed 8192-token matched ablation had not yet produced durable live evidence at cutoff.

The full frozen comparator remains `direct-json-v1`: `gemma-4-26b-a4b-it`, `temperature=1.0`, `top_p=0.95`, `top_k=64`, `max_output_tokens=2048`, exactly two attempts per test input, deterministic cache/fingerprints, exact full-task scoring, all 174 deterministic `dev_validation` tasks.

ARC-R011 established the empty-output mechanism on deterministic task `00dbd492`, test index 0: with the frozen 2048 output cap, the call used 2,982 input tokens and 2,045 thought tokens, emitted zero candidate tokens, returned zero visible text and finished `MAX_TOKENS`. Runtime 43.2723 s; total usage 5,027. Across 113 cached baseline responses, `total_tokens - input_tokens = 2,045` for 113/113 and visible text is empty.

ARC-R012 committed a one-variable ablation on that exact request. `src/arc_lab/output_budget_ablation.py` holds model, prompt construction, task/test/attempt identity, solver-version identity and sampling fixed, changing only `max_output_tokens` from 2048 to 8192. `.github/workflows/gemma-output-budget-ablation.yml` fetches only pinned public training data, runs tests, executes at most one treatment call, verifies prompt/model/task/sampling identity against `lab/recon/gemma-empty-output-latest.json`, then persists sanitized evidence to `lab/recon/gemma-output-budget-ablation-latest.json`.

Trigger commit: `5d3a05f5f0b96ce9fac4c2ae6a2409999a40e29b`.

At ARC-R012 cutoff the treatment evidence file was still absent and the connected status surface exposed no status context for that trigger. Do not infer a call, tokens, runtime, finish reason, ARC result or failure from this absence. ARC-R012 claims zero durably verified treatment calls.

Next execute exactly one task: continue `T0002-GEMMA-BASELINE`. First audit whether the existing ARC-R012 trigger produced `lab/recon/gemma-output-budget-ablation-latest.json`, a workflow run, or artifact. Do **not** issue another 8192-token call until you establish that the first did not execute. If the evidence exists, record the exact treatment result and decide whether the larger output cap restores a final candidate. If no execution occurred, repair only the orchestration path and run the already-frozen ablation once.

Keep the earlier input-TPM issue separate: 61-second pacing already avoided the aggregate 16k input-TPM 429 for a 42-minute chunk. Do not add 31B routing, thinking controls, prompt changes, or public-evaluation access in the same experiment.

Full record: `lab/runs/2026-08-23/ARC-R012.md`.

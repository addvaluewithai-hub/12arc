# Handoff

Start from `lab/RUNNER.md` and current Git state. Do not continue the old Gemma plan.

## Active model policy

Routine research uses NVIDIA NIM. Fixed primary target model: `deepseek-ai/deepseek-v4-flash-0731`. Nemotron remains escalation/research only. Gemma and GPT-OSS are legacy comparators unless explicitly queued.

## ARC-R016 is complete

`T0002C-NVIDIA-BASELINE` is complete and ARC-R016 should not be resumed.

Frozen comparator:

- run: `ARC-R016`;
- solver: `nvidia-direct-json-baseline-v1`;
- split: all 174 deterministic `dev_validation` IDs;
- model: `deepseek-ai/deepseek-v4-flash-0731` on NVIDIA NIM;
- generation: temperature 0.0, top_p 1.0, top_k null, max_output_tokens 4096;
- one attempt per test input;
- no hidden provider retries;
- manifest SHA-256: `97102661ae8ae093dcc4afe3fb0122fbca7b0480893302d5b7a7a1044cb88433`;
- public evaluation used: no.

Final result: **45 / 174 = 25.8621% exact task accuracy**.

Resource/accounting evidence: 179 durable request records, 458,626 input tokens, 175,994 output tokens, 634,620 total tokens, 4,625.097828976 seconds summed model runtime, 13 parse failures recorded, 10 provider failures recorded, and 108 wrong-but-parseable task records.

Evidence:

- `lab/experiments/ARC-R016-protocol.json`
- `lab/results/ARC-R016-baseline.json`
- `lab/results/ARC-R016-cache-manifest.json`
- `lab/results/ARC-R016-cache-archives/`
- `lab/runs/2026-08-23/ARC-R016.md`

Recovery history: workflow run `32649224421` originally lost chunk 3 to the 45-minute job timeout. Recovery job `97234116594` completed chunk 3; aggregate job `97237369824` reused the five original successful artifacts plus recovered chunk 3 and persisted the complete result. Do not repeat ARC-R016 inference.

## Next shift: ARC-R017

Execute exactly one task: `T0003-FIRST-ARCHITECTURE-TOURNAMENT`.

The research goal is no longer baseline establishment. Invent and test one structured hypothesis-generation + exact-verification treatment against the frozen ARC-R016 direct-JSON comparator.

Before inference, freeze a falsifiable matched experiment contract: one primary architecture variable, declared task slice from public-training-derived development data, exact model/settings, attempts and budget, and success/falsification criteria. Prefer a small but informative slice for the first architecture tournament rather than immediately spending another full 174-task baseline budget.

Measure exact new solves and regressions versus the ARC-R016 comparator on the same task IDs, plus parse failures, provider failures, calls/tokens/runtime and qualitative failure families. Distinguish genuine reasoning gains from output-validity or provider-reliability gains. Public evaluation remains sealed/milestone-only.

Stop after the one architecture-tournament task; do not chain into a second research task in the same shift.

# Handoff

Start from `lab/RUNNER.md`.

`ARC-R001 / T0001-BENCHMARK-HARNESS` is complete. The benchmark surface now has pinned ARC-AGI-2 public-training source metadata, deterministic development splitting, strict grid/task validation, explicit output-vs-task scoring, reproducibility tests, and a development validation path that does not require public-evaluation data.

Next execute `T0001A-GEMMA-EXECUTION-PATH`. Build a provider-independent Gemma client around the authorized repository secret, verify the provider's current live model identifier, add deterministic request fingerprinting/cache plus usage/runtime accounting, and perform only a non-ARC smoke call for infrastructure validation. Never expose or commit the secret.

After that, unblock and execute `T0002-GEMMA-BASELINE` on the frozen development split. Do not use public evaluation as iterative feedback.

The GitHub connector could not surface a push-triggered Actions run for ARC-R001, so do not silently assume hosted CI is green; the implementation was locally exercised with 16 passing tests, and CI is configured to perform the pinned-corpus integration validation on GitHub.

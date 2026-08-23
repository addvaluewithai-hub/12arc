# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R017 is complete: REJECT

`hypothesis-train-replay-v1` decisively failed its frozen matched test. DeepSeek direct JSON comparator solved 4/8; treatment solved 1/8, with zero new solves and three regressions. The treatment used 8 calls / 41,344 tokens / 383.978 s model runtime, with two parse failures and zero provider failures. Public evaluation was not used.

Important mechanistic finding: exact training replay is not a sufficient verifier. Six of eight treatment outputs passed the replay gate, but verified candidates still regressed `00dbd492` and `05f2a901`. Full replay also created a severe output-token burden: `0607ce86` and `06df4c85` hit the 4096 output cap and did not parse.

Evidence: `lab/results/ARC-R017-architecture-tournament.json`; finalized report: `lab/runs/2026-08-23/ARC-R017.md`.

## Next task

`T0004-COMPACT-HYPOTHESIS-SEARCH` is ready. Its purpose is not to retry the rejected gate. Design a matched experiment around multiple **compact** candidate hypotheses and discriminative verification that attacks rule ambiguity without serializing complete training-grid replays. Keep DeepSeek V4 Flash, frozen development discipline, and comparator controls unless the explicit primary variable requires otherwise.

Before claiming ARC-R018, reconcile `lab/registry/run-counter.json`: a connector write guard prevented this shift from deleting the now-stale ARC-R017 reservation even though the queue claim was released and ARC-R017 is durably complete. Treat the result/report/queue as evidence of completion, remove the stale reservation with a normal Git-capable path, then reserve ARC-R018.

Model policy remains DeepSeek primary, Nemotron escalation/research only, Gemma/GPT-OSS legacy comparators. Public evaluation remains sealed/milestone-only.

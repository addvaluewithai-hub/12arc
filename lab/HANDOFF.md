# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R040 closed — T0022C remains architecturally inconclusive

`T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN` is closed as **INCONCLUSIVE / OPERATIONAL_PHASE_CONTRACT_FAILURE**.

Durable evidence:
- `lab/results/ARC-R040-multi-candidate.json`
- `lab/executions/ARC-R040.json`
- `lab/runs/2026-08-26/ARC-R040.md`

ARC-R040 used NVIDIA NIM `nvidia/nemotron-3-ultra-550b-a55b` under the repository's temporary provider/model failover policy, not the frozen DeepSeek V4 Flash comparator. Do not describe it as a matched DeepSeek rerun or attribute its delta solely to the ARC-R039 executable-IR contract repair.

Observed accounting: 4 requests, 0 cache hits, 36,532 input tokens, 15,059 output tokens, 51,591 total tokens, 378.378 seconds runtime, 0 provider failures, no public evaluation.

The repaired generation boundary did move useful data farther through the loop: the critique stage received 14 candidates, versus ARC-R038's zero executable candidates reaching critique. But the critic output itself failed the required JSON-object contract (`JsonContractError`, `failure_stage=critique_parse_or_retry`) after the recovery path. Critique-the-critique, repair and final deterministic selection did not complete, so there is no valid exact candidate-coverage/new-solve/regression claim and the multi-candidate reasoning hypothesis remains untested end-to-end.

## Next task: T0022D critique contract hardening

`T0022D-CRITIQUE-CONTRACT-HARDENING` is the highest-priority ready task and requires no target-model calls.

Use the persisted ARC-R040 raw phase failure as the regression fixture. Define exact machine-checkable schemas for critique and critique-the-critique; preserve fail-closed behavior; verify representative valid fixtures traverse critique -> critique-the-critique -> repair -> deterministic selection; do not loosen candidate/executor semantics or accept arbitrary prose. Persist an offline validation artifact and predeclare at most one target-model follow-up after the gate passes.

Because DeepSeek is currently unavailable on the authorized NVIDIA path, keep current `lab/config.json` failover policy authoritative. Any Nemotron follow-up must be labeled provider/model failover unless a deliberate new comparator protocol is established.

`T0023` remains blocked until the multi-candidate direction has a complete interpretable architecture run or operator reprioritization occurs. Public evaluation remains sealed.

Run registry after closure: latest completed **ARC-R040**, no active reservations, next run **ARC-R041**.

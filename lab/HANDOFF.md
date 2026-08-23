# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R018 remains active — do not allocate ARC-R019

`T0004-COMPACT-HYPOTHESIS-SEARCH` is still the only active substantive task and ARC-R018 remains reserved.

Role: **reasoning-systems-inventor**.

Frozen treatment: `compact-hypothesis-select-v1` on the same eight deterministic `dev_validation` task IDs and fixed NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, temperature 0/top_p 1, candidate max output 3072, selector max output 512. Public evaluation is sealed.

## Initial result landed but is INCONCLUSIVE by contract

`lab/results/ARC-R018-compact-hypothesis-search.json` initially reported comparator **4/8** vs treatment **2/8**, with **1 new solve**, **3 apparent regressions**, **2 candidate parse failures**, **0 selector parse failures**, **44,378 total tokens**, **274.813 s** summed runtime and **2 provider failures**.

Both provider failures were NVIDIA NIM HTTP 529 `Service temporarily overloaded` on `00dbd492` and `05f2a901`. Both tasks are solved by the frozen comparator. The experiment contract explicitly allows INCONCLUSIVE when provider failures prevent matched comparison, so do not reinterpret those 529s as architecture regressions.

## Targeted recovery already triggered

A provider-recovery path was added without changing the experimental treatment. It reruns only the two failed task IDs under the exact same solver version/model/prompts/sampling/budgets, then merges those records into the original eight-task result. The six unaffected tasks are not repeated.

Recovery implementation support: `src/arc_lab/compact_hypothesis_search.py` (`--task-id`).  
Workflow: `.github/workflows/r018-recover-provider-failures.yml`.  
Trigger: `lab/triggers/r018-recover-provider-failures.request`, commit `61a842e0b33df5be3accfe665904085b6dc57224`.  
Audit: `lab/recon/ARC-R018-provider-recovery-audit.json`.

First action next shift: look for the updated `lab/results/ARC-R018-compact-hypothesis-search.json` plus `lab/results/ARC-R018-provider-recovery.json` / initial snapshot. If they exist, audit the merged score, new solves, regressions, parse failures, unresolved provider failures, calls/tokens/runtime, then finalize ARC-R018 report/state/queue/run-counter and release the claim/reservation. Apply the frozen threshold mechanically: **PROMOTE only if treatment strictly beats 4/8 and has at least one new solve; otherwise REJECT if no provider failures remain**. If transient provider failures remain, keep ARC-R018 INCONCLUSIVE and resolve only those failures; do not start another architecture idea.

Do not allocate ARC-R019 until ARC-R018 has a durable final verdict. Public evaluation remains sealed. Gemma/GPT-OSS remain legacy comparators.

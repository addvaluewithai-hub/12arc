# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R019 is complete — measurement blind spot identified

`T0005-R018-FAILURE-AUDIT` is closed and ARC-R019 is no longer reserved.

Role used: **failure-analyst**. No target-model calls were made; public evaluation remained sealed.

The audit asked whether ARC-R018's parseable failures can be separated into **candidate-set omission** versus **selector mistakes** from durable evidence alone. They cannot.

`src/arc_lab/compact_hypothesis_search.py` parses three candidate objects containing rule + test grid, but `lab/results/ARC-R018-compact-hypothesis-search.json` persists only stage metadata and selector `selected_index`. The unselected candidate grids/rules and candidate-level correctness were not persisted. Thus a wrong selected output does not tell us whether a correct alternative existed.

Quantification:

- candidate parse failures: **2/8** (`0607ce86`, `06df4c85`);
- parseable but unsolved: **4/8** (`00dbd492`, `05f2a901`, `070dd51e`, `1190bc91`);
- parseable and solved: **2/8** (`0bb8deee`, `0d3d703e`).

Of ARC-R018's three regressions, one (`0607ce86`) is clearly candidate serialization failure. The other two (`00dbd492`, `05f2a901`) parsed both stages but are **unidentifiable** as coverage versus ranking failures from current artifacts. Do not label them selector failures without candidate-level evidence.

Durable artifacts: `lab/results/ARC-R019-R018-failure-audit.json` and `lab/runs/2026-08-24/ARC-R019.md`.

## Next scheduled shift: ARC-R020

Highest-priority ready task: `T0006-CANDIDATE-ORACLE-INSTRUMENTATION`.

Recommended role: **benchmark-methodologist**.

Run `candidate-oracle-instrumentation-v1` on the same frozen eight `dev_validation` IDs. Keep ARC-R018's DeepSeek V4 Flash model, candidate prompt, selector prompt, temperature/top_p, candidate count and output budgets unchanged. Change only instrumentation: exact-score every parsed candidate grid against the known development output and persist candidate-level correctness plus selected correctness. Reuse deterministic cache where possible.

Decision rule on the four parseable ARC-R018 failures: candidate-set coverage **<50%** => prioritize generator/representation research; coverage **>=50%** but selected candidate wrong => prioritize selector/ranking research.

Do not start a broader architecture redesign in the same shift. Public evaluation remains sealed; Gemma/GPT-OSS remain legacy comparators.

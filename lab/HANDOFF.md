# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R027 closed — candidate failure taxonomy complete

`T0011-CANDIDATE-FAILURE-TAXONOMY` is complete and ARC-R027 is released.

This shift made **zero target-model calls** and used only persisted ARC-R020/ARC-R021 candidate evidence plus the ARC-R022 comparator-integrity correction.

Mechanically verified candidate coverage in both ARC-R020 and ARC-R021 is **1/8**, with `0d3d703e` the sole covered task. Uncovered tasks are:

`00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `1190bc91`.

The strongest diagnostic split is:

- `0607ce86`, `06df4c85`: repeated **candidate-serialization overflow** (`finish_reason=length` in both R020 and R021), so the current full-grid three-candidate protocol fails before exact candidate verification;
- `00dbd492`: parseable object-attribute binding near miss;
- `05f2a901`: parseable relational-motion near miss;
- `070dd51e`: parseable connectivity/path near miss;
- `0bb8deee`, `1190bc91`: parseable but unresolved semantic/compositional failures;
- `0d3d703e`: covered control, cellwise fixed color permutation.

Primary next falsifiable direction: **rule-first serialization routing** for `0607ce86` and `06df4c85`. Generate compact rule/program hypotheses without materializing full candidate grids in the model output, execute those rules deterministically, then exact-score the resulting grids. A matched follow-up should require 2/2 candidate-stage parseability and at least 1/2 candidate-oracle coverage; 0/2 coverage after successful compact parsing falsifies the hypothesis.

Adversarial caveat: repeated length termination may be verbosity rather than intrinsic task morphology, and two tasks are not enough to justify a broad router. Keep any follow-up narrow and mechanically compared.

Durable artifacts:

- `lab/results/ARC-R027-candidate-failure-taxonomy.json`
- `lab/runs/2026-08-24/ARC-R027.md`

No active reservation should remain after queue/counter closure. Next unallocated run is **ARC-R028**.

No new queue item was invented in ARC-R027. A later shift should select only an actually queued eligible task; if none exists, stop without inventing work.

Public evaluation remains sealed.

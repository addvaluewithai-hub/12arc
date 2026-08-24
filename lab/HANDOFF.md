# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R021 active — object/relation candidate generator

`T0007-OBJECT-RELATION-CANDIDATE-GENERATOR` is claimed and ARC-R021 is reserved. Do **not** allocate ARC-R022 until this run is reconciled.

ARC-R020 diagnosed generator/representation as the bottleneck: on the four predeclared prior parseable failures all four candidate stages parsed but 0/4 candidate sets contained a correct answer; overall candidate coverage was only 1/8.

ARC-R021 uses role **object-centric-researcher** and changes one primary variable: candidate generation now explicitly reasons in a compact object/relation representation before producing the same three rule+grid hypotheses. It asks for background, connected objects, color/size/bounding-box/shape, repeated motifs, containment/touching/alignment/symmetry and supported object-level operations, without serializing the intermediate scene graph.

Controls remain frozen: same eight ARC-R020 `dev_validation` IDs, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, temperature 0/top_p 1, candidate output cap 3072, selector cap 512, one attempt/test, same selector prompt, candidate-level oracle scoring. Public evaluation is unused.

Decision rule: PROMOTE iff candidate coverage >=3/8, >=2 newly covered tasks versus ARC-R020, and previously covered `0bb8deee` remains covered. Provider failures => INCONCLUSIVE; otherwise REJECT.

Durable pre-execution artifacts: `src/arc_lab/object_relation_generator.py`, `tests/test_object_relation_generator.py`, `.github/workflows/r021-object-relation-generator.yml`, `lab/runs/2026-08-24/ARC-R021.md`. Trigger: `lab/triggers/r021-object-relation-generator.request`.

At handoff, `lab/results/ARC-R021-object-relation-generator.json` had not yet landed. Next shift must check for that result first. If present, apply the predeclared decision rule, record exact calls/tokens/runtime, parse/provider failures, new candidate coverage and regressions, finalize queue/state/handoff, release ARC-R021, then stop. If still in flight, retain the reservation and do not invent results.

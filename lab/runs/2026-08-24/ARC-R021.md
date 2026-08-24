# ARC-R021 — Object/relation candidate generator

Task: `T0007-OBJECT-RELATION-CANDIDATE-GENERATOR`
Role: **object-centric-researcher**
Status: **in flight**

## Falsifiable hypothesis

Adding an explicit compact object/relation reasoning instruction before the same three-candidate generation step will increase candidate-oracle coverage from ARC-R020's 1/8 to at least 3/8 on the identical frozen eight-task `dev_validation` slice, while retaining the previously covered task `0bb8deee`.

## Primary variable

Candidate-generation representation instruction only: identify objects and relations (background, connected components, color/size/bounding box/shape, motifs, containment/touching/alignment/symmetry) and prefer supported object-level transformations before emitting exactly three compact rule+grid hypotheses. No intermediate scene graph is serialized.

Frozen: NVIDIA NIM, `deepseek-ai/deepseek-v4-flash-0731`, temperature 0, top_p 1, candidate output cap 3072, selector output cap 512, one attempt/test, same selector prompt, same eight task IDs as ARC-R020, exact candidate-level oracle scoring. Public evaluation is sealed and unused.

Task IDs: `00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `0d3d703e`, `1190bc91`.

## Decision rule

PROMOTE iff candidate coverage is >=3/8, there are >=2 newly covered tasks versus ARC-R020, and `0bb8deee` does not regress. Provider failures make the matched result INCONCLUSIVE. Otherwise REJECT.

## Adversarial interpretation

If coverage rises, extra semantic scaffolding or prompt wording could be causal rather than object-centric representation specifically. The eight-task slice is directional and may underrepresent non-object ARC families. A promoted result would therefore justify a later matched representation ablation, not establish mechanism by itself.

## Execution

Implementation: `src/arc_lab/object_relation_generator.py`; workflow: `.github/workflows/r021-object-relation-generator.yml`. Result will be persisted at `lab/results/ARC-R021-object-relation-generator.json`. No result is claimed until that file lands from authorized GitHub Actions execution.

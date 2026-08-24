# ARC-R027 — Candidate failure taxonomy

Task: `T0011-CANDIDATE-FAILURE-TAXONOMY`  
Role: **failure-analyst**  
Status: **COMPLETE**

## Hypothesis / objective

Mechanically verified ARC-R020/ARC-R021 candidate evidence contains distinguishable failure families that can support a narrower, falsifiable next generator treatment without new target-model calls.

Primary diagnostic variable: classify the seven mechanically uncovered tasks by observable candidate-stage and transformation features, while treating ARC-R022's comparator correction as authoritative and ignoring the corrected-away manual coverage swap.

No target-model calls were made. Public evaluation was not used.

## Sources and comparator integrity

Durable sources:

- `lab/results/ARC-R020-candidate-oracle.json`
- `lab/results/ARC-R021-object-relation-generator.json`
- `lab/results/ARC-R022-representation-coverage-audit.json`

Mechanical coverage is identical in R020 and R021: **1/8**, with only `0d3d703e` covered. Uncovered IDs are:

`00dbd492`, `05f2a901`, `0607ce86`, `06df4c85`, `070dd51e`, `0bb8deee`, `1190bc91`.

## Taxonomy

### 1. Candidate-serialization overflow

Tasks: `0607ce86`, `06df4c85`.

Both terminate candidate generation with `finish_reason=length` in ARC-R020 and again in ARC-R021. This is qualitatively different from a parseable-but-wrong candidate set: the current protocol spends the fixed 3072-token candidate budget materializing large full-grid hypotheses before candidate-oracle verification can operate.

Failure layer: representation/output protocol before semantic verification.

### 2. Parseable object-attribute binding near miss

Task: `00dbd492`.

Both runs parse successfully but have zero exact candidate coverage. Persisted rules repeatedly identify red rectangles and propose interior fills based on object attributes, so broad object detection is not the missing capability; the binding from the relevant object property to the correct fill action remains wrong.

### 3. Parseable relational motion near miss

Task: `05f2a901`.

Both runs parse successfully with zero coverage. Persisted candidates propose moving one colored object relative to another using alternative alignment rules. The observable failure is therefore in the relational goal/termination condition, not basic object extraction.

### 4. Parseable connectivity/path near miss

Task: `070dd51e`.

Both runs parse successfully with zero coverage. Persisted rules recognize same-color endpoint connection with horizontal/vertical lines but miss exact path/interaction details. This points to relation/path construction and precedence rather than a generic object representation gap.

### 5. Parseable unresolved compositional failures

Tasks: `0bb8deee`, `1190bc91`.

Both remain parseable with zero mechanically verified coverage under generic compact generation and the object/relation prompt. The durable evidence does not justify a narrower morphology label without importing manual annotations, so they remain an explicit unresolved bucket rather than being overclassified.

### Control case

`0d3d703e` is mechanically covered in both runs and ARC-R022 identifies it as a cellwise fixed color permutation. This is evidence against routing every task through heavier object-centric machinery.

## Primary falsifiable next hypothesis

**Rule-first serialization routing for repeated length-overflow tasks.**

For `0607ce86` and `06df4c85`, generate compact rule/program hypotheses without materializing full predicted grids inside the model response; execute the rules deterministically to obtain grids for exact candidate-oracle scoring.

Frozen comparator: ARC-R020 compact-hypothesis candidate generation on the same IDs/model/settings.

Success threshold: **2/2 candidate stages parseable and at least 1/2 mechanically verified candidate coverage**, with no full-grid candidate serialization in the model response.

Falsification: either task still fails to produce a parseable compact rule under the same candidate token budget, or both rules parse but deterministic execution produces **0/2** exact candidate coverage.

## Adversarial review

- `finish_reason=length` could be verbosity rather than intrinsic morphology; a shorter prompt may be sufficient.
- Two repeated overflow tasks are a local diagnostic, not evidence for a population-wide router.
- Parseable zero-coverage may reflect only the three-candidate search width rather than a missing primitive.
- Semantically plausible candidate rules are not proof of the true transformation.
- Hosted inference can vary, so any follow-up must keep a matched comparator and mechanical coverage derivation.

## Result

Verdict: **RESEARCH_DIRECTION**.

The strongest uncertainty-reducing next treatment is not another universal representation prompt. It is a compact rule-first candidate representation on the two repeated serialization-overflow tasks, followed by deterministic execution and exact candidate-oracle scoring.

Durable taxonomy: `lab/results/ARC-R027-candidate-failure-taxonomy.json`.

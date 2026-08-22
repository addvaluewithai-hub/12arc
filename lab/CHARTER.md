# ARC Research Lab Charter

## Objective

Discover a reproducible inference-time reasoning architecture that makes a fixed open-weight target model materially better on novel ARC-AGI-2 tasks.

The research team is the inventor. Gemma is the controlled experimental engine. ARC exact-match scoring is the judge.

## What may change

Prompt protocol, intermediate representations, object extraction, DSL primitives, candidate generation, search strategy, verifier, critic, memory/context construction, tool use, routing between target models, and carefully justified learned components.

## What stays fixed inside an experiment series

Target model version, benchmark split, scorer, generation budget, temperature/sampling configuration unless that variable is the explicit treatment, and all unrelated solver components.

## Non-goals

- Do not optimize by repeatedly looking at public-evaluation feedback.
- Do not count research-team answers as target-model solves.
- Do not claim a score from qualitative inspection.
- Do not hide retries, token use, compute, regressions or failed tasks.
- Do not depend on an online proprietary API in the final reproducible evaluation path.

## Success

A result matters when it survives matched ablation, solves genuinely held-out development tasks, has explainable new-solves/regressions, and remains feasible under ARC Prize efficiency and reproducibility constraints.

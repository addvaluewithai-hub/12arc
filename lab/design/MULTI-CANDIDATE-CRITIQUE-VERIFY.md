# Multi-candidate critique/verify direction

Status: predeclared research direction; do not treat this as completed evidence.

## Principle

Use target models as proposal engines, not judges. The model may generate hypotheses, critique hypotheses, and repair hypotheses. Deterministic Python execution and exact scoring remain the only evidence.

This direction responds to the current evidence chain:

- ARC-R030 removed compact-serialization parse pressure but still produced 0/2 exact candidate coverage.
- ARC-R032 showed the richer lattice-region language was actually used but still produced 0/2 exact coverage.
- ARC-R035 showed a no-model search can traverse a much larger state graph after overlap alignment, but still miss an exact program.

The next architecture should therefore test whether a broader, critique-driven proposal distribution can produce useful candidate programs that the deterministic verifier can rank or falsify.

## Proposed architecture

1. **Generate many candidates.** Ask the target model for 16-32 distinct compact candidate programs/rules for a selected task. Diversity should be explicit: visual rule, object rule, lattice/region rule, exception rule, minimal program rule, and alternative decomposition prompts.

2. **Normalize and deduplicate.** Parse each candidate into the current IR or reject it fail-closed. Normalize ASTs so duplicate candidates collapse before scoring.

3. **Critique candidates.** Run model critique only to propose failure hypotheses and repairs. A critique is not evidence. It should say which training pair may fail, whether the candidate relies on forbidden constants, and whether it destroys separators or unchanged regions.

4. **Critique the critique.** Challenge the critique to avoid discarding repairable candidates because of model misunderstanding. This pass may propose a repaired rule, but the repair must go back through parsing and Python scoring.

5. **Verify in Python.** Execute candidates on permitted public training pairs only. Compute parse status, validation failure, exact coverage, cell-error distance, shape match, separator preservation, unchanged-cell preservation, program cost, duplicate cluster, new coverage, and regressions.

6. **Select deterministically.** Pick candidates by exact Python metrics, not model confidence. Exact training consistency wins; otherwise rank by coverage, cell-error distance, structural preservation, simplicity, and stability across independent generations.

## Initial target policy

Prefer starting with `06df4c85` after the currently active T0021 recovery/closure is resolved. It already executed lattice programs in ARC-R032 but remained exact-wrong, so it is a clean first target for proposal-diversity and deterministic selector tests.

Use `0607ce86` only after T0021 produces durable failure taxonomy or after a queued follow-up explicitly freezes the mechanism to test.

## Guardrails

- Never claim model critique as evidence.
- Never let the model choose the winner by self-confidence.
- Never use private/sealed evaluation data or repeated public-evaluation feedback.
- Keep exact task IDs, model/provider/version, generation settings, request counts, token usage, runtime, parse failures, provider failures, score, new coverage, regressions, and failure clusters in the durable report.
- Evolve one variable at a time if the loop fails.

## Evolution path

If the first loop does not improve coverage, keep the same direction but mutate one component at a time:

1. increase candidate diversity prompts;
2. separate generator and critic roles;
3. add repair rounds;
4. strengthen IR translation constraints;
5. adjust deterministic selector ranking;
6. add a no-model diagnostic around the dominant failure cluster.

Progress means either exact candidate coverage improves, or the loop produces a dominant mechanical failure class that supports exactly one next ablation.

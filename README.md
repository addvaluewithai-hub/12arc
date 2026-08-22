# ARC Research Lab

A reproducible research operating system for ARC-AGI-2.

## Mission

Develop a solver architecture that makes a fixed open-weight model materially better at ARC-style novel reasoning through representations, inference-time algorithms, search, verification, tool use, prompt protocols, and learned or symbolic components.

The research team invents; the target model executes; ARC benchmarks judge.

```text
Research team / ChatGPT
        ↓
hypothesis + algorithm + prompt protocol
        ↓
fixed Gemma baseline
        ↓
ARC tasks
        ↓
exact scorer + failure analysis
        ↓
promote / reject / next experiment
```

## Initial model policy

- Treat Gemma as the experimental engine, not the research lead.
- Keep the primary model fixed during controlled experiment series so score changes can be attributed to solver changes.
- Use hosted inference during R&D when available; preserve a path to offline/open-weight execution for reproducibility.
- Do not let model choice, prompt, search depth, representation, and benchmark split all change in the same experiment.

## Research principles

1. Exact benchmark truth beats qualitative impressions.
2. Every claimed improvement needs a fixed split, baseline, seed/config, compute budget, and regression accounting.
3. Public evaluation tasks are not a day-to-day optimization loop. Development feedback comes from leakage-safe splits derived from the public training set.
4. Cache model responses and never spend quota repeating identical work without a reason.
5. Track score improvement per compute/API cost, not score alone.
6. Analyze new solves and regressions task-by-task.
7. Prefer architectures that can be reproduced without proprietary online APIs at evaluation time.
8. One research shift changes one important thing and ends with a falsifiable verdict.

## Current phase

**PHASE 0 — infrastructure + reconnaissance.** No solver result is claimed yet.

The authoritative research runner and benchmark discipline will live under `lab/`.

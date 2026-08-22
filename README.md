# ARC Research Lab

A reproducible research operating system for ARC-AGI-2.

## Thesis

**The research team invents. Gemma executes. ARC judges.**

We are not treating the target model as the scientist. The lab uses research agents to invent better inference algorithms, prompt protocols, representations, search, verification and routing around a fixed open-weight model, then tests those changes objectively on held-out ARC tasks.

```text
Research team / ChatGPT
        ↓
hypothesis + solver change
        ↓
Gemma 4 fixed target model
        ↓
ARC held-out tasks
        ↓
exact benchmark + regressions + cost
        ↓
promote / reject / next experiment
```

## Initial target models

- Primary: `gemma-4-26b-a4b-it`
- Escalation candidate: `gemma-4-31b-it`

Hosted inference may be used during development, but mature solver paths must remain reproducible with the open weights offline because ARC Prize evaluation has no internet.

## Research OS

Start with [`lab/RUNNER.md`](lab/RUNNER.md). It defines queue claiming, one-task-per-shift execution, leakage policy, experiment contracts, model discipline, persistence and handoff.

Current phase: **infrastructure + benchmark discipline**. There is deliberately no ARC score claim yet.

## Core rules

1. Development feedback uses deterministic splits derived from the public training set.
2. Public evaluation is milestone-only, not a tuning loop.
3. Keep the target model fixed inside controlled experiment series.
4. Change one important variable at a time.
5. Cache identical target-model requests.
6. Report new solves and regressions, not only aggregate accuracy.
7. Track score improvement per calls/tokens/runtime.
8. Never credit a research agent's hand-solved output to Gemma.

## License

MIT-0 for lab-authored code/methods unless a file states otherwise. Third-party data/models retain their own licenses.

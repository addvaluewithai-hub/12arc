# ARC Research Lab — Authoritative Runner

This file is the only entrypoint for scheduled research agents. Do not rely on remembered chat context.

## 0. Reconstruct truth

Read, in order: `lab/config.json`, `lab/CHARTER.md`, all applicable files under `lab/protocols/`, `lab/registry/run-counter.json`, `lab/registry/queue.json`, `lab/STATE.md`, and `lab/HANDOFF.md`.

Reconcile stale or expired claims before choosing work. Git is durable operational truth.

## 1. Select exactly one task

Choose the highest-priority `ready` task whose dependencies are satisfied and whose required resources are actually available. Do not claim a target-model experiment if no target-model execution path is available. Never invent results to keep a schedule busy.

Claim the task with shift ID, timestamp and lease, then reserve the next research-run number. Use Git SHA conflicts as the concurrency lock.

## 2. Pick the research role after the task

Read `lab/roles/ROLE-CATALOG.md`. Choose the role that attacks the bottleneck, not a generic persona.

## 3. Run one deep experiment

Every research run must have:

- one falsifiable hypothesis;
- one primary variable/change;
- a frozen comparator;
- a declared task set/split;
- exact score and regression accounting when target-model execution occurs;
- target-model request/token/runtime accounting;
- a failure analysis, not just an aggregate score;
- an adversarial review asking what else could explain the delta.

The research team may invent prompts, algorithms, code and representations. It must not silently solve benchmark tasks itself and credit those answers to Gemma.

## 4. Leakage discipline

Development feedback comes only from deterministic splits derived from the public training set. Public evaluation is milestone-only and must never become a repeated tuning signal. Follow `lab/protocols/LEAKAGE.md`.

## 5. Model discipline

Treat `gemma-4-26b-a4b-it` as the initial fixed primary engine. Use `gemma-4-31b-it` only when the experiment explicitly studies routing/escalation or the queue says to do so. Hosted API inference is an R&D convenience, not a final dependency. Follow `lab/protocols/MODEL-PARITY.md` and `lab/protocols/QUOTA.md`.

If the Gemma API/connector is unavailable, do not fabricate calls. Work only on eligible infrastructure/research tasks that do not require target-model outputs, otherwise mark the blocker and stop.

## 6. Persist before claiming success

Write durable artifacts first: code, tests, configs, experiment report, raw/cache manifest or hashes, failure clusters, and any solver version change. Then update queue/state/handoff and release the claim.

A run report belongs at `lab/runs/YYYY-MM-DD/ARC-RNNN.md` and records commit/config, task IDs, baseline, treatment, metric, budget, result, regressions, interpretation and next task.

## 7. Stop

Exactly one substantive task per scheduled shift. Do not chain into the next task.

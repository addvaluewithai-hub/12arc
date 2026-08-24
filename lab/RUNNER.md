# ARC Research Lab — Authoritative Runner

This file is the only entrypoint for scheduled research agents. Do not rely on remembered chat context.

## 0. Reconstruct truth

Read, in order: `lab/config.json`, `lab/CHARTER.md`, all applicable files under `lab/protocols/`, `lab/registry/run-counter.json`, `lab/registry/queue.json`, `lab/STATE.md`, and `lab/HANDOFF.md`.

Reconcile stale or expired claims before choosing work. Git is durable operational truth.

### Resume external execution before selecting new work

Some target-model tasks declare an `execution_path` in the queue and execute through a push-triggered GitHub Actions workflow that owns provider-secret access. Follow `lab/protocols/EXTERNAL-EXECUTION.md`.

Before normal task selection, inspect any claimed task with an `execution_path` and its matching active run reservation/trigger/status/result:

- a matching external execution that is `running`, or is still within its declared `max_wait_minutes`, is **not stale solely because the ordinary claim lease elapsed**; do not duplicate its run or trigger;
- if its durable result/status is complete, resume that same task and reserved run for analysis/report/state/queue closure without reserving another run;
- if it failed or exceeded its declared wait window, resume the same task/run for recovery or persist a blocker instead of silently starting a duplicate experiment.

A declared push-triggered workflow is a valid target-model execution path even when the scheduled agent cannot call NVIDIA directly or invoke workflow-dispatch. The agent can claim/reserve the task and write the declared trigger file; the workflow then uses repository secrets. After durably writing that external handoff, stop the shift and let later scheduled shifts observe Git state.

Never disable, delete or reschedule the external hourly scheduler/automation from inside a research shift. Scheduler control belongs to the operator.

## 1. Select exactly one task

Choose the highest-priority `ready` task whose dependencies are satisfied and whose required resources are actually available. Do not claim a target-model experiment if no target-model execution path is available. Never invent results to keep a schedule busy.

Claim the task with shift ID, timestamp and lease, then reserve the next research-run number. Use Git SHA conflicts as the concurrency lock.

For a task with a declared external `execution_path`, after claim/reservation write its trigger payload exactly as specified by the task/protocol. Do not require direct provider access when the authorized workflow path is available.

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

The research team may invent prompts, algorithms, code and representations. It must not silently solve benchmark tasks itself and credit those answers to the target model.

## 4. Leakage discipline

Development feedback comes only from deterministic splits derived from the public training set. Public evaluation is milestone-only and must never become a repeated tuning signal. Follow `lab/protocols/LEAKAGE.md`.

ARC-specific pretraining on public/permitted data is not automatically disqualifying. When a foundation model has known ARC-specific exposure, label that exposure in reports so development scores are interpreted as competition utility rather than a clean measure of de-novo ARC reasoning. Never use private/sealed evaluation data or repeated public-evaluation feedback.

## 5. Model discipline

Current hosted research provider is NVIDIA NIM using repository secret `NVIDIA_API_KEY`; never print, persist or expose the secret.

The provisional primary target model is `deepseek-ai/deepseek-v4-flash-0731`. The provisional escalation/second candidate is `nvidia/nemotron-3-ultra-550b-a55b`. These choices must be validated by a small frozen development model tournament before a new full baseline is established.

Gemma (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`) and `openai/gpt-oss-120b` are legacy comparators, not routine research targets. Do not spend calls debugging or benchmarking them unless a queued experiment explicitly needs them for a controlled comparator/parity question.

Hosted API inference is an R&D convenience, not a final dependency. Keep the model-facing interface provider-neutral and preserve an open-weight/offline path. Follow `lab/protocols/MODEL-PARITY.md` and `lab/protocols/QUOTA.md`.

If the authorized target-model API is unavailable, do not fabricate calls. Work only on eligible infrastructure/research tasks that do not require target-model outputs, otherwise persist the blocker and stop.

## 6. Persist before claiming success

Write durable artifacts first: code, tests, configs, experiment report, raw/cache manifest or hashes, failure clusters, and any solver version change. Then update queue/state/handoff and release the claim.

A run report belongs at `lab/runs/YYYY-MM-DD/ARC-RNNN.md` and records commit/config, task IDs, baseline, treatment, metric, budget, result, regressions, interpretation and next task.

For an externally executed target-model task, the trigger shift does not claim experimental success. Completion is only claimable after the external workflow has persisted the result and a later shift has analyzed/closed that same reserved run.

## 7. Stop

Exactly one substantive task per scheduled shift. Do not chain into the next task.

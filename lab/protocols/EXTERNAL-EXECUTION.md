# External Execution Handoff

Some target-model tasks execute through a GitHub Actions workflow because the scheduled research agent may have GitHub read/write access without direct provider secrets or workflow-dispatch capability.

## Trigger-by-push is an available execution path

A queued task may declare an `execution_path` with a trigger file, workflow file, expected result template, execution-status template and maximum wait time. If that workflow uses repository secrets to reach the authorized provider, the task is executable even when the research agent cannot call the provider directly.

For such a `ready` task:

1. claim the task normally;
2. reserve the next ARC run normally;
3. write the declared trigger file with `schema_version`, `task_id`, reserved `run`, claim `shift_id`, and `requested_at`;
4. do not fabricate completion while the external workflow is running;
5. stop the shift after the trigger/handoff is durably written.

The workflow must validate that the trigger matches the active task claim and run reservation before inference.

## Later scheduled shifts

Before selecting a new task, inspect claimed tasks that declare `execution_path`.

- If a matching trigger/reservation exists and the execution-status file says `running`, or the trigger is still within the declared `max_wait_minutes`, do **not** expire the task merely because the ordinary claim lease elapsed. Do not create a duplicate reservation or trigger. Stop the shift unless another task is explicitly allowed to proceed concurrently by its dependencies.
- If the expected durable result exists and/or the execution-status file says `complete`, resume the **same task and same reserved run** for analysis, report/state/queue closure. Do not reserve a second run.
- If the execution-status file says `failed`, or no result/status appears after `max_wait_minutes`, resume the same task/run for recovery or persist a blocker. A fresh research-run number is only appropriate for a genuinely new experiment, not transport recovery of the same frozen protocol.

## Durable workflow state

External workflows should persist `lab/executions/ARC-RNNN.json` with at least `run`, `task_id`, `status`, workflow identity, start/end timestamps when known, and expected/result paths. Successful workflows persist the sanitized experiment result in Git before claiming completion.

## Scheduler rule

A research shift may stop because work is waiting, blocked or unavailable, but it must **never disable, delete or reschedule the external hourly scheduler/automation on its own**. Scheduler control belongs to the operator. Persist the blocker/state and stop that shift.

## Leakage and retry discipline

External execution does not relax `LEAKAGE.md`, `MODEL-PARITY.md` or `QUOTA.md`. Provider/transport retries must be explicit and separately accounted so recovered availability is not misreported as reasoning improvement.

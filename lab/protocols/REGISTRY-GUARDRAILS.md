# Registry guardrails protocol

This protocol exists because several research shifts lost time to malformed `lab/registry/queue.json`, ambiguous claim/reservation validation, and false workflow success where experiment evidence was not durably staged.

## Invariants

- `lab/registry/queue.json` and `lab/registry/run-counter.json` must parse before any substantive work or model inference.
- Every active reservation must point to exactly one `claimed` task with the same `shift_id`.
- Every `claimed` task must have `claim.shift_id`, `claim.claimed_at`, and `claim.lease_expires_at`.
- Non-claimed tasks must have `claim: null`.
- Dependencies must refer to existing task IDs.
- Trigger files are not evidence. A trigger is valid only when it matches a claimed task and one active reservation.
- A workflow must not report successful external execution unless result and execution-status artifacts exist and parse.

## Required tools

Use `python lab/tools/registry_guard.py` for workflow and local validation.

Common commands:

```bash
python lab/tools/registry_guard.py validate
python lab/tools/registry_guard.py validate-trigger lab/triggers/<name>.request
python lab/tools/registry_guard.py repair-queue-from-trigger lab/triggers/<name>.request
python lab/tools/registry_guard.py assert-evidence --run ARC-RNNN \
  --result lab/results/<result>.json \
  --execution lab/executions/ARC-RNNN.json
```

## External workflow preflight

Before any target-model call or no-model external diagnostic, a workflow must:

1. checkout with `fetch-depth: 0` so Git history is available for repair;
2. run `repair-queue-from-trigger` for the relevant trigger;
3. if repair occurred, commit the repaired registry before continuing;
4. run strict `validate-trigger`;
5. only then fetch data, install dependencies, or call providers.

## Persistence gate

Before a workflow pushes a successful result, it must:

1. write `lab/results/...`;
2. write `lab/executions/...` with terminal status;
3. run `assert-evidence`;
4. upload the same files as a GitHub Actions artifact;
5. stage the result/status/cache paths explicitly;
6. fail if nothing is staged.

## Recovery rule

If a queue file is malformed but a valid trigger and active reservation exist, the recovery path may reconstruct queue state from the latest parseable historical queue and reapply the exact same task claim and `shift_id`. This is an execution-path repair, not a new research result. It must not change solver semantics, model settings, task IDs, generation budgets, or frozen comparators.

## CI rule

The main CI and the registry-integrity workflow both run registry validation. A commit that corrupts the registry must fail fast before it can become a silent research blocker.

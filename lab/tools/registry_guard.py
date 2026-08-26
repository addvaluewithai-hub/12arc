#!/usr/bin/env python3
"""Durable registry guardrails for ARC Research Lab workflows.

This tool is intentionally dependency-free so GitHub Actions can run it before
installing the package. It prevents the recurring failure mode where queue.json
or run-counter.json become malformed or semantically inconsistent, causing
research shifts to spend runs on plumbing recovery rather than ARC evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RUN_RE = re.compile(r"^ARC-R\d{3,}$")
DEFAULT_LEASE_MINUTES = 120


class GuardError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise GuardError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        _fail(f"{path} is malformed JSON: {exc}")
    except FileNotFoundError:
        _fail(f"missing required file: {path}")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=False) + "\n")


def parse_utc(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        _fail(f"invalid UTC timestamp {ts!r}: {exc}")


def task_index(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        _fail("queue.tasks must be a list")
    out: dict[str, dict[str, Any]] = {}
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            _fail(f"queue.tasks[{i}] must be an object")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            _fail(f"queue.tasks[{i}].id must be a non-empty string")
        if task_id in out:
            _fail(f"duplicate task id: {task_id}")
        out[task_id] = task
    return out


def validate_queue(queue: dict[str, Any], *, semantic: bool = True) -> dict[str, dict[str, Any]]:
    if not isinstance(queue, dict):
        _fail("queue root must be an object")
    if queue.get("schema_version") != 1:
        _fail("queue.schema_version must be 1")
    statuses = queue.get("statuses")
    if not isinstance(statuses, list) or not statuses:
        _fail("queue.statuses must be a non-empty list")
    status_set = set(statuses)
    required = {"ready", "claimed", "blocked", "done", "cancelled"}
    missing = sorted(required - status_set)
    if missing:
        _fail(f"queue.statuses missing required values: {missing}")
    tasks = task_index(queue)
    if not semantic:
        return tasks
    for task_id, task in tasks.items():
        status = task.get("status")
        if status not in status_set:
            _fail(f"{task_id}: status {status!r} is not in queue.statuses")
        depends_on = task.get("depends_on", [])
        if not isinstance(depends_on, list):
            _fail(f"{task_id}: depends_on must be a list")
        for dep in depends_on:
            if dep not in tasks:
                _fail(f"{task_id}: missing dependency {dep}")
        claim = task.get("claim")
        if status == "claimed":
            if not isinstance(claim, dict):
                _fail(f"{task_id}: claimed task must have claim object")
            for key in ("shift_id", "claimed_at", "lease_expires_at"):
                if not isinstance(claim.get(key), str) or not claim[key]:
                    _fail(f"{task_id}: claim.{key} must be a non-empty string")
            parse_utc(claim["claimed_at"])
            parse_utc(claim["lease_expires_at"])
        elif claim is not None:
            _fail(f"{task_id}: non-claimed task must have claim=null")
    return tasks


def validate_counter(counter: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> None:
    if not isinstance(counter, dict):
        _fail("run-counter root must be an object")
    if counter.get("schema_version") != 1:
        _fail("run-counter.schema_version must be 1")
    next_run_number = counter.get("next_run_number")
    if not isinstance(next_run_number, int) or next_run_number <= 0:
        _fail("run-counter.next_run_number must be a positive integer")
    last_completed = counter.get("last_completed_run")
    if not isinstance(last_completed, str) or not RUN_RE.match(last_completed):
        _fail("run-counter.last_completed_run must be an ARC-RNNN string")
    reservations = counter.get("active_reservations")
    if not isinstance(reservations, list):
        _fail("run-counter.active_reservations must be a list")
    seen_runs: set[str] = set()
    for i, res in enumerate(reservations):
        if not isinstance(res, dict):
            _fail(f"active_reservations[{i}] must be an object")
        for key in ("run", "task_id", "shift_id", "reserved_at"):
            if not isinstance(res.get(key), str) or not res[key]:
                _fail(f"active_reservations[{i}].{key} must be a non-empty string")
        if not RUN_RE.match(res["run"]):
            _fail(f"active_reservations[{i}].run is not ARC-RNNN: {res['run']}")
        if res["run"] in seen_runs:
            _fail(f"duplicate active reservation for {res['run']}")
        seen_runs.add(res["run"])
        parse_utc(res["reserved_at"])
        task = tasks.get(res["task_id"])
        if task is None:
            _fail(f"reservation {res['run']} references unknown task {res['task_id']}")
        if task.get("status") != "claimed":
            _fail(f"reservation {res['run']} task {res['task_id']} is not claimed")
        claim = task.get("claim") or {}
        if claim.get("shift_id") != res["shift_id"]:
            _fail(
                f"reservation {res['run']} shift_id mismatch: "
                f"counter={res['shift_id']} queue={claim.get('shift_id')}"
            )


def validate_all(repo: Path) -> None:
    queue = load_json(repo / "lab/registry/queue.json")
    counter = load_json(repo / "lab/registry/run-counter.json")
    tasks = validate_queue(queue)
    validate_counter(counter, tasks)
    print("registry validation passed")


def validate_trigger(repo: Path, trigger_path: Path) -> None:
    trigger = load_json(trigger_path)
    queue = load_json(repo / "lab/registry/queue.json")
    counter = load_json(repo / "lab/registry/run-counter.json")
    tasks = validate_queue(queue)
    validate_counter(counter, tasks)
    for key in ("schema_version", "task_id", "run", "shift_id"):
        if key not in trigger:
            _fail(f"trigger missing required key: {key}")
    if trigger["schema_version"] != 1:
        _fail("trigger.schema_version must be 1")
    task = tasks.get(trigger["task_id"])
    if task is None:
        _fail(f"trigger references unknown task {trigger['task_id']}")
    if task.get("status") != "claimed":
        _fail(f"trigger task {trigger['task_id']} is not claimed")
    claim = task.get("claim") or {}
    if claim.get("shift_id") != trigger["shift_id"]:
        _fail(
            f"trigger shift_id mismatch: trigger={trigger['shift_id']} "
            f"queue={claim.get('shift_id')}"
        )
    matches = [
        r
        for r in counter.get("active_reservations", [])
        if r.get("run") == trigger["run"]
        and r.get("task_id") == trigger["task_id"]
        and r.get("shift_id") == trigger["shift_id"]
    ]
    if len(matches) != 1:
        _fail(
            f"expected exactly one active reservation matching trigger; observed {len(matches)}"
        )
    print(
        "trigger validation passed: "
        f"task={trigger['task_id']} run={trigger['run']} shift={trigger['shift_id']}"
    )


def git_show(repo: Path, commit: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def git_rev_list(repo: Path, path: str) -> list[str]:
    proc = subprocess.run(
        ["git", "rev-list", "HEAD", "--", path],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def latest_parseable_queue_from_history(repo: Path, task_id: str) -> dict[str, Any]:
    for commit in git_rev_list(repo, "lab/registry/queue.json"):
        text = git_show(repo, commit, "lab/registry/queue.json")
        if text is None:
            continue
        try:
            queue = json.loads(text)
            tasks = validate_queue(queue, semantic=False)
        except Exception as exc:
            print(f"skip malformed historical queue at {commit[:12]}: {exc}")
            continue
        if task_id in tasks:
            print(f"using parseable historical queue from {commit}")
            return queue
    _fail(f"could not find parseable historical queue containing task {task_id}")


def repair_queue_from_trigger(repo: Path, trigger_path: Path) -> bool:
    queue_path = repo / "lab/registry/queue.json"
    trigger = load_json(trigger_path)
    counter = load_json(repo / "lab/registry/run-counter.json")
    task_id = trigger.get("task_id")
    run = trigger.get("run")
    shift_id = trigger.get("shift_id")
    if not all(isinstance(x, str) and x for x in (task_id, run, shift_id)):
        _fail("trigger must contain non-empty task_id, run, and shift_id")

    try:
        queue = json.loads(queue_path.read_text())
        validate_queue(queue)
        print("queue registry parses and validates; no repair needed")
        return False
    except Exception as exc:
        print(f"queue registry needs repair: {exc}")

    reservations = counter.get("active_reservations", [])
    matches = [
        r
        for r in reservations
        if r.get("run") == run and r.get("task_id") == task_id and r.get("shift_id") == shift_id
    ]
    if len(matches) != 1:
        _fail(f"cannot repair queue: active reservation match count is {len(matches)}")
    reservation = matches[0]

    queue = latest_parseable_queue_from_history(repo, task_id)
    tasks = validate_queue(queue, semantic=False)
    task = tasks[task_id]
    claimed_at = reservation["reserved_at"]
    lease = (parse_utc(claimed_at) + timedelta(minutes=DEFAULT_LEASE_MINUTES)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    task["status"] = "claimed"
    task["claim"] = {
        "shift_id": shift_id,
        "claimed_at": claimed_at,
        "lease_expires_at": lease,
    }
    write_json(queue_path, queue)
    repaired_queue = load_json(queue_path)
    repaired_tasks = validate_queue(repaired_queue)
    validate_counter(counter, repaired_tasks)
    validate_trigger(repo, trigger_path)
    print("queue registry repaired and matching claim reapplied")
    return True


def assert_evidence(repo: Path, run: str, result_path: str | None, execution_path: str | None) -> None:
    if not RUN_RE.match(run):
        _fail(f"invalid run id: {run}")
    result = Path(result_path) if result_path else repo / "lab/results" / f"{run}-multi-candidate.json"
    execution = Path(execution_path) if execution_path else repo / "lab/executions" / f"{run}.json"
    if not result.exists():
        _fail(f"missing result artifact: {result}")
    if not execution.exists():
        _fail(f"missing execution status artifact: {execution}")
    result_payload = load_json(result)
    execution_payload = load_json(execution)
    if execution_payload.get("run") != run:
        _fail(f"execution.run mismatch: {execution_payload.get('run')} != {run}")
    if execution_payload.get("result_path") not in {str(result), result.as_posix()}:
        _fail(
            f"execution.result_path mismatch: {execution_payload.get('result_path')} != {result}"
        )
    if execution_payload.get("status") not in {"complete", "failed"}:
        _fail(f"execution status is not terminal: {execution_payload.get('status')}")
    if not isinstance(result_payload, dict) or not result_payload:
        _fail("result payload must be a non-empty JSON object")
    print(f"evidence artifacts validated for {run}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_validate = sub.add_parser("validate", help="validate queue and run-counter invariants")
    p_validate.add_argument("--repo", default=".")
    p_trigger = sub.add_parser("validate-trigger", help="validate trigger against queue/counter")
    p_trigger.add_argument("trigger")
    p_trigger.add_argument("--repo", default=".")
    p_repair = sub.add_parser("repair-queue-from-trigger", help="repair malformed queue and reapply trigger claim")
    p_repair.add_argument("trigger")
    p_repair.add_argument("--repo", default=".")
    p_evidence = sub.add_parser("assert-evidence", help="fail unless durable result/status evidence exists")
    p_evidence.add_argument("--run", required=True)
    p_evidence.add_argument("--result")
    p_evidence.add_argument("--execution")
    p_evidence.add_argument("--repo", default=".")
    args = parser.parse_args(argv)

    try:
        repo = Path(args.repo)
        if args.command == "validate":
            validate_all(repo)
        elif args.command == "validate-trigger":
            validate_trigger(repo, Path(args.trigger))
        elif args.command == "repair-queue-from-trigger":
            repaired = repair_queue_from_trigger(repo, Path(args.trigger))
            return 2 if repaired else 0
        elif args.command == "assert-evidence":
            assert_evidence(repo, args.run, args.result, args.execution)
        return 0
    except GuardError as exc:
        print(f"REGISTRY_GUARD_ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

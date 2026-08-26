import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("registry_guard", ROOT / "lab/tools/registry_guard.py")
registry_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(registry_guard)


def minimal_queue(status="claimed", claim=None):
    if claim is None and status == "claimed":
        claim = {
            "shift_id": "SHIFT-1",
            "claimed_at": "2026-08-26T00:00:00Z",
            "lease_expires_at": "2026-08-26T02:00:00Z",
        }
    return {
        "schema_version": 1,
        "statuses": ["ready", "claimed", "blocked", "done", "cancelled"],
        "tasks": [
            {
                "id": "T-ONE",
                "title": "One",
                "type": "research",
                "status": status,
                "priority": 1,
                "depends_on": [],
                "recommended_role": "tester",
                "success_test": "complete",
                "claim": claim,
            }
        ],
    }


def minimal_counter():
    return {
        "schema_version": 1,
        "next_run_number": 41,
        "last_completed_run": "ARC-R039",
        "active_reservations": [
            {
                "run": "ARC-R040",
                "task_id": "T-ONE",
                "shift_id": "SHIFT-1",
                "reserved_at": "2026-08-26T00:00:00Z",
            }
        ],
    }


def test_validate_queue_and_counter_happy_path():
    tasks = registry_guard.validate_queue(minimal_queue())
    registry_guard.validate_counter(minimal_counter(), tasks)


def test_nonclaimed_task_cannot_keep_claim():
    queue = minimal_queue(status="ready", claim={"shift_id": "SHIFT-1"})
    with pytest.raises(registry_guard.GuardError, match="non-claimed task"):
        registry_guard.validate_queue(queue)


def test_reservation_must_match_claim_shift():
    queue = minimal_queue()
    counter = minimal_counter()
    counter["active_reservations"][0]["shift_id"] = "OTHER"
    tasks = registry_guard.validate_queue(queue)
    with pytest.raises(registry_guard.GuardError, match="shift_id mismatch"):
        registry_guard.validate_counter(counter, tasks)


def test_duplicate_task_ids_fail():
    queue = minimal_queue()
    queue["tasks"].append(dict(queue["tasks"][0]))
    with pytest.raises(registry_guard.GuardError, match="duplicate task id"):
        registry_guard.validate_queue(queue)

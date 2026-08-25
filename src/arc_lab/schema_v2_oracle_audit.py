from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any, Iterable

from .lattice_region import execute_program
from .taskio import validate_grid

TASK_IDS = ("0607ce86", "06df4c85")
MAX_DEPTH = 4

OPS = tuple(
    {"op": "lattice_peer_reduce", "axis": axis, "reduce": reduce, "write": write}
    for axis in ("all", "row", "col")
    for reduce in ("majority", "majority_nonbackground", "first_nonbackground")
    for write in ("all", "background_only", "outliers_only")
)


def _sig(grids: Iterable[list[list[int]]]) -> tuple:
    return tuple(tuple(tuple(row) for row in grid) for grid in grids)


def _program(steps: list[dict[str, str]]) -> dict[str, Any]:
    return {"schema_version": 2, "steps": steps or [{"op": "identity"}]}


def audit_task(task: dict[str, Any], *, max_depth: int = MAX_DEPTH) -> dict[str, Any]:
    train = task["train"]
    inputs = [validate_grid(pair["input"]) for pair in train]
    targets = [validate_grid(pair["output"]) for pair in train]
    target_sig = _sig(targets)
    initial_sig = _sig(inputs)
    if initial_sig == target_sig:
        return {
            "expressible": True,
            "oracle_program": _program([]),
            "depth": 0,
            "programs_expanded": 0,
            "operator_applications": 0,
            "unique_states": 1,
            "validation_failures": 0,
        }

    queue = deque([(inputs, [])])
    seen = {initial_sig}
    programs_expanded = 0
    operator_applications = 0
    validation_failures = 0
    depth_counts = {0: 1}

    while queue:
        grids, steps = queue.popleft()
        if len(steps) >= max_depth:
            continue
        programs_expanded += 1
        for op in OPS:
            operator_applications += 1
            next_grids = []
            failed = False
            for grid in grids:
                try:
                    next_grids.append(execute_program({"schema_version": 2, "steps": [op]}, grid))
                except ValueError:
                    validation_failures += 1
                    failed = True
                    break
            if failed:
                continue
            next_steps = [*steps, op]
            sig = _sig(next_grids)
            if sig == target_sig:
                return {
                    "expressible": True,
                    "oracle_program": _program(next_steps),
                    "depth": len(next_steps),
                    "programs_expanded": programs_expanded,
                    "operator_applications": operator_applications,
                    "unique_states": len(seen) + (sig not in seen),
                    "validation_failures": validation_failures,
                    "depth_counts": depth_counts,
                }
            if sig in seen:
                continue
            seen.add(sig)
            depth_counts[len(next_steps)] = depth_counts.get(len(next_steps), 0) + 1
            queue.append((next_grids, next_steps))

    return {
        "expressible": False,
        "oracle_program": None,
        "depth": None,
        "programs_expanded": programs_expanded,
        "operator_applications": operator_applications,
        "unique_states": len(seen),
        "validation_failures": validation_failures,
        "depth_counts": depth_counts,
    }


def run(training_dir: str | Path, output: str | Path) -> dict[str, Any]:
    training_dir = Path(training_dir)
    records = {}
    for task_id in TASK_IDS:
        task = json.loads((training_dir / f"{task_id}.json").read_text())
        records[task_id] = audit_task(task)
    result = {
        "schema_version": 1,
        "run": "ARC-R033",
        "task_id": "T0018-SCHEMA-V2-EXPRESSIBILITY-ORACLE-AUDIT",
        "role": "program-synthesis-researcher",
        "public_evaluation_used": False,
        "target_model_calls": 0,
        "max_depth": MAX_DEPTH,
        "operator_count": len(OPS),
        "anti_overfit_constraints": [
            "no task IDs in DSL semantics",
            "no absolute task-specific coordinates",
            "no task-specific color constants",
            "no hand-entered target patterns",
        ],
        "records": records,
    }
    Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_dir")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.training_dir, args.output), sort_keys=True))


if __name__ == "__main__":
    main()

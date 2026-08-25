from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable

from .lattice_region import execute_program
from .schema_v2_oracle_audit import MAX_DEPTH, OPS
from .taskio import validate_grid

TASK_ID = "0607ce86"
RUN = "ARC-R035"
LAB_TASK_ID = "T0020-VARIABLE-SPAN-OVERLAP-ALIGNMENT-ABLATION"


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
            "first_step_valid_transitions": 0,
            "programs_expanded": 0,
            "operator_applications": 0,
            "unique_states": 1,
            "execution_failures": 0,
            "failure_types": {},
            "depth_counts": {0: 1},
        }

    queue = deque([(inputs, [])])
    seen = {initial_sig}
    programs_expanded = 0
    operator_applications = 0
    execution_failures = 0
    failure_types: Counter[str] = Counter()
    first_step_valid_transitions = 0
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
                except (ValueError, IndexError) as exc:
                    execution_failures += 1
                    failure_types[type(exc).__name__] += 1
                    failed = True
                    break
            if failed:
                continue
            if not steps:
                first_step_valid_transitions += 1
            next_steps = [*steps, op]
            sig = _sig(next_grids)
            if sig == target_sig:
                return {
                    "expressible": True,
                    "oracle_program": _program(next_steps),
                    "depth": len(next_steps),
                    "first_step_valid_transitions": first_step_valid_transitions,
                    "programs_expanded": programs_expanded,
                    "operator_applications": operator_applications,
                    "unique_states": len(seen) + (sig not in seen),
                    "execution_failures": execution_failures,
                    "failure_types": dict(sorted(failure_types.items())),
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
        "first_step_valid_transitions": first_step_valid_transitions,
        "programs_expanded": programs_expanded,
        "operator_applications": operator_applications,
        "unique_states": len(seen),
        "execution_failures": execution_failures,
        "failure_types": dict(sorted(failure_types.items())),
        "depth_counts": depth_counts,
    }


def classify(record: dict[str, Any]) -> str:
    if record["expressible"] and record["first_step_valid_transitions"] > 0:
        return "SUCCESS_EXACT_PROGRAM"
    if record["first_step_valid_transitions"] > 0:
        return "PARTIAL_ALIGNMENT_BLOCKER_REMOVED_SEMANTICS_INSUFFICIENT"
    return "FALSIFIED_NO_VALID_FIRST_STEP"


def run(training_dir: str | Path, output: str | Path) -> dict[str, Any]:
    training_dir = Path(training_dir)
    task = json.loads((training_dir / f"{TASK_ID}.json").read_text())
    record = audit_task(task)
    result = {
        "schema_version": 1,
        "run": RUN,
        "task_id": LAB_TASK_ID,
        "role": "program-synthesis-researcher",
        "public_evaluation_used": False,
        "target_model_calls": 0,
        "primary_change": "shared-overlap relative-coordinate peer alignment; preserve non-overlap cells",
        "frozen_operator_count": len(OPS),
        "max_depth": MAX_DEPTH,
        "benchmark_task_ids": [TASK_ID],
        "verdict": classify(record),
        "record": record,
        "adversarial_interpretation": "Valid transitions would only show that the equal-shape indexing failure was removed. Without an exact program they do not establish sufficiency of the existing peer-reduction semantics; overlap anchoring itself may also be the wrong generic alignment relation.",
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

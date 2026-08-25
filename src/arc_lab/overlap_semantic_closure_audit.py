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
RUN = "ARC-R036"
LAB_TASK_ID = "T0021-OVERLAP-SEMANTIC-CLOSURE-AUDIT"


def _sig(grids: Iterable[list[list[int]]]) -> tuple:
    return tuple(tuple(tuple(row) for row in grid) for grid in grids)


def _program(steps: list[dict[str, str]]) -> dict[str, Any]:
    return {"schema_version": 2, "steps": steps or [{"op": "identity"}]}


def _cell_error(grid: list[list[int]], target: list[list[int]]) -> int:
    if len(grid) != len(target) or any(len(a) != len(b) for a, b in zip(grid, target)):
        raise ValueError("cell-error distance requires shape-matched grids")
    return sum(a != b for row_a, row_b in zip(grid, target) for a, b in zip(row_a, row_b))


def _distance(grids: list[list[list[int]]], targets: list[list[list[int]]]) -> dict[str, Any]:
    per_pair = [_cell_error(g, t) for g, t in zip(grids, targets)]
    return {"total_cell_error": sum(per_pair), "per_training_pair": per_pair}


def _reason(exc: Exception) -> str:
    message = str(exc)
    if message in {
        "no uniform separator lines found",
        "lattice inference requires at least two regions",
        "lattice must contain multiple cells",
    }:
        return "separator_structure_lost"
    if message in {"region lattice shape mismatch", "region size mismatch"}:
        return "region_reassembly_invariant"
    if "shape" in message or "size" in message:
        return "shape_invariant"
    return "other_execution_invariant"


def audit_task(task: dict[str, Any], *, max_depth: int = MAX_DEPTH, top_k: int = 20) -> dict[str, Any]:
    train = task["train"]
    inputs = [validate_grid(pair["input"]) for pair in train]
    targets = [validate_grid(pair["output"]) for pair in train]
    target_sig = _sig(targets)
    initial_sig = _sig(inputs)

    queue = deque([(inputs, [])])
    seen = {initial_sig}
    state_records: list[dict[str, Any]] = [{"depth": 0, "program": _program([]), **_distance(inputs, targets)}]
    failures: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    message_counts: Counter[str] = Counter()
    operator_applications = 0
    programs_expanded = 0
    first_step_valid_transitions = 0

    while queue:
        grids, steps = queue.popleft()
        if len(steps) >= max_depth:
            continue
        programs_expanded += 1
        for op in OPS:
            operator_applications += 1
            next_grids = []
            failure = None
            for pair_index, grid in enumerate(grids):
                try:
                    next_grids.append(execute_program({"schema_version": 2, "steps": [op]}, grid))
                except (ValueError, IndexError) as exc:
                    reason = _reason(exc)
                    reason_counts[reason] += 1
                    message_counts[f"{type(exc).__name__}: {exc}"] += 1
                    failure = {
                        "depth_before": len(steps),
                        "training_pair_index": pair_index,
                        "reason": reason,
                        "exception_type": type(exc).__name__,
                        "message": str(exc),
                        "program_prefix": _program(steps),
                        "attempted_op": op,
                    }
                    failures.append(failure)
                    break
            if failure is not None:
                continue
            if not steps:
                first_step_valid_transitions += 1
            next_steps = [*steps, op]
            sig = _sig(next_grids)
            if sig in seen:
                continue
            seen.add(sig)
            record = {"depth": len(next_steps), "program": _program(next_steps), **_distance(next_grids, targets)}
            state_records.append(record)
            if sig == target_sig:
                record["exact"] = True
            queue.append((next_grids, next_steps))

    ranked = sorted(state_records, key=lambda r: (r["total_cell_error"], r["depth"], json.dumps(r["program"], sort_keys=True)))
    dominant_reason = None
    dominant_fraction = 0.0
    if failures:
        reason, count = reason_counts.most_common(1)[0]
        dominant_fraction = count / len(failures)
        if dominant_fraction >= 0.8:
            dominant_reason = reason

    return {
        "expressible": any(r.get("exact") for r in state_records),
        "first_step_valid_transitions": first_step_valid_transitions,
        "programs_expanded": programs_expanded,
        "operator_applications": operator_applications,
        "unique_states": len(seen),
        "execution_failures": len(failures),
        "failure_reason_counts": dict(sorted(reason_counts.items())),
        "failure_message_counts": dict(sorted(message_counts.items())),
        "dominant_failure_reason": dominant_reason,
        "dominant_failure_fraction": dominant_fraction,
        "failure_records": failures,
        "closest_reachable_states": ranked[:top_k],
        "initial_cell_error": state_records[0]["total_cell_error"],
        "best_cell_error": ranked[0]["total_cell_error"],
    }


def classify(record: dict[str, Any]) -> str:
    if record["expressible"]:
        return "UNEXPECTED_EXACT_PROGRAM"
    if record["dominant_failure_reason"] is not None:
        return "DOMINANT_FAILURE_MECHANISM_IDENTIFIED"
    return "AMBIGUOUS_SEMANTIC_CLOSURE"


def run(training_dir: str | Path, output: str | Path) -> dict[str, Any]:
    task = json.loads((Path(training_dir) / f"{TASK_ID}.json").read_text())
    record = audit_task(task)
    result = {
        "schema_version": 1,
        "run": RUN,
        "task_id": LAB_TASK_ID,
        "role": "failure-analyst",
        "public_evaluation_used": False,
        "target_model_calls": 0,
        "primary_change": "diagnostics only; ARC-R035 solver semantics frozen",
        "frozen_operator_count": len(OPS),
        "max_depth": MAX_DEPTH,
        "benchmark_task_ids": [TASK_ID],
        "verdict": classify(record),
        "record": record,
        "adversarial_interpretation": "A dominant execution invariant does not by itself prove that fixing it will make the task expressible. Near-miss ranking can also be misleading when cell-error distance does not reflect semantic proximity. Any follow-up must change exactly one mechanism and preserve ARC-R035 controls.",
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

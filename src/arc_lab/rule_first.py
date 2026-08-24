from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .comparator_integrity import coverage_delta
from .scoring import exact_grid_match
from .taskio import Grid, validate_grid

SCHEMA_VERSION = 1
MAX_STEPS = 8
SUPPORTED_OPS = {"identity", "rotate90", "rotate180", "rotate270", "flip_h", "flip_v", "recolor"}


def parse_program(value: str | Mapping[str, Any]) -> dict[str, Any]:
    """Parse and validate a compact generic rule program; malformed input fails closed."""
    try:
        obj = json.loads(value) if isinstance(value, str) else dict(value)
    except Exception as exc:
        raise ValueError("program is not valid JSON/object") from exc
    if set(obj) != {"schema_version", "steps"} or obj.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported program schema")
    steps = obj.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_STEPS:
        raise ValueError("steps must be a non-empty bounded list")
    clean: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict) or "op" not in step:
            raise ValueError("each step must be an object with op")
        op = step["op"]
        if op not in SUPPORTED_OPS:
            raise ValueError(f"unsupported op: {op!r}")
        if op == "recolor":
            if set(step) != {"op", "from", "to"}:
                raise ValueError("recolor accepts only op/from/to")
            src, dst = step["from"], step["to"]
            if not isinstance(src, int) or isinstance(src, bool) or not 0 <= src <= 9:
                raise ValueError("recolor from must be 0..9")
            if not isinstance(dst, int) or isinstance(dst, bool) or not 0 <= dst <= 9:
                raise ValueError("recolor to must be 0..9")
            clean.append({"op": op, "from": src, "to": dst})
        else:
            if set(step) != {"op"}:
                raise ValueError(f"{op} accepts no parameters")
            clean.append({"op": op})
    return {"schema_version": SCHEMA_VERSION, "steps": clean}


def _rotate90(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid[::-1])]


def execute_program(program: str | Mapping[str, Any], input_grid: Grid) -> Grid:
    p = parse_program(program)
    current = deepcopy(validate_grid(input_grid))
    for step in p["steps"]:
        op = step["op"]
        if op == "identity":
            pass
        elif op == "rotate90":
            current = _rotate90(current)
        elif op == "rotate180":
            current = _rotate90(_rotate90(current))
        elif op == "rotate270":
            current = _rotate90(_rotate90(_rotate90(current)))
        elif op == "flip_h":
            current = [list(reversed(row)) for row in current]
        elif op == "flip_v":
            current = list(reversed(current))
        elif op == "recolor":
            current = [[step["to"] if cell == step["from"] else cell for cell in row] for row in current]
        else:  # guarded by parse_program; defensive fail closed
            raise ValueError(f"unsupported op: {op}")
        validate_grid(current)
    return current


def score_program_candidates(programs: Sequence[str | Mapping[str, Any]], input_grid: Grid, expected: Grid) -> list[dict[str, Any]]:
    """Execute programs first; exact scorer sees only materialized validated grids."""
    validate_grid(expected)
    records: list[dict[str, Any]] = []
    for raw in programs:
        program = parse_program(raw)
        grid = execute_program(program, input_grid)
        records.append({"program": program, "test_output": grid, "candidate_correct": exact_grid_match(grid, expected)})
    return records


def derive_program_coverage(records_by_task: Mapping[str, Sequence[Sequence[Mapping[str, Any]]]]) -> dict[str, bool]:
    """A task is covered iff every test has at least one exactly correct executed candidate."""
    return {
        task_id: bool(tests) and all(any(c.get("candidate_correct") is True for c in candidates) for candidates in tests)
        for task_id, tests in records_by_task.items()
    }


def matched_coverage_delta(comparator: Mapping[str, bool], treatment: Mapping[str, bool]) -> dict[str, list[str]]:
    """Enforce matched task IDs through the existing comparator-integrity boundary."""
    return coverage_delta(comparator, treatment)

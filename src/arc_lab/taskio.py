from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

Grid = list[list[int]]
TASK_ID_RE = re.compile(r"^[0-9a-f]{8}$")
MAX_GRID_DIM = 30


def validate_grid(grid: Any) -> Grid:
    if not isinstance(grid, list) or not grid:
        raise ValueError("grid must be a non-empty list")
    if len(grid) > MAX_GRID_DIM:
        raise ValueError("grid height exceeds ARC maximum of 30")
    if not all(isinstance(row, list) and row for row in grid):
        raise ValueError("grid rows must be non-empty lists")
    width = len(grid[0])
    if width > MAX_GRID_DIM:
        raise ValueError("grid width exceeds ARC maximum of 30")
    if any(len(row) != width for row in grid):
        raise ValueError("grid must be rectangular")
    for row in grid:
        for cell in row:
            if not isinstance(cell, int) or isinstance(cell, bool) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integers 0..9")
    return grid


def _validate_pair(pair: Any, *, require_output: bool) -> None:
    if not isinstance(pair, dict):
        raise ValueError("pair must be an object")
    if "input" not in pair:
        raise ValueError("pair must contain input")
    validate_grid(pair["input"])
    if require_output and "output" not in pair:
        raise ValueError("pair must contain output")
    if "output" in pair:
        validate_grid(pair["output"])


def validate_task(task: Any, *, require_test_outputs: bool = False) -> dict[str, Any]:
    if not isinstance(task, dict) or "train" not in task or "test" not in task:
        raise ValueError("task must contain train and test")
    if not isinstance(task["train"], list) or not isinstance(task["test"], list):
        raise ValueError("task train/test must be lists")
    if not task["train"] or not task["test"]:
        raise ValueError("task train/test cannot be empty")
    for pair in task["train"]:
        _validate_pair(pair, require_output=True)
    for pair in task["test"]:
        _validate_pair(pair, require_output=require_test_outputs)
    return task


def load_task(path: str | Path, *, require_test_outputs: bool = False) -> dict[str, Any]:
    task = json.loads(Path(path).read_text())
    return validate_task(task, require_test_outputs=require_test_outputs)


def task_id_from_path(path: str | Path) -> str:
    task_id = Path(path).stem
    if not TASK_ID_RE.fullmatch(task_id):
        raise ValueError(f"invalid ARC task id: {task_id}")
    return task_id


def task_paths(directory: str | Path) -> list[Path]:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"task directory does not exist: {directory}")
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise ValueError(f"no JSON tasks found in {directory}")
    ids = [task_id_from_path(path) for path in paths]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task ids")
    return paths


def validate_task_directory(
    directory: str | Path, *, require_test_outputs: bool = True
) -> dict[str, int]:
    paths = task_paths(directory)
    train_pairs = 0
    test_pairs = 0
    for path in paths:
        task = load_task(path, require_test_outputs=require_test_outputs)
        train_pairs += len(task["train"])
        test_pairs += len(task["test"])
    return {"task_count": len(paths), "train_pairs": train_pairs, "test_pairs": test_pairs}

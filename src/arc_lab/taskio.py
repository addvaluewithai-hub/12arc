from __future__ import annotations

import json
from pathlib import Path
from typing import Any

Grid = list[list[int]]


def validate_grid(grid: Any) -> Grid:
    if not isinstance(grid, list) or not grid:
        raise ValueError("grid must be a non-empty list")
    if not all(isinstance(row, list) and row for row in grid):
        raise ValueError("grid rows must be non-empty lists")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("grid must be rectangular")
    for row in grid:
        for cell in row:
            if not isinstance(cell, int) or isinstance(cell, bool) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integers 0..9")
    return grid


def validate_task(task: Any) -> dict[str, Any]:
    if not isinstance(task, dict) or "train" not in task or "test" not in task:
        raise ValueError("task must contain train and test")
    if not task["train"] or not task["test"]:
        raise ValueError("task train/test cannot be empty")
    for pair in task["train"]:
        validate_grid(pair["input"])
        validate_grid(pair["output"])
    for pair in task["test"]:
        validate_grid(pair["input"])
        if "output" in pair:
            validate_grid(pair["output"])
    return task


def load_task(path: str | Path) -> dict[str, Any]:
    task = json.loads(Path(path).read_text())
    return validate_task(task)

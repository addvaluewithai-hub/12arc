import json
from pathlib import Path

import pytest

from arc_lab.taskio import validate_grid, validate_task, validate_task_directory


def test_grid_enforces_arc_bounds_and_values():
    assert validate_grid([[0, 9], [1, 2]]) == [[0, 9], [1, 2]]
    with pytest.raises(ValueError):
        validate_grid([])
    with pytest.raises(ValueError):
        validate_grid([[1], [1, 2]])
    with pytest.raises(ValueError):
        validate_grid([[10]])
    with pytest.raises(ValueError):
        validate_grid([[True]])
    with pytest.raises(ValueError):
        validate_grid([[0] * 31])
    with pytest.raises(ValueError):
        validate_grid([[0] for _ in range(31)])


def test_task_shape_and_hidden_test_support():
    task = {
        "train": [{"input": [[1]], "output": [[2]]}],
        "test": [{"input": [[3]]}],
    }
    validate_task(task)
    with pytest.raises(ValueError):
        validate_task(task, require_test_outputs=True)


def test_training_directory_validation(tmp_path: Path):
    task = {
        "train": [{"input": [[1]], "output": [[2]]}],
        "test": [{"input": [[3]], "output": [[4]]}],
    }
    (tmp_path / "deadbeef.json").write_text(json.dumps(task))
    assert validate_task_directory(tmp_path) == {
        "task_count": 1,
        "train_pairs": 1,
        "test_pairs": 1,
    }

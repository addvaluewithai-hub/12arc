from __future__ import annotations

from collections.abc import Mapping, Sequence

from .taskio import Grid, validate_grid


def exact_grid_match(prediction: Grid, truth: Grid) -> bool:
    validate_grid(prediction)
    validate_grid(truth)
    return prediction == truth


def pass_at_two(predictions: Sequence[Grid], truth: Grid) -> bool:
    if not 1 <= len(predictions) <= 2:
        raise ValueError("ARC-AGI-2 scoring expects one or two attempts")
    return any(exact_grid_match(pred, truth) for pred in predictions)


def output_accuracy(predictions_by_test: Sequence[Sequence[Grid]], truths: Sequence[Grid]) -> float:
    if len(predictions_by_test) != len(truths):
        raise ValueError("prediction/test count mismatch")
    if not truths:
        raise ValueError("task has no test outputs")
    solved = sum(pass_at_two(preds, truth) for preds, truth in zip(predictions_by_test, truths))
    return solved / len(truths)


def task_solved(predictions_by_test: Sequence[Sequence[Grid]], truths: Sequence[Grid]) -> bool:
    if len(predictions_by_test) != len(truths):
        raise ValueError("prediction/test count mismatch")
    if not truths:
        raise ValueError("task has no test outputs")
    return all(pass_at_two(preds, truth) for preds, truth in zip(predictions_by_test, truths))


def task_accuracy(
    predictions_by_task: Mapping[str, Sequence[Sequence[Grid]]],
    truths_by_task: Mapping[str, Sequence[Grid]],
) -> float:
    if set(predictions_by_task) != set(truths_by_task):
        raise ValueError("prediction/task ids do not match truth/task ids")
    if not truths_by_task:
        raise ValueError("dataset has no tasks")
    solved = sum(
        task_solved(predictions_by_task[task_id], truths)
        for task_id, truths in truths_by_task.items()
    )
    return solved / len(truths_by_task)

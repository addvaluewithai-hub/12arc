from __future__ import annotations

from collections.abc import Sequence

from .taskio import Grid, validate_grid


def exact_grid_match(prediction: Grid, truth: Grid) -> bool:
    validate_grid(prediction)
    validate_grid(truth)
    return prediction == truth


def pass_at_two(predictions: Sequence[Grid], truth: Grid) -> bool:
    if not 1 <= len(predictions) <= 2:
        raise ValueError("ARC-AGI-2 scoring expects one or two attempts")
    return any(exact_grid_match(pred, truth) for pred in predictions)


def score_task(predictions_by_test: Sequence[Sequence[Grid]], truths: Sequence[Grid]) -> float:
    if len(predictions_by_test) != len(truths):
        raise ValueError("prediction/test count mismatch")
    if not truths:
        raise ValueError("task has no test outputs")
    solved = sum(pass_at_two(preds, truth) for preds, truth in zip(predictions_by_test, truths))
    return solved / len(truths)

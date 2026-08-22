import pytest

from arc_lab.scoring import exact_grid_match, pass_at_two, score_task


def test_exact_and_pass_at_two():
    truth = [[1, 0], [0, 1]]
    wrong = [[0, 1], [1, 0]]
    assert exact_grid_match(truth, truth)
    assert not exact_grid_match(wrong, truth)
    assert pass_at_two([wrong, truth], truth)
    assert not pass_at_two([wrong], truth)


def test_task_score_multiple_test_inputs():
    truths = [[[1]], [[2]]]
    preds = [[[[1]]], [[[0]], [[2]]]]
    assert score_task(preds, truths) == 1.0


def test_rejects_more_than_two_attempts():
    with pytest.raises(ValueError):
        pass_at_two([[[1]], [[1]], [[1]]], [[1]])

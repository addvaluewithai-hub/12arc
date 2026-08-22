import pytest

from arc_lab.scoring import exact_grid_match, output_accuracy, pass_at_two, task_accuracy, task_solved


def test_exact_and_pass_at_two():
    truth = [[1, 0], [0, 1]]
    wrong = [[0, 1], [1, 0]]
    assert exact_grid_match(truth, truth)
    assert not exact_grid_match(wrong, truth)
    assert pass_at_two([wrong, truth], truth)
    assert not pass_at_two([wrong], truth)


def test_output_accuracy_is_not_task_success():
    truths = [[[1]], [[2]]]
    preds = [[[[1]]], [[[0]]]]
    assert output_accuracy(preds, truths) == 0.5
    assert task_solved(preds, truths) is False


def test_task_requires_all_test_inputs():
    truths = [[[1]], [[2]]]
    preds = [[[[0]], [[1]]], [[[9]], [[2]]]]
    assert task_solved(preds, truths) is True


def test_dataset_task_accuracy():
    truths = {"a": [[[1]]], "b": [[[2]], [[3]]]}
    preds = {"a": [[[[1]]]], "b": [[[[2]]], [[[0]]]]}
    assert task_accuracy(preds, truths) == 0.5


def test_rejects_more_than_two_attempts():
    with pytest.raises(ValueError):
        pass_at_two([[[1]], [[1]], [[1]]], [[1]])

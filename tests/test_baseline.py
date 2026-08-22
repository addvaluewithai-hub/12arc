from arc_lab.baseline import build_prompt, parse_grid


def test_parse_grid_accepts_strict_json_and_embedded_grid():
    assert parse_grid("[[1,0],[0,1]]") == [[1, 0], [0, 1]]
    assert parse_grid("answer: [[2]] done") == [[2]]


def test_parse_grid_rejects_invalid_arc_grid():
    assert parse_grid("[[10]]") is None
    assert parse_grid("not a grid") is None


def test_prompt_contains_training_and_test_but_not_test_output():
    task = {
        "train": [{"input": [[1]], "output": [[2]]}],
        "test": [{"input": [[3]], "output": [[9]]}],
    }
    prompt = build_prompt(task, task["test"][0]["input"])
    assert '"output":[[2]]' in prompt
    assert "TEST_INPUT=[[3]]" in prompt
    assert "[[9]]" not in prompt

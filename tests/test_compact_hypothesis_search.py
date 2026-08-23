from arc_lab.compact_hypothesis_search import (
    candidate_prompt,
    parse_hypotheses,
    parse_selector,
    protocol_manifest,
    selector_prompt,
)


def _task():
    return {
        "train": [
            {"input": [[1]], "output": [[2]]},
            {"input": [[3]], "output": [[4]]},
        ],
        "test": [{"input": [[5]], "output": [[6]]}],
    }


def test_candidate_parser_requires_exactly_three_compact_hypotheses():
    text = '{"hypotheses":[{"rule":"a","test_output":[[1]]},{"rule":"b","test_output":[[2]]},{"rule":"c","test_output":[[3]]}]}'
    parsed = parse_hypotheses(text)
    assert parsed is not None
    assert [x["rule"] for x in parsed] == ["a", "b", "c"]
    assert parse_hypotheses('{"hypotheses":[]}') is None


def test_selector_parser_accepts_only_three_indices():
    assert parse_selector('{"selected_index":2,"reason":"best"}') == 2
    assert parse_selector('{"selected_index":3}') is None
    assert parse_selector('not json') is None


def test_selector_prompt_is_training_only_and_excludes_test_input_and_candidate_outputs():
    task = _task()
    rules = ["rule-a", "rule-b", "rule-c"]
    prompt = selector_prompt(task, rules)
    assert "rule-a" in prompt and "rule-c" in prompt
    assert '[[5]]' not in prompt
    assert "test_output" not in prompt
    assert '[[6]]' not in prompt


def test_candidate_prompt_does_not_request_full_training_replay():
    prompt = candidate_prompt(_task(), [[5]])
    assert "Do not replay or serialize training outputs" in prompt
    assert "exactly three" in prompt


def test_protocol_output_budget_is_below_frozen_comparator_cap():
    manifest = protocol_manifest()
    assert manifest["max_total_output_tokens_per_test"] == 3584
    assert manifest["max_total_output_tokens_per_test"] < 4096
    assert manifest["public_evaluation_used"] is False


def test_protocol_manifest_can_scope_transient_failure_recovery_without_changing_protocol():
    full = protocol_manifest()
    scoped = protocol_manifest(["00dbd492", "05f2a901"])
    assert scoped["task_ids"] == ["00dbd492", "05f2a901"]
    assert scoped["solver_version"] == full["solver_version"]
    assert scoped["candidate_generation"] == full["candidate_generation"]
    assert scoped["selector_generation"] == full["selector_generation"]
    assert scoped["primary_variable"] == full["primary_variable"]
    assert scoped["manifest_sha256"] != full["manifest_sha256"]

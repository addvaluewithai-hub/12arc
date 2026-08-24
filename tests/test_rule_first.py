import pytest

from arc_lab.rule_first import (
    derive_program_coverage,
    execute_program,
    matched_coverage_delta,
    parse_program,
    score_program_candidates,
)


def test_valid_program_parses_and_executes_deterministically_without_mutating_input():
    program = {"schema_version": 1, "steps": [{"op": "rotate90"}, {"op": "recolor", "from": 1, "to": 2}]}
    grid = [[1, 0], [0, 1]]
    original = [row[:] for row in grid]
    first = execute_program(program, grid)
    second = execute_program(program, grid)
    assert first == second == [[0, 2], [2, 0]]
    assert grid == original


def test_malformed_and_unsupported_programs_fail_closed():
    with pytest.raises(ValueError):
        parse_program('{"schema_version":1,"steps":[{"op":"task_specific_magic"}]}')
    with pytest.raises(ValueError):
        parse_program({"schema_version": 1, "steps": [{"op": "recolor", "from": 10, "to": 1}]})
    with pytest.raises(ValueError):
        parse_program({"schema_version": 2, "steps": [{"op": "identity"}]})


def test_candidate_oracle_scores_only_executed_grids_exactly():
    inp = [[1, 0], [0, 1]]
    truth = [[0, 2], [2, 0]]
    records = score_program_candidates(
        [
            {"schema_version": 1, "steps": [{"op": "identity"}]},
            {"schema_version": 1, "steps": [{"op": "rotate90"}, {"op": "recolor", "from": 1, "to": 2}]},
        ],
        inp,
        truth,
    )
    assert [r["candidate_correct"] for r in records] == [False, True]
    assert records[1]["test_output"] == truth


def test_program_coverage_requires_every_test_to_have_exact_candidate():
    coverage = derive_program_coverage({
        "aaaaaaaa": [[{"candidate_correct": True}], [{"candidate_correct": True}]],
        "bbbbbbbb": [[{"candidate_correct": True}], [{"candidate_correct": False}]],
    })
    assert coverage == {"aaaaaaaa": True, "bbbbbbbb": False}


def test_matched_comparator_task_ids_are_mechanically_enforced():
    delta = matched_coverage_delta({"a": False, "b": True}, {"a": True, "b": True})
    assert delta == {"new_covered_task_ids": ["a"], "regressed_task_ids": []}
    with pytest.raises(ValueError, match="task sets differ"):
        matched_coverage_delta({"a": False}, {"a": True, "b": False})

import pytest

from arc_lab.comparator_integrity import (
    assert_annotations_match,
    coverage_delta,
    derive_task_candidate_coverage,
)


def _result():
    return {
        "records": [
            {"task_id": "0bb8deee", "tests": [{"candidate_stage": {"parsed": True}, "candidates": [{"candidate_correct": False}]}]},
            {"task_id": "0d3d703e", "tests": [{"candidate_stage": {"parsed": True}, "candidates": [{"candidate_correct": True}, {"candidate_correct": False}]}]},
            {"task_id": "parsefail", "tests": [{"candidate_stage": {"parsed": False}}]},
        ]
    }


def test_derives_coverage_from_candidate_correctness_not_annotations():
    coverage = derive_task_candidate_coverage(_result())
    assert coverage == {"0bb8deee": False, "0d3d703e": True, "parsefail": False}


def test_rejects_arc_r021_style_inversion():
    coverage = derive_task_candidate_coverage(_result())
    with pytest.raises(ValueError, match="0bb8deee, 0d3d703e"):
        assert_annotations_match(coverage, {"0bb8deee": True, "0d3d703e": False})


def test_accepts_mechanically_matching_annotations():
    coverage = derive_task_candidate_coverage(_result())
    assert_annotations_match(coverage, {"0bb8deee": False, "0d3d703e": True})


def test_delta_is_derived_from_matched_maps():
    assert coverage_delta(
        {"a": False, "b": True, "c": False},
        {"a": True, "b": False, "c": False},
    ) == {"new_covered_task_ids": ["a"], "regressed_task_ids": ["b"]}


def test_delta_rejects_different_task_sets():
    with pytest.raises(ValueError, match="task sets differ"):
        coverage_delta({"a": True}, {"b": True})

import json
import pytest
from arc_lab.architecture_reporting import build_candidate_coverage_report, persist_candidate_coverage_report


def result(coverage):
    return {"records": [{"task_id": task_id, "tests": [{"candidate_stage": {"parsed": True}, "candidates": [{"candidate_correct": covered}]}]} for task_id, covered in coverage.items()]}


def test_reporting_uses_durable_comparator_evidence(tmp_path):
    comparator = tmp_path / "comparator.json"
    comparator.write_text(json.dumps(result({"task_a": False, "task_b": True})))
    report = build_candidate_coverage_report(comparator_result_path=comparator, treatment_result=result({"task_a": True, "task_b": False}))
    assert report["comparator_candidate_coverage"] == {"task_a": False, "task_b": True}
    assert report["new_covered_task_ids"] == ["task_a"]
    assert report["regressed_task_ids"] == ["task_b"]


def test_manual_inversion_cannot_override_persisted_delta(tmp_path):
    comparator = tmp_path / "comparator.json"
    comparator.write_text(json.dumps(result({"task_a": False, "task_b": True})))
    output = tmp_path / "report.json"
    persist_candidate_coverage_report(comparator_result_path=comparator, treatment_result=result({"task_a": False, "task_b": True}), output_path=output)
    persisted = json.loads(output.read_text())
    assert persisted["new_covered_task_ids"] == []
    assert persisted["regressed_task_ids"] == []


def test_mismatched_task_sets_fail_before_write(tmp_path):
    comparator = tmp_path / "comparator.json"
    comparator.write_text(json.dumps(result({"task_a": False, "task_b": True})))
    output = tmp_path / "report.json"
    with pytest.raises(ValueError, match="task sets differ"):
        persist_candidate_coverage_report(comparator_result_path=comparator, treatment_result=result({"task_a": True}), output_path=output)
    assert not output.exists()

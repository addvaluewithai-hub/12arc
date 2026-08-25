from arc_lab.variable_span_overlap_audit import audit_task, classify


def _task(inp, out):
    return {"train": [{"input": inp, "output": out}]}


def test_overlap_alignment_restores_valid_first_steps_without_changing_operator_count():
    inp = [
        [1, 0, 9, 1, 0],
        [0, 2, 9, 0, 0],
        [9, 9, 9, 9, 9],
        [1, 0, 9, 1, 0],
        [0, 2, 9, 0, 0],
        [1, 7, 9, 8, 6],
    ]
    out = [row[:] for row in inp]
    out[0][1] = 2
    result = audit_task(_task(inp, out), max_depth=1)
    assert result["operator_applications"] == 27
    assert result["first_step_valid_transitions"] == 27
    assert result["execution_failures"] == 0


def test_classification_distinguishes_partial_from_falsified():
    assert classify({"expressible": False, "first_step_valid_transitions": 3}) == "PARTIAL_ALIGNMENT_BLOCKER_REMOVED_SEMANTICS_INSUFFICIENT"
    assert classify({"expressible": False, "first_step_valid_transitions": 0}) == "FALSIFIED_NO_VALID_FIRST_STEP"

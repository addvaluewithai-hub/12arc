from arc_lab.overlap_semantic_closure_audit import _reason, audit_task, classify


def _task(inp, out):
    return {"train": [{"input": inp, "output": out}]}


def test_reason_classifies_separator_loss_exactly():
    assert _reason(ValueError("no uniform separator lines found")) == "separator_structure_lost"
    assert _reason(ValueError("lattice inference requires at least two regions")) == "separator_structure_lost"


def test_audit_retains_program_paths_and_cell_error_ranking():
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
    record = audit_task(_task(inp, out), max_depth=1, top_k=3)
    assert record["operator_applications"] == 27
    assert record["first_step_valid_transitions"] == 27
    assert record["initial_cell_error"] == 1
    assert record["closest_reachable_states"]
    assert "program" in record["closest_reachable_states"][0]
    assert "per_training_pair" in record["closest_reachable_states"][0]


def test_classification_requires_dominant_mechanism_or_reports_ambiguity():
    assert classify({"expressible": False, "dominant_failure_reason": "separator_structure_lost"}) == "DOMINANT_FAILURE_MECHANISM_IDENTIFIED"
    assert classify({"expressible": False, "dominant_failure_reason": None}) == "AMBIGUOUS_SEMANTIC_CLOSURE"

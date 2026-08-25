from arc_lab.schema_v2_oracle_audit import audit_task


def _task(inp, out):
    return {"train": [{"input": inp, "output": out}]}


def test_identity_is_detected_at_depth_zero():
    grid = [[1, 1], [1, 1]]
    result = audit_task(_task(grid, grid))
    assert result["expressible"] is True
    assert result["depth"] == 0


def test_non_lattice_non_identity_is_not_expressible():
    inp = [[0, 1], [1, 0]]
    out = [[1, 0], [0, 1]]
    result = audit_task(_task(inp, out), max_depth=2)
    assert result["expressible"] is False
    assert result["operator_applications"] == 27
    assert result["validation_failures"] == 27


def test_regular_lattice_reduction_can_be_found():
    inp = [
        [1, 0, 9, 1, 1],
        [0, 0, 9, 0, 0],
        [9, 9, 9, 9, 9],
        [1, 1, 9, 0, 1],
        [0, 0, 9, 0, 0],
    ]
    out = [
        [1, 1, 9, 1, 1],
        [0, 0, 9, 0, 0],
        [9, 9, 9, 9, 9],
        [1, 1, 9, 1, 1],
        [0, 0, 9, 0, 0],
    ]
    result = audit_task(_task(inp, out), max_depth=1)
    assert result["expressible"] is True
    assert result["depth"] == 1

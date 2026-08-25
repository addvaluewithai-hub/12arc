import pytest

from arc_lab.lattice_region import (
    execute_program,
    extract_regions,
    infer_lattice,
    parse_program,
    reassemble_regions,
)


def lattice_grid():
    return [
        [1, 0, 9, 1, 0],
        [0, 2, 9, 0, 0],
        [9, 9, 9, 9, 9],
        [1, 0, 9, 1, 0],
        [0, 2, 9, 0, 0],
    ]


def test_lattice_inference_extract_and_reassemble_are_deterministic():
    grid = lattice_grid()
    lattice = infer_lattice(grid)
    assert lattice["separator_rows"] == [2]
    assert lattice["separator_cols"] == [2]
    regions = extract_regions(grid, lattice)
    assert len(regions) == 2 and len(regions[0]) == 2
    assert regions[0][0] == [[1, 0], [0, 2]]
    assert reassemble_regions(grid, lattice, regions) == grid


def test_background_only_peer_reduce_fills_from_inferred_peers_without_color_constants():
    program = {
        "schema_version": 2,
        "steps": [{"op": "lattice_peer_reduce", "axis": "all", "reduce": "majority_nonbackground", "write": "background_only"}],
    }
    out = execute_program(program, lattice_grid())
    assert out[1][4] == 2
    assert out[2] == [9, 9, 9, 9, 9]
    assert out[0][2] == 9


def test_outliers_only_repairs_region_peer_disagreement():
    grid = lattice_grid()
    grid[4][4] = 7
    program = {
        "schema_version": 2,
        "steps": [{"op": "lattice_peer_reduce", "axis": "all", "reduce": "majority", "write": "outliers_only"}],
    }
    out = execute_program(program, grid)
    # Relative cell (1,1) across the four lattice regions is [2, 0, 2, 7],
    # so deterministic majority is 2; the injected 7 is the outlier to repair.
    assert out[4][4] == 2


def test_validation_fails_closed_and_has_no_task_specific_coordinate_or_color_fields():
    with pytest.raises(ValueError):
        parse_program({"schema_version": 2, "steps": [{"op": "lattice_peer_reduce", "axis": "all", "reduce": "majority", "write": "all", "color": 3}]})
    with pytest.raises(ValueError):
        parse_program({"schema_version": 2, "steps": [{"op": "lattice_peer_reduce", "axis": "row", "reduce": "magic", "write": "all"}]})
    with pytest.raises(ValueError):
        execute_program({"schema_version": 2, "steps": [{"op": "lattice_peer_reduce", "axis": "all", "reduce": "majority", "write": "all"}]}, [[1, 2], [3, 4]])

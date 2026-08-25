from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .scoring import exact_grid_match
from .taskio import Grid, validate_grid

SCHEMA_VERSION = 2
MAX_STEPS = 4
SUPPORTED_OPS = {"identity", "lattice_peer_reduce"}
AXES = {"all", "row", "col"}
REDUCERS = {"majority", "majority_nonbackground", "first_nonbackground"}
WRITE_MODES = {"all", "background_only", "outliers_only"}


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def _uniform_rows(grid: Grid) -> list[int]:
    return [r for r, row in enumerate(grid) if len(set(row)) == 1]


def _uniform_cols(grid: Grid) -> list[int]:
    width = len(grid[0])
    return [c for c in range(width) if len({row[c] for row in grid}) == 1]


def _intervals(size: int, separators: Sequence[int]) -> list[tuple[int, int]]:
    sep = sorted(set(separators))
    cuts = [-1, *sep, size]
    spans = [(cuts[i] + 1, cuts[i + 1]) for i in range(len(cuts) - 1) if cuts[i] + 1 < cuts[i + 1]]
    if len(spans) < 2:
        raise ValueError("lattice inference requires at least two regions")
    return spans


def infer_lattice(grid: Grid) -> dict[str, Any]:
    """Infer a separator-defined lattice; region spans may have unequal sizes."""
    g = validate_grid(grid)
    rows = _uniform_rows(g)
    cols = _uniform_cols(g)
    if not rows and not cols:
        raise ValueError("no uniform separator lines found")
    row_spans = _intervals(len(g), rows) if rows else [(0, len(g))]
    col_spans = _intervals(len(g[0]), cols) if cols else [(0, len(g[0]))]
    if len(row_spans) * len(col_spans) < 2:
        raise ValueError("lattice must contain multiple cells")
    return {"row_spans": row_spans, "col_spans": col_spans, "separator_rows": rows, "separator_cols": cols}


def extract_regions(grid: Grid, lattice: Mapping[str, Any]) -> list[list[Grid]]:
    g = validate_grid(grid)
    rows = lattice["row_spans"]
    cols = lattice["col_spans"]
    return [[[row[c0:c1] for row in g[r0:r1]] for c0, c1 in cols] for r0, r1 in rows]


def reassemble_regions(original: Grid, lattice: Mapping[str, Any], regions: Sequence[Sequence[Grid]]) -> Grid:
    out = deepcopy(validate_grid(original))
    row_spans = lattice["row_spans"]
    col_spans = lattice["col_spans"]
    if len(regions) != len(row_spans) or any(len(rr) != len(col_spans) for rr in regions):
        raise ValueError("region lattice shape mismatch")
    for ri, (r0, r1) in enumerate(row_spans):
        for ci, (c0, c1) in enumerate(col_spans):
            region = validate_grid(regions[ri][ci])
            if len(region) != r1 - r0 or len(region[0]) != c1 - c0:
                raise ValueError("region size mismatch")
            for dr, row in enumerate(region):
                out[r0 + dr][c0:c1] = row
    return validate_grid(out)


def _reduce(values: Sequence[int], reducer: str, background: int) -> int:
    pool = list(values)
    if reducer in {"majority_nonbackground", "first_nonbackground"}:
        nonbg = [v for v in pool if v != background]
        if nonbg:
            pool = nonbg
    if reducer == "first_nonbackground":
        return pool[0]
    counts = Counter(pool)
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def _peer_indices(ri: int, ci: int, nr: int, nc: int, axis: str) -> list[tuple[int, int]]:
    if axis == "all":
        return [(r, c) for r in range(nr) for c in range(nc)]
    if axis == "row":
        return [(ri, c) for c in range(nc)]
    return [(r, ci) for r in range(nr)]


def _shared_overlap(regions: Sequence[Sequence[Grid]], peers: Sequence[tuple[int, int]]) -> tuple[int, int]:
    """Return the top-left relative-coordinate domain shared by every peer."""
    if not peers:
        raise ValueError("peer set must be non-empty")
    heights = [len(regions[pr][pc]) for pr, pc in peers]
    widths = [len(regions[pr][pc][0]) for pr, pc in peers]
    return min(heights), min(widths)


def lattice_peer_reduce(grid: Grid, *, axis: str, reducer: str, write: str) -> Grid:
    lattice = infer_lattice(grid)
    regions = extract_regions(grid, lattice)
    nr, nc = len(regions), len(regions[0])
    bg = _background(grid)
    updated = deepcopy(regions)
    for ri in range(nr):
        for ci in range(nc):
            peers = _peer_indices(ri, ci, nr, nc, axis)
            overlap_h, overlap_w = _shared_overlap(regions, peers)
            # T0020 treatment: only relative coordinates shared by every selected
            # peer participate in reduction. Cells outside that top-left overlap
            # remain exactly as they were in the target region.
            for r in range(overlap_h):
                for c in range(overlap_w):
                    vals = [regions[pr][pc][r][c] for pr, pc in peers]
                    target = _reduce(vals, reducer, bg)
                    current = regions[ri][ci][r][c]
                    should_write = (
                        write == "all"
                        or (write == "background_only" and current == bg and target != bg)
                        or (write == "outliers_only" and current != target)
                    )
                    if should_write:
                        updated[ri][ci][r][c] = target
    return reassemble_regions(grid, lattice, updated)


def parse_program(value: str | Mapping[str, Any]) -> dict[str, Any]:
    try:
        obj = json.loads(value) if isinstance(value, str) else dict(value)
    except Exception as exc:
        raise ValueError("program is not valid JSON/object") from exc
    if set(obj) != {"schema_version", "steps"} or obj.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported lattice program schema")
    steps = obj.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_STEPS:
        raise ValueError("steps must be a non-empty bounded list")
    clean: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict) or step.get("op") not in SUPPORTED_OPS:
            raise ValueError("unsupported lattice op")
        if step["op"] == "identity":
            if set(step) != {"op"}:
                raise ValueError("identity accepts no parameters")
            clean.append({"op": "identity"})
            continue
        if set(step) != {"op", "axis", "reduce", "write"}:
            raise ValueError("lattice_peer_reduce requires op/axis/reduce/write")
        if step["axis"] not in AXES or step["reduce"] not in REDUCERS or step["write"] not in WRITE_MODES:
            raise ValueError("invalid generic lattice parameter")
        clean.append(dict(step))
    return {"schema_version": SCHEMA_VERSION, "steps": clean}


def execute_program(program: str | Mapping[str, Any], input_grid: Grid) -> Grid:
    p = parse_program(program)
    current = deepcopy(validate_grid(input_grid))
    for step in p["steps"]:
        if step["op"] == "identity":
            continue
        current = lattice_peer_reduce(current, axis=step["axis"], reducer=step["reduce"], write=step["write"])
        validate_grid(current)
    return current


def score_program_candidates(programs: Sequence[str | Mapping[str, Any]], input_grid: Grid, expected: Grid) -> list[dict[str, Any]]:
    validate_grid(expected)
    records = []
    for raw in programs:
        program = parse_program(raw)
        grid = execute_program(program, input_grid)
        records.append({"program": program, "test_output": grid, "candidate_correct": exact_grid_match(grid, expected)})
    return records

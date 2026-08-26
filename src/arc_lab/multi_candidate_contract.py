from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from .multi_candidate import canonical_program


SCHEMA_V1_EXAMPLE: dict[str, Any] = {
    "schema_version": 1,
    "steps": [{"op": "rotate90"}],
}

SCHEMA_V2_EXAMPLE: dict[str, Any] = {
    "schema_version": 2,
    "steps": [
        {
            "op": "lattice_peer_reduce",
            "axis": "row",
            "reduce": "majority_nonbackground",
            "write": "background_only",
        }
    ],
}


def prompt_contract_fragment() -> str:
    """Return the exact executable IR contract used by generation and repair prompts."""
    return """EXECUTABLE CANDIDATE CONTRACT (mandatory):
Each candidate MUST be a JSON object with exactly two top-level keys: schema_version and steps.
`schema_version` MUST be the JSON integer 1 or 2, never a quoted string.

Schema 1:
- object: {\"schema_version\":1,\"steps\":[...]}
- 1 to 8 steps.
- allowed parameter-free steps: identity, rotate90, rotate180, rotate270, flip_h, flip_v.
- parameter-free step shape: {\"op\":\"rotate90\"} (replace op with another allowed name).
- recolor step shape exactly: {\"op\":\"recolor\",\"from\":0,\"to\":1}; from/to are integer colors 0..9.

Schema 2:
- object: {\"schema_version\":2,\"steps\":[...]}
- 1 to 4 steps.
- identity step shape exactly: {\"op\":\"identity\"}.
- lattice step shape exactly: {\"op\":\"lattice_peer_reduce\",\"axis\":\"row\",\"reduce\":\"majority_nonbackground\",\"write\":\"background_only\"}.
- axis is one of: all, row, col.
- reduce is one of: majority, majority_nonbackground, first_nonbackground.
- write is one of: all, background_only, outliers_only.

Valid schema-1 example:
""" + json.dumps(SCHEMA_V1_EXAMPLE, separators=(",", ":")) + """
Valid schema-2 example:
""" + json.dumps(SCHEMA_V2_EXAMPLE, separators=(",", ":")) + """

FORBIDDEN candidate forms:
- no `instructions`, `strategy`, `program`, `confidence`, or other extra top-level keys;
- no natural-language or pseudocode strings in place of steps;
- no quoted schema_version such as \"1\" or \"2\";
- no unsupported op names or extra step parameters.
Return the requested JSON container only; do not wrap it in markdown fences or prose."""


def validate_candidate_contract(records: Sequence[Mapping[str, Any] | str]) -> dict[str, Any]:
    """Mechanically validate model-facing candidate objects with the frozen parser."""
    valid: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, raw in enumerate(records):
        try:
            valid.append(canonical_program(raw))
        except Exception as exc:
            failures.append({
                "index": index,
                "failure": f"{type(exc).__name__}: {exc}",
            })
    return {
        "submitted_candidates": len(records),
        "contract_valid_candidates": len(valid),
        "contract_invalid_candidates": len(failures),
        "failures": failures,
        "canonical_candidates": valid,
    }

import pytest

from arc_lab.multi_candidate import verify_candidate_batch
from arc_lab.multi_candidate_contract import (
    prompt_contract_fragment,
    validate_candidate_contract,
)


POSITIVE_CANDIDATES = [
    {"schema_version": 1, "steps": [{"op": "identity"}]},
    {"schema_version": 1, "steps": [{"op": "rotate90"}]},
    {"schema_version": 1, "steps": [{"op": "rotate180"}]},
    {"schema_version": 1, "steps": [{"op": "rotate270"}]},
    {"schema_version": 1, "steps": [{"op": "flip_h"}]},
    {"schema_version": 1, "steps": [{"op": "flip_v"}]},
    {"schema_version": 1, "steps": [{"op": "recolor", "from": 1, "to": 2}]},
    {"schema_version": 1, "steps": [{"op": "recolor", "from": 2, "to": 1}]},
    {"schema_version": 2, "steps": [{"op": "identity"}]},
    {
        "schema_version": 2,
        "steps": [
            {
                "op": "lattice_peer_reduce",
                "axis": "row",
                "reduce": "majority_nonbackground",
                "write": "background_only",
            }
        ],
    },
]


TRAINING_PAIRS = [
    {
        "input": [
            [1, 0, 9, 1, 0],
            [0, 0, 9, 0, 0],
            [2, 0, 9, 2, 0],
        ],
        "output": [
            [1, 0, 9, 1, 0],
            [0, 0, 9, 0, 0],
            [2, 0, 9, 2, 0],
        ],
    }
]


def test_contract_fragment_exposes_exact_machine_checkable_shapes():
    text = prompt_contract_fragment()
    assert '"schema_version":1' in text
    assert '"schema_version":2' in text
    assert '"steps"' in text
    assert "lattice_peer_reduce" in text
    assert "quoted schema_version" in text
    assert "no `instructions`" in text
    assert "no natural-language or pseudocode strings" in text


def test_offline_gate_has_at_least_eight_parseable_nonduplicate_scored_fixtures():
    contract = validate_candidate_contract(POSITIVE_CANDIDATES)
    assert contract["submitted_candidates"] == 10
    assert contract["contract_valid_candidates"] == 10
    assert contract["contract_invalid_candidates"] == 0

    scored = verify_candidate_batch(POSITIVE_CANDIDATES, TRAINING_PAIRS)
    assert scored["parseable_candidates"] == 10
    assert scored["unique_candidates"] == 10
    assert scored["duplicate_candidates"] == 0
    assert len(scored["ranked_candidates"]) == 10
    assert all("total_cell_error" in record for record in scored["ranked_candidates"])


@pytest.mark.parametrize(
    "malformed, expected_fragment",
    [
        (
            {
                "schema_version": 1,
                "instructions": "Identify a lattice and fill a natural-language bounding box.",
            },
            "unsupported program schema",
        ),
        (
            {
                "schema_version": "2",
                "strategy": "general repair",
                "program": "for each cell, connect same-colored blocks",
            },
            "unsupported candidate schema_version: '2'",
        ),
    ],
)
def test_arc_r038_malformed_candidate_forms_fail_closed(malformed, expected_fragment):
    result = validate_candidate_contract([malformed])
    assert result["contract_valid_candidates"] == 0
    assert result["contract_invalid_candidates"] == 1
    assert expected_fragment in result["failures"][0]["failure"]


def test_extra_top_level_prose_keys_fail_closed_even_with_valid_steps():
    malformed = {
        "schema_version": 1,
        "steps": [{"op": "identity"}],
        "instructions": "ignore this prose",
    }
    result = validate_candidate_contract([malformed])
    assert result["contract_valid_candidates"] == 0
    assert "unsupported program schema" in result["failures"][0]["failure"]

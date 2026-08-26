import pytest

from arc_lab.multi_candidate_experiment import (
    JsonContractError,
    _candidate_acceptor,
    _dict_key_acceptor,
    _json_slice,
)


def test_json_slice_extracts_only_contract_valid_candidate_array():
    text = (
        "analysis with a distracting raw list [1, 2, 3] before the actual answer\n"
        '[{"schema_version":1,"steps":[{"op":"identity"}]}]'
    )

    value = _json_slice(text, "[", "]", accept=_candidate_acceptor())

    assert value == [{"schema_version": 1, "steps": [{"op": "identity"}]}]


def test_json_slice_rejects_prose_without_executable_candidate_json():
    text = "I think the transformation is lattice propagation but here is no JSON."

    with pytest.raises(JsonContractError):
        _json_slice(text, "[", "]", accept=_candidate_acceptor())


def test_json_slice_extracts_required_dict_key():
    text = "notes first {\"wrong\": []} then {\"critiques\": []}"

    value = _json_slice(text, "{", "}", accept=_dict_key_acceptor("critiques"))

    assert value == {"critiques": []}

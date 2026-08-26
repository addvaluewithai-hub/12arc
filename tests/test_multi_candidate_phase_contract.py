import json
from pathlib import Path

import pytest

from arc_lab.multi_candidate import verify_candidate_batch
from arc_lab.multi_candidate_experiment import JsonContractError, _candidate_acceptor, _json_slice
from arc_lab.multi_candidate_phase_contract import (
    challenge_contract_instruction,
    critique_contract_instruction,
    strict_phase_acceptor,
    validate_challenge_manifest,
    validate_critique_manifest,
)


R040_RESULT = Path("lab/results/ARC-R040-multi-candidate.json")
TINY_TRAINING = [
    {
        "input": [[0, 1], [1, 0]],
        "output": [[0, 1], [1, 0]],
    }
]


def _r040_manifest():
    return json.loads(R040_RESULT.read_text())


def _phase_records(*names: str):
    wanted = set(names)
    return [record for record in _r040_manifest()["raw_phase_manifest"] if record["phase"] in wanted]


def _r040_generated():
    records = _phase_records("generate", "generate_json_retry")
    assert records, "ARC-R040 must persist generation/recovery evidence"
    errors = []
    for record in records:
        try:
            return _json_slice(
                record["response_text"],
                "[",
                "]",
                accept=_candidate_acceptor(expected_count=16),
            )
        except JsonContractError as exc:
            errors.append(str(exc))
    raise AssertionError(f"ARC-R040 has no contract-valid 16-candidate generation record: {errors}")


def test_arc_r040_critic_failure_replays_and_fails_closed():
    records = _phase_records("critique", "critique_json_retry")
    assert records, "ARC-R040 must persist critic and/or critic-recovery evidence"
    for record in records:
        with pytest.raises(JsonContractError):
            _json_slice(
                record["response_text"],
                "{",
                "}",
                accept=strict_phase_acceptor("critiques"),
            )


def test_strict_critique_and_challenge_contracts_reject_loose_shapes():
    candidate_id = "a" * 64
    with pytest.raises(ValueError):
        validate_critique_manifest({"critiques": [{"candidate_id": candidate_id}]})
    with pytest.raises(ValueError):
        validate_challenge_manifest(
            {
                "challenges": [
                    {
                        "candidate_id": candidate_id,
                        "critique_valid": "true",
                        "reason": "unsupported assumption",
                        "smallest_general_repair": "none",
                    }
                ]
            }
        )
    assert "exactly" in critique_contract_instruction()
    assert "JSON boolean" in challenge_contract_instruction()


def test_r040_generation_batch_traverses_mocked_hardened_phases_to_python_selection():
    generated = _r040_generated()
    first = verify_candidate_batch(generated, TINY_TRAINING)
    assert first["parseable_candidates"] == 16
    assert first["unique_candidates"] == 14
    candidate_ids = [row["candidate_id"] for row in first["ranked_candidates"]]

    critiques = {
        "critiques": [
            {
                "candidate_id": candidate_id,
                "likely_failure": "candidate is not exact on the deterministic training check",
                "violated_training_pair": 0,
                "forbidden_constant_risk": "no unsupported constant claim accepted",
                "separator_or_unchanged_region_risk": "preservation must be checked by Python",
                "repair_suggestion": "prefer the smallest executable general repair",
            }
            for candidate_id in candidate_ids
        ]
    }
    strict_critiques = validate_critique_manifest(
        critiques,
        candidate_ids=candidate_ids,
        training_pair_count=1,
    )

    challenges = {
        "challenges": [
            {
                "candidate_id": row["candidate_id"],
                "critique_valid": True,
                "reason": "the critique is grounded only in deterministic metrics",
                "smallest_general_repair": "retain executable IR and change one operation at most",
            }
            for row in strict_critiques["critiques"]
        ]
    }
    strict_challenges = validate_challenge_manifest(challenges, candidate_ids=candidate_ids)
    assert len(strict_challenges["challenges"]) == 14

    repaired = [{"schema_version": 1, "steps": [{"op": "identity"}]}]
    final = verify_candidate_batch([*generated, *repaired], TINY_TRAINING)
    assert final["best_candidate_id"] is not None
    assert final["parseable_candidates"] == 17
    assert final["ranked_candidates"][0]["exact_training_consistent"] is True

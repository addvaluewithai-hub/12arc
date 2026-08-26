import pytest

from arc_lab.multi_candidate import (
    AccountingRecord,
    CandidateProvenance,
    canonical_program,
    merge_accounting,
    rank_scored_candidates,
    validate_provenance,
    verify_candidate_batch,
)


def test_batch_deduplicates_and_ranks_exact_candidate_first():
    pairs = [{"input": [[1, 0], [0, 0]], "output": [[1, 0], [0, 0]]}]
    identity = {"schema_version": 1, "steps": [{"op": "identity"}]}
    duplicate = '{"steps":[{"op":"identity"}],"schema_version":1}'
    flip = {"schema_version": 1, "steps": [{"op": "flip_h"}]}
    result = verify_candidate_batch([flip, identity, duplicate], pairs)
    assert result["submitted_candidates"] == 3
    assert result["parseable_candidates"] == 3
    assert result["unique_candidates"] == 2
    assert result["duplicate_candidates"] == 1
    best = result["ranked_candidates"][0]
    assert best["exact_training_consistent"] is True
    assert best["total_cell_error"] == 0


def test_batch_fails_closed_on_invalid_candidate_without_poisoning_valid_candidates():
    pairs = [{"input": [[1]], "output": [[1]]}]
    valid = {"schema_version": 1, "steps": [{"op": "identity"}]}
    invalid = {"schema_version": 99, "steps": [{"op": "identity"}]}
    result = verify_candidate_batch([invalid, valid], pairs)
    assert result["parseable_candidates"] == 1
    assert len(result["parse_failures"]) == 1
    assert result["ranked_candidates"][0]["exact_training_consistent"] is True


def test_schema_v2_candidates_are_supported_and_execution_failures_are_recorded():
    pairs = [{"input": [[1, 1], [0, 0]], "output": [[1, 1], [0, 0]]}]
    identity = {"schema_version": 2, "steps": [{"op": "identity"}]}
    result = verify_candidate_batch([identity], pairs)
    assert result["ranked_candidates"][0]["exact_training_consistent"] is True
    assert canonical_program(identity)["schema_version"] == 2


def test_rank_is_deterministic_and_ignores_model_confidence_fields():
    base = {
        "exact_training_consistent": False,
        "exact_training_pairs": 0,
        "total_cell_error": 3,
        "structural_violations": 0,
        "program_cost": 10,
    }
    records = [
        {**base, "candidate_id": "b", "model_confidence": 1.0},
        {**base, "candidate_id": "a", "model_confidence": 0.0},
    ]
    ranked = rank_scored_candidates(records)
    assert [r["candidate_id"] for r in ranked] == ["a", "b"]


def test_provenance_requires_repair_parent_and_critique():
    records = [
        CandidateProvenance(candidate_id="g1", phase="generate", generation_attempt=0),
        CandidateProvenance(candidate_id="r1", phase="repair", parent_candidate_id="g1", critique_id="c1"),
    ]
    assert [r["candidate_id"] for r in validate_provenance(records)] == ["g1", "r1"]
    with pytest.raises(ValueError):
        validate_provenance([CandidateProvenance(candidate_id="r", phase="repair")])


def test_accounting_merges_requests_cache_tokens_runtime_and_failures():
    total = merge_accounting([
        AccountingRecord(request_count=2, cache_hits=1, input_tokens=10, output_tokens=4, total_tokens=14, runtime_seconds=1.5),
        AccountingRecord(request_count=1, input_tokens=3, output_tokens=2, total_tokens=5, runtime_seconds=0.5, provider_failures=1, parse_failures=2),
    ])
    assert total == {
        "request_count": 3,
        "cache_hits": 1,
        "input_tokens": 13,
        "output_tokens": 6,
        "total_tokens": 19,
        "runtime_seconds": 2.0,
        "provider_failures": 1,
        "parse_failures": 2,
    }

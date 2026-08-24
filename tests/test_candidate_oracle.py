from arc_lab.candidate_oracle import _candidate_record


def test_candidate_record_exact_correctness_and_hash():
    expected = [[1, 2], [3, 4]]
    correct = _candidate_record({"rule": "identity", "test_output": expected}, expected)
    wrong = _candidate_record({"rule": "wrong", "test_output": [[1, 2], [4, 3]]}, expected)
    assert correct["candidate_correct"] is True
    assert wrong["candidate_correct"] is False
    assert len(correct["rule_sha256"]) == 64
    assert correct["test_output"] == expected

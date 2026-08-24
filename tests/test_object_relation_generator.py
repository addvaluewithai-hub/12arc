from arc_lab.object_relation_generator import BASELINE_COVERED, SOLVER_VERSION, candidate_prompt


def test_object_relation_prompt_and_frozen_baseline():
    task={"train":[{"input":[[1]],"output":[[2]]}]}
    p=candidate_prompt(task,[[1]])
    assert "OBJECT/RELATION" in p
    assert "exactly three DISTINCT" in p
    assert "intermediate scene graph" in p
    assert SOLVER_VERSION == "object-relation-candidates-v1"
    assert BASELINE_COVERED == {"0bb8deee"}

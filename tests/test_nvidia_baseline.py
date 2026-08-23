from arc_lab.nvidia_baseline import CHUNK_COUNT, GENERATION, MODEL, chunk_task_ids


def test_chunking_covers_each_task_exactly_once():
    ids = [f"task-{i:03d}" for i in range(37)]
    chunks = [chunk_task_ids(ids, i, CHUNK_COUNT) for i in range(CHUNK_COUNT)]
    flattened = [task_id for chunk in chunks for task_id in chunk]
    assert sorted(flattened) == sorted(ids)
    assert len(flattened) == len(set(flattened))


def test_baseline_configuration_is_frozen_to_tournament_winner():
    assert MODEL == "deepseek-ai/deepseek-v4-flash-0731"
    assert GENERATION.temperature == 0.0
    assert GENERATION.top_p == 1.0
    assert GENERATION.top_k is None
    assert GENERATION.max_output_tokens == 4096

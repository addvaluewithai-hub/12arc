from arc_lab.splits import partition, split_name


def test_split_is_deterministic():
    ids = ["a", "b", "c", "d", "e"]
    assert partition(ids) == partition(list(reversed(ids)))


def test_every_id_has_one_split():
    ids = [f"task-{i}" for i in range(100)]
    parts = partition(ids)
    flat = sum(parts.values(), [])
    assert sorted(flat) == sorted(ids)
    assert len(flat) == len(set(flat))


def test_split_names_are_closed_set():
    assert split_name("anything") in {"dev_train", "dev_validation", "dev_holdout"}

from arc_lab.splits import build_split_manifest, manifest_digest, partition, split_name


def test_split_is_deterministic():
    ids = ["deadbeef", "cafebabe", "01234567", "89abcdef"]
    assert partition(ids) == partition(list(reversed(ids)))


def test_every_id_has_one_split():
    ids = [f"{i:08x}" for i in range(100)]
    parts = partition(ids)
    flat = sum(parts.values(), [])
    assert sorted(flat) == sorted(ids)
    assert len(flat) == len(set(flat))


def test_split_names_are_closed_set():
    assert split_name("deadbeef") in {"dev_train", "dev_validation", "dev_holdout"}


def test_manifest_self_hash_is_stable():
    manifest = build_split_manifest(["deadbeef", "cafebabe"])
    assert manifest["manifest_sha256"] == manifest_digest(manifest)
    assert manifest == build_split_manifest(["cafebabe", "deadbeef"])

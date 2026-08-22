import json
from pathlib import Path

from arc_lab.benchmark import (
    file_sha256,
    read_task_ids,
    validate_development_dataset,
    verify_split_manifest,
    write_split_manifest,
)


def test_manifest_reproduces_from_same_id_list(tmp_path: Path):
    ids = tmp_path / "training.txt"
    ids.write_text("deadbeef\ncafebabe\n01234567\n")
    manifest = tmp_path / "split.json"
    first = write_split_manifest(ids, manifest, source_commit="abc123")
    verify_split_manifest(ids, manifest)
    second = json.loads(manifest.read_text())
    assert first == second


def test_default_development_path_does_not_need_evaluation(tmp_path: Path):
    training = tmp_path / "training"
    training.mkdir()
    task = {
        "train": [{"input": [[1]], "output": [[1]]}],
        "test": [{"input": [[2]], "output": [[2]]}],
    }
    (training / "deadbeef.json").write_text(json.dumps(task))

    summary = validate_development_dataset(training, expected_task_ids=["deadbeef"])
    assert summary["task_count"] == 1
    assert not (tmp_path / "evaluation").exists()


def test_ids_must_be_unique_and_arc_shaped(tmp_path: Path):
    ids = tmp_path / "ids.txt"
    ids.write_text("deadbeef\ndeadbeef\n")
    try:
        read_task_ids(ids)
        assert False, "expected duplicate rejection"
    except ValueError:
        pass


def test_committed_official_training_spec_is_reproducible(tmp_path: Path):
    ids_file = Path("lab/benchmarks/arc-agi-2-training-ids.txt")
    source_file = Path("lab/benchmarks/arc-agi-2-source.json")
    source = json.loads(source_file.read_text())

    ids = read_task_ids(ids_file)
    assert len(ids) == source["public_training"]["task_count"] == 1000
    assert file_sha256(ids_file) == source["public_training"]["local_id_list_sha256"]

    generated = tmp_path / "split.json"
    manifest = write_split_manifest(
        ids_file,
        generated,
        source_commit=source["pinned_commit"],
    )
    verify_split_manifest(ids_file, generated)
    assert manifest["counts"] == source["split_manifest"]["counts"]
    assert manifest["manifest_sha256"] == source["split_manifest"]["reference_sha256"]

from pathlib import Path

from arc_lab.target_model import (
    CachedTargetClient,
    GenerationConfig,
    TargetRequest,
    TargetResponse,
)


class FakeProvider:
    def __init__(self):
        self.calls = 0

    def generate(self, request: TargetRequest) -> TargetResponse:
        self.calls += 1
        return TargetResponse(
            model_requested=request.model,
            model_resolved=request.model,
            text="ok",
            input_tokens=3,
            output_tokens=1,
            total_tokens=4,
            runtime_seconds=0.01,
        )


def test_request_fingerprint_changes_with_experimental_inputs():
    base = TargetRequest(
        model="gemma-4-26b-a4b-it",
        prompt="hello",
        solver_version="test",
        task_id="non-benchmark-smoke",
        attempt_index=0,
    )
    same = TargetRequest(**base.__dict__)
    changed = TargetRequest(
        **{**base.__dict__, "generation": GenerationConfig(temperature=0.1)}
    )
    assert base.fingerprint() == same.fingerprint()
    assert base.fingerprint() != changed.fingerprint()


def test_identical_request_reuses_cache(tmp_path: Path):
    provider = FakeProvider()
    client = CachedTargetClient(provider, tmp_path)
    request = TargetRequest(
        model="gemma-4-26b-a4b-it",
        prompt="Return exactly OK.",
        solver_version="test",
        task_id="non-benchmark-smoke",
        attempt_index=0,
    )

    first = client.generate(request)
    second = client.generate(request)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.text == second.text == "ok"
    assert provider.calls == 1
    assert len(list(tmp_path.glob("*.json"))) == 1

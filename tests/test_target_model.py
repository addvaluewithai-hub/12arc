import json
from pathlib import Path
from unittest.mock import patch

import pytest

from arc_lab.gemma_smoke import validate_smoke
from arc_lab.target_model import (
    CachedTargetClient,
    GenerationConfig,
    NvidiaNIMProvider,
    TargetRequest,
    TargetResponse,
)


class FakeProvider:
    provider_id = "fake-provider"

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


def _request(attempt_index: int = 0) -> TargetRequest:
    return TargetRequest(
        model="gemma-4-26b-a4b-it",
        prompt="Return exactly OK.",
        solver_version="test",
        task_id="non-benchmark-smoke",
        attempt_index=attempt_index,
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


def test_request_fingerprint_can_include_provider_identity():
    request = _request()
    assert request.fingerprint("nvidia-nim") == request.fingerprint("nvidia-nim")
    assert request.fingerprint("nvidia-nim") != request.fingerprint("google-genai")


def test_identical_request_reuses_cache(tmp_path: Path):
    provider = FakeProvider()
    client = CachedTargetClient(provider, tmp_path)
    request = _request()

    first = client.generate(request)
    second = client.generate(request)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.text == second.text == "ok"
    assert provider.calls == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_same_request_on_different_providers_uses_different_cache_keys(tmp_path: Path):
    first_provider = FakeProvider()
    second_provider = FakeProvider()
    second_provider.provider_id = "other-provider"
    request = _request()

    CachedTargetClient(first_provider, tmp_path).generate(request)
    CachedTargetClient(second_provider, tmp_path).generate(request)

    assert first_provider.calls == 1
    assert second_provider.calls == 1
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_live_call_pacing_waits_between_uncached_requests(tmp_path: Path):
    provider = FakeProvider()
    now = [100.0]
    sleeps: list[float] = []

    def clock() -> float:
        return now[0]

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds

    client = CachedTargetClient(
        provider,
        tmp_path,
        min_live_call_interval_seconds=61.0,
        clock=clock,
        sleep=sleep,
    )
    client.generate(_request(0))
    now[0] += 43.0
    client.generate(_request(1))

    assert provider.calls == 2
    assert sleeps == [18.0]


def test_cache_hits_do_not_consume_live_call_slots(tmp_path: Path):
    provider = FakeProvider()
    now = [100.0]
    sleeps: list[float] = []

    def clock() -> float:
        return now[0]

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds

    client = CachedTargetClient(
        provider,
        tmp_path,
        min_live_call_interval_seconds=61.0,
        clock=clock,
        sleep=sleep,
    )
    first = _request(0)
    client.generate(first)
    now[0] += 10.0
    cached = client.generate(first)
    now[0] += 33.0
    client.generate(_request(1))

    assert cached.cache_hit is True
    assert provider.calls == 2
    assert sleeps == [18.0]


def test_negative_live_call_interval_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="non-negative"):
        CachedTargetClient(
            FakeProvider(),
            tmp_path,
            min_live_call_interval_seconds=-1.0,
        )


class _Headers(dict):
    def items(self):
        return super().items()


class _FakeHTTPResponse:
    status = 200
    headers = _Headers({"X-RateLimit-Limit": "40", "Content-Type": "application/json"})

    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode()


def test_nvidia_provider_parses_usage_without_persisting_reasoning_text():
    payload = {
        "model": "deepseek-ai/deepseek-v4-flash-0731",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": "OK", "reasoning_content": "private reasoning"},
            }
        ],
        "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12},
    }
    provider = NvidiaNIMProvider(api_key="test-secret")
    request = TargetRequest(
        model="deepseek-ai/deepseek-v4-flash-0731",
        prompt="Reply OK",
        solver_version="smoke",
        task_id="non-benchmark-smoke",
        attempt_index=0,
    )
    with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse(payload)):
        response = provider.generate(request)

    assert response.text == "OK"
    assert response.input_tokens == 9
    assert response.output_tokens == 3
    assert response.total_tokens == 12
    assert response.provider_metadata["provider"] == "nvidia-nim"
    assert response.provider_metadata["reasoning_chars"] == len("private reasoning")
    assert "private reasoning" not in json.dumps(response.provider_metadata)
    assert response.provider_metadata["rate_limit_headers"]["x-ratelimit-limit"] == "40"


def test_nvidia_provider_requires_environment_secret(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY"):
        NvidiaNIMProvider()


def _smoke_response(*, cache_hit: bool, text: str = "available") -> TargetResponse:
    return TargetResponse(
        model_requested="gemma-4-26b-a4b-it",
        model_resolved="gemma-4-26b-a4b-it",
        text=text,
        input_tokens=10,
        output_tokens=2,
        total_tokens=12,
        runtime_seconds=0.5,
        cache_hit=cache_hit,
        provider_metadata={"model": {"name": "models/gemma-4-26b-a4b-it"}},
    )


def test_smoke_validation_checks_model_catalog_and_cache_not_exact_wording():
    validate_smoke(
        _smoke_response(cache_hit=False, text="Text generation is available."),
        _smoke_response(cache_hit=True, text="Text generation is available."),
        requested_model="gemma-4-26b-a4b-it",
    )


def test_smoke_validation_rejects_wrong_catalog_model():
    first = _smoke_response(cache_hit=False)
    first.provider_metadata = {"model": {"name": "models/gemma-4-31b-it"}}
    with pytest.raises(ValueError, match="provider catalog resolved"):
        validate_smoke(
            first,
            _smoke_response(cache_hit=True),
            requested_model="gemma-4-26b-a4b-it",
        )

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class GenerationConfig:
    temperature: float = 1.0
    top_p: float | None = 0.95
    top_k: int | None = 64
    max_output_tokens: int = 256


@dataclass(frozen=True)
class TargetRequest:
    model: str
    prompt: str
    solver_version: str
    task_id: str
    attempt_index: int
    generation: GenerationConfig = GenerationConfig()

    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class TargetResponse:
    model_requested: str
    model_resolved: str | None
    text: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    runtime_seconds: float
    cache_hit: bool = False
    provider_metadata: dict[str, Any] | None = None


class TargetProvider(Protocol):
    def generate(self, request: TargetRequest) -> TargetResponse: ...


class CachedTargetClient:
    def __init__(
        self,
        provider: TargetProvider,
        cache_dir: str | Path,
        *,
        min_live_call_interval_seconds: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if min_live_call_interval_seconds < 0:
            raise ValueError("min_live_call_interval_seconds must be non-negative")
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.min_live_call_interval_seconds = min_live_call_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_live_call_started: float | None = None

    def _wait_for_live_slot(self) -> None:
        if self._last_live_call_started is None:
            return
        elapsed = self._clock() - self._last_live_call_started
        remaining = self.min_live_call_interval_seconds - elapsed
        if remaining > 0:
            self._sleep(remaining)

    def generate(self, request: TargetRequest) -> TargetResponse:
        key = request.fingerprint()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            payload = json.loads(path.read_text())
            payload["cache_hit"] = True
            return TargetResponse(**payload)

        self._wait_for_live_slot()
        self._last_live_call_started = self._clock()
        response = self.provider.generate(request)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(response)
        payload["cache_hit"] = False
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return response


class GoogleGenAIProvider:
    def __init__(self, api_key: str | None = None):
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("install the 'gemma' optional dependency") from exc

        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=key)

    @staticmethod
    def _get(value: Any, name: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)

    def resolve_model(self, model: str) -> dict[str, Any]:
        info = self._client.models.get(model=model)
        return {
            "name": self._get(info, "name"),
            "display_name": self._get(info, "display_name"),
            "version": self._get(info, "version"),
        }

    def generate(self, request: TargetRequest) -> TargetResponse:
        from google.genai import types

        model_info = self.resolve_model(request.model)
        started = time.perf_counter()
        response = self._client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=types.GenerateContentConfig(
                temperature=request.generation.temperature,
                top_p=request.generation.top_p,
                top_k=request.generation.top_k,
                max_output_tokens=request.generation.max_output_tokens,
            ),
        )
        runtime = time.perf_counter() - started
        usage = self._get(response, "usage_metadata")
        resolved = self._get(response, "model_version") or model_info.get("name")
        return TargetResponse(
            model_requested=request.model,
            model_resolved=resolved,
            text=response.text or "",
            input_tokens=self._get(usage, "prompt_token_count"),
            output_tokens=self._get(usage, "candidates_token_count"),
            total_tokens=self._get(usage, "total_token_count"),
            runtime_seconds=runtime,
            provider_metadata={"model": model_info},
        )

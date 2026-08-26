from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping


CRITIQUE_KEYS = {
    "candidate_id",
    "likely_failure",
    "violated_training_pair",
    "forbidden_constant_risk",
    "separator_or_unchanged_region_risk",
    "repair_suggestion",
}

CHALLENGE_KEYS = {
    "candidate_id",
    "critique_valid",
    "reason",
    "smallest_general_repair",
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _candidate_id(value: Any) -> bool:
    return _nonempty_text(value) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate_critique_manifest(
    value: Any,
    *,
    candidate_ids: Iterable[str] | None = None,
    training_pair_count: int | None = None,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"critiques"}:
        raise ValueError("critique manifest must contain exactly top-level key 'critiques'")
    records = value["critiques"]
    if not isinstance(records, list) or not records:
        raise ValueError("critiques must be a non-empty JSON array")
    allowed_ids = set(candidate_ids) if candidate_ids is not None else None
    seen: set[str] = set()
    canonical: list[dict[str, Any]] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping) or set(raw) != CRITIQUE_KEYS:
            raise ValueError(f"critique[{index}] must contain exactly the required six keys")
        candidate_id = raw["candidate_id"]
        if not _candidate_id(candidate_id):
            raise ValueError(f"critique[{index}].candidate_id must be a 64-char lowercase hex fingerprint")
        if candidate_id in seen:
            raise ValueError(f"duplicate critique candidate_id: {candidate_id}")
        if allowed_ids is not None and candidate_id not in allowed_ids:
            raise ValueError(f"unknown critique candidate_id: {candidate_id}")
        pair_index = raw["violated_training_pair"]
        if not isinstance(pair_index, int) or isinstance(pair_index, bool) or pair_index < 0:
            raise ValueError(f"critique[{index}].violated_training_pair must be a non-negative integer")
        if training_pair_count is not None and pair_index >= training_pair_count:
            raise ValueError(f"critique[{index}].violated_training_pair is outside the training-pair range")
        for key in (
            "likely_failure",
            "forbidden_constant_risk",
            "separator_or_unchanged_region_risk",
            "repair_suggestion",
        ):
            if not _nonempty_text(raw[key]):
                raise ValueError(f"critique[{index}].{key} must be non-empty text")
        seen.add(candidate_id)
        canonical.append(dict(raw))
    return {"critiques": canonical}


def validate_challenge_manifest(
    value: Any,
    *,
    candidate_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"challenges"}:
        raise ValueError("challenge manifest must contain exactly top-level key 'challenges'")
    records = value["challenges"]
    if not isinstance(records, list) or not records:
        raise ValueError("challenges must be a non-empty JSON array")
    allowed_ids = set(candidate_ids) if candidate_ids is not None else None
    seen: set[str] = set()
    canonical: list[dict[str, Any]] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping) or set(raw) != CHALLENGE_KEYS:
            raise ValueError(f"challenge[{index}] must contain exactly the required four keys")
        candidate_id = raw["candidate_id"]
        if not _candidate_id(candidate_id):
            raise ValueError(f"challenge[{index}].candidate_id must be a 64-char lowercase hex fingerprint")
        if candidate_id in seen:
            raise ValueError(f"duplicate challenge candidate_id: {candidate_id}")
        if allowed_ids is not None and candidate_id not in allowed_ids:
            raise ValueError(f"unknown challenge candidate_id: {candidate_id}")
        if not isinstance(raw["critique_valid"], bool):
            raise ValueError(f"challenge[{index}].critique_valid must be JSON boolean")
        for key in ("reason", "smallest_general_repair"):
            if not _nonempty_text(raw[key]):
                raise ValueError(f"challenge[{index}].{key} must be non-empty text")
        seen.add(candidate_id)
        canonical.append(dict(raw))
    return {"challenges": canonical}


def strict_phase_acceptor(key: str) -> Callable[[Any], bool]:
    if key == "critiques":
        validator = validate_critique_manifest
    elif key == "challenges":
        validator = validate_challenge_manifest
    else:
        raise ValueError(f"unsupported phase contract key: {key}")

    def accept(value: Any) -> bool:
        try:
            validator(value)
            return True
        except (TypeError, ValueError):
            return False

    return accept


def critique_contract_instruction() -> str:
    return (
        'Return exactly one JSON object with exactly key "critiques". Its value must be a non-empty array. '
        'Each item must contain exactly candidate_id, likely_failure, violated_training_pair, '
        'forbidden_constant_risk, separator_or_unchanged_region_risk, repair_suggestion. '
        'candidate_id must be the 64-character lowercase hexadecimal candidate fingerprint; '
        'violated_training_pair must be a non-negative JSON integer; all four text fields must be non-empty strings. '
        'No extra keys, markdown, prose outside the object, nulls, or pseudocode.'
    )


def challenge_contract_instruction() -> str:
    return (
        'Return exactly one JSON object with exactly key "challenges". Its value must be a non-empty array. '
        'Each item must contain exactly candidate_id, critique_valid, reason, smallest_general_repair. '
        'candidate_id must be the 64-character lowercase hexadecimal candidate fingerprint; '
        'critique_valid must be a JSON boolean; reason and smallest_general_repair must be non-empty strings. '
        'No extra keys, markdown, prose outside the object, nulls, or invented execution results.'
    )

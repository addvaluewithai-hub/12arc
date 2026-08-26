from __future__ import annotations

from typing import Any

from . import multi_candidate_experiment as _base
from .multi_candidate_phase_contract import (
    challenge_contract_instruction,
    critique_contract_instruction,
    strict_phase_acceptor,
)


# Preserve generation/repair candidate semantics and all execution/scoring behavior.
# Only replace the previously loose critique/challenge boundary with exact fail-closed
# record validation and exact correction instructions.
_base._dict_key_acceptor = strict_phase_acceptor
_original_parse_json_or_retry = _base._parse_json_or_retry


def _hardened_parse_json_or_retry(*args: Any, **kwargs: Any) -> Any:
    stage = kwargs.get("stage")
    if stage == "critique":
        kwargs["retry_instruction"] = critique_contract_instruction()
    elif stage == "critique_the_critique":
        kwargs["retry_instruction"] = challenge_contract_instruction()
    return _original_parse_json_or_retry(*args, **kwargs)


_base._parse_json_or_retry = _hardened_parse_json_or_retry

run = _base.run
main = _base.main


if __name__ == "__main__":
    main()

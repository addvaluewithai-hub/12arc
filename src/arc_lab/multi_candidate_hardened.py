from __future__ import annotations

from . import multi_candidate_experiment as _base
from .multi_candidate_phase_contract import strict_phase_acceptor


# Preserve generation/repair candidate semantics and all execution/scoring behavior.
# Only replace the previously loose phase-container acceptor with exact fail-closed
# critique/challenge record validation.
_base._dict_key_acceptor = strict_phase_acceptor

run = _base.run
main = _base.main


if __name__ == "__main__":
    main()

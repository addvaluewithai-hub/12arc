from __future__ import annotations

import json
from pathlib import Path

TASK_ID = "T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR"
NEXT_TASK_ID = "T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN"
RUN = "ARC-R039"
SHIFT_ID = "ARC-SHIFT-20260826T060924Z"


def main() -> None:
    queue_path = Path("lab/registry/queue.json")
    counter_path = Path("lab/registry/run-counter.json")
    validation_path = Path("lab/validation/T0022B-schema-contract.json")

    queue = json.loads(queue_path.read_text())
    counter = json.loads(counter_path.read_text())
    validation = json.loads(validation_path.read_text())

    task = next(t for t in queue["tasks"] if t["id"] == TASK_ID)
    assert task["status"] == "claimed"
    assert task["claim"]["shift_id"] == SHIFT_ID
    matches = [
        r for r in counter["active_reservations"]
        if r["run"] == RUN and r["task_id"] == TASK_ID and r["shift_id"] == SHIFT_ID
    ]
    assert len(matches) == 1
    assert validation["verdict"] == "PASS"
    assert validation["target_model_calls"] == 0
    assert validation["public_evaluation_used"] is False
    assert validation["offline_contract_gate"]["parseable_candidates"] >= 8
    assert validation["offline_contract_gate"]["unique_candidates"] >= 8

    task["status"] = "done"
    task["completed_run"] = RUN
    task["progress"] = (
        "INFRA_ONLY / PASS. Added an explicit machine-checkable executable-IR prompt contract for "
        "schema-v1/v2 generation and repair, contract-validation instrumentation, and ARC-R038 "
        "regression tests. Offline gate: 10/10 representative fixtures parseable, 10 unique, all "
        "entered deterministic Python scoring; malformed instructions and string-version/pseudocode "
        "forms fail closed. GitHub Actions CI 32937412114 passed pytest, policy validation, frozen "
        "split reproduction, and pinned public-training validation. Zero target-model calls; public "
        "evaluation sealed."
    )
    task["claim"] = None

    if not any(t["id"] == NEXT_TASK_ID for t in queue["tasks"]):
        queue["tasks"].append({
            "id": NEXT_TASK_ID,
            "title": "Matched rerun of multi-candidate critique/repair with repaired executable-IR contract",
            "type": "target-model-experiment",
            "status": "ready",
            "priority": 62,
            "depends_on": [TASK_ID],
            "recommended_role": "reasoning-systems-inventor",
            "success_test": (
                "On exactly public-training task 06df4c85, rerun the frozen four-phase T0022 loop with "
                "only the executable-IR prompt/output contract changed. Operational success requires "
                ">=8 parseable non-duplicate candidates; research progress then requires >=1 exact "
                "train-consistent candidate or a dominant mechanically observed failure class/near-miss "
                "improvement. Protocol: lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json."
            ),
            "required_resources": [
                "validated T0022B contract gate",
                "validated T0022A parser/verifier",
                "authorized GitHub Actions push-trigger path",
                "NVIDIA_API_KEY repository secret",
                "permitted public ARC training data only",
            ],
            "expected_artifacts": [
                "sanitized model/cache manifest",
                "contract-validation metrics",
                "normalized candidate IR manifest",
                "critique and repair manifest",
                "deterministic Python scoring/ranking",
                "matched comparator delta vs ARC-R038",
                "failure analysis",
                "queue/state/handoff updates",
            ],
            "evidence": (
                "ARC-R038 had 0/24 executable candidates due a prompt/parser contract mismatch. ARC-R039 "
                "repaired that interface and passed 10/10 offline representative fixtures plus exact "
                "malformed-form regressions without changing parser/verifier semantics."
            ),
            "execution_path": {
                "kind": "github-actions-push-trigger",
                "workflow": ".github/workflows/t0022-multi-candidate.yml",
                "trigger_file": "lab/triggers/t0022-multi-candidate.request",
                "expected_result": "lab/results/{run}-multi-candidate.json",
                "status_file": "lab/executions/{run}.json",
                "max_wait_minutes": 180,
                "required_secret": "NVIDIA_API_KEY",
                "on_trigger": (
                    "write JSON with schema_version=1, task_id, reserved run, claim shift_id, and "
                    "requested_at; then stop the shift and let GitHub Actions execute"
                ),
            },
            "claim": None,
        })

    queue_path.write_text(json.dumps(queue, separators=(",", ":")) + "\n")

    counter["last_completed_run"] = RUN
    counter["next_run_number"] = 40
    counter["active_reservations"] = []
    counter_path.write_text(json.dumps(counter, separators=(",", ":")) + "\n")

    Path("lab/STATE.md").write_text("""# ARC Research Lab — Current State

Updated: 2026-08-26
Phase: **PHASE 2 — architecture research**
Latest completed research run: **ARC-R039**
Next unallocated research run: **ARC-R040**

## Fixed comparator and model policy

Routine hosted research uses NVIDIA NIM with primary `deepseek-ai/deepseek-v4-flash-0731`. ARC-R016 direct-JSON baseline remains frozen at **45/174 = 25.8621%** on deterministic public-training-derived `dev_validation`. Public evaluation remains sealed.

## Current evidence chain

ARC-R038 attempted the first multi-candidate generate -> critique -> critique-the-critique -> repair -> Python-select loop on `06df4c85`, but it was operationally inconclusive: all 24 submitted records failed the executable IR parser, so no valid candidate reached critique or deterministic selection. Provider execution itself succeeded; the failure was the model-facing schema contract.

ARC-R039 completed `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR` as **INFRA_ONLY / PASS** with zero target-model calls. The only changed component was the generation/repair prompt-output contract and contract-validation instrumentation. Parser/executor semantics, normalization/deduplication, and Python ranking remained frozen.

The repaired contract now states exact schema-v1/v2 top-level keys, legal operators and parameter domains, integer `schema_version`, valid executable examples, and explicit prohibitions on the exact ARC-R038 malformed `instructions` and pseudocode `program` forms. Offline regression tests passed **10/10 parseable, 10 unique** representative fixtures through parse -> normalize -> deduplicate -> deterministic Python scoring; malformed ARC-R038 forms fail closed. GitHub Actions CI run `32937412114` passed pytest, policy validation, frozen development split reproduction, and pinned public-training-only validation. Validation artifact: `lab/validation/T0022B-schema-contract.json`.

This proves interface consistency offline, not model adherence. It does not claim that DeepSeek will follow the repaired contract or that candidate quality improved.

## Next active research direction

Highest-priority ready task: `T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN`.

Run exactly the matched T0022 rerun on public-training task `06df4c85` using NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`. Freeze the four phases, 4-request maximum, temperatures/top-p/top-k/output-token budgets, deterministic parser/verifier, deduplication, Python ranking, and comparator context from ARC-R038. Change only the executable-IR contract injected into generation and repair prompts.

Operational gate: at least **8 parseable non-duplicate executable candidates**. Only after that gate may the run be interpreted as evidence about multi-candidate reasoning. Research progress is either at least one exact train-consistent candidate or a dominant mechanical failure/near-miss signal supporting exactly one next ablation.

Protocol: `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`.

## Adjacent semantic follow-up

`T0023-PERSISTENT-LATTICE-TOPOLOGY-ABLATION` remains blocked so it does not displace the multi-candidate direction. Public evaluation remains sealed.
""")

    Path("lab/HANDOFF.md").write_text("""# Handoff

Start from `lab/RUNNER.md` and current Git state.

## ARC-R039 closed — T0022B executable-IR contract gate passed

`T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR` completed as **INFRA_ONLY / PASS** with zero target-model calls and no public evaluation.

Durable evidence:
- `src/arc_lab/multi_candidate_contract.py`
- `tests/test_multi_candidate_contract.py`
- `lab/experiments/T0022-executable-candidate-contract.json`
- `lab/validation/T0022B-schema-contract.json`
- `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`
- `lab/runs/2026-08-26/ARC-R039.md`

The repair changes only the model-facing generation/repair contract. It supplies exact executable schema-v1/v2 shapes, legal operators/parameters, valid examples, and explicit forbidden ARC-R038 forms. Existing parser/verifier semantics and Python ranking are unchanged.

Offline gate: **10/10 parseable, 10 unique** representative candidates entered deterministic Python scoring. ARC-R038 natural-language `instructions`, string-valued schema versions with pseudocode `program`, and extra prose keys all fail closed. CI run `32937412114` passed the complete repository verification path.

This is infrastructure evidence only: it does not show the target model will obey the contract.

## Next task: T0022C matched contract rerun

`T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN` is ready. Protocol: `lab/experiments/T0022C-multi-candidate-contract-matched-rerun.json`.

Use exactly `06df4c85`, NVIDIA NIM `deepseek-ai/deepseek-v4-flash-0731`, and the frozen ARC-R038 four-phase generation settings and request budgets. The only treatment change is the repaired executable-IR contract. Trigger through `.github/workflows/t0022-multi-candidate.yml` after claim/reservation.

Do not interpret the architecture unless >=8 parseable non-duplicate candidates survive. If the contract gate passes but no exact candidate appears, use Python near-miss/failure clustering to evolve one component at a time. If the model still violates the explicit contract, treat that as an interface/constrained-generation problem rather than a reasoning rejection.

`T0023` remains blocked. Public evaluation remains sealed.

Run registry after closure: latest completed **ARC-R039**, no active reservations, next run **ARC-R040**.
""")

    report_path = Path("lab/runs/2026-08-26/ARC-R039.md")
    report_path.write_text("""# ARC-R039 — T0022B Multi-Candidate Schema Contract Repair

## Task and role

- Task: `T0022B-MULTI-CANDIDATE-SCHEMA-CONTRACT-REPAIR`
- Primary role: reasoning-systems-inventor
- Run: `ARC-R039`
- Target-model calls: **0**
- Public evaluation used: **false**

## Hypothesis

ARC-R038 failed operationally because generation and repair prompts did not expose the exact parser-supported executable IR. Making that contract explicit and mechanically testable should restore executable candidate flow without changing the multi-candidate architecture or deterministic verifier.

## Primary variable and frozen controls

Changed only the model-facing generation/repair prompt-output contract plus contract-validation instrumentation. Frozen: schema-v1/v2 parser/executor semantics, normalized-IR deduplication, deterministic Python ranking, eventual task `06df4c85`, and eventual NVIDIA/DeepSeek comparator setup.

## Implementation

Added `src/arc_lab/multi_candidate_contract.py` with exact executable shapes and prompt fragment; updated `multi_candidate_experiment.py` to inject the same contract into generation and repair and record mechanical contract validation; added `lab/experiments/T0022-executable-candidate-contract.json`; added regression tests for ARC-R038 malformed records; generalized the existing T0022 workflow to accept the predeclared T0022C task while preserving its provider/task execution path.

## Verification

GitHub Actions CI run `32937412114` on commit `a0b9287d40f01f5b6f445d828cd03dcb0392f3fe` completed successfully. Pytest, policy validation, frozen split reproduction, and pinned public-training-only corpus validation all passed.

Offline contract gate asserted **10 submitted / 10 parseable / 10 unique / 0 duplicates**, with all 10 entering deterministic Python scoring. Both exact ARC-R038 malformed families fail closed: natural-language `instructions` objects, and string `schema_version` plus pseudocode `program`; an extra-top-level-prose regression also fails closed.

## Result

**INFRA_ONLY / PASS.** The predeclared >=8 parseable non-duplicate fixture threshold was exceeded without changing solver semantics. No model inference occurred, so no exact ARC score, new solves, regressions, provider failures, token usage, or runtime claims are applicable beyond zero model requests.

## Adversarial interpretation

This validates only the interface contract offline. It does not prove DeepSeek will obey the contract under live generation, nor that the allowed IR is expressive enough for `06df4c85`. A live matched rerun is required before attributing any change to candidate diversity, critique, or repair.

## Next task

Predeclared exactly one matched continuation: `T0022C-MULTI-CANDIDATE-CONTRACT-MATCHED-RERUN`, on exactly `06df4c85`, changing only the repaired executable-IR prompt contract versus ARC-R038 while freezing provider/model/four-phase budgets and Python verification.
""")

    # Final internal consistency checks before Git persistence.
    queue = json.loads(queue_path.read_text())
    counter = json.loads(counter_path.read_text())
    closed = next(t for t in queue["tasks"] if t["id"] == TASK_ID)
    nxt = next(t for t in queue["tasks"] if t["id"] == NEXT_TASK_ID)
    assert closed["status"] == "done" and closed["claim"] is None and closed["completed_run"] == RUN
    assert nxt["status"] == "ready"
    assert counter["last_completed_run"] == RUN
    assert counter["next_run_number"] == 40
    assert counter["active_reservations"] == []


if __name__ == "__main__":
    main()

# Hosted / Offline Model Parity

Hosted inference is an R&D convenience. Prize-eligible evaluation has no internet, so the solver must preserve a path to open-weight offline execution.

Current hosted provider preference is NVIDIA NIM, with `deepseek-ai/deepseek-v4-flash-0731` and `nvidia/nemotron-3-ultra-550b-a55b` as provisional active candidates. Hosted availability does not by itself make a model acceptable for final competition use; verify weight/license/runtime feasibility before promotion to a mature solver.

## Rules

1. Pin exact provider and target-model identifiers and prompt templates.
2. Persist generation configuration and all deterministic preprocessing.
3. Keep model-facing interfaces provider-neutral.
4. Never rely on hidden hosted tools, search, proprietary retrieval or unexportable memory.
5. Record known ARC-specific pretraining/exposure for each foundation model; treat it as an interpretation/provenance issue, not an automatic exclusion when the data and model are competition-permitted.
6. Before treating an architecture as mature, run a parity study on a representative task slice comparing hosted and offline/open-weight execution when offline compute is available.
7. If parity is imperfect, quantify it; do not assume hosted serving and local weights are behaviorally identical.

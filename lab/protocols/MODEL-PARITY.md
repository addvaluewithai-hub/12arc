# Hosted / Offline Model Parity

Hosted Gemma inference is an R&D convenience. Prize-eligible evaluation has no internet, so the solver must preserve a path to open-weight offline execution.

## Rules

1. Pin exact target-model identifiers and prompt templates.
2. Persist generation configuration and all deterministic preprocessing.
3. Keep model-facing interfaces provider-neutral.
4. Never rely on hidden hosted tools, search, proprietary retrieval or unexportable memory.
5. Before treating an architecture as mature, run a parity study on a representative task slice comparing hosted and offline/open-weight execution when offline compute is available.
6. If parity is imperfect, quantify it; do not assume the API and local weights are behaviorally identical.

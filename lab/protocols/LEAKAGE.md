# Leakage Policy

ARC rewards novel-task generalization. A score is meaningless if the solver has been tuned against the same evaluation tasks repeatedly.

## Development data

Use the public ARC-AGI-2 training set to construct deterministic research splits. The split algorithm must depend only on task ID plus a versioned seed and must be committed.

Recommended initial policy:

- `dev_train`: 70%
- `dev_validation`: 20%
- `dev_holdout`: 10%

The holdout is used less frequently than validation and never for prompt-by-prompt tweaking.

## Public evaluation

Treat the 120-task public evaluation set as sealed milestone evaluation. Do not inspect individual failures and then modify the solver in response. Do not run it every shift. Record every public-eval exposure in an audit file when milestone evaluation begins.

## Forbidden

- Hand-solving eval tasks and encoding the discovered rules.
- Asking the research model to inspect public-eval solutions during ordinary development.
- Choosing prompt/algorithm variants by public-eval score.
- Mixing task-specific hints from evaluation tasks into the system prompt, DSL or training corpus.

## Synthetic data

Synthetic tasks are allowed only with provenance. Keep generator code, seed, generation policy and source models recorded so a claimed effect can be reproduced and audited.

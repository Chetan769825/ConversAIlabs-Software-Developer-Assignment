# Architecture

## Components and data flow

The CLI creates configuration, a provider, and an `Orchestrator`. The orchestrator
validates the root, asks `RepositoryExplorer` for a `RepositorySummary`, and gives its
important/relevant file list to `ContextBuilder`. The builder reads progressively
within file and total-context limits. `Planner` requests a schema-constrained
`ExecutionPlan`; `Executor` requests `ImplementationActions` and maps each action to
an explicit tool. `Validator` runs discovered scripts, `Reviewer` emits a typed
`ReviewResult`, and `Reporter` persists the evidence.

Pydantic contracts are the boundaries between non-deterministic model output and
deterministic code. Invalid structured output is repaired once by the provider and
then fails clearly. Tool errors, timeouts, patch failures, repository errors, and
provider errors cross the orchestration boundary and transition the run to `FAILED`.

## State and artifacts

`INITIALISE → VALIDATE_REPOSITORY → EXPLORE → BUILD_CONTEXT → PLAN → IMPLEMENT →
VALIDATE → REVIEW → (CORRECT → VALIDATE → REVIEW) → SUMMARISE → DONE`.
Any unhandled failure ends in `FAILED`. The correction cycle is capped by
`AGENT_MAX_ITERATIONS` (default two).

Every run stores request, redacted configuration, repository summary, plan, JSONL
tool audit, validation output, review, final patch, and final summary. Provider
replacement requires implementing the small `LLMProvider.structured` protocol and
adding it to the factory. New tools should preserve root confinement and audit
logging.

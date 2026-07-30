# Interview Preparation

**Why tags, not folders?** Tags are optional, backward-compatible, and let a note
belong to several topics. Folders require hierarchy and move/conflict semantics.

**Why not semantic search?** The requirement and dataset do not justify embeddings,
infrastructure, privacy cost, or ranking complexity. Keyword search is predictable.

**Why a custom state machine?** It makes transitions, retries, budgets, and failure
conditions visible and testable without a large framework dependency.

**How does it generalize?** Exploration and planning operate on manifests, entry
points, architectural naming, request terms, imports, structured plans, and generic
tools—not note/tag keywords or target-specific branches.

**How are destructive actions prevented?** Canonical path confinement, symlink
checks, explicit tools, argument-array command execution, allow/block lists, timeouts,
iteration caps, dirty-tree warnings, and no push/reset. Real production still needs
container isolation and approvals.

**What happens when tests fail?** Validation evidence is passed to review. A
critical/high finding permits one bounded correction by default, then tests and
review rerun. Remaining failure is reported honestly.

**How would this scale to a monorepo?** Add manifest/workspace discovery, dependency
graphs, AST-aware symbols, changed-scope test selection, indexed search, context
ranking, and per-package budgets.

**How would you add approval?** Insert an `APPROVE_PLAN` transition and require signed
approval for file deletion, dependency changes, migrations, or commands above a risk
threshold.

**What would you improve?** Container isolation, AST/semantic retrieval, streaming
observability, richer evaluations, multi-provider support, and PR automation.

**Can it implement pinning, archiving, rate limiting, API docs, or soft deletion?**
Yes. Those are inferred through repository context and the same plan/action schemas;
no domain-specific branch is required. The planner identifies layers and compatibility
risks, the executor patches them, and repository scripts validate the result.

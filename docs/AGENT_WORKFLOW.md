# Agent Workflow

1. `VALIDATE_REPOSITORY` rejects missing or empty paths and records initial Git state.
2. `EXPLORE` filters generated/private paths, detects manifests, languages,
   frameworks, scripts, layers, and requirement-term matches.
3. `BUILD_CONTEXT` reads only prioritized text files under per-file and total limits.
4. `PLAN` validates model JSON as an `ExecutionPlan` and prints it before edits.
5. `IMPLEMENT` executes typed actions through filesystem, patch, shell, and Git tools.
6. `VALIDATE` runs test/build/lint commands actually declared by the repository.
7. `REVIEW` assesses requirement coverage, compatibility, security, validation,
   errors, tests, scope, maintainability, and documentation.
8. `CORRECT` is permitted once by default for critical/high findings, followed by
   validation and review again.
9. `SUMMARISE` captures diff, changed files, evidence, and unresolved findings.

Dry-run ends after planning and writes a complete artifact set identifying skipped
stages. Existing changes produce a warning. Failures are visible and result in a
non-zero CLI exit; they are never rewritten as successes.

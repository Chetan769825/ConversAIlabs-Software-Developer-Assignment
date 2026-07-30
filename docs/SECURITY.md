# Security

## Threat model

The model and repository content are untrusted. Relevant threats include path
traversal and symlink escape, secret collection, oversized/binary content, command
injection, destructive Git or operating-system operations, runaway processes,
unbounded loops, and misleading audit output.

## Mitigations

`SafeFilesystem` resolves canonical paths and requires the approved root to be the
path or an ancestor. It rejects binary and oversized reads. Generated directories,
logs, and `.env` are excluded from exploration. `SafeShell` uses `shell=False`,
argument arrays, an executable allowlist, dangerous-pattern blocks, confined working
directories, timeouts, captured output, and an output cap. Tool records contain
arguments and timing but configuration artifacts omit credentials. Patch and Git
operations never push or force-reset. Iterations and context are bounded.

## Boundaries

This is not a secure OS sandbox. An allowlisted interpreter can still execute harmful
code, dependencies can run install scripts, and application tests are repository
code. Production deployment needs disposable containers or VMs, least-privilege
credentials, egress restrictions, resource quotas, syscall policy, immutable audit
storage, secret scanning, and human approval for high-impact actions.

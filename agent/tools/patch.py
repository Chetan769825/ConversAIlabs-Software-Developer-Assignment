"""Minimal unified-patch application through the allowlisted Git binary."""

import subprocess
from pathlib import Path

from agent.errors import AgentError


def apply_patch(root: Path, patch: str) -> None:
    completed = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=root, input=patch, capture_output=True, text=True, shell=False, check=False,
    )
    if completed.returncode:
        raise AgentError(f"Patch failed: {completed.stderr.strip()}")

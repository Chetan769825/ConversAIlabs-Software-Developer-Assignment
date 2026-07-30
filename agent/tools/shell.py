"""Allowlisted, non-shell command execution."""

import subprocess
import os
from dataclasses import dataclass
from pathlib import Path

from agent.errors import SecurityError

ALLOWED_EXECUTABLES = {"git", "python", "pytest", "node", "npm", "npm.cmd", "npx", "npx.cmd"}
BLOCKED_FRAGMENTS = {
    "rm -rf", "sudo", "shutdown", "reboot", "mkfs", "chmod -r 777",
    "git push --force", "git reset --hard", "curl | sh", "wget | sh",
}


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class SafeShell:
    def __init__(self, root: Path, timeout: int = 120, output_limit: int = 100_000):
        self.root = root.resolve(strict=True)
        self.timeout = timeout
        self.output_limit = output_limit

    def validate(self, command: list[str]) -> None:
        if not command or command[0].lower() not in ALLOWED_EXECUTABLES:
            raise SecurityError("Command executable is not allowlisted")
        rendered = " ".join(command).lower()
        if any(fragment in rendered for fragment in BLOCKED_FRAGMENTS):
            raise SecurityError("Dangerous command pattern rejected")

    def run(self, command: list[str], cwd: str | Path = ".") -> CommandResult:
        self.validate(command)
        directory = (self.root / cwd).resolve()
        if directory != self.root and self.root not in directory.parents:
            raise SecurityError("Command working directory escapes approved root")
        executable_command = command
        if os.name == "nt" and command[0].lower() in {"npm", "npx"}:
            executable_command = [f"{command[0]}.cmd", *command[1:]]
        completed = subprocess.run(
            executable_command, cwd=directory, capture_output=True, text=True,
            timeout=self.timeout, shell=False, check=False,
        )
        return CommandResult(
            command, completed.returncode,
            completed.stdout[-self.output_limit:], completed.stderr[-self.output_limit:],
        )

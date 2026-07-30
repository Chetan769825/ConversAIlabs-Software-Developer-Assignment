import subprocess
from pathlib import Path

import pytest

from agent.errors import SecurityError
from agent.tools.shell import SafeShell


def test_allowlisted_command_runs(tmp_path: Path) -> None:
    result = SafeShell(tmp_path).run(["python", "--version"])
    assert result.returncode == 0


@pytest.mark.parametrize("command", [
    ["powershell", "Get-ChildItem"],
    ["git", "reset", "--hard"],
    ["npm", "run", "x", "rm -rf"],
])
def test_dangerous_commands_are_rejected(tmp_path: Path, command: list[str]) -> None:
    with pytest.raises(SecurityError):
        SafeShell(tmp_path).validate(command)


def test_timeout_is_enforced(tmp_path: Path) -> None:
    with pytest.raises(subprocess.TimeoutExpired):
        SafeShell(tmp_path, timeout=1).run(["python", "-c", "import time;time.sleep(2)"])

"""Read-only Git helpers."""

import subprocess
import difflib
from pathlib import Path


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", *args],
        cwd=root, capture_output=True, text=True, shell=False, check=False,
    )
    return (result.stdout or result.stderr).strip()


def git_status(root: Path) -> str:
    return git_output(root, "status", "--short")


def git_diff(root: Path) -> str:
    tracked_diff = git_output(root, "diff", "--", ".")
    untracked = git_output(root, "ls-files", "--others", "--exclude-standard").splitlines()
    additions: list[str] = []
    for name in untracked:
        path = root / name
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        except (OSError, UnicodeDecodeError):
            continue
        additions.extend(difflib.unified_diff(
            [], lines, fromfile="/dev/null", tofile=f"b/{name}", lineterm="\n"
        ))
    sections = [section for section in (tracked_diff, "".join(additions)) if section]
    return "\n".join(sections)


def git_show(root: Path, revision: str = "HEAD") -> str:
    return git_output(root, "show", "--stat", "--oneline", revision)

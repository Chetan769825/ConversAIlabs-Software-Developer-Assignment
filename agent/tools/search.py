"""Small, dependency-free repository search helpers."""

import fnmatch
import re
from pathlib import Path

from agent.tools.filesystem import SafeFilesystem

IGNORED = {
    ".git", "node_modules", "dist", "build", "coverage", ".next", ".cache",
    "venv", ".venv", "__pycache__",
}


def repository_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and not any(part in IGNORED for part in path.relative_to(root).parts)
        and path.suffix != ".log"
        and path.name != ".env"
    )


def find_files(root: Path, pattern: str) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for path in repository_files(root)
        if fnmatch.fnmatch(path.name, pattern)
    ]


def search_code(fs: SafeFilesystem, query: str, *, max_results: int = 100) -> list[dict[str, object]]:
    regex = re.compile(re.escape(query), re.IGNORECASE)
    results: list[dict[str, object]] = []
    for path in repository_files(fs.root):
        try:
            text = fs.read_file(path)
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                results.append({
                    "path": path.relative_to(fs.root).as_posix(),
                    "line": number,
                    "text": line.strip()[:300],
                })
                if len(results) >= max_results:
                    return results
    return results

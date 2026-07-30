"""Heuristic, progressive repository exploration."""

import json
from collections import Counter
from pathlib import Path

from agent.errors import AgentError
from agent.models import RepositorySummary
from agent.tools.filesystem import SafeFilesystem
from agent.tools.git import git_status
from agent.tools.search import repository_files, search_code

EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".java": "Java", ".go": "Go", ".rs": "Rust",
}


class RepositoryExplorer:
    def __init__(self, root: Path, max_file_size: int = 250_000):
        if not root.exists() or not root.is_dir():
            raise AgentError(f"Repository not found: {root}")
        if not any(root.iterdir()):
            raise AgentError(f"Repository is empty: {root}")
        self.root = root.resolve()
        self.fs = SafeFilesystem(self.root, max_file_size)

    def explore(self, request: str = "") -> RepositorySummary:
        files = repository_files(self.root)
        relative = [path.relative_to(self.root).as_posix() for path in files]
        languages = Counter(EXTENSIONS.get(path.suffix) for path in files)
        languages.pop(None, None)
        manifests = [name for name in relative if Path(name).name in {
            "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod",
        }]
        frameworks: list[str] = []
        test_commands: list[str] = []
        build_commands: list[str] = []
        lint_commands: list[str] = []
        if "package.json" in relative:
            package = json.loads(self.fs.read_file("package.json"))
            dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            frameworks.extend(name for name in ("express", "mongoose", "react", "next", "jest") if name in dependencies)
            scripts = package.get("scripts", {})
            if "test" in scripts:
                test_commands.append("npm test")
            if "build" in scripts:
                build_commands.append("npm run build")
            if "lint" in scripts:
                lint_commands.append("npm run lint")
        entry_points = [
            name for name in relative
            if Path(name).name in {"server.js", "index.js", "main.py", "app.py", "main.ts"}
        ]
        terms = [word.strip(".,!?").lower() for word in request.split() if len(word) > 4][:8]
        relevant = set(manifests + entry_points)
        for term in terms:
            relevant.update(item["path"] for item in search_code(self.fs, term, max_results=20))
        for name in relative:
            if any(part in name.lower() for part in ("route", "controller", "model", "service", "test")):
                relevant.add(name)
        risks = []
        if not any("test" in name.lower() for name in relative):
            risks.append("No test files were discovered")
        if not (self.root / ".git").exists():
            risks.append("Repository is not Git-managed")
        return RepositorySummary(
            repository_name=self.root.name,
            root_path=str(self.root),
            primary_languages=[name for name, _ in languages.most_common()],
            frameworks=frameworks,
            package_managers=["npm"] if "package.json" in relative else [],
            entry_points=entry_points,
            important_files=(manifests + entry_points)[:30],
            architecture_summary=(
                f"Repository with {len(files)} relevant files; likely layers include "
                + ", ".join(sorted({part for name in relative for part in name.split("/")[:-1]}))
            ),
            test_commands=test_commands,
            build_commands=build_commands,
            lint_commands=lint_commands,
            relevant_files=sorted(relevant)[:100],
            relevant_symbols=[],
            risks=risks,
            git_status=git_status(self.root) if (self.root / ".git").exists() else "not a git repository",
        )

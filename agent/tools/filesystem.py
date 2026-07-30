"""Workspace-confined filesystem operations."""

from pathlib import Path

from agent.errors import SecurityError


class SafeFilesystem:
    def __init__(self, root: Path, max_file_size: int = 250_000):
        self.root = root.resolve(strict=True)
        self.max_file_size = max_file_size

    def resolve(self, path: str | Path, *, must_exist: bool = True) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve(strict=must_exist)
        if resolved != self.root and self.root not in resolved.parents:
            raise SecurityError(f"Path escapes approved root: {path}")
        return resolved

    def read_file(self, path: str | Path) -> str:
        resolved = self.resolve(path)
        if resolved.stat().st_size > self.max_file_size:
            raise SecurityError(f"File exceeds size limit: {path}")
        data = resolved.read_bytes()
        if b"\x00" in data:
            raise SecurityError(f"Binary file rejected: {path}")
        return data.decode("utf-8")

    def write_file(self, path: str | Path, content: str, *, create_only: bool = False) -> None:
        resolved = self.resolve(path, must_exist=False)
        if create_only and resolved.exists():
            raise FileExistsError(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

    def list_directory(self, path: str | Path = ".") -> list[str]:
        resolved = self.resolve(path)
        return sorted(item.name for item in resolved.iterdir())

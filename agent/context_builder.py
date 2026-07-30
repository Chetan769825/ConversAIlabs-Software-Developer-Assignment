"""Bounded progressive context construction."""

from agent.models import RepositorySummary
from agent.tools.filesystem import SafeFilesystem


class ContextBuilder:
    def __init__(self, fs: SafeFilesystem, character_limit: int):
        self.fs = fs
        self.character_limit = character_limit

    def build(self, summary: RepositorySummary) -> str:
        chunks = [summary.model_dump_json(indent=2)]
        used = len(chunks[0])
        ordered = list(dict.fromkeys(summary.important_files + summary.relevant_files))
        for path in ordered:
            try:
                content = self.fs.read_file(path)
            except (OSError, UnicodeDecodeError):
                continue
            chunk = f"\n--- {path} ---\n{content}"
            if used + len(chunk) > self.character_limit:
                break
            chunks.append(chunk)
            used += len(chunk)
        return "".join(chunks)

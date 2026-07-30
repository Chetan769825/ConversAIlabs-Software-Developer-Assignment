import subprocess
from pathlib import Path

from agent.tools.git import git_diff


def test_diff_includes_untracked_text_files(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    (tmp_path / "new.txt").write_text("new content\n", encoding="utf-8")
    diff = git_diff(tmp_path)
    assert "b/new.txt" in diff
    assert "+new content" in diff

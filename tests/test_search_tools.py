from pathlib import Path

from agent.tools.filesystem import SafeFilesystem
from agent.tools.search import find_files, repository_files, search_code


def test_tree_filters_generated_directories(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("needle", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "bad.js").write_text("needle", encoding="utf-8")
    assert [p.name for p in repository_files(tmp_path)] == ["app.py"]
    assert find_files(tmp_path, "*.py") == ["src/app.py"]


def test_code_search_reports_path_and_line(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("one\nNeedle here\n", encoding="utf-8")
    result = search_code(SafeFilesystem(tmp_path), "needle")
    assert result == [{"path": "app.py", "line": 2, "text": "Needle here"}]

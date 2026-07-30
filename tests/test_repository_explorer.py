import json
from pathlib import Path

from agent.explorer import RepositoryExplorer


def test_summary_generation(tmp_path: Path) -> None:
    (tmp_path / "server.js").write_text("require('express')", encoding="utf-8")
    (tmp_path / "package.json").write_text(json.dumps({
        "dependencies": {"express": "1"}, "scripts": {"test": "jest"}
    }), encoding="utf-8")
    summary = RepositoryExplorer(tmp_path).explore("improve search")
    assert summary.primary_languages == ["JavaScript"]
    assert summary.frameworks == ["express"]
    assert summary.test_commands == ["npm test"]

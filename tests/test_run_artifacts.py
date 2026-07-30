import json
from pathlib import Path

from agent.config import ensure_directory
from agent.tools.logger import ToolLogger


def test_run_directory_and_logging(tmp_path: Path) -> None:
    run = ensure_directory(tmp_path / "run")
    logger = ToolLogger(run / "tool-calls.jsonl")
    assert logger.call("EXPLORE", "read_file", {"path": "x"}, "test", lambda: 42) == 42
    record = json.loads((run / "tool-calls.jsonl").read_text(encoding="utf-8"))
    assert record["success"] is True
    assert record["tool"] == "read_file"

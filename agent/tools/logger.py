"""JSONL audit logging for tool invocations."""

import json
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any, Callable


class ToolLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.touch(exist_ok=True)

    def call(
        self, state: str, tool: str, arguments: dict[str, Any],
        reason: str, operation: Callable[[], Any],
    ) -> Any:
        start = monotonic()
        success = False
        try:
            result = operation()
            success = True
            return result
        finally:
            record = {
                "timestamp": datetime.now(UTC).isoformat(),
                "state": state,
                "tool": tool,
                "arguments": arguments,
                "reason": reason,
                "success": success,
                "duration_ms": round((monotonic() - start) * 1000),
            }
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")

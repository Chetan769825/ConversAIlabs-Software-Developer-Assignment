from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from agent.config import AgentConfig
from agent.models import ExecutionPlan
from agent.orchestrator import Orchestrator

T = TypeVar("T", bound=BaseModel)


class MockProvider:
    def structured(self, system: str, prompt: str, schema: type[T]) -> T:
        assert schema is ExecutionPlan
        return schema.model_validate({
            "requirement_understanding": "change",
            "repository_understanding": "small repository",
            "selected_approach": "minimal change",
            "files_to_change": [{
                "path": "app.py", "purpose": "change", "change_type": "modify",
                "expected_effect": "improvement",
            }],
            "validation_steps": [],
        })


def test_dry_run_creates_complete_artifacts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("print('x')", encoding="utf-8")
    output = tmp_path / "runs"
    run = Orchestrator(repo, "change", AgentConfig(), MockProvider(), output).run(dry_run=True)
    expected = {
        "request.txt", "configuration.json", "repository-summary.json",
        "execution-plan.json", "tool-calls.jsonl", "validation-output.txt",
        "review.json", "final-diff.patch", "final-summary.md",
    }
    assert expected == {path.name for path in run.iterdir()}

"""Model-directed execution through explicit tools."""

from pathlib import Path

from agent.llm.base import LLMProvider
from agent.models.actions import ImplementationActions
from agent.models.plan import ExecutionPlan
from agent.tools.filesystem import SafeFilesystem
from agent.tools.logger import ToolLogger
from agent.tools.patch import apply_patch
from agent.tools.shell import SafeShell


class Executor:
    def __init__(
        self, root: Path, provider: LLMProvider, logger: ToolLogger,
        fs: SafeFilesystem, shell: SafeShell,
    ):
        self.root, self.provider, self.logger, self.fs, self.shell = root, provider, logger, fs, shell

    def execute(self, request: str, context: str, plan: ExecutionPlan) -> list[str]:
        response = self.provider.structured(
            "Produce small safe implementation actions. Prefer unified patches. "
            "Commands must be argument arrays using only git, python, pytest, node, npm, or npx.",
            f"Request:\n{request}\nPlan:\n{plan.model_dump_json()}\nContext:\n{context}",
            ImplementationActions,
        )
        changed: list[str] = []
        for action in response.actions:
            if action.tool == "apply_patch" and action.patch:
                self.logger.call("IMPLEMENT", "apply_patch", {"path": action.path}, action.reason,
                                 lambda p=action.patch: apply_patch(self.root, p))
            elif action.tool in {"write_file", "create_file"} and action.path and action.content is not None:
                self.logger.call(
                    "IMPLEMENT", action.tool, {"path": action.path}, action.reason,
                    lambda a=action: self.fs.write_file(
                        a.path or "", a.content or "", create_only=a.tool == "create_file"
                    ),
                )
                changed.append(action.path)
            elif action.tool == "run_command" and action.command:
                self.logger.call(
                    "IMPLEMENT", "run_command", {"command": action.command}, action.reason,
                    lambda c=action.command: self.shell.run(c),
                )
        return changed

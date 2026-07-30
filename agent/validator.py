"""Repository-aware validation command discovery and execution."""

from agent.models import RepositorySummary
from agent.tools.shell import CommandResult, SafeShell


class Validator:
    def __init__(self, shell: SafeShell):
        self.shell = shell

    def run(self, summary: RepositorySummary) -> list[CommandResult]:
        commands = summary.test_commands + summary.build_commands + summary.lint_commands
        return [self.shell.run(command.split()) for command in commands]

"""Deterministic agent workflow orchestration."""

from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console

from agent.config import AgentConfig, ensure_directory
from agent.context_builder import ContextBuilder
from agent.executor import Executor
from agent.explorer import RepositoryExplorer
from agent.llm.base import LLMProvider
from agent.models import ReviewResult
from agent.planner import Planner
from agent.reporter import final_summary, write_json
from agent.reviewer import Reviewer
from agent.state import AgentState
from agent.tools.filesystem import SafeFilesystem
from agent.tools.git import git_diff, git_status
from agent.tools.logger import ToolLogger
from agent.tools.shell import SafeShell
from agent.validator import Validator


class Orchestrator:
    """Runs one bounded explore-plan-implement-validate-review workflow."""

    def __init__(
        self, repo: Path, request: str, config: AgentConfig, provider: LLMProvider,
        output_root: Path, console: Console | None = None,
    ):
        self.repo, self.request, self.config, self.provider = repo.resolve(), request, config, provider
        self.output_root = output_root
        self.console = console or Console()

    def transition(self, state: AgentState) -> None:
        self.console.print(f"[bold cyan]State: {state.value}[/bold cyan]")

    def run(self, *, dry_run: bool = False) -> Path:
        stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
        run_dir = ensure_directory(self.output_root / stamp)
        (run_dir / "request.txt").write_text(self.request, encoding="utf-8")
        write_json(run_dir / "configuration.json", self.config.public_dict())
        logger = ToolLogger(run_dir / "tool-calls.jsonl")
        try:
            self.transition(AgentState.VALIDATE_REPOSITORY)
            explorer = RepositoryExplorer(self.repo, self.config.agent_max_file_size_bytes)
            initial_status = git_status(self.repo) if (self.repo / ".git").exists() else ""
            if initial_status:
                self.console.print("[yellow]Warning: pre-existing repository changes detected.[/yellow]")
            self.transition(AgentState.EXPLORE)
            summary = explorer.explore(self.request)
            write_json(run_dir / "repository-summary.json", summary)
            self.transition(AgentState.BUILD_CONTEXT)
            fs = SafeFilesystem(self.repo, self.config.agent_max_file_size_bytes)
            context = ContextBuilder(fs, self.config.agent_max_context_characters).build(summary)
            self.transition(AgentState.PLAN)
            plan = Planner(self.provider).create(self.request, context)
            write_json(run_dir / "execution-plan.json", plan)
            self.console.print(f"[bold]Selected approach:[/bold] {plan.selected_approach}")
            for change in plan.files_to_change:
                self.console.print(f"  {change.change_type}: {change.path}")
            if dry_run:
                review = ReviewResult(approved=True, summary="Dry run: implementation intentionally skipped.")
                write_json(run_dir / "review.json", review)
                (run_dir / "validation-output.txt").write_text("Dry run: validation skipped.\n", encoding="utf-8")
                (run_dir / "final-diff.patch").write_text("", encoding="utf-8")
                (run_dir / "final-summary.md").write_text(
                    final_summary(self.request, plan, "Dry run", review, []), encoding="utf-8"
                )
                self.transition(AgentState.DONE)
                return run_dir
            shell = SafeShell(self.repo, self.config.agent_command_timeout_seconds)
            changed: list[str] = []
            validation_text = ""
            review = ReviewResult(approved=False, summary="Review was not reached.")
            for iteration in range(self.config.agent_max_iterations):
                self.transition(AgentState.IMPLEMENT if iteration == 0 else AgentState.CORRECT)
                changed.extend(Executor(self.repo, self.provider, logger, fs, shell).execute(
                    self.request, context, plan
                ))
                self.transition(AgentState.VALIDATE)
                results = Validator(shell).run(summary)
                validation_text = "\n".join(
                    f"$ {' '.join(result.command)}\n{result.stdout}{result.stderr}"
                    for result in results
                )
                (run_dir / "validation-output.txt").write_text(validation_text, encoding="utf-8")
                self.transition(AgentState.REVIEW)
                review = Reviewer(self.provider).review(
                    self.request, summary, plan, git_diff(self.repo), validation_text
                )
                if review.approved or not any(
                    finding.severity in {"critical", "high"} for finding in review.findings
                ):
                    break
            write_json(run_dir / "review.json", review)
            diff = git_diff(self.repo)
            (run_dir / "final-diff.patch").write_text(diff, encoding="utf-8")
            self.transition(AgentState.SUMMARISE)
            if not changed:
                changed = [line[3:] for line in git_status(self.repo).splitlines() if len(line) > 3]
            (run_dir / "final-summary.md").write_text(
                final_summary(self.request, plan, validation_text, review, changed), encoding="utf-8"
            )
            self.transition(AgentState.DONE)
            return run_dir
        except Exception:
            self.transition(AgentState.FAILED)
            raise

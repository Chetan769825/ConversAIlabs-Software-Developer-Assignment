"""Command-line entry point."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from agent.config import AgentConfig
from agent.explorer import RepositoryExplorer
from agent.llm import create_provider
from agent.orchestrator import Orchestrator
from agent.tools.shell import SafeShell
from agent.validator import Validator

app = typer.Typer(help="Controlled repository-aware coding agent", no_args_is_help=True)
console = Console()


@app.command()
def inspect(repo: Annotated[Path, typer.Option(exists=True, file_okay=False)]) -> None:
    """Inspect a repository without using an LLM."""
    summary = RepositoryExplorer(repo).explore()
    table = Table(title="Repository summary")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", summary.repository_name)
    table.add_row("Languages", ", ".join(summary.primary_languages) or "unknown")
    table.add_row("Frameworks", ", ".join(summary.frameworks) or "unknown")
    table.add_row("Entry points", ", ".join(summary.entry_points) or "none")
    table.add_row("Relevant files", str(len(summary.relevant_files)))
    console.print(table)
    console.print(summary.model_dump_json(indent=2))


@app.command()
def run(
    repo: Annotated[Path, typer.Option(exists=True, file_okay=False)],
    request: Annotated[str, typer.Option()],
    model: Annotated[str | None, typer.Option()] = None,
    provider: Annotated[str | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option()] = False,
    max_iterations: Annotated[int | None, typer.Option(min=1, max=5)] = None,
    verbose: Annotated[bool, typer.Option()] = True,
    output_dir: Annotated[Path, typer.Option()] = Path(".agent-runs"),
    non_interactive: Annotated[bool, typer.Option()] = False,
) -> None:
    """Run the complete coding workflow."""
    del non_interactive
    config = AgentConfig()
    updates: dict[str, object] = {"agent_verbose": verbose}
    if model:
        updates["llm_model"] = model
    if provider:
        updates["llm_provider"] = provider
    if max_iterations:
        updates["agent_max_iterations"] = max_iterations
    config = config.model_copy(update=updates)
    result = Orchestrator(
        repo, request, config, create_provider(config), output_dir, console
    ).run(dry_run=dry_run)
    console.print(f"[green]Run artifacts: {result}[/green]")


@app.command()
def validate(repo: Annotated[Path, typer.Option(exists=True, file_okay=False)]) -> None:
    """Run validation commands discovered from repository configuration."""
    summary = RepositoryExplorer(repo).explore()
    results = Validator(SafeShell(repo)).run(summary)
    failed = False
    for result in results:
        console.print(f"$ {' '.join(result.command)}")
        console.print(result.stdout + result.stderr)
        failed |= result.returncode != 0
    if failed:
        raise typer.Exit(1)


@app.command("show-last-run")
def show_last_run(output_dir: Path = Path(".agent-runs")) -> None:
    """Display the newest run summary."""
    runs = sorted(path for path in output_dir.glob("*") if path.is_dir())
    if not runs:
        console.print("[yellow]No run artifacts found.[/yellow]")
        raise typer.Exit(1)
    console.print((runs[-1] / "final-summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()

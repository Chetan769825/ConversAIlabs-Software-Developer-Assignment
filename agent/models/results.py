"""Exploration and review models."""

from typing import Literal

from pydantic import BaseModel, Field


class RepositorySummary(BaseModel):
    repository_name: str
    root_path: str
    primary_languages: list[str]
    frameworks: list[str]
    package_managers: list[str]
    entry_points: list[str]
    important_files: list[str]
    architecture_summary: str
    test_commands: list[str]
    build_commands: list[str]
    lint_commands: list[str]
    relevant_files: list[str]
    relevant_symbols: list[str]
    risks: list[str]
    git_status: str


class ReviewFinding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    file: str | None = None
    description: str
    recommended_fix: str


class ReviewResult(BaseModel):
    approved: bool
    summary: str
    findings: list[ReviewFinding] = Field(default_factory=list)

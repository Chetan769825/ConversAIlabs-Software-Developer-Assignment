"""Planning models."""

from typing import Literal

from pydantic import BaseModel, Field


class FileChange(BaseModel):
    path: str
    purpose: str
    change_type: Literal["create", "modify", "delete"]
    expected_effect: str


class ExecutionPlan(BaseModel):
    requirement_understanding: str
    repository_understanding: str
    selected_approach: str
    assumptions: list[str] = Field(default_factory=list)
    alternatives_considered: list[str] = Field(default_factory=list)
    files_to_change: list[FileChange]
    validation_steps: list[str]
    compatibility_considerations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

"""Structured implementation actions."""

from typing import Literal

from pydantic import BaseModel, Field


class ToolAction(BaseModel):
    tool: Literal["apply_patch", "write_file", "create_file", "run_command"]
    path: str | None = None
    content: str | None = None
    patch: str | None = None
    command: list[str] | None = None
    reason: str


class ImplementationActions(BaseModel):
    actions: list[ToolAction] = Field(default_factory=list)

"""Explicit finite workflow states."""

from enum import StrEnum


class AgentState(StrEnum):
    INITIALISE = "INITIALISE"
    VALIDATE_REPOSITORY = "VALIDATE_REPOSITORY"
    EXPLORE = "EXPLORE"
    BUILD_CONTEXT = "BUILD_CONTEXT"
    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    VALIDATE = "VALIDATE"
    REVIEW = "REVIEW"
    CORRECT = "CORRECT"
    SUMMARISE = "SUMMARISE"
    DONE = "DONE"
    FAILED = "FAILED"

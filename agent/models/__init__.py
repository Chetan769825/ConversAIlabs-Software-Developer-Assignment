"""Structured contracts used between agent stages."""

from .plan import ExecutionPlan, FileChange
from .results import RepositorySummary, ReviewFinding, ReviewResult

__all__ = [
    "ExecutionPlan",
    "FileChange",
    "RepositorySummary",
    "ReviewFinding",
    "ReviewResult",
]

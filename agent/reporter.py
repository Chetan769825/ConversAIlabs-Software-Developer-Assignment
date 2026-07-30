"""Run-artifact reporting."""

import json
from pathlib import Path

from agent.models import ExecutionPlan, RepositorySummary, ReviewResult


def write_json(path: Path, value: object) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump()  # type: ignore[union-attr]
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def final_summary(
    request: str, plan: ExecutionPlan, validation: str,
    review: ReviewResult, changed: list[str],
) -> str:
    return (
        "# Agent run summary\n\n"
        f"## Requirement\n\n{request}\n\n"
        f"## Selected approach\n\n{plan.selected_approach}\n\n"
        f"## Files changed\n\n" + "\n".join(f"- {path}" for path in changed) + "\n\n"
        f"## Validation\n\n```\n{validation}\n```\n\n"
        f"## Review\n\n{review.summary}\n\n"
        f"Approved: {review.approved}\n"
    )

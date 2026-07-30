"""Independent structured self-review."""

from agent.llm.base import LLMProvider
from agent.models import ExecutionPlan, RepositorySummary, ReviewResult


class Reviewer:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def review(
        self, request: str, summary: RepositorySummary, plan: ExecutionPlan,
        diff: str, validation: str,
    ) -> ReviewResult:
        return self.provider.structured(
            "Review changes for requirements, compatibility, security, validation, API consistency, "
            "error handling, coverage, scope, maintainability, and documentation.",
            f"Request:{request}\nSummary:{summary.model_dump_json()}\nPlan:{plan.model_dump_json()}"
            f"\nDiff:{diff}\nValidation:{validation}",
            ReviewResult,
        )

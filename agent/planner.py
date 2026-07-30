"""Structured planning stage."""

from agent.llm.base import LLMProvider
from agent.models import ExecutionPlan


class Planner:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def create(self, request: str, context: str) -> ExecutionPlan:
        return self.provider.structured(
            "You are a careful senior software engineer. Plan minimal, backward-compatible changes. "
            "Never hardcode behavior based on a particular product domain.",
            f"Product requirement:\n{request}\n\nRepository context:\n{context}",
            ExecutionPlan,
        )

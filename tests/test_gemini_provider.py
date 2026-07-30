from types import SimpleNamespace

import pytest

from agent.config import AgentConfig
from agent.errors import ProviderError
from agent.llm.factory import create_provider
from agent.llm.gemini_provider import GeminiProvider
from agent.models import ExecutionPlan


class FakeModels:
    def __init__(self, response: object):
        self.response = response
        self.calls: list[dict[str, object]] = []

    def generate_content(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.response


def test_gemini_provider_parses_structured_json() -> None:
    models = FakeModels(SimpleNamespace(
        parsed=None,
        text=ExecutionPlan(
            requirement_understanding="Improve organization",
            repository_understanding="Small API",
            selected_approach="Add generic query features",
            files_to_change=[],
            validation_steps=["pytest"],
        ).model_dump_json(),
    ))
    provider = GeminiProvider("test-key", "gemini-test", SimpleNamespace(models=models))
    result = provider.structured("system", "prompt", ExecutionPlan)
    assert result.selected_approach == "Add generic query features"
    assert models.calls[0]["model"] == "gemini-test"


def test_factory_requires_gemini_key() -> None:
    with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
        create_provider(AgentConfig(gemini_api_key=None))


def test_factory_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderError, match="Unsupported provider"):
        create_provider(AgentConfig(llm_provider="unknown"))

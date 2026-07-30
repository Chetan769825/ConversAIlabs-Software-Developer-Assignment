"""Provider construction."""

from agent.config import AgentConfig
from agent.errors import ProviderError
from agent.llm.base import LLMProvider
from agent.llm.openai_provider import OpenAIProvider


def create_provider(config: AgentConfig) -> LLMProvider:
    if config.llm_provider != "openai":
        raise ProviderError(f"Unsupported provider: {config.llm_provider}")
    if not config.openai_api_key:
        raise ProviderError("OPENAI_API_KEY is required for a full or dry run")
    return OpenAIProvider(config.openai_api_key, config.llm_model)

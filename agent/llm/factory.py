"""Provider construction."""

from agent.config import AgentConfig
from agent.errors import ProviderError
from agent.llm.base import LLMProvider
from agent.llm.gemini_provider import GeminiProvider


def create_provider(config: AgentConfig) -> LLMProvider:
    if config.llm_provider != "gemini":
        raise ProviderError(f"Unsupported provider: {config.llm_provider}")
    if not config.gemini_api_key:
        raise ProviderError("GEMINI_API_KEY is required for a full or dry run")
    return GeminiProvider(config.gemini_api_key, config.llm_model)

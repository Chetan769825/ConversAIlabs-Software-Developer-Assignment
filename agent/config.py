"""Environment-backed agent configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    """Runtime settings; secrets are never serialized into run artifacts."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "openai"
    llm_model: str = "gpt-5-mini"
    openai_api_key: str | None = Field(default=None, repr=False)
    agent_max_iterations: int = Field(default=2, ge=1, le=5)
    agent_command_timeout_seconds: int = Field(default=120, ge=1, le=600)
    agent_max_file_size_bytes: int = Field(default=250_000, ge=1024)
    agent_max_context_characters: int = Field(default=120_000, ge=10_000)
    agent_verbose: bool = True

    def public_dict(self) -> dict[str, object]:
        return {
            "provider": self.llm_provider,
            "model": self.llm_model,
            "max_iterations": self.agent_max_iterations,
            "command_timeout_seconds": self.agent_command_timeout_seconds,
            "max_file_size_bytes": self.agent_max_file_size_bytes,
            "max_context_characters": self.agent_max_context_characters,
            "verbose": self.agent_verbose,
        }


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=False)
    return path

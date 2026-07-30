"""Provider protocol."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    def structured(self, system: str, prompt: str, schema: type[T]) -> T:
        """Return a response validated against schema."""

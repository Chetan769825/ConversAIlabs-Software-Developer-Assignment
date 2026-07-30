"""OpenAI implementation using structured responses."""

from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from agent.errors import ProviderError

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def structured(self, system: str, prompt: str, schema: type[T]) -> T:
        last_error: Exception | None = None
        current_prompt = prompt
        for _ in range(2):
            try:
                response = self.client.responses.parse(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": current_prompt},
                    ],
                    text_format=schema,
                )
                if response.output_parsed is None:
                    raise ProviderError("Model returned no parsed output")
                return response.output_parsed
            except (ValidationError, ValueError, ProviderError) as exc:
                last_error = exc
                current_prompt += "\nRepair the response so it exactly matches the requested schema."
        raise ProviderError(f"Structured response failed: {last_error}")

"""Google Gemini implementation using schema-constrained responses."""

from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from agent.errors import ProviderError

T = TypeVar("T", bound=BaseModel)


class GeminiProvider:
    """Generate Pydantic-validated output with the Google Gen AI SDK."""

    def __init__(self, api_key: str, model: str, client: Any | None = None):
        self.client = client or genai.Client(api_key=api_key)
        self.model = model

    def structured(self, system: str, prompt: str, schema: type[T]) -> T:
        last_error: Exception | None = None
        current_prompt = prompt
        for _ in range(2):
            response = self.client.models.generate_content(
                model=self.model,
                contents=current_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.1,
                ),
            )
            try:
                if isinstance(response.parsed, schema):
                    return response.parsed
                if response.text:
                    return schema.model_validate_json(response.text)
                raise ProviderError("Gemini returned no structured output")
            except (ValidationError, ValueError, ProviderError) as exc:
                last_error = exc
                current_prompt += "\nRepair the response so it exactly matches the required schema."
        raise ProviderError(f"Structured Gemini response failed: {last_error}")

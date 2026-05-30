"""Concrete placeholder AI provider implementations."""

from app.ai.base import AIProvider


class MockAIProvider(AIProvider):
    """Default local provider used when no paid API key is configured."""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def status(self) -> str:
        return "ready"

    def describe(self) -> str:
        return (
            "Mock provider enabled for local development; future PulseOps AI workflows can be "
            "implemented without external credentials."
        )

    async def generate_completion(self, prompt: str) -> str:
        return f"[mock completion] {prompt}"


class OpenAIProvider(AIProvider):
    """Placeholder OpenAI provider with environment-driven configuration only."""

    def __init__(self, *, model: str, api_key: str | None) -> None:
        super().__init__(model=model)
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "openai"

    @property
    def status(self) -> str:
        return "configured" if self._api_key else "missing_api_key"

    def describe(self) -> str:
        if self._api_key:
            return (
                f"OpenAI placeholder provider selected with model '{self.model}'. Actual API "
                "calls are intentionally deferred until feature work begins."
            )
        return "OpenAI placeholder provider selected but OPENAI_API_KEY is not set yet."

    async def generate_completion(self, prompt: str) -> str:
        return f"[openai placeholder:{self.model}] {prompt}"


class GroqProvider(AIProvider):
    """Placeholder Groq provider with environment-driven configuration only."""

    def __init__(self, *, model: str, api_key: str | None) -> None:
        super().__init__(model=model)
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "groq"

    @property
    def status(self) -> str:
        return "configured" if self._api_key else "missing_api_key"

    def describe(self) -> str:
        if self._api_key:
            return (
                f"Groq placeholder provider selected with model '{self.model}'. Actual API "
                "calls are intentionally deferred until feature work begins."
            )
        return "Groq placeholder provider selected but GROQ_API_KEY is not set yet."

    async def generate_completion(self, prompt: str) -> str:
        return f"[groq placeholder:{self.model}] {prompt}"

"""Factory for selecting the configured AI provider implementation."""

from app.ai.base import AIProvider
from app.ai.providers import GroqProvider, MockAIProvider, OpenAIProvider
from app.core.config import Settings


def create_ai_provider(settings: Settings) -> AIProvider:
    """Instantiate the configured AI provider without making network calls."""
    if settings.ai_provider == "mock":
        return MockAIProvider(model=settings.ai_model)
    if settings.ai_provider == "openai":
        return OpenAIProvider(
            model=settings.ai_model,
            api_key=(
                settings.openai_api_key.get_secret_value()
                if settings.openai_api_key is not None
                else None
            ),
        )
    if settings.ai_provider == "groq":
        return GroqProvider(
            model=settings.ai_model,
            api_key=(
                settings.groq_api_key.get_secret_value()
                if settings.groq_api_key is not None
                else None
            ),
        )
    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")

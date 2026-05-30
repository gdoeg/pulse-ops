"""Abstract AI provider contract for PulseOps."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract interface for provider-specific AI integrations."""

    def __init__(self, *, model: str) -> None:
        self._model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider identifier."""

    @property
    def model(self) -> str:
        """Return the configured model identifier."""
        return self._model

    @property
    @abstractmethod
    def status(self) -> str:
        """Return the provider configuration state."""

    @abstractmethod
    def describe(self) -> str:
        """Describe how the provider is configured for the current runtime."""

    @abstractmethod
    async def generate_completion(self, prompt: str) -> str:
        """Return a placeholder completion without making external API calls."""

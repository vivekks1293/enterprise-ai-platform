from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.application.ai.contracts.provider_chunk import ProviderChunk
from app.application.ai.contracts.provider_request import ProviderRequest
from app.application.ai.contracts.provider_response import ProviderResponse


class AIProvider(ABC):
    """
    Contract implemented by all AI providers.

    Examples:
        - OpenAI
        - Anthropic
        - Gemini
        - Azure OpenAI
        - Ollama
        - Fake Provider
    """

    @abstractmethod
    async def stream(
        self,
        request: ProviderRequest,
    ) -> AsyncIterator[ProviderChunk]:
        """
        Streams the model response incrementally.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:
        """
        Generates a complete response without streaming.
        """
        raise NotImplementedError
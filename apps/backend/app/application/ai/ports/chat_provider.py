from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.application.ai.contracts.provider_chunk import ProviderChunk
from app.application.ai.contracts.provider_request import ProviderRequest
from app.application.ai.contracts.provider_response import ProviderResponse


class ChatProvider(ABC):
    """
    Contract implemented by all chat model providers.

    Examples:
        - OpenAI
        - Anthropic
        - Gemini
        - Azure OpenAI
        - Ollama
        - FakeChatModel
    """

    @abstractmethod
    async def stream(
        self,
        request: ProviderRequest,
    ) -> AsyncIterator[ProviderChunk]:
        """
        Streams the response incrementally.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:
        """
        Generates a complete response.
        """
        raise NotImplementedError
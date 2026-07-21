from abc import ABC, abstractmethod

from app.application.ai.ports.chat_provider import ChatProvider


class ChatProviderResolver(ABC):
    """
    Resolves the appropriate chat model for a request.
    """

    @abstractmethod
    async def resolve(
        self,
    ) -> ChatProvider:
        raise NotImplementedError
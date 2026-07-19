from abc import ABC, abstractmethod

from app.application.ai.ports.chat_model import ChatModel


class ChatModelResolver(ABC):
    """
    Resolves the appropriate chat model for a request.
    """

    @abstractmethod
    async def resolve(
        self,
    ) -> ChatModel:
        raise NotImplementedError
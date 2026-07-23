from abc import ABC, abstractmethod

from app.domain.ai.models.chat_message import ChatMessage


class ContextProvider(ABC):

    @abstractmethod
    async def get_messages(
        self,
    ) -> list[ChatMessage]:
        ...
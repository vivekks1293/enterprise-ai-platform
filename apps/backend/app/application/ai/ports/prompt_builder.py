from abc import ABC, abstractmethod

from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest


class PromptBuilder(ABC):

    @abstractmethod
    async def build(
        self,
        *,
        messages: list[ChatMessage],
    ) -> ChatRequest:
        raise NotImplementedError
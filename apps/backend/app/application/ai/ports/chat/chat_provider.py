from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncIterator

from app.application.ai.dto.chat_chunk import ChatChunk
from app.application.ai.dto.chat_request import ChatRequest
from app.application.ai.dto.chat_response import ChatResponse


class ChatProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        ...

    @abstractmethod
    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatChunk]:
        ...
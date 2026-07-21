from collections.abc import AsyncIterator

from app.application.ai.ports.chat_provider import ChatProvider
from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.chat_response import ChatResponse
from app.infrastructure.ai.langchain.client.langchain_chat_client import (
    LangChainChatClient,
)


class OpenAIChatProvider(ChatProvider):
    """
    ChatProvider implementation backed by OpenAI via LangChain.
    """

    def __init__(
        self,
        chat_client: LangChainChatClient,
    ) -> None:
        self._chat_client = chat_client

    async def generate(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        return await self._chat_client.generate(request)

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatChunk]:
        async for chunk in self._chat_client.stream(request):
            yield chunk
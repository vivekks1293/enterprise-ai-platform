from collections.abc import AsyncIterator

from langchain_core.language_models.chat_models import BaseChatModel

from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.chat_response import ChatResponse
from app.infrastructure.ai.langchain.mappers.LangChainMessageMapper import (
    LangChainMessageMapper,
)


class LangChainChatClient:
    """
    Infrastructure client responsible for interacting with LangChain chat models.
    """

    def __init__(
        self,
        chat_model: BaseChatModel,
    ) -> None:
        self._chat_model = chat_model

    async def generate(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Execute a non-streaming chat completion.
        """

        messages = LangChainMessageMapper.to_langchain(request.messages)

        response = await self._chat_model.ainvoke(messages)

        return ChatResponse(
            content=response.content,
        )

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatChunk]:
        """
        Execute a streaming chat completion.
        """

        messages = LangChainMessageMapper.to_langchain(request.messages)

        async for chunk in self._chat_model.astream(messages):

            if not chunk.content:
                continue

            yield ChatChunk(
                content=chunk.content,
                is_final=False,
            )

        yield ChatChunk(
            content="",
            is_final=True,
        )
from collections.abc import AsyncIterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessageChunk

from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.chat_response import ChatResponse
from app.domain.ai.models.chat_usage import ChatUsage
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

        messages = self._map_messages(request)

        chat_model = self._chat_model.bind(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        response = await chat_model.ainvoke(messages)

        return ChatResponse(
            content=self._extract_text(response.content),
            usage=self._extract_usage(response),
        )

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[ChatChunk]:
        """
        Execute a streaming chat completion.
        """

        messages = self._map_messages(request)

        chat_model = self._chat_model.bind(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        usage: ChatUsage | None = None

        async for chunk in chat_model.astream(messages):

            if not isinstance(chunk, AIMessageChunk):
                continue

            usage = self._extract_usage(chunk) or usage
            text = self._extract_text(chunk.content)

            if not text:
                continue

            yield ChatChunk(
                content=text,
                is_final=False,
            )

        yield ChatChunk(
            content="",
            is_final=True,
            usage=usage,
        )

    @staticmethod
    def _extract_usage(message: object) -> ChatUsage | None:
        usage_metadata = getattr(message, "usage_metadata", None)
        if isinstance(usage_metadata, dict):
            usage = ChatUsage(
                prompt_tokens=usage_metadata.get("input_tokens"),
                completion_tokens=usage_metadata.get("output_tokens"),
                total_tokens=usage_metadata.get("total_tokens"),
            )
            if any(value is not None for value in (
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )):
                return usage

        response_metadata = getattr(message, "response_metadata", None)
        if isinstance(response_metadata, dict):
            token_usage = response_metadata.get("token_usage")
            if isinstance(token_usage, dict):
                usage = ChatUsage(
                    prompt_tokens=token_usage.get("prompt_tokens"),
                    completion_tokens=token_usage.get("completion_tokens"),
                    total_tokens=token_usage.get("total_tokens"),
                )
                if any(value is not None for value in (
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    usage.total_tokens,
                )):
                    return usage

        return None

    @staticmethod
    def _map_messages(
        request: ChatRequest,
    ):
        """
        Convert domain messages into LangChain messages.
        """

        return LangChainMessageMapper.to_langchain(
            request.messages,
        )

    @staticmethod
    def _extract_text(
        content: object,
    ) -> str:
        """
        Extract plain text from a LangChain response.

        Multimodal responses are intentionally not supported yet.
        """

        if isinstance(content, str):
            return content

        raise ValueError(
            "Only text responses are currently supported."
        )
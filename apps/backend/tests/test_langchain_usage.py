import asyncio

from langchain_core.messages import AIMessage, AIMessageChunk

from app.domain.ai.models.chat_request import ChatRequest
from app.infrastructure.ai.langchain.client.langchain_chat_client import (
    LangChainChatClient,
)


class StubChatModel:
    def __init__(self, response, chunks):
        self.response = response
        self.chunks = chunks
        self.bound_kwargs = None

    async def ainvoke(self, messages):
        return self.response

    def bind(self, **kwargs):
        self.bound_kwargs = kwargs
        return self

    async def astream(self, messages):
        for chunk in self.chunks:
            yield chunk


def request() -> ChatRequest:
    return ChatRequest(messages=[])


def test_stream_extracts_usage_from_final_usage_chunk():
    model = StubChatModel(
        response=AIMessage(content="unused"),
        chunks=[
            AIMessageChunk(content="answer"),
            AIMessageChunk(
                content="",
                usage_metadata={
                    "input_tokens": 12,
                    "output_tokens": 4,
                    "total_tokens": 16,
                },
            ),
        ],
    )

    chunks = asyncio.run(_collect_stream(LangChainChatClient(model), request()))

    assert chunks[0].content == "answer"
    assert chunks[-1].is_final is True
    assert chunks[-1].usage.prompt_tokens == 12
    assert chunks[-1].usage.completion_tokens == 4
    assert chunks[-1].usage.total_tokens == 16


def test_stream_without_usage_preserves_unknown_usage():
    model = StubChatModel(
        response=AIMessage(content="unused"),
        chunks=[AIMessageChunk(content="answer")],
    )

    chunks = asyncio.run(_collect_stream(LangChainChatClient(model), request()))

    assert chunks[-1].usage is None


def test_normal_completion_extracts_usage():
    model = StubChatModel(
        response=AIMessage(
            content="answer",
            usage_metadata={
                "input_tokens": 8,
                "output_tokens": 3,
                "total_tokens": 11,
            },
        ),
        chunks=[],
    )

    response = asyncio.run(LangChainChatClient(model).generate(request()))

    assert response.usage.prompt_tokens == 8
    assert response.usage.completion_tokens == 3
    assert response.usage.total_tokens == 11


async def _collect_stream(client, chat_request):
    return [chunk async for chunk in client.stream(chat_request)]
import asyncio
from collections.abc import AsyncIterator

from app.application.ai.contracts.provider_chunk import ProviderChunk
from app.application.ai.contracts.provider_request import ProviderRequest
from app.application.ai.contracts.provider_response import ProviderResponse
from app.application.ai.ports.chat_model import ChatModel


class FakeChatModel(ChatModel):
    """
    Fake chat model used for local development,
    integration testing and UI development.
    """

    async def stream(
        self,
        request: ProviderRequest,
    ) -> AsyncIterator[ProviderChunk]:

        response = (
            "Hello! This is a fake response generated "
            "by the FakeChatModel."
        )

        for word in response.split():

            await asyncio.sleep(0.08)

            yield ProviderChunk(
                content=f"{word} "
            )

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:

        return ProviderResponse(
            content=(
                "Hello! This is a fake response generated "
                "by the FakeChatModel."
            )
        )
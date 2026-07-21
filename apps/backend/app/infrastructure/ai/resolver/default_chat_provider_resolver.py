from app.application.ai.ports.chat_provider import ChatProvider
from app.application.ai.ports.chat_provider_resolver import (
    ChatProviderResolver,
)


class DefaultChatProviderResolver(ChatProviderResolver):
    """
    Returns the application's configured chat provider.
    """

    def __init__(
        self,
        chat_provider: ChatProvider,
    ) -> None:
        self._chat_provider = chat_provider

    async def resolve(
        self,
    ) -> ChatProvider:
        return self._chat_provider
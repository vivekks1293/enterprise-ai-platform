from fastapi import Depends
from langchain_openai import ChatOpenAI

from app.application.ai.ports.chat_provider import ChatProvider
from app.application.ai.ports.chat_provider_resolver import ChatProviderResolver
from app.core.config.settings import settings
from app.infrastructure.ai.langchain.client.langchain_chat_client import (
    LangChainChatClient,
)
from app.infrastructure.ai.providers.openai.openai_chat_provider import (
    OpenAIChatProvider,
)
from app.infrastructure.ai.resolver.default_chat_provider_resolver import (
    DefaultChatProviderResolver,
)


def get_chat_provider() -> ChatProvider:
    chat_model = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        temperature=settings.openai_temperature,
        max_tokens=settings.openai_max_tokens,
    )

    chat_client = LangChainChatClient(chat_model)

    return OpenAIChatProvider(chat_client)


def get_chat_provider_resolver(
    chat_provider: ChatProvider = Depends(get_chat_provider),
) -> ChatProviderResolver:
    return DefaultChatProviderResolver(chat_provider)
from fastapi import Depends

from app.application.ai.ports.chat_model import ChatModel
from app.application.ai.ports.chat_model_resolver import ChatModelResolver
from app.infrastructure.ai.fake.fake_chat_model import FakeChatModel
from app.infrastructure.ai.resolver.default_chat_model_resolver import (
    DefaultChatModelResolver,
)


def get_chat_model() -> ChatModel:
    """
    Returns the configured chat model.
    """

    return FakeChatModel()


def get_chat_model_resolver(
    chat_model: ChatModel = Depends(get_chat_model),
) -> ChatModelResolver:
    """
    Returns the application's chat model resolver.
    """

    return DefaultChatModelResolver(chat_model)
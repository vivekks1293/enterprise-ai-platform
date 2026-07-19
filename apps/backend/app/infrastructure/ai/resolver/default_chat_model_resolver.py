from app.application.ai.ports.chat_model import ChatModel
from app.application.ai.ports.chat_model_resolver import ChatModelResolver


class DefaultChatModelResolver(ChatModelResolver):
    """
    Returns the application's default chat model.
    """

    def __init__(
        self,
        chat_model: ChatModel,
    ) -> None:
        self._chat_model = chat_model

    async def resolve(
        self,
    ) -> ChatModel:
        return self._chat_model
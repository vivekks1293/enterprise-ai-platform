from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from app.domain.ai.enums.message_role import MessageRole
from app.domain.ai.models.chat_message import ChatMessage


class LangChainMessageMapper:
    """Maps between domain chat messages and LangChain messages."""

    @staticmethod
    def to_langchain(
        messages: list[ChatMessage],
    ) -> list[BaseMessage]:
        """
        Convert domain chat messages into LangChain messages.
        """

        langchain_messages: list[BaseMessage] = []

        for message in messages:
            match message.role:

                case MessageRole.SYSTEM:
                    langchain_messages.append(
                        SystemMessage(content=message.content)
                    )

                case MessageRole.USER:
                    langchain_messages.append(
                        HumanMessage(content=message.content)
                    )

                case MessageRole.ASSISTANT:
                    langchain_messages.append(
                        AIMessage(content=message.content)
                    )

                case _:
                    raise ValueError(
                        f"Unsupported message role: {message.role}"
                    )

        return langchain_messages

    @staticmethod
    def from_langchain(
        message: BaseMessage,
    ) -> ChatMessage:
        """
        Convert a LangChain message into a domain chat message.
        """

        if isinstance(message, SystemMessage):
            role = MessageRole.SYSTEM

        elif isinstance(message, HumanMessage):
            role = MessageRole.USER

        elif isinstance(message, AIMessage):
            role = MessageRole.ASSISTANT

        else:
            raise ValueError(
                f"Unsupported LangChain message type: {type(message).__name__}"
            )

        return ChatMessage(
            role=role,
            content=message.content,
        )
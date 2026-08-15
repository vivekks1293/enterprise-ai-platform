from app.domain.ai.models.chat_message import ChatMessage


class RetrievalQueryBuilder:
    """
    Builds a retrieval query using the current user prompt
    and recent conversation context.
    """

    MAX_HISTORY_MESSAGES = 4

    @classmethod
    def build(
        cls,
        *,
        messages: list[ChatMessage],
        user_prompt: str,
    ) -> str:

        history = [
            message
            for message in messages[:-1]
            if message.content.strip()
        ]

        recent_history = history[-cls.MAX_HISTORY_MESSAGES:]

        if not recent_history:
            return user_prompt

        context = "\n".join(
            f"{message.role}: {message.content}"
            for message in recent_history
        )

        return (
            f"Conversation context:\n"
            f"{context}\n\n"
            f"Current question:\n"
            f"{user_prompt}"
        )
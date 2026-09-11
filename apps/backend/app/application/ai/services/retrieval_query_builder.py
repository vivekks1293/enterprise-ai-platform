from app.domain.ai.models.chat_message import ChatMessage


class RetrievalQueryBuilder:
    """
    Builds a focused retrieval query for knowledge search.
    Focuses specifically on the current user prompt to prevent
    cross-turn query contamination and stale citation leakage.
    """

    @classmethod
    def build(
        cls,
        *,
        messages: list[ChatMessage],
        user_prompt: str,
    ) -> str:
        """
        Extracts the retrieval query scoped strictly to the current user prompt.
        """
        return user_prompt.strip()
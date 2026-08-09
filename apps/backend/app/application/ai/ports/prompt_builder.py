from abc import ABC, abstractmethod

from app.application.ai.dto.prompt_context import PromptContext
from app.domain.ai.models.chat_request import ChatRequest


class PromptBuilder(ABC):
    """
    Builds the final prompt sent to the LLM.
    """

    @abstractmethod
    async def build(
    self,
    context: PromptContext,
) -> ChatRequest:
        """
        Builds the final prompt for the LLM.
        """

        retrieved_context = "\n\n".join(
            chunk.content
            for chunk in context.retrieved_chunks
        )

        system_prompt = f"""
    You are an Enterprise AI Assistant.

    Answer ONLY using the supplied context.

    If the answer cannot be found in the context,
    respond that you do not have enough information.

    =========================
    Context
    =========================

    {retrieved_context}
    """

        messages = [
            ChatMessage(
                role="system",
                content=system_prompt,
            )
        ]

        messages.extend(context.messages)

        return ChatRequest(
            messages=messages,
        )
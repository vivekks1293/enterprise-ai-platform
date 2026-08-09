from app.application.ai.dto.prompt_context import PromptContext
from app.application.ai.ports.prompt_builder import PromptBuilder
from app.core.config.settings import settings
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.message_role import MessageRole


class DefaultPromptBuilder(PromptBuilder):
    """
    Default implementation responsible for constructing
    the final prompt sent to the LLM.
    """

    async def build(
        self,
        context: PromptContext,
    ) -> ChatRequest:
        """
        Builds the final ChatRequest by combining:
        - System prompt
        - Retrieved knowledge
        - Conversation history
        """

        # --------------------------------------------------
        # Build retrieved context
        # --------------------------------------------------

        retrieved_context = "\n\n".join(
            chunk.content
            for chunk in context.retrieved_chunks
        )

        # --------------------------------------------------
        # Build system prompt
        # --------------------------------------------------

        system_prompt = f"""
{settings.ai_system_prompt}

==================================================
Knowledge Context
==================================================

{retrieved_context}

==================================================
Instructions
==================================================

- Answer ONLY using the supplied knowledge context.
- If the answer is not available in the context,
  clearly state that you do not have enough information.
- Do not fabricate facts.
"""

        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt,
        )

        # --------------------------------------------------
        # Final ChatRequest
        # --------------------------------------------------

        return ChatRequest(
            messages=[
                system_message,
                *context.messages,
            ]
        )
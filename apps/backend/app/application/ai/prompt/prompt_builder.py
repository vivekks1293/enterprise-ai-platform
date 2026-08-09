from app.application.ai.dto.prompt_context import (
    PromptContext,
)


class PromptBuilder:
    """
    Builds the final prompt sent to the LLM.
    """

    def build_prompt(
        self,
        context: PromptContext,
    ) -> str:

        retrieved_context = "\n\n".join(
            chunk.content
            for chunk in context.retrieved_chunks
        )

        return f"""
You are an Enterprise AI Assistant.

Answer ONLY using the supplied context.

If the answer cannot be found, say you do not have enough information.

------------------------
Context
------------------------

{retrieved_context}

------------------------
Question
------------------------

{context.user_prompt}
"""
from app.application.ai.dto.prompt_context import PromptContext
from app.application.ai.ports.prompt_builder import PromptBuilder
from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
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
        Builds the final ChatRequest from system instructions, retrieved
        knowledge, conversation history, and the current user question.
        """

        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"""
{settings.ai_system_prompt}

GROUNDING RULES
- Use retrieved knowledge when answering knowledge-base questions.
- Do not invent facts not supported by the retrieved knowledge.
- If the retrieved knowledge only partially answers a question, state what
    is supported and what is not supported.
- Do not claim that information exists in the knowledge base when it does not.
- When the retrieved knowledge is insufficient, clearly state that the
    available knowledge is insufficient.
- Conversation history provides conversational context, but retrieved
  enterprise knowledge is authoritative for knowledge-base questions.
""".strip(),
        )

        retrieved_knowledge_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=self._format_retrieved_knowledge(
                context.retrieved_chunks,
            ),
        )

        conversation_history = context.messages[:-1]
        current_question_message = ChatMessage(
            role=MessageRole.USER,
            content=f"CURRENT QUESTION\n{context.user_prompt}",
        )

        return ChatRequest(
            messages=[
                system_message,
                retrieved_knowledge_message,
                *conversation_history,
                current_question_message,
            ]
        )

    @staticmethod
    def _format_retrieved_knowledge(
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        if not retrieved_chunks:
            return "RETRIEVED KNOWLEDGE\nNo retrieved knowledge is available."

        sources = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            page_number = (
                str(chunk.metadata.page_number)
                if chunk.metadata.page_number is not None
                else "Not available"
            )
            sources.append(
                f"""[Source {index}]
Document ID: {chunk.metadata.document_id}
Chunk ID: {chunk.metadata.chunk_id}
Filename: {chunk.metadata.filename}
Page: {page_number}
Score: {chunk.score}
Content:
{chunk.content}"""
            )

        return "RETRIEVED KNOWLEDGE\n\n" + "\n\n".join(sources)
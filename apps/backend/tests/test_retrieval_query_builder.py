from app.application.ai.services.retrieval_query_builder import RetrievalQueryBuilder
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.conversation.enums.message_role import MessageRole


def test_retrieval_query_is_strictly_scoped_to_current_prompt():
    messages = [
        ChatMessage(
            role=MessageRole.USER,
            content="who is Vivek",
        ),
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="Vivek Kumar Singh is a Senior Software Engineer with Angular and Python experience.",
        ),
        ChatMessage(
            role=MessageRole.USER,
            content="who is Harshita?",
        ),
    ]

    query = RetrievalQueryBuilder.build(
        messages=messages,
        user_prompt="who is Harshita?",
    )

    # Retrieval query must strictly be the current question, never polluted by prior answers
    assert query == "who is Harshita?"
    assert "Vivek" not in query
    assert "Conversation context" not in query


def test_retrieval_query_strips_surrounding_whitespace():
    messages = [
        ChatMessage(
            role=MessageRole.USER,
            content="   what are the enterprise deployment guidelines?   \n",
        )
    ]

    query = RetrievalQueryBuilder.build(
        messages=messages,
        user_prompt="   what are the enterprise deployment guidelines?   \n",
    )

    assert query == "what are the enterprise deployment guidelines?"


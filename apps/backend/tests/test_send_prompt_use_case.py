import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import UUID

from app.application.ai.dto.ai_stream_event import AIStreamEvent
from app.application.conversation.dto.send_prompt import SendPromptRequest
from app.application.conversation.use_cases.send_prompt import SendPromptUseCase
from app.domain.conversation.entities.conversation import Conversation
from app.domain.conversation.entities.message import Message
from app.domain.conversation.enums.message_role import MessageRole


CONVERSATION_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


class InMemoryConversationRepository:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.conversation = Conversation(
            id=CONVERSATION_ID,
            owner_id=OWNER_ID,
            title="Test conversation",
            created_at=now,
            updated_at=now,
        )
        self.touched = False

    async def get_by_id(self, conversation_id: UUID, owner_id: UUID):
        return self.conversation

    async def touch(self, conversation_id: UUID, updated_at: datetime) -> None:
        self.touched = True


class InMemoryMessageRepository:
    def __init__(self) -> None:
        self.messages: list[Message] = []

    async def save(self, message: Message) -> None:
        self.messages.append(message)

    async def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        return self.messages


class StubOrchestrator:
    async def respond(
        self,
        *,
        owner_id: UUID,
        messages,
    ) -> AsyncIterator[AIStreamEvent]:
        yield AIStreamEvent(type="token", content="Grounded ")
        yield AIStreamEvent(type="token", content="answer")
        yield AIStreamEvent(type="complete")


class StubUnitOfWork:
    def __init__(self) -> None:
        self.commit_count = 0

    async def commit(self) -> None:
        self.commit_count += 1


async def collect_events(use_case: SendPromptUseCase) -> list[AIStreamEvent]:
    return [
        event
        async for event in use_case.execute(
            SendPromptRequest(
                conversation_id=CONVERSATION_ID,
                owner_id=OWNER_ID,
                prompt="What is the answer?",
            )
        )
    ]


def test_streamed_response_is_persisted_as_one_assistant_message():
    conversation_repository = InMemoryConversationRepository()
    message_repository = InMemoryMessageRepository()
    unit_of_work = StubUnitOfWork()
    use_case = SendPromptUseCase(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        ai_orchestrator=StubOrchestrator(),
        unit_of_work=unit_of_work,
    )

    events = asyncio.run(collect_events(use_case))

    assert [event.type for event in events] == ["token", "token", "complete"]
    assert [message.role for message in message_repository.messages] == [
        MessageRole.USER,
        MessageRole.ASSISTANT,
    ]
    assert message_repository.messages[-1].content == "Grounded answer"
    assert conversation_repository.touched is True
    assert unit_of_work.commit_count == 2
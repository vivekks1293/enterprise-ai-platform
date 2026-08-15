import json

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import StreamingResponse

from app.application.ai.dto.ai_stream_event import (
    AIStreamEvent,
)
from app.application.conversation.dto.create_conversation import (
    CreateConversationRequest as CreateConversationDto,
)
from app.application.conversation.dto.get_conversation import (
    GetConversationRequest as GetConversationDto,
)
from app.application.conversation.dto.list_conversations import (
    ListConversationsRequest as ListConversationsDto,
)
from app.application.conversation.dto.send_prompt import (
    SendPromptRequest as SendPromptDto,
)
from app.application.conversation.use_cases.create_conversation import (
    CreateConversationUseCase,
)
from app.application.conversation.use_cases.get_conversation import (
    GetConversationUseCase,
)
from app.application.conversation.use_cases.list_conversations import (
    ListConversationsUseCase,
)
from app.application.conversation.use_cases.send_prompt import (
    SendPromptUseCase,
)
from app.core.dependencies.authentication import get_current_user
from app.delivery.api.dependencies.conversation import (
    get_create_conversation_use_case,
    get_get_conversation_use_case,
    get_list_conversations_use_case,
    get_send_prompt_use_case,
)
from app.delivery.api.schemas.conversation import (
    ConversationResponse,
    ConversationSummaryResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    MessageResponse,
    SendPromptRequest,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=CreateConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_user),
    use_case: CreateConversationUseCase = Depends(
        get_create_conversation_use_case,
    ),
):
    result = await use_case.execute(
        CreateConversationDto(
            owner_id=current_user.id,
            title=request.title,
        )
    )

    return CreateConversationResponse(
        id=result.id,
        title=result.title,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get(
    "",
    response_model=list[ConversationSummaryResponse],
)
async def list_conversations(
    current_user=Depends(get_current_user),
    use_case: ListConversationsUseCase = Depends(
        get_list_conversations_use_case,
    ),
):
    result = await use_case.execute(
        ListConversationsDto(
            owner_id=current_user.id,
        )
    )

    return [
        ConversationSummaryResponse(
            id=item.id,
            title=item.title,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in result.conversations
    ]


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
    conversation_id=Path(...),
    current_user=Depends(get_current_user),
    use_case: GetConversationUseCase = Depends(
        get_get_conversation_use_case,
    ),
):
    conversation = await use_case.execute(
        GetConversationDto(
            owner_id=current_user.id,
            conversation_id=conversation_id,
        )
    )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
            )
            for message in conversation.messages
        ],
    )


def _serialize_ai_event(
    event: AIStreamEvent,
) -> str:
    """
    Converts an application AI stream event
    into an SSE message.
    """

    if event.type == "token":
        data = {
            "content": event.content,
        }

    elif event.type == "citations":
        data = {
            "citations": [
                {
                    "citation_id": citation.citation_id,
                    "document_id": str(citation.document_id),
                    "chunk_id": citation.chunk_id,
                    "filename": citation.filename,
                    "page_number": citation.page_number,
                    "similarity_score": citation.similarity_score,
                }
                for citation in (event.citations or [])
            ],
        }

    elif event.type == "complete":
        data = {}

    else:
        raise ValueError(
            f"Unsupported AI stream event type: {event.type}"
        )

    return (
        f"event: {event.type}\n"
        f"data: {json.dumps(data)}\n\n"
    )


async def _stream_ai_events(
    stream,
):
    """
    Serializes application AI events into SSE messages.
    """

    async for event in stream:
        yield _serialize_ai_event(event)


@router.post(
    "/{conversation_id}/messages",
    response_class=StreamingResponse,
)
async def send_prompt(
    request: SendPromptRequest,
    conversation_id=Path(...),
    current_user=Depends(get_current_user),
    use_case: SendPromptUseCase = Depends(
        get_send_prompt_use_case,
    ),
):
    stream = use_case.execute(
        SendPromptDto(
            owner_id=current_user.id,
            conversation_id=conversation_id,
            prompt=request.prompt,
        )
    )

    return StreamingResponse(
        _stream_ai_events(stream),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
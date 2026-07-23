from fastapi import Depends

from app.application.ai.ports.chat_provider_resolver import ChatProviderResolver
from app.application.common.ports.unit_of_work import UnitOfWork
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
from app.core.dependencies.ai import (get_chat_provider_resolver, get_prompt_builder)
from app.application.ai.ports.prompt_builder import PromptBuilder
from app.core.dependencies.common import get_unit_of_work
from app.core.dependencies.conversation import (
    get_conversation_repository,
    get_message_repository,
)
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)
from app.domain.conversation.repositories.message_repository import (
    MessageRepository,
)

def get_create_conversation_use_case(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> CreateConversationUseCase:
    return CreateConversationUseCase(
        conversation_repository,
        unit_of_work,
    )

def get_list_conversations_use_case(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
) -> ListConversationsUseCase:
    return ListConversationsUseCase(
        conversation_repository,
    )

def get_get_conversation_use_case(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
) -> GetConversationUseCase:
    return GetConversationUseCase(
        conversation_repository,
        message_repository,
    )

def get_send_prompt_use_case(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
    chat_provider_resolver: ChatProviderResolver = Depends(
        get_chat_provider_resolver
    ),
    prompt_builder: PromptBuilder = Depends(
        get_prompt_builder
    ),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> SendPromptUseCase:
    return SendPromptUseCase(
        conversation_repository,
        message_repository,
        chat_provider_resolver,
        prompt_builder,
        unit_of_work,
    )
from fastapi import Depends
from langchain_openai import ChatOpenAI

from app.application.ai.orchestrator.ai_orchestrator import (
    AIOrchestrator,
)
from app.application.ai.ports.chat_provider import ChatProvider
from app.application.ai.ports.chat_provider_resolver import ChatProviderResolver
from app.application.ai.ports.prompt_builder import PromptBuilder
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.application.ai.services.default_prompt_builder import (
    DefaultPromptBuilder,
)
from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.application.knowledge.ports.keyword_store import KeywordStore
from app.application.knowledge.ports.reranker import Reranker
from app.core.config.settings import settings
from app.core.dependencies.knowledge import (
    get_embedding_provider,
    get_keyword_store,
    get_vector_store,
)
from app.infrastructure.ai.langchain.client.langchain_chat_client import (
    LangChainChatClient,
)
from app.infrastructure.ai.providers.openai.openai_chat_provider import (
    OpenAIChatProvider,
)
from app.infrastructure.ai.resolver.default_chat_provider_resolver import (
    DefaultChatProviderResolver,
)
from app.infrastructure.knowledge.rerank.cross_encoder_reranker import (
    CrossEncoderReranker,
)


def get_chat_provider() -> ChatProvider:

    chat_model = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        temperature=settings.openai_temperature,
        max_tokens=settings.openai_max_tokens,
    )

    chat_client = LangChainChatClient(chat_model)

    return OpenAIChatProvider(chat_client)


def get_chat_provider_resolver(
    chat_provider: ChatProvider = Depends(
        get_chat_provider,
    ),
) -> ChatProviderResolver:

    return DefaultChatProviderResolver(chat_provider)


def get_prompt_builder() -> PromptBuilder:

    return DefaultPromptBuilder()


def get_document_retrieval_service(
    embedding_provider: EmbeddingProvider = Depends(
        get_embedding_provider,
    ),
    vector_store: VectorStore = Depends(
        get_vector_store,
    ),
    keyword_store: KeywordStore = Depends(get_keyword_store),
) -> DocumentRetrievalService:

    return DocumentRetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        keyword_store=keyword_store,
        reranker=CrossEncoderReranker(),
    )


def get_ai_orchestrator(
    retrieval_service: DocumentRetrievalService = Depends(
        get_document_retrieval_service,
    ),
    prompt_builder: PromptBuilder = Depends(
        get_prompt_builder,
    ),
    chat_provider_resolver: ChatProviderResolver = Depends(
        get_chat_provider_resolver,
    ),
) -> AIOrchestrator:

    return AIOrchestrator(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        chat_provider_resolver=chat_provider_resolver,
    )

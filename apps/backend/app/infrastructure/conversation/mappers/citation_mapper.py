from app.domain.conversation.value_objects.citation import Citation
from app.infrastructure.conversation.models.message_citation_model import (
    MessageCitationModel,
)


def to_domain(
    model: MessageCitationModel,
) -> Citation:

    return Citation(
        document_id=model.document_id,
        chunk_id=model.chunk_id,
        chunk_index=model.chunk_index,
        page_number=model.page_number,
        similarity_score=model.similarity_score,
    )


def to_model(
    citation: Citation,
    message_id,
) -> MessageCitationModel:

    return MessageCitationModel(
        message_id=message_id,
        document_id=citation.document_id,
        chunk_id=citation.chunk_id,
        chunk_index=citation.chunk_index,
        page_number=citation.page_number,
        similarity_score=citation.similarity_score,
    )
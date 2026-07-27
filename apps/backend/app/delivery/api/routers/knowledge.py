from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.application.knowledge.dto.upload_document import (
    UploadDocumentRequest,
)
from app.application.knowledge.use_cases.upload_document import (
    UploadDocumentUseCase,
)
from app.core.dependencies.authentication import (
    get_current_user,
)
from app.delivery.api.adapters.upload_file_stream import (
    stream_upload_file,
)
from app.delivery.api.schemas.knowledge import (
    UploadDocumentResponse, DocumentSummaryResponse, DocumentResponse
)

from app.application.knowledge.dto.list_documents import (
    ListDocumentsRequest,
)
from app.application.knowledge.use_cases.list_documents import (
    ListDocumentsUseCase,
)

from app.delivery.dependencies.knowledge import (
    get_list_documents_use_case,
    get_upload_document_use_case,
    get_get_document_use_case,
    get_download_document_use_case,
    get_delete_document_use_case,
    get_ingest_document_use_case
)

from app.application.knowledge.dto.get_document import (
    GetDocumentRequest,
)
from app.application.knowledge.use_cases.get_document import (
    GetDocumentUseCase,
)
from fastapi.responses import StreamingResponse

from app.application.knowledge.dto.download_document import (
    DownloadDocumentRequest,
)
from app.application.knowledge.use_cases.download_document import (
    DownloadDocumentUseCase,
)

from app.application.knowledge.dto.delete_document import (
    DeleteDocumentRequest,
)
from app.application.knowledge.use_cases.delete_document import (
    DeleteDocumentUseCase,
)

from app.application.knowledge.dto.ingest_document import (
    IngestDocumentRequest,
)
from app.application.knowledge.use_cases.ingest_document import (
    IngestDocumentUseCase,
)

from app.delivery.api.schemas.knowledge import (
    IngestDocumentResponse,
    ParsedDocumentResponse,
    ParsedDocumentSectionResponse,
)

from uuid import UUID

from fastapi import Path

router = APIRouter(
    prefix="/documents",
    tags=["Knowledge"],
)


@router.post(
    "",
    response_model=UploadDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[
        UploadFile,
        File(...),
    ],
    current_user=Depends(get_current_user),
    use_case: UploadDocumentUseCase = Depends(
        get_upload_document_use_case,
    ),
):
    """
    Uploads a document to the Knowledge capability.
    """

    if file.size is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine uploaded file size.",
        )

    result = await use_case.execute(
        UploadDocumentRequest(
            owner_id=current_user.id,
            filename=file.filename or "",
            content_type=file.content_type or "",
            size_bytes=file.size,
            content=stream_upload_file(file),
        )
    )

    return UploadDocumentResponse(
        id=result.id,
        filename=result.filename,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        status=result.status,
        created_at=result.created_at,
    )


@router.get(
    "",
    response_model=list[DocumentSummaryResponse],
)
async def list_documents(
    current_user=Depends(get_current_user),
    use_case: ListDocumentsUseCase = Depends(
        get_list_documents_use_case,
    ),
):
    result = await use_case.execute(
        ListDocumentsRequest(
            owner_id=current_user.id,
        )
    )

    return [
        DocumentSummaryResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        for document in result.documents
    ]

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: UUID = Path(...),
    current_user=Depends(get_current_user),
    use_case: GetDocumentUseCase = Depends(
        get_get_document_use_case,
    ),
):
    result = await use_case.execute(
        GetDocumentRequest(
            owner_id=current_user.id,
            document_id=document_id,
        )
    )

    return DocumentResponse(
        id=result.id,
        filename=result.filename,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )

@router.get(
    "/{document_id}/download",
    response_class=StreamingResponse,
)
async def download_document(
    document_id: UUID = Path(...),
    current_user=Depends(get_current_user),
    use_case: DownloadDocumentUseCase = Depends(
        get_download_document_use_case,
    ),
):
    result = await use_case.execute(
        DownloadDocumentRequest(
            owner_id=current_user.id,
            document_id=document_id,
        )
    )

    return StreamingResponse(
        result.content,
        media_type=result.content_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{result.filename}"'
            )
        },
    )

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: UUID = Path(...),
    current_user=Depends(get_current_user),
    use_case: DeleteDocumentUseCase = Depends(
        get_delete_document_use_case,
    ),
) -> None:

    await use_case.execute(
        DeleteDocumentRequest(
            owner_id=current_user.id,
            document_id=document_id,
        )
    )

@router.post(
    "/{document_id}/ingest",
    response_model=IngestDocumentResponse,
)
async def ingest_document(
    document_id: UUID = Path(...),
    current_user=Depends(get_current_user),
    use_case: IngestDocumentUseCase = Depends(
        get_ingest_document_use_case,
    ),
):
    result = await use_case.execute(
        IngestDocumentRequest(
            owner_id=current_user.id,
            document_id=document_id,
        )
    )

    return IngestDocumentResponse(
        document_id=result.document_id,
        status=result.status,
        parsed_document=ParsedDocumentResponse(
            sections=[
                ParsedDocumentSectionResponse(
                    content=section.content,
                    metadata=section.metadata,
                )
                for section in result.parsed_document.sections
            ],
            metadata=result.parsed_document.metadata,
        ),
    )
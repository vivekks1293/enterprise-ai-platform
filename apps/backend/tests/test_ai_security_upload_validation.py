from uuid import UUID

import pytest

from app.application.knowledge.dto.upload_document import UploadDocumentRequest
from app.application.knowledge.use_cases.upload_document import (
    UploadDocumentUseCase,
)
from app.core.config.settings import settings


OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


async def _empty_content():
    return
    yield b""


def make_request(**overrides) -> UploadDocumentRequest:
    defaults = dict(
        owner_id=OWNER_ID,
        filename="policy.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        content=_empty_content(),
    )
    defaults.update(overrides)
    return UploadDocumentRequest(**defaults)


def test_oversized_document_is_rejected():
    request = make_request(
        size_bytes=settings.knowledge_upload_max_size_bytes + 1,
    )

    with pytest.raises(ValueError, match="maximum allowed upload size"):
        UploadDocumentUseCase._validate_request(request)


def test_document_within_size_limit_is_accepted():
    request = make_request(size_bytes=settings.knowledge_upload_max_size_bytes)

    UploadDocumentUseCase._validate_request(request)


def test_unsupported_file_type_is_rejected():
    request = make_request(filename="malware.exe")

    with pytest.raises(ValueError, match="Unsupported document type"):
        UploadDocumentUseCase._validate_request(request)


def test_empty_filename_is_rejected():
    request = make_request(filename="   ")

    with pytest.raises(ValueError, match="filename cannot be empty"):
        UploadDocumentUseCase._validate_request(request)


def test_zero_size_document_is_rejected():
    request = make_request(size_bytes=0)

    with pytest.raises(ValueError, match="size must be greater than zero"):
        UploadDocumentUseCase._validate_request(request)


def test_empty_content_type_is_rejected():
    request = make_request(content_type="  ")

    with pytest.raises(ValueError, match="content type cannot be empty"):
        UploadDocumentUseCase._validate_request(request)


def test_path_traversal_filename_does_not_escape_storage_prefix():
    document_id = UUID("22222222-2222-2222-2222-222222222222")

    storage_key = UploadDocumentUseCase._build_storage_key(
        owner_id=OWNER_ID,
        document_id=document_id,
        filename="../../etc/passwd.pdf",
    )

    assert storage_key == f"{OWNER_ID}/{document_id}.pdf"
    assert ".." not in storage_key

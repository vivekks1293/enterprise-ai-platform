from collections.abc import AsyncIterator

from fastapi import UploadFile


async def stream_upload_file(
    file: UploadFile,
    *,
    chunk_size: int = 1024 * 1024,
) -> AsyncIterator[bytes]:
    """
    Streams an uploaded file in chunks without loading
    the complete file into application memory.
    """

    while chunk := await file.read(chunk_size):
        yield chunk
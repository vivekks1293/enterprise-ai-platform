from enum import Enum


class DocumentStatus(str, Enum):

    UPLOADING = "uploading"

    AVAILABLE = "available"

    INDEXING = "indexing"

    INDEXED = "indexed"

    FAILED = "failed"
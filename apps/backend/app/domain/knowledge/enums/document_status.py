from enum import Enum


class DocumentStatus(str, Enum):
    """
    Represents the lifecycle state of a knowledge document.
    """

    UPLOADING = "uploading"
    AVAILABLE = "available"
    FAILED = "failed"


class DocumentStatus(str, Enum):
    """
    Represents the lifecycle state of a knowledge document.
    """

    UPLOADING = "uploading"
    AVAILABLE = "available"

    PROCESSING = "processing"
    PROCESSED = "processed"

    FAILED = "failed"

from enum import Enum


class DocumentStatus(str, Enum):
    """
    Represents the lifecycle of a knowledge document.
    """

    UPLOADING = "uploading"

    AVAILABLE = "available"

    INDEXING = "indexing"

    INDEXED = "indexed"

    FAILED = "failed"
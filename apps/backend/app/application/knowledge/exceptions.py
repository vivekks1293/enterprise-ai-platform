class DocumentNotFoundError(Exception):
    """
    Raised when a requested document does not exist
    or does not belong to the authenticated user.
    """

    def __init__(self) -> None:
        super().__init__("Document not found.")

class DocumentParsingError(Exception):
    """
    Raised when usable textual content cannot be extracted
    from a document.
    """

    def __init__(
        self,
        message: str = "Unable to extract document content.",
    ) -> None:
        super().__init__(message)
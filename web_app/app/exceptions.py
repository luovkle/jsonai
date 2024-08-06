class ExceptionBase(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.__doc__)


class ChatGPTCompletionError(ExceptionBase):
    """An error occurred while generating the completion."""


class JSONExtractionError(ExceptionBase):
    """Failed to extract JSON from the completion."""


class CouldNotSaveDocumentError(ExceptionBase):
    """Could not save the document."""


class DocumentNotFoundError(ExceptionBase):
    """Exception raised for errors in finding the document."""

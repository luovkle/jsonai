class ChatGPTCompletionError(Exception):
    """An error occurred while generating the completion"""


class JSONExtractionError(Exception):
    """Failed to extract JSON from the completion"""


class CouldNotSaveDocumentError(Exception):
    """Could not save the document"""


class DocumentNotFoundError(Exception):
    """Exception raised for errors in finding the document"""

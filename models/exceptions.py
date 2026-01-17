"""
Exception hierarchy for model operations.
"""


class ModelError(Exception):
    """Base exception for all model-related errors"""
    pass


class ModelTimeoutError(ModelError):
    """Model request timed out"""
    pass


class ModelResponseError(ModelError):
    """Model returned invalid or empty response"""
    pass


class ModelServerError(ModelError):
    """Model server returned error status"""
    pass


class ModelConnectionError(ModelError):
    """Failed to connect to model server"""
    pass
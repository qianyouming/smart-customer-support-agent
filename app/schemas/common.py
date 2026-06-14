"""Common API schemas."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Simple error payload shape."""

    error: str

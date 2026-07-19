from datetime import datetime, timezone

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime = datetime.now(timezone.utc)
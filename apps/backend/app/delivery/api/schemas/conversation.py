from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

from datetime import datetime
from uuid import UUID


class ConversationSummaryResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

class SendPromptRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
    )

class CreateConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
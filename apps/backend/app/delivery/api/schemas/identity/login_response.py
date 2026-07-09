from pydantic import BaseModel, ConfigDict, Field

from app.delivery.api.schemas.identity.user_response import (
    UserResponseSchema,
)


class LoginResponseSchema(BaseModel):
    """
    HTTP response returned after successful authentication.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    access_token: str = Field(
        description="JWT access token.",
    )

    token_type: str = Field(
        description="Authentication scheme.",
        examples=["Bearer"],
    )

    expires_in: int = Field(
        description="Access token lifetime in seconds.",
        examples=[3600],
    )

    user: UserResponseSchema
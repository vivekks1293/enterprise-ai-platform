from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponseSchema(BaseModel):
    """
    HTTP response representing an authenticated user.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    email: EmailStr
    name: str
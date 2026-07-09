from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequestSchema(BaseModel):
    """
    HTTP request body for user authentication.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: EmailStr = Field(
        description="Registered email address.",
        examples=["admin@example.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password.",
        examples=["Admin@123"],
    )
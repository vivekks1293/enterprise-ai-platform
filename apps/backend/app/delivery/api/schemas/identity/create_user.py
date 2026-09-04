from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.domain.identity.entities.user import RoleType


class CreateUserRequestSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    username: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role_type: RoleType = Field(alias="roleType")
    role_type_name: str = Field(
        alias="roleTypeName",
        min_length=4,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_role_name(self):
        expected_name = {
            RoleType.ADMIN: "admin",
            RoleType.USER: "user",
        }[self.role_type]
        if self.role_type_name != expected_name:
            raise ValueError("roleTypeName must match roleType")
        return self


class CreateUserResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    username: EmailStr
    name: str
    role_type: RoleType = Field(alias="roleType")
    role_type_name: str = Field(alias="roleTypeName")
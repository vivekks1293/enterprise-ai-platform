from dataclasses import dataclass
from uuid import UUID

from app.domain.identity.entities.user import RoleType
from app.domain.identity.value_objects.email import Email


@dataclass(frozen=True, slots=True)
class CreateUserRequest:
    email: Email
    password: str
    role_type: RoleType
    role_type_name: str


@dataclass(frozen=True, slots=True)
class CreateUserResponse:
    id: UUID
    email: str
    name: str
    role_type: RoleType
    role_type_name: str
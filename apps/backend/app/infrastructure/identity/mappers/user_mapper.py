from app.domain.identity.entities.user import User
from app.domain.identity.value_objects.email import Email

from app.infrastructure.identity.models.user_model import UserModel


def to_domain(model: UserModel) -> User:
    """
    Converts a SQLAlchemy UserModel into a Domain User entity.
    """
    return User(
        id=model.id,
        email=Email(model.email),
        hashed_password=model.hashed_password,
        name=model.name,
        is_active=model.is_active,
        created_at=model.created_at,
        role_type=model.role_type,
        role_type_name=model.role_type_name,
    )


def to_model(entity: User) -> UserModel:
    """
    Converts a Domain User entity into a SQLAlchemy UserModel.
    """
    return UserModel(
        id=entity.id,
        email=str(entity.email),
        hashed_password=entity.hashed_password,
        name=entity.name,
        is_active=entity.is_active,
        created_at=entity.created_at,
        role_type=entity.role_type,
        role_type_name=entity.role_type_name,
    )
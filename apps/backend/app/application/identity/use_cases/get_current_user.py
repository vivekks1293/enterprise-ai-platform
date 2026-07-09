from app.application.identity.dto.user_summary import user_summary
from app.domain.identity.entities.user import User


class GetCurrentUserUseCase:
    """
    Return information about the authenticated user.
    """

    async def execute(
        self,
        user: User,
    ) -> user_summary:

        return user_summary(
            id=user.id,
            email=str(user.email),
            name=user.name,
        )
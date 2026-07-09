from fastapi import APIRouter, Depends, Response, status

from app.application.identity.dto.login_request import LoginRequest
from app.core.dependencies.identity import get_login_use_case
from app.core.dependencies.identity import get_logout_use_case
from app.application.identity.use_cases.login import LoginUseCase
from app.delivery.api.schemas.identity.login_request import LoginRequestSchema
from app.delivery.api.schemas.identity.login_response import LoginResponseSchema
from app.domain.identity.value_objects.email import Email


from app.application.identity.use_cases.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.identity.use_cases.logout import (
    LogoutUseCase,
)
from app.core.dependencies.authentication import get_current_user
from app.core.dependencies.identity import (
    get_current_user_use_case,
)
from app.domain.identity.entities.user import User
from app.delivery.api.schemas.identity.user_response import (
    UserResponseSchema,
)
from app.delivery.api.schemas.identity.user_response import (
    UserResponseSchema,
)
router = APIRouter(
    prefix="/identity",
    tags=["Identity"],
)


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user",
)
async def login(
    request: LoginRequestSchema,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponseSchema:

    response = await use_case.execute(
        LoginRequest(
            email=Email(request.email),
            password=request.password,
        )
    )

    return LoginResponseSchema.model_validate(response)

@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Get current authenticated user",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    use_case: GetCurrentUserUseCase = Depends(
        get_current_user_use_case
    ),
) -> UserResponseSchema:

    response = await use_case.execute(current_user)

    return UserResponseSchema.model_validate(response)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    current_user: User = Depends(get_current_user),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> Response:
    await use_case.execute()

    return Response()
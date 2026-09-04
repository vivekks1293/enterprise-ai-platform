from fastapi import APIRouter, Depends, Response, status

from app.application.identity.dto.login_request import LoginRequest
from app.application.identity.dto.create_user import CreateUserRequest
from app.core.dependencies.identity import get_login_use_case
from app.core.dependencies.identity import get_create_user_use_case
from app.core.dependencies.identity import get_logout_use_case
from app.application.identity.use_cases.login import LoginUseCase
from app.application.identity.use_cases.create_user import CreateUserUseCase
from app.delivery.api.schemas.identity.login_request import LoginRequestSchema
from app.delivery.api.schemas.identity.login_response import LoginResponseSchema
from app.delivery.api.schemas.identity.create_user import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)
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
    "/users",
    response_model=CreateUserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create an application user",
)
async def create_user(
    request: CreateUserRequestSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> CreateUserResponseSchema:
    response = await use_case.execute(
        CreateUserRequest(
            email=Email(request.username),
            password=request.password,
            role_type=request.role_type,
            role_type_name=request.role_type_name,
        )
    )

    return CreateUserResponseSchema(
        id=str(response.id),
        username=response.email,
        name=response.name,
        roleType=response.role_type,
        roleTypeName=response.role_type_name,
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
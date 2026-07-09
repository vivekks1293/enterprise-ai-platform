class LogoutUseCase:
    """
    Complete the logout workflow.

    For stateless JWT authentication, logout is currently a no-op.

    Future implementations may revoke refresh tokens,
    invalidate sessions, or blacklist access tokens.
    """

    async def execute(self) -> None:
        return None
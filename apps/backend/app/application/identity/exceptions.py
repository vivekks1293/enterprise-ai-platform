class IdentityError(Exception):
    """
    Base exception for the Identity application.
    """


class InvalidCredentialsError(IdentityError):
    """
    Raised when authentication credentials are invalid.
    """


class InactiveUserError(IdentityError):
    """
    Raised when an inactive user attempts to authenticate.
    """


class InvalidTokenError(IdentityError):
    """
    Raised when an authentication token is invalid or expired.
    """

class UserNotFoundError(IdentityError):
    """
    Raised when an authentication token is invalid or expired.
    """
from bcrypt import checkpw, gensalt, hashpw

from app.application.identity.ports.password_hasher import PasswordHasher


class BCryptPasswordHasher(PasswordHasher):
    """
    BCrypt implementation of the PasswordHasher port.
    """

    def hash(self, password: str) -> str:
        return hashpw(
            password.encode("utf-8"),
            gensalt(),
        ).decode("utf-8")

    def verify(
        self,
        password: str,
        hashed_password: str,
    ) -> bool:
        return checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
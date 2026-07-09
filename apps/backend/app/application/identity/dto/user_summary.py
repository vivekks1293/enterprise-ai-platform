from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class user_summary:
    """
    Authenticated user information exposed by application use cases.
    """

    id: UUID
    email: str
    name: str
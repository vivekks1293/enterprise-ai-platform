from dataclasses import dataclass
import re


_EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()

        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("Invalid email address.")

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
from dataclasses import dataclass
# from uuid import UUID
from citation import Citation

@dataclass
class AIResponse:

    answer: str

    citations: list[Citation]
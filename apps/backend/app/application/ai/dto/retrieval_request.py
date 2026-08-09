from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
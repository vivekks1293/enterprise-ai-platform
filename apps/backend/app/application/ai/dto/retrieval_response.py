from pydantic import BaseModel


class RetrievedChunkResponse(BaseModel):
    content: str
    score: float
    filename: str
    chunk_index: int


class RetrievalResponse(BaseModel):
    chunks: list[RetrievedChunkResponse]
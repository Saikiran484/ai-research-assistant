from pydantic import BaseModel, Field


class RagRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=5, ge=1, le=10)


class RagSource(BaseModel):
    text: str
    filename: str | None = None
    document_id: str | None = None
    distance: float


class RagResponse(BaseModel):
    question: str
    answer: str
    sources: list[RagSource]

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    id: str
    text: str
    metadata: dict
    distance: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]


class IndexResponse(BaseModel):
    document_id: str
    chunks_indexed: int

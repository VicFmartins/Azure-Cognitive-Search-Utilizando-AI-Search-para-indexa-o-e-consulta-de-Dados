from pydantic import BaseModel, Field


class SearchDocument(BaseModel):
    id: str
    title: str
    category: str
    tags: list[str] = Field(default_factory=list)
    content: str
    source: str | None = None


class IndexDocumentsRequest(BaseModel):
    documents: list[SearchDocument]


class SearchRequest(BaseModel):
    query: str
    top: int = Field(default=5, ge=1, le=20)
    category: str | None = None
    tags: list[str] = Field(default_factory=list)


class SearchHit(BaseModel):
    id: str
    title: str
    category: str
    tags: list[str]
    score: float
    highlights: list[str]
    source: str | None = None


class SearchResponse(BaseModel):
    query: str
    total_hits: int
    hits: list[SearchHit]


class IndexStatsResponse(BaseModel):
    documents: int
    unique_terms: int
    categories: list[str]

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import IndexResponse, SearchRequest, SearchResponse, SearchResultItem
from app.services import index_service

router = APIRouter(tags=["search"])


@router.post("/documents/{document_id}/index", response_model=IndexResponse)
def index_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    result = index_service.index_document(db, document_id)
    return IndexResponse(**result)


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    results = index_service.search_documents(request.query, request.limit)
    return SearchResponse(
        query=request.query,
        results=[SearchResultItem(**item) for item in results],
    )

from fastapi import APIRouter

from app.schemas.rag import RagRequest, RagResponse, RagSource
from app.services import rag_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ask", response_model=RagResponse)
def ask(request: RagRequest):
    result = rag_service.ask(request.question, request.limit)
    return RagResponse(**result)

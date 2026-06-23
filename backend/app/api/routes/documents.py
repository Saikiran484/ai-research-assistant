import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await document_service.create_document(db, file)


@router.get("", response_model=DocumentListResponse)
def get_documents(db: Session = Depends(get_db)):
    documents = document_service.list_documents(db)
    return DocumentListResponse(
        items=documents,
        total=len(documents),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return document_service.get_document(db, document_id)


@router.post("/{document_id}/parse", response_model=DocumentResponse)
def parse_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return document_service.parse_document(db, document_id)

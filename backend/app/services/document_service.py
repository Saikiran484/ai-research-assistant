import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.services import parser_service

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _validate_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {allowed}",
        )
    return extension


async def create_document(db: Session, file: UploadFile) -> Document:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    extension = _validate_extension(file.filename)
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb} MB",
        )

    stored_filename = f"{uuid.uuid4()}{extension}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.upload_dir / stored_filename
    file_path.write_bytes(content)

    document = Document(
        filename=stored_filename,
        original_filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return parse_document(db, document.id)


def parse_document(db: Session, document_id: uuid.UUID) -> Document:
    document = get_document(db, document_id)
    document.status = DocumentStatus.PROCESSING
    document.parse_error = None
    db.commit()

    try:
        file_path = settings.upload_dir / document.filename
        document.extracted_text = parser_service.extract_text(file_path)
        document.status = DocumentStatus.READY
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        document.parse_error = str(exc)[:500]
        document.extracted_text = None

    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def get_document(db: Session, document_id: uuid.UUID) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document

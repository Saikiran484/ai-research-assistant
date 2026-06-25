import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.services import chunk_service, ollama_service
from app.services.document_service import get_document
from app.vector.chroma_store import get_collection


def index_document(db: Session, document_id: uuid.UUID) -> dict:
    document = get_document(db, document_id)

    if document.status != DocumentStatus.READY or not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be parsed before indexing",
        )

    chunks = chunk_service.chunk_text(document.extracted_text)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text chunks to index",
        )

    collection = get_collection()

    # Remove old chunks for this document before re-indexing
    try:
        collection.delete(where={"document_id": str(document_id)})
    except Exception:
        pass

    ids: list[str] = []
    embeddings: list[list[float]] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for index, chunk in enumerate(chunks):
        ids.append(f"{document_id}-{index}")
        embeddings.append(ollama_service.get_embedding(chunk))
        documents.append(chunk)
        metadatas.append({
            "document_id": str(document_id),
            "original_filename": document.original_filename,
            "chunk_index": index,
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return {"document_id": str(document_id), "chunks_indexed": len(chunks)}


def search_documents(query: str, limit: int = 5) -> list[dict]:
    collection = get_collection()
    query_embedding = ollama_service.get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        include=["documents", "metadatas", "distances"],
    )

    items: list[dict] = []
    if not results["ids"] or not results["ids"][0]:
        return items

    for i, chunk_id in enumerate(results["ids"][0]):
        items.append({
            "id": chunk_id,
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return items

from app.core.config import settings


def chunk_text(text: str) -> list[str]:
    chunk_size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap

    return chunks

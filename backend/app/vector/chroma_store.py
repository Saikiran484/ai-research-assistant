import chromadb

from app.core.config import settings

_client = None


def get_chroma_client() -> chromadb.HttpClient:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
    return _client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=settings.chroma_collection)


def check_chroma_connection() -> bool:
    try:
        get_chroma_client().heartbeat()
        return True
    except Exception:
        return False

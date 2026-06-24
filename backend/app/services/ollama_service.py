import httpx

from app.core.config import settings


def check_ollama_connection() -> bool:
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def get_embedding(text: str) -> list[float]:
    response = httpx.post(
        f"{settings.ollama_base_url}/api/embeddings",
        json={"model": settings.ollama_embedding_model, "prompt": text},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def generate(prompt: str, system: str | None = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={"model": settings.ollama_model, "messages": messages, "stream": False},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

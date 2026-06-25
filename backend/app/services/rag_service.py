from app.schemas.rag import RagSource
from app.services import index_service, ollama_service

RAG_SYSTEM = """You are a research assistant. Answer ONLY using the provided context.
If the context does not contain enough information, say you don't know.
Cite source filenames when relevant. Be concise and accurate."""


def ask(question: str, limit: int = 5) -> dict:
    chunks = index_service.search_documents(question, limit)

    if not chunks:
        return {
            "question": question,
            "answer": "No indexed documents found. Upload and index documents first.",
            "sources": [],
        }

    context_parts = []
    sources: list[RagSource] = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        filename = meta.get("original_filename", "unknown")
        context_parts.append(f"[{filename}]\n{chunk['text']}")
        sources.append(RagSource(
            text=chunk["text"],
            filename=filename,
            document_id=meta.get("document_id"),
            distance=chunk["distance"],
        ))

    context = "\n\n---\n\n".join(context_parts)
    prompt = f"""Context from uploaded documents:

{context}

Question: {question}

Answer:"""

    answer = ollama_service.generate(prompt, system=RAG_SYSTEM)
    return {"question": question, "answer": answer, "sources": sources}

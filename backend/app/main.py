from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, chat, documents, rag, search
from app.core.config import settings
from app.db.session import check_db_connection
from app.vector.chroma_store import check_chroma_connection
from app.services import ollama_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agent.router)


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    db_connected = check_db_connection()
    chroma_connected = check_chroma_connection()
    ollama_connected = ollama_service.check_ollama_connection()
    all_ok = db_connected and chroma_connected
    return {
        "status": "healthy" if all_ok else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "chroma": "connected" if chroma_connected else "disconnected",
        "ollama": "connected" if ollama_connected else "disconnected",
    }

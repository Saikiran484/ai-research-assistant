from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import documents, search
from app.core.config import settings
from app.db.session import check_db_connection
from app.vector.chroma_store import check_chroma_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents.router)
app.include_router(search.router)


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API",
    }


@app.get("/health")
def health():
    db_connected = check_db_connection()
    chroma_connected = check_chroma_connection()
    all_ok = db_connected and chroma_connected
    return {
        "status": "healthy" if all_ok else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "chroma": "connected" if chroma_connected else "disconnected",
    }

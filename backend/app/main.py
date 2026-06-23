from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import documents
from app.core.config import settings
from app.db.session import check_db_connection


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


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API",
    }


@app.get("/health")
def health():
    db_connected = check_db_connection()
    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
    }

from fastapi import FastAPI

from app.db.session import check_db_connection

app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0",
)


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

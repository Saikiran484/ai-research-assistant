from fastapi import FastAPI

app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API"
    }
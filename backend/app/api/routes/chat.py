from fastapi import APIRouter

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ollama_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = ollama_service.generate(request.prompt, request.system)
    return ChatResponse(model=settings.ollama_model, response=response)

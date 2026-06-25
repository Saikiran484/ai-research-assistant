from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.research_agent import run_agent
from app.db.session import get_db
from app.schemas.agent import AgentRequest, AgentResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentResponse)
def agent_run(request: AgentRequest, db: Session = Depends(get_db)):
    result = run_agent(db, request.query)
    return AgentResponse(query=result["query"], answer=result["answer"])

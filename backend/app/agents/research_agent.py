import json

from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import document_service, index_service

REACT_PROMPT = PromptTemplate.from_template("""You are a research assistant with access to tools.
Answer questions about uploaded research documents.

Tools: {tools}
Tool names: {tool_names}

Use this format:
Thought: think about what to do
Action: tool name
Action Input: input for the tool
Observation: tool result
... (repeat as needed)
Thought: I have enough information
Final Answer: your answer to the user

Question: {input}
{agent_scratchpad}""")


def _build_tools(db: Session):
    @tool
    def search_documents(query: str) -> str:
        """Search indexed documents semantically. Input: search query string."""
        results = index_service.search_documents(query.strip(), limit=5)
        if not results:
            return "No matching chunks found."
        return json.dumps([{
            "text": r["text"][:500],
            "filename": (r.get("metadata") or {}).get("original_filename"),
            "distance": r["distance"],
        }])

    @tool
    def list_uploaded_documents(_: str = "") -> str:
        """List all uploaded documents with status. No input required."""
        docs = document_service.list_documents(db)
        if not docs:
            return "No documents uploaded yet."
        return json.dumps([{
            "id": str(d.id),
            "filename": d.original_filename,
            "status": d.status.value,
        } for d in docs])

    return [search_documents, list_uploaded_documents]


def run_agent(db: Session, query: str) -> dict:
    llm = ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.2,
    )
    tools = _build_tools(db)
    agent = create_react_agent(llm, tools, REACT_PROMPT)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    result = executor.invoke({"input": query})
    return {"query": query, "answer": result.get("output", ""), "steps": result.get("intermediate_steps", [])}

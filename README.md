# AI Research Assistant

A self-hosted, agentic RAG platform for document analysis, Q&A generation, and research intelligence.

**No paid APIs.** Everything runs locally using Ollama, ChromaDB, and PostgreSQL.

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Python, FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Vector Store | ChromaDB |
| LLM | Ollama (local) |
| Orchestration | LangChain |
| Frontend | Next.js (Phase 10) |
| Infra | Docker, GitHub Actions |

## Project Structure

```
ai-research-assistant/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py       # Environment-based settings
│   │   ├── db/
│   │   │   ├── base.py         # SQLAlchemy declarative base
│   │   │   └── session.py      # Engine, sessions, health check
│   │   ├── models/
│   │   │   └── document.py     # Document table model
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI application entry point
│   ├── alembic/                # Database migration scripts
│   ├── alembic.ini
│   ├── docker-entrypoint.sh    # Runs migrations, then starts API
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── venv/                # Local virtual environment (not committed)
├── docker-compose.yml       # API + PostgreSQL services
├── .env.example             # Template for environment variables
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- Git
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Phase 2+)

## Local Development (Phase 1)

### 1. Clone and enter the project

```bash
cd ai-research-assistant
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Verify

| Endpoint | URL | Expected response |
|----------|-----|-------------------|
| Root | http://localhost:8000/ | `{"message": "AI Research Assistant API"}` |
| Health | http://localhost:8000/health | `{"status": "healthy", "database": "connected"}` |
| API docs | http://localhost:8000/docs | Swagger UI |

## Docker + PostgreSQL (Phase 2)

Phase 2 runs the API and PostgreSQL together via Docker Compose.

### 1. Create your local environment file

```powershell
copy .env.example .env
```

### 2. Start all services

From the project root:

```powershell
docker compose up --build
```

**Expected:** Both `research-assistant-db` and `research-assistant-api` start. The API waits until PostgreSQL passes its health check.

### 3. Verify

| Check | Command / URL | Expected |
|-------|---------------|----------|
| Containers running | `docker compose ps` | `db` and `api` both `running` |
| API health | http://localhost:8000/health | `{"status":"healthy","database":"connected"}` |
| API docs | http://localhost:8000/docs | Swagger UI |

### 4. Stop services

```powershell
docker compose down
```

To remove the database volume as well:

```powershell
docker compose down -v
```

### Hybrid mode (DB in Docker, API locally)

Useful during development with hot-reload:

```powershell
docker compose up db -d
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API reads `DATABASE_URL` from `.env` (defaults to `localhost:5432`).

## SQLAlchemy Models + Migrations (Phase 3)

Phase 3 defines database tables as Python models and applies schema changes with Alembic.

### What was added

- `documents` table — stores uploaded file metadata (upload logic comes in Phase 4)
- Alembic migration history under `backend/alembic/versions/`
- Auto-migration on container start via `docker-entrypoint.sh`

### Docker (migrations run automatically)

```powershell
docker compose up --build
```

On startup, the API container runs `alembic upgrade head` before Uvicorn starts.

### Local development (run migrations manually)

```powershell
docker compose up db -d
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Useful Alembic commands

| Command | Purpose |
|---------|---------|
| `alembic current` | Show current migration revision |
| `alembic history` | List all migrations |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back one migration |

### Verify the table exists

```powershell
docker compose exec db psql -U postgres -d research_assistant -c "\dt"
```

**Expected:** `documents` table listed.

```powershell
docker compose exec db psql -U postgres -d research_assistant -c "\d documents"
```

**Expected:** Columns `id`, `filename`, `original_filename`, `content_type`, `file_size`, `status`, `created_at`, `updated_at`.

## Document Upload API (Phase 4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents` | Upload `.pdf`, `.docx`, or `.txt` (max 10 MB) |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}` | Get one document |

### Test via Swagger

1. `docker compose up --build -d`
2. Open http://localhost:8000/docs
3. Use **POST /documents** → upload a file
4. Use **GET /documents** to confirm it appears

### Test via curl

```powershell
curl -X POST "http://localhost:8000/documents" -F "file=@C:\path\to\file.txt"
curl http://localhost:8000/documents
```

## ChromaDB Vector Store (Phase 6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/{id}/index` | Chunk text + embed + store in ChromaDB |
| POST | `/search` | Semantic search over indexed chunks |

Upload auto-indexes after parsing (requires Ollama embedding model).

```powershell
docker compose up --build -d
```

ChromaDB runs at http://localhost:8001

## Ollama Integration (Phase 7)

Install [Ollama](https://ollama.com/) locally, then:

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Chat with local LLM |

`/health` reports `database`, `chroma`, and `ollama` status.

## RAG Pipeline (Phase 8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rag/ask` | Retrieve relevant chunks + generate grounded answer |

```powershell
curl -X POST http://localhost:8000/rag/ask -H "Content-Type: application/json" -d "{\"question\":\"What is in my documents?\"}"
```

## Agent Architecture (Phase 9)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent/run` | LangChain ReAct agent with search + list tools |

```powershell
curl -X POST http://localhost:8000/agent/run -H "Content-Type: application/json" -d "{\"query\":\"List my documents and summarize topics\"}"
```

## Next.js Frontend (Phase 10)

```powershell
# Option A: Docker
docker compose up --build -d
# Open http://localhost:3000

# Option B: Local dev
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local` if needed.

## Development Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Repository structure, FastAPI skeleton, health endpoint | Done |
| 2 | Docker + PostgreSQL | Done |
| 3 | SQLAlchemy models + Alembic migrations | Done |
| 4 | Document upload API | Done |
| 5 | PDF and DOCX parsing | Done |
| 6 | ChromaDB vector store | Done |
| 7 | Ollama integration | Done |
| 8 | RAG pipeline | Done |
| 9 | Agent architecture | Done |
| 10 | Next.js frontend | Done |

## License

TBD

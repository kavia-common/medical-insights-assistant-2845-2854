# medical-insights-assistant-2845-2854

Medical Insights Backend (FastAPI) - Ocean Professional theme.

Features:
- Patient Interview Agent: structured patient Q&A generation.
- Medical Advisor Agent: evidence-based suggestions via RAG (vector DB).
- REST endpoints for orchestration, patients, interviews, and OneDrive-synced file I/O.
- Modular, well-documented code with logging of agent activities.

Quick start:
1) Ensure environment variables are set (see medical_backend/.env.example).
2) Install dependencies:
   pip install -r medical_backend/requirements.txt
3) Run:
   uvicorn medical_backend.src.api.main:app --reload --host 0.0.0.0 --port 8000

Primary endpoints (see /docs):
- GET /                         -> Health check
- /patients/*                   -> Patient CRUD
- /interviews/*                 -> Interview CRUD and steps
- /agents/*                     -> Orchestration endpoints
- /files/*                      -> OneDrive/local file read/write

Notes:
- Vector DB URL/API key pulled from env. The client expects POST {VECTOR_DB_URL}/query.
- Storage directories are created at startup if missing.

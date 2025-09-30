# Medical Backend - Run Notes

- Default container port: 3001 (set via PORT env).
- Entrypoint module: medical_backend.src.api.main:app
- To run locally:
  - Install deps: pip install -r requirements.txt
  - Run with uvicorn directly:
    uvicorn medical_backend.src.api.main:app --reload --host 0.0.0.0 --port 8000
  - Or use the provided runner (defaults to PORT=3001):
    PORT=3001 python -m medical_backend.src.run_server

Environment variables (see .env.example):
- PORT, HOST, LOG_LEVEL, RELOAD, WORKERS
- ONEDRIVE_BASE_PATH, STORAGE_BASE_PATH
- VECTOR_DB_URL, VECTOR_DB_API_KEY
- CORS_ALLOW_ORIGINS

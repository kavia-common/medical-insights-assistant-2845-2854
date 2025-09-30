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
  - Defaults are set to writable paths under the workspace to avoid permission issues:
    - ONEDRIVE_BASE_PATH: ./var/onedrive
    - STORAGE_BASE_PATH: ./var/storage
  - Override these via env vars when deploying with mounted volumes.
- VECTOR_DB_URL, VECTOR_DB_API_KEY
- CORS_ALLOW_ORIGINS

Interview storage and session behavior:
- Interviews are stored as plain text files in the OneDrive Interview folder.
- Path: {ONEDRIVE_BASE_PATH}/Interview/{patient_id}.txt
- Agent-driven Interview Session (recommended):
  - POST /interview-session/{patient_id}/start { chief_complaint?, context? } -> returns initial questions
  - POST /interview-session/{patient_id}/answer { answer } -> returns next adaptive question(s)
  - POST /interview-session/{patient_id}/end -> writes full transcript to OneDrive as {patient_id}.txt
- File utilities (compatibility):
  - GET /interviews/{patient_id} -> fetch text
  - DELETE /interviews/{patient_id} -> remove file
  - POST /agents/advisor/run?patient_id=... -> run advisor on the saved text
- Deprecated:
  - POST /interviews/{patient_id} { content } -> manual write (use session endpoints instead)

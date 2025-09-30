import os
import uvicorn

# PUBLIC_INTERFACE
def main():
    """Entrypoint to run the FastAPI app with uvicorn.
    Respects environment variables:
    - PORT: port to bind (defaults to 3001 for container readiness)
    - HOST: host to bind (defaults to 0.0.0.0)
    - LOG_LEVEL: uvicorn log level (defaults to info)
    """
    host = os.getenv("HOST", "0.0.0.0")
    port_str = os.getenv("PORT", "3001")
    try:
        port = int(port_str)
    except ValueError:
        port = 3001
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    # medical_backend.src.api.main:app is the ASGI app path
    uvicorn.run(
        "medical_backend.src.api.main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=log_level,
        workers=int(os.getenv("WORKERS", "1")),
    )


if __name__ == "__main__":
    main()

# PUBLIC_INTERFACE
def get_app():
    """Return the FastAPI app instance for external import."""
    from .main import app
    return app

# Export default app for uvicorn path: medical_backend.src.api:app
from .main import app

__all__ = ["app", "get_app"]

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import patients, interviews, agents, files
from .routers import interview_session
from .core.logging_conf import configure_logging
from .core.config import get_settings
from .core.openapi import build_openapi, openapi_tags, swagger_ui_parameters


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler to initialize and gracefully shutdown application resources.
    Initializes logging and ensures storage directories exist.
    """
    # Configure logging once at startup
    configure_logging()
    settings = get_settings()
    # Ensure OneDrive-synced base directory exists
    os.makedirs(settings.ONEDRIVE_BASE_PATH, exist_ok=True)
    os.makedirs(settings.STORAGE_BASE_PATH, exist_ok=True)
    logging.getLogger("app").info("Application startup complete.")
    yield
    logging.getLogger("app").info("Application shutdown complete.")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with Ocean Professional theme,
    routers, CORS settings, and OpenAPI metadata.
    """
    settings = get_settings()

    app = FastAPI(
        title="Medical Insights Backend",
        description=(
            "Ocean Professional themed API for orchestrating medical agents. "
            "Features: Patient Interview Agent, Medical Advisor Agent (RAG), "
            "OneDrive-synced file I/O, rich logging, and clean modular design."
        ),
        version="0.1.0",
        contact={"name": "Medical Insights Team"},
        license_info={"name": "Proprietary"},
        lifespan=lifespan,
        swagger_ui_parameters=swagger_ui_parameters(),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(patients.router)
    app.include_router(interviews.router)
    app.include_router(interview_session.router)
    app.include_router(agents.router)
    app.include_router(files.router)

    # OpenAPI customizations
    app.openapi_tags = openapi_tags()
    app.openapi = build_openapi(app)

    # Health endpoint
    @app.get("/", tags=["health"], summary="Health Check", description="Simple liveness probe.")
    # PUBLIC_INTERFACE
    def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "theme": settings.THEME_NAME}

    # WebSocket usage help placeholder (document-only for now)
    @app.get(
        "/ws-info",
        tags=["realtime"],
        summary="WebSocket Info",
        description="This project currently exposes only REST endpoints. If WebSockets are added for real-time status streaming, documentation will appear here.",
    )
    # PUBLIC_INTERFACE
    def websocket_info() -> Dict[str, str]:
        """Describe websocket usage when available."""
        return {"message": "No websocket endpoints currently available."}

    return app


app = create_app()

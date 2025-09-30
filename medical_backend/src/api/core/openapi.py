from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .config import get_settings


def openapi_tags() -> List[Dict[str, Any]]:
    """
    Define OpenAPI tags grouped by domain.
    """
    # PUBLIC_INTERFACE
    return [
        {"name": "health", "description": "Health and diagnostics."},
        {"name": "patients", "description": "Patient profile management."},
        {"name": "interview-session", "description": "Agent-driven, chatbot-style patient interviews."},
        {"name": "agents", "description": "Agent orchestration endpoints."},
        {"name": "files", "description": "OneDrive-synced file operations."},
        {"name": "realtime", "description": "WebSocket usage hints."},
    ]


def swagger_ui_parameters() -> Dict[str, Any]:
    """
    Set Ocean Professional inspired swagger UI parameters.
    """
    # PUBLIC_INTERFACE
    return {
        "displayRequestDuration": True,
        "docExpansion": "list",
        "tryItOutEnabled": True,
        "persistAuthorization": True,
        # Theme hint via custom CSS url could be added in a full deployment.
    }


def build_openapi(app: FastAPI):
    """
    Build the OpenAPI schema once and cache it on the app.
    Adds theme metadata into components.extensions for clarity.

    Note:
    - Do NOT call app.openapi() here as it will point back to this function after override,
      causing recursion and a 500 at /openapi.json. Use fastapi.openapi.utils.get_openapi.
    """
    # PUBLIC_INTERFACE
    def _openapi():
        # Return cached schema if present
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema

        # Generate schema using FastAPI utility
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=openapi_tags(),
        )

        # Inject theme metadata
        theme = {
            "themeName": get_settings().THEME_NAME,
            "colors": {
                "primary": get_settings().THEME_PRIMARY,
                "secondary": get_settings().THEME_SECONDARY,
            },
            "style": "Modern minimalist with blue & amber accents",
        }
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        openapi_schema["components"]["x-theme"] = theme

        # Cache schema on app
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return _openapi

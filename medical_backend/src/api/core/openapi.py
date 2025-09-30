from typing import Any, Dict, List
from fastapi import FastAPI
from .config import get_settings


def openapi_tags() -> List[Dict[str, Any]]:
    """
    Define OpenAPI tags grouped by domain.
    """
    # PUBLIC_INTERFACE
    return [
        {"name": "health", "description": "Health and diagnostics."},
        {"name": "patients", "description": "Patient profile management."},
        {"name": "interviews", "description": "Patient interview sessions and transcripts."},
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
    """
    # PUBLIC_INTERFACE
    def _openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = app.openapi()
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
        return openapi_schema

    return _openapi

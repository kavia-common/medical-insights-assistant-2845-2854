import os
from functools import lru_cache
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.
    Note: Do not hardcode secrets. Ask orchestrator to provide values via .env.
    """
    THEME_NAME: str = Field(default="Ocean Professional", description="UI/Docs theme name.")
    THEME_PRIMARY: str = Field(default="#2563EB", description="Primary color (blue).")
    THEME_SECONDARY: str = Field(default="#F59E0B", description="Secondary color (amber).")

    # Storage paths (OneDrive-synced and local storage)
    # Defaults point to writable relative paths inside the application workspace to avoid permission errors
    # in environments where writing to /data is not allowed. These can be overridden via environment variables.
    ONEDRIVE_BASE_PATH: str = Field(default_factory=lambda: os.getenv("ONEDRIVE_BASE_PATH", os.path.abspath("./var/onedrive")))
    STORAGE_BASE_PATH: str = Field(default_factory=lambda: os.getenv("STORAGE_BASE_PATH", os.path.abspath("./var/storage")))

    # Vector DB connectivity (assumed provided by system design)
    VECTOR_DB_URL: str = Field(default_factory=lambda: os.getenv("VECTOR_DB_URL", "http://medical_vector_database:8000"))
    VECTOR_DB_API_KEY: str = Field(default_factory=lambda: os.getenv("VECTOR_DB_API_KEY", ""))

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
    )

    # Logging
    LOG_LEVEL: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retrieve cached Settings instance.
    """
    # PUBLIC_INTERFACE
    return Settings()
